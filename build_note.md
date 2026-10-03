# Phase 2: Build Note
**Client:** Dhaga & Co.  
**Engagement:** Mini Project 1 — Pattern-Based Workflow  
**Project:** Cataloging Pipeline Accelerator  
**Date:** October 3, 2026  
**Authors:** Five-Member Project Team  
**Scope:** Two Pages Maximum

---

## 1. The Code Versus Model Table

Every step in our system sits deliberately on either side of the code-model line. A model earns its place on judgment, cultural nuance, and unstructured mapping, not on arithmetic, exact lookups, or validation.

| Step | Pipeline Component | Execution Mode | Rationale (Why Code vs. Model?) |
| :---: | :--- | :---: | :--- |
| **1** | **Intake & Price Bound Validation** | **Deterministic Code** | Checking required columns, SKU ID formatting, and Dhaga's catalog price limits (₹399–₹1,499) is strict rule validation. A model call here would be wasteful and prone to hallucinated thresholds. |
| **2** | **Category & Taxonomy Routing** | **Cheap Model**<br>(`gemini-2.5-flash`, Temp: `0.0`) | Vendor category strings vary wildly ("girls ethnic party frock" vs "ladies daily anarkali"). Language understanding is required to map erratic titles to Dhaga's core departments (Womenswear, Kidswear, Menswear). |
| **3** | **Canonical Color Normalization** | **Deterministic Code**<br>(with normalized lookup) | Dhaga's catalogue suffered from ~90 different spellings for colors ("dusty gulabi", "deep royal navy"). Exact string normalization and canonical dictionary mapping solve 95%+ of cases deterministically without token cost. |
| **4** | **Hinglish Product Copy & Occasion Generation** | **Strong Model**<br>(`gemini-2.5-pro`, Temp: `0.7`) | Dhaga's customers are young women in Tier-2/Tier-3 cities searching in Hinglish by occasion ("mehndi function dress", "office wear kurti"). Synthesizing appealing brand copy and cultural search tags requires creative linguistic judgment. |
| **5** | **Structured Output Schema Enforcement** | **Deterministic Code**<br>(Pydantic validation) | Validating output types, enums, non-empty lists, and JSON boundaries must be strictly deterministic. Downstream code never parses loose free text. |
| **6** | **Evaluator-Optimizer Brand Guardrail** | **Strong Model**<br>(`gemini-2.5-pro`, Temp: `0.1`) | Detecting subtle, domain-specific contradictions (e.g. claiming an item is "100% denim silk velvet" or "wipe clean with oil") requires logical reasoning to catch bad vendor claims before they go live. |
| **7** | **Cost & Token Accounting** | **Deterministic Code** | Computing prompt and completion token totals, multiplying by OpenRouter rate cards, and projecting weekly batch economics is pure arithmetic. |

---

## 2. Why Each Pattern Is There (And What Breaks Without It)

Our pipeline combines three specific design patterns: **Routing**, **Prompt Chaining**, and **Evaluator-Optimizer**.

### A. Routing Pattern
* **Why It Is There:** Dhaga's inventory spans three distinct departments with different listing requirements: Womenswear (60% GMV, heavy occasion focus), Kidswear (30% GMV, sizing/durability focus), and Men's Basics (10% GMV, fit/utility focus). The Router inspects messy vendor intake and routes each item into its appropriate sub-category and department schema.
* **What Breaks Without It:** A monolithic prompt tries to handle everything at once, producing generic copy that misses department-specific nuances (e.g. treating a toddler frock like an adult wedding dress, or omitting school uniform tags).

### B. Prompt Chaining Pattern
* **Why It Is There:** Generating listing copy directly from raw vendor sheets in one single prompt forces the LLM to simultaneously extract messy specs, resolve color codes, determine wash care, and write creative copy. We chained the process into sequential steps:
  1. *Step 1:* Clean and extract raw garment attributes.
  2. *Step 2:* Map color deterministically.
  3. *Step 3:* Feed standardized attributes into the copy generator.
* **What Breaks Without It:** One-shot generation frequently hallucinates attributes (e.g. changing rayon to polyester) and suffers from cognitive drift, forgetting to include mandatory Hinglish occasion tags. Chaining ensures that creative copy is grounded strictly in validated attributes.

### C. Evaluator-Optimizer Guardrail Pattern
* **Why It Is There:** The brief's non-negotiable rule states: *"Anything customer-facing either has to be safe to publish unread, or has to have a human review step that you designed on purpose."* The Evaluator acts as an adversarial QA check, inspecting the generated title, fabric, and care notes for contradictions or impossible care instructions.
* **What Breaks Without It:** The system publishes contradictory listings (such as `DHG-999`'s "100% denim silk velvet") unread, eroding customer trust, generating return complaints, and embarrassing the brand. With the Evaluator, conflicting items fail visibly and are held in the Human Review Queue.

---

## 3. The Cost Line (The Arithmetic for the CTO)

Dev (CTO) asked: *"Whatever you build, somebody here has to run it on the Monday after you leave. Cost per action matters at 48,000 orders a week. A rupee is a rupee."*

### One Run (Single SKU) Cost Breakdown:
* **Cheap Model (`gemini-2.5-flash`):**
  * Input: ~250 tokens @ $0.075 / 1M = $0.00001875
  * Output: ~80 tokens @ $0.300 / 1M = $0.00002400
* **Strong Model (`gemini-2.5-pro`):**
  * Copy Generation: ~450 tokens in, ~180 tokens out = $0.00056250 + $0.00090000 = $0.00146250
  * Evaluator Guardrail: ~300 tokens in, ~60 tokens out = $0.00037500 + $0.00030000 = $0.00067500
* **Total API Cost per SKU:** **$0.00208 (~₹0.18 INR)**

### Scaled Volume Arithmetic (Dhaga's Actual 400 SKUs/Week):
* **Weekly API Compute Cost:** $400 \times ₹0.18 = \mathbf{₹72.00 \text{ / week}}$ ($~₹288 \text{ / month}$).
* **Current Manual Labor:** 6 listing agents spend ~15 minutes per SKU typing 60 attributes by hand = $400 \times 0.25 \text{ hrs} = \mathbf{100 \text{ hours/week}}$ (~₹25,000/week in listing labor).
* **With Cataloging MVP:** Listing staff spend ~2 minutes reviewing flagged items or confirming drafts = $400 \times 0.033 \text{ hrs} = \mathbf{13.3 \text{ hours/week}}$ (~₹3,333/week).
* **Net Financial Impact:** Saves **~86.7 listing team hours every week** and yields a **net labor saving of ~₹21,600/week (~₹1.03 Lakhs/month)** for an API cost of just ₹72/week.

---

## 4. The Thing That Broke That We Did Not Expect

### What Broke:
When testing with real-shaped vendor intake from Jaipur and Tiruppur, our initial implementation passed raw vendor color strings directly to an LLM prompt to "standardize the color." 

We expected the LLM to easily standardize colors like *"dusty gulabi"* or *"royal midnight navy blue"*. Instead, the model began creatively embellishing the colors:
* *"dusty gulabi"* was translated into *"Muted Rose Quartz Pink with Vintage Hues"*.
* *"light faded aasmaani"* became *"Ethereal Cerulean Morning Sky"*.

While poetic, this broke Dhaga's app filters completely. Dhaga's catalog search database requires one of **16 strict canonical color codes** (`RANI_PINK`, `SKY_BLUE`, `NAVY_BLUE`, etc.) so that customers tapping the "Pink" or "Blue" filter pills on low-end Android handsets can actually find the product. The LLM had generated 90 *new* poetic variations rather than solving the existing 90 variations!

### How We Fixed It:
We realized this was a violation of the **Code vs. Model Line**. Color normalization is a taxonomy mapping problem, not a creative writing task. We moved color normalization entirely into **deterministic code** (`core/color_normalizer.py`):
1. Built a dictionary of aliases mapping colloquial, Hindi, and English color names directly to the 16 canonical keys.
2. Used deterministic alias and regex whole-word matching.
3. If an input is truly unmapped or ambiguous, the code assigns `UNMAPPED_AMBIGUOUS`, which explicitly triggers the **Evaluator Guardrail** and routes the item to Vivek's human review queue with the warning: *"Color is ambiguous and could not be mapped to canonical taxonomy."*

This made color mapping **instantaneous, 100% reproducible, zero-cost in tokens**, and safe against creative drift.
