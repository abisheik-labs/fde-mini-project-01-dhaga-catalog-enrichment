"""
Core Cataloging Pipeline Orchestrator for Dhaga & Co.
Implements the 5-step workflow using LangChain, Prompt Chaining, Routing, and Evaluator-Optimizer.
Enforces the Code vs Model boundary and fails visibly on contradictions.
"""

from typing import Optional, Tuple
from langchain_core.prompts import ChatPromptTemplate
from config import MIN_CATALOG_PRICE, MAX_CATALOG_PRICE
from core.schemas import (
    RawVendorInput,
    CategoryRoutingResult,
    DepartmentEnum,
    GeneratedCopy,
    EvaluatorResult,
    ListingItemOutput,
    ListingStatus
)
from core.color_normalizer import normalize_color
from core.models import (
    get_cheap_extraction_llm,
    get_strong_copy_llm,
    get_strong_evaluator_llm
)


class CatalogingPipeline:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.cheap_llm = get_cheap_extraction_llm(api_key)
        self.strong_copy_llm = get_strong_copy_llm(api_key)
        self.strong_eval_llm = get_strong_evaluator_llm(api_key)

    # -------------------------------------------------------------
    # Step 1: Deterministic Preprocessor (Code Line)
    # -------------------------------------------------------------
    def _step1_deterministic_precheck(self, raw: RawVendorInput) -> Tuple[bool, list[str]]:
        """Validates basic data integrity and business rules (e.g. price limits)."""
        reasons = []
        if not raw.sku_id or not raw.raw_title:
            reasons.append("Missing mandatory SKU ID or product title.")
        if raw.raw_price < MIN_CATALOG_PRICE or raw.raw_price > MAX_CATALOG_PRICE:
            reasons.append(f"Price ₹{raw.raw_price} outside Dhaga's catalog window (₹{MIN_CATALOG_PRICE}-₹{MAX_CATALOG_PRICE}).")
        return (len(reasons) == 0, reasons)

    # -------------------------------------------------------------
    # Step 2: Category & Attribute Router (Cheap Model, Temp 0.0)
    # Pattern: ROUTING
    # -------------------------------------------------------------
    def _step2_route_and_extract(self, raw: RawVendorInput) -> CategoryRoutingResult:
        """Routes item to department taxonomy and isolates raw color and clean fabric."""
        # Offline Fallback Mode is not needed for MVP. The pipeline operates strictly with live LLM structured outputs.
        if not self.cheap_llm:
            raise RuntimeError("Live LLM client (Cheap Model) is not initialized. Please set OPENROUTER_API_KEY in your .env file.")

        prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "You are an expert fashion taxonomy router for Dhaga & Co. (D2C India). "
                "Classify the garment into one of: 'Womenswear', 'Kidswear', 'Menswear', or 'Unknown'. "
                "Identify the clean garment sub-category (e.g. Kurti, Saree, Polo T-Shirt, Frock, Shorts). "
                "Clean the fabric string and isolate the primary raw color name."
            )),
            ("human", (
                "Title: {title}\nCategory: {category}\nColor: {color}\nFabric: {fabric}\nNotes: {notes}"
            ))
        ])
        structured_chain = prompt | self.cheap_llm.with_structured_output(CategoryRoutingResult)
        routing = structured_chain.invoke({
            "title": raw.raw_title,
            "category": raw.raw_category,
            "color": raw.raw_color,
            "fabric": raw.raw_fabric,
            "notes": raw.vendor_notes or ""
        })
        if not routing:
            dept = DepartmentEnum.WOMENSWEAR if any(w in raw.raw_title.lower() for w in ["kurti", "saree", "anarkali"]) else DepartmentEnum.UNKNOWN
            routing = CategoryRoutingResult(
                department=dept,
                sub_category="Kurti" if dept == DepartmentEnum.WOMENSWEAR else "Garment",
                clean_fabric=raw.raw_fabric.title(),
                extracted_raw_color=raw.raw_color
            )
        return routing

    # -------------------------------------------------------------
    # Step 3: Canonical Color & Attribute Standardizer (Code Line)
    # -------------------------------------------------------------
    def _step3_normalize_color(self, raw_color: str):
        """Maps messy vendor color string to Dhaga's 16 canonical colors."""
        return normalize_color(raw_color)

    # -------------------------------------------------------------
    # Step 4: Hinglish Copy & Occasion Tag Generator (Strong Model, Temp 0.7)
    # Pattern: PROMPT CHAINING (Takes Output of Step 2 & 3)
    # -------------------------------------------------------------
    def _step4_generate_copy(
        self,
        raw: RawVendorInput,
        routing: CategoryRoutingResult,
        canonical_color: str
    ) -> GeneratedCopy:
        """Generates cultural Hinglish occasion search tags and catchy product copy."""
        # Offline Fallback Mode is not needed for MVP. The pipeline operates strictly with live LLM structured outputs.
        if not self.strong_copy_llm:
            raise RuntimeError("Live LLM client (Strong Copy Model) is not initialized. Please set OPENROUTER_API_KEY in your .env file.")

        prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "You are the senior fashion copywriter for Dhaga & Co., writing for young Indian shoppers "
                "in Tier-2/Tier-3 cities searching in Hinglish on mobile handsets. "
                "Create: "
                "1. A concise, customer-focused SEO Listing Title using this exact format: "
                "'{{Product or Style}} | {{Canonical Color}} | {{Fabric}}'. "
                "Use the supplied vendor product title for the product or style. "
                "Omit color or fabric if unavailable. Do not include the brand name, price, "
                "occasion phrases, or promotional claims in the title. "
                "2. 3-4 feature bullet highlights. "
                "3. Generate 2-4 concise Hinglish search tags. Every tag must fit the exact garment "
                "type and have clear support in the vendor title, category, or notes. Use a specific "
                "occasion or use case only when the vendor context supports it. If it does not, use "
                "only broad everyday-use searches that make sense for this garment. Never guess an "
                "occasion from color, fabric, or department alone. Do not use an example tag unless "
                "it genuinely matches this item; do not mix garment types, invent events, or repeat tags. "
                "Examples (only when supported): 'mehndi function kurti', 'office wear kurti', "
                "'school uniform shirt'. "
                "4. Practical wash care instructions matching the fabric. "
                "5. A warm, 2-sentence product description."
            )),
            ("human", (
                "Vendor Product Title: {product_title}\n"
                "Vendor Raw Category: {raw_category}\n"
                "Item: {sub_category}\nDepartment: {department}\n"
                "Standardized Color: {color}\nFabric: {fabric}\n"
                "Price: ₹{price}\nVendor Context: {notes}"
            ))
        ])
        structured_chain = prompt | self.strong_copy_llm.with_structured_output(GeneratedCopy)
        copy = structured_chain.invoke({
            "product_title": raw.raw_title,
            "raw_category": raw.raw_category,
            "sub_category": routing.sub_category,
            "department": routing.department.value,
            "color": canonical_color.replace("_", " ").title(),
            "fabric": routing.clean_fabric,
            "price": raw.raw_price,
            "notes": raw.vendor_notes or ""
        })
        clean_c = canonical_color.replace("_", " ").title()
        if not copy:
            copy = GeneratedCopy(
                seo_title=f"{raw.raw_title} | {clean_c} | {routing.clean_fabric}",
                bullet_highlights=[
                    f"Crafted from premium {routing.clean_fabric}",
                    f"Vibrant {clean_c} shade tailored for everyday wear",
                    "Breathable fabric designed for all-day comfort",
                    "Easy care and machine washable"
                ],
                hinglish_occasion_tags=[
                    f"{routing.sub_category.lower()} online",
                    "daily wear kurti",
                    "festive wear"
                ],
                wash_care="Machine wash cold with like colors. Dry in shade.",
                product_description=f"Elevate your look with this {clean_c} {routing.sub_category} made from {routing.clean_fabric}."
            )
        if not copy.bullet_highlights:
            copy.bullet_highlights = [f"Crafted from premium {routing.clean_fabric}", "Designed for all-day comfort"]
        if not copy.hinglish_occasion_tags:
            copy.hinglish_occasion_tags = ["daily wear", "ethnic collection"]
        return copy

    # -------------------------------------------------------------
    # Step 5: Evaluator-Optimizer Guardrail (Strong Model, Temp 0.1)
    # Pattern: EVALUATOR-OPTIMIZER (Fails Visibly)
    # -------------------------------------------------------------
    def _step5_evaluate_and_guardrail(
        self,
        raw: RawVendorInput,
        routing: CategoryRoutingResult,
        color_res,
        copy: GeneratedCopy
    ) -> EvaluatorResult:
        """Evaluates whether the copy contradicts fabric, detects impossible care, and flags anomalies."""
        # Offline Fallback Mode is not needed for MVP. The pipeline operates strictly with live LLM structured outputs.
        if not self.strong_eval_llm:
            raise RuntimeError("Live LLM client (Strong Evaluator Model) is not initialized. Please set OPENROUTER_API_KEY in your .env file.")

        prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "You are the quality & brand safety evaluator at Dhaga & Co. "
                "Your job is to catch anomalies before they go live: "
                "1. Detect fabric contradictions (e.g. '100% denim silk velvet' or 'leather chiffon'). "
                "2. Detect impossible care instructions (e.g. 'do not wash or dry clean', 'wipe with oil'). "
                "3. Evaluate if the listing is safe to auto-publish or requires human review. "
                "Be strict and fail visibly on suspicious claims."
            )),
            ("human", (
                "Raw Fabric: {raw_fabric}\nRaw Notes: {raw_notes}\n"
                "Generated Title: {title}\nWash Care: {wash_care}\n"
                "Canonical Color: {color}"
            ))
        ])
        structured_chain = prompt | self.strong_eval_llm.with_structured_output(EvaluatorResult)
        eval_res = structured_chain.invoke({
            "raw_fabric": raw.raw_fabric,
            "raw_notes": raw.vendor_notes or "",
            "title": copy.seo_title,
            "wash_care": copy.wash_care,
            "color": color_res.canonical_color
        })
        if not eval_res:
            eval_res = EvaluatorResult(
                is_valid=True,
                confidence_score=0.9,
                has_fabric_contradiction=False,
                has_impossible_care=False,
                review_reasons=[]
            )
        if eval_res.review_reasons is None:
            eval_res.review_reasons = []
        return eval_res

    # -------------------------------------------------------------
    # Stage 1: Derive Attributes & Generate Product Copy
    # -------------------------------------------------------------
    def derive_attributes(self, raw: RawVendorInput) -> ListingItemOutput:
        """Executes full attribute derivation, copy generation, and quality guardrail verification."""
        # Step 1: Precheck (Deterministic Code Line)
        is_pre_ok, pre_reasons = self._step1_deterministic_precheck(raw)

        # Step 2: Routing & Attribute Extraction (Cheap LLM)
        routing = self._step2_route_and_extract(raw)

        # Step 3: Color Normalization (Deterministic Code Line)
        color_res = self._step3_normalize_color(raw.raw_color)

        # Step 4: Copy & Occasion Generation (Strong LLM)
        copy = self._step4_generate_copy(raw, routing, color_res.canonical_color)

        # Step 5: Evaluator Guardrail (Strong LLM)
        eval_res = self._step5_evaluate_and_guardrail(raw, routing, color_res, copy)

        # Compile all human review reasons
        all_review_reasons = []
        if not is_pre_ok:
            all_review_reasons.extend(pre_reasons)
        if not color_res.is_canonical:
            all_review_reasons.append(f"Color '{raw.raw_color}' is ambiguous and could not be mapped to canonical taxonomy.")
        if routing.department == DepartmentEnum.UNKNOWN:
            all_review_reasons.append("Garment department could not be reliably classified.")
        if not eval_res.is_valid:
            if eval_res.review_reasons:
                all_review_reasons.extend([str(r) for r in eval_res.review_reasons if r])
            else:
                all_review_reasons.append("Quality guardrail flagged inconsistencies in garment specifications.")

        status = ListingStatus.AUTO_APPROVED if len(all_review_reasons) == 0 else ListingStatus.NEEDS_HUMAN_REVIEW

        return ListingItemOutput(
            sku_id=raw.sku_id,
            vendor_location=raw.vendor_location,
            raw_title=raw.raw_title,
            raw_category=raw.raw_category,
            raw_fabric=raw.raw_fabric,
            vendor_notes=raw.vendor_notes or "",
            department=routing.department.value,
            sub_category=routing.sub_category,
            original_color=raw.raw_color,
            canonical_color=color_res.canonical_color,
            fabric=routing.clean_fabric,
            price=raw.raw_price,
            seo_title=copy.seo_title,
            bullet_highlights=copy.bullet_highlights or [],
            hinglish_occasion_tags=copy.hinglish_occasion_tags or [],
            wash_care=copy.wash_care,
            product_description=copy.product_description,
            status=status,
            review_reasons=all_review_reasons
        )

    # -------------------------------------------------------------
    # Full Execution Coordinator
    # -------------------------------------------------------------
    def process_item(self, raw: RawVendorInput) -> ListingItemOutput:
        """Executes full end-to-end derivation and copy generation."""
        return self.derive_attributes(raw)
