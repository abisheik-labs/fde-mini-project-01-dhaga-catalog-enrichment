"""Integration tests for the CatalogingPipeline and Evaluator Guardrail."""

import pytest
from langchain_core.runnables import RunnableLambda
from core.schemas import (
    CategoryRoutingResult,
    DepartmentEnum,
    GeneratedCopy,
    RawVendorInput,
    ListingStatus,
)
from core.pipeline import CatalogingPipeline
from core.cost_tracker import CostTracker


def test_occasion_tag_prompt_grounds_tags_in_vendor_context():
    pipeline = CatalogingPipeline()
    captured = {}
    generated_copy = GeneratedCopy(
        seo_title="Anarkali Kurti | Rani Pink | Slub Rayon",
        bullet_highlights=["Lightweight fabric", "Gotapatti detailing", "Anarkali silhouette"],
        hinglish_occasion_tags=["mehndi function kurti"],
        wash_care="Gentle hand wash.",
        product_description="A festive kurti with delicate detailing. Style it for family celebrations."
    )

    class StubCopyModel:
        def with_structured_output(self, _schema):
            return RunnableLambda(
                lambda prompt_value: captured.update({"messages": prompt_value.messages}) or generated_copy
            )

    pipeline.strong_copy_llm = StubCopyModel()
    result = pipeline._step4_generate_copy(
        RawVendorInput(
            sku_id="DHG-101",
            vendor_location="Jaipur",
            raw_title="Anarkali Kurti with Gotapatti",
            raw_category="womens kurtis",
            raw_color="dusty gulabi",
            raw_fabric="100% pure slub rayon with foil work",
            raw_price=799.0,
            vendor_notes="popular for mehndi and family functions"
        ),
        CategoryRoutingResult(
            department=DepartmentEnum.WOMENSWEAR,
            sub_category="Kurti",
            clean_fabric="Slub rayon",
            extracted_raw_color="dusty gulabi"
        ),
        "RANI_PINK"
    )

    prompt_messages = captured["messages"]
    system_prompt = prompt_messages[0].content
    human_prompt = prompt_messages[1].content
    assert "clear support in the vendor title, category, or notes" in system_prompt
    assert "Never guess an occasion from color, fabric, or department alone" in system_prompt
    assert "Vendor Raw Category: womens kurtis" in human_prompt
    assert "Vendor Context: popular for mehndi and family functions" in human_prompt
    assert result.hinglish_occasion_tags == ["mehndi function kurti"]


def test_pipeline_happy_path():
    pipeline = CatalogingPipeline()
    happy_item = RawVendorInput(
        sku_id="DHG-101",
        vendor_location="Jaipur",
        raw_title="Anarkali Kurti with Gotapatti",
        raw_category="womens kurtis",
        raw_color="dusty gulabi",
        raw_fabric="100% pure slub rayon with foil work",
        raw_price=799.0,
        vendor_notes="popular for mehndi and family functions"
    )

    output = pipeline.process_item(happy_item)
    assert output.sku_id == "DHG-101"
    assert output.status == ListingStatus.AUTO_APPROVED
    assert output.canonical_color == "RANI_PINK"
    assert len(output.hinglish_occasion_tags) > 0
    assert output.seo_title != ""
    assert output.department == "Womenswear"
    assert output.sub_category != ""


def test_pipeline_intentional_failure_case():
    """
    Tests the mandatory intentional failure case:
    Contradictory fabric ('denim' and 'silk') + impossible care instructions.
    Must fail visibly and set status to NEEDS_HUMAN_REVIEW.
    """
    pipeline = CatalogingPipeline()
    failure_item = RawVendorInput(
        sku_id="DHG-999",
        vendor_location="Jaipur",
        raw_title="Conflicted Spec Kurti Sample",
        raw_category="unknown",
        raw_color="weird mixture blend",
        raw_fabric="100% heavy denim silk velvet",
        raw_price=450.0,
        vendor_notes="do not wash do not dry clean tight oversized fit"
    )

    output = pipeline.process_item(failure_item)
    assert output.sku_id == "DHG-999"
    assert output.status == ListingStatus.NEEDS_HUMAN_REVIEW
    assert len(output.review_reasons) > 0
    # Must flag fabric contradiction and bad care
    reasons_str = " ".join(output.review_reasons).lower()
    assert "contradictory" in reasons_str or "unusable care" in reasons_str or "ambiguous" in reasons_str


def test_cost_arithmetic_volume():
    proj = CostTracker.calculate_volume_projections(avg_cost_inr_per_sku=0.18)
    assert proj["weekly_skus"] == 400
    assert proj["weekly_api_cost_inr"] == 72.0
    assert proj["weekly_hours_saved"] > 80.0
    assert proj["weekly_labor_saved_inr"] > 20000.0
