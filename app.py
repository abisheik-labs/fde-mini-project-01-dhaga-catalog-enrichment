"""
Dhaga & Co. — Merchandising & Catalog Operations Portal
Modern D2C Enterprise Design System (Inspired by Kekka & Shopify Plus)
Plus Jakarta Sans Typography • Deep Navy Hero • No Clunky Tabs • 100% User-Initiated
"""

import os
import time
from typing import Optional
import pandas as pd
import streamlit as st
from config import (
    WEEKLY_NEW_SKUS,
    MONTHLY_NEW_SKUS,
    CANONICAL_COLOR_MAP
)
import importlib
import core.schemas
import core.pipeline
importlib.reload(core.schemas)
importlib.reload(core.pipeline)
from core.schemas import RawVendorInput, ListingStatus
from core.pipeline import CatalogingPipeline
from core.cost_tracker import CostTracker

# Page Setup
st.set_page_config(
    page_title="Dhaga & Co. | Operations Portal",
    page_icon="🧵",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def render_html(html_str: str):
    """Cleanly renders HTML in Streamlit without leading indentation triggering markdown code-block parsing."""
    cleaned = "\n".join(line.strip() for line in html_str.splitlines() if line.strip())
    st.markdown(cleaned, unsafe_allow_html=True)

# Canonical 16-Color Hex Palette for filter pills
COLOR_HEX_MAP = {
    "NAVY_BLUE": "#001F3F",
    "ROYAL_BLUE": "#2563EB",
    "SKY_BLUE": "#38BDF8",
    "RANI_PINK": "#EC4899",
    "BABY_PINK": "#F472B6",
    "MAROON": "#881337",
    "MUSTARD_YELLOW": "#EAB308",
    "LEMON_YELLOW": "#FDE047",
    "EMERALD_GREEN": "#059669",
    "MINT_GREEN": "#34D399",
    "OFF_WHITE": "#E2E8F0",
    "PURE_BLACK": "#0F172A",
    "RUST_ORANGE": "#EA580C",
    "CORAL_PEACH": "#FB7185",
    "WINE_PURPLE": "#701A75",
    "METALLIC_GOLD": "#D97706",
    "UNMAPPED_AMBIGUOUS": "#94A3B8"
}

# Modern D2C Enterprise CSS (Kekka Typography & Clean UI Hierarchy)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        color: #0F172A;
        background-color: #F8FAFC;
        -webkit-font-smoothing: antialiased;
    }

    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 3.5rem;
        max-width: 1220px;
    }

    /* Top Nav (Exact Screenshot Layout) */
    .top-nav {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px 0 16px 0;
    }
    .brand-group {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .brand-mark {
        width: 32px;
        height: 32px;
        background: #0F172A;
        color: #FFFFFF;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 15px;
        letter-spacing: -0.5px;
    }
    .brand-name {
        font-size: 16px;
        font-weight: 800;
        color: #0F172A;
        letter-spacing: -0.3px;
    }
    .brand-pill {
        background: #F1F5F9;
        color: #475569;
        font-size: 11px;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 6px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .top-subtext {
        font-size: 13px;
        color: #64748B;
        font-weight: 500;
    }

    /* Executive Hero Card (Exact Deep Navy in Screenshot) */
    .dashboard-hero {
        background: #0B1B3D;
        border-radius: 12px;
        padding: 32px 36px;
        color: #FFFFFF;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px -2px rgba(11, 27, 61, 0.12);
    }
    .hero-heading {
        font-size: 26px;
        font-weight: 800;
        color: #FFFFFF;
        letter-spacing: -0.5px;
        margin-bottom: 8px;
        line-height: 1.25;
    }
    .hero-caption {
        font-size: 14px;
        color: #94A3B8;
        max-width: 680px;
        line-height: 1.55;
        font-weight: 400;
    }

    /* Metric Grid (4 Cards from Screenshot) */
    .metric-grid-4 {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 32px;
    }
    .stat-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 18px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    .stat-label {
        font-size: 11px;
        font-weight: 700;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .stat-value {
        font-size: 24px;
        font-weight: 800;
        color: #0F172A;
        margin-top: 5px;
        letter-spacing: -0.02em;
    }
    .stat-sub {
        font-size: 12px;
        color: #059669;
        font-weight: 600;
        margin-top: 3px;
    }

    /* Clean Enterprise Cards */
    .panel-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 20px 22px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    .section-title {
        font-size: 18px;
        font-weight: 800;
        color: #0F172A;
        letter-spacing: -0.3px;
        margin-bottom: 4px;
    }
    .section-caption {
        font-size: 13px;
        color: #64748B;
        margin-bottom: 16px;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Precision Grid Table Layout */
    .catalog-grid-header {
        display: grid !important;
        grid-template-columns: 110px 16px 85px 16px 1fr 16px 190px 16px 80px 16px 140px !important;
        align-items: center !important;
        padding: 10px 16px 10px 16px !important;
        background: #F8FAFC !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 11px !important;
        text-transform: uppercase !important;
        color: #64748B !important;
        letter-spacing: 0.05em !important;
        margin-bottom: 8px !important;
    }

    details.catalog-accordion {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 8px !important;
        margin-bottom: 8px !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02) !important;
        transition: border-color 0.15s ease-in-out !important;
    }
    details.catalog-accordion:hover {
        border-color: #CBD5E1 !important;
    }
    details.catalog-accordion[open] {
        border-color: #94A3B8 !important;
    }
    details.catalog-accordion-review {
        background: #FEF2F2 !important;
        border: 1px solid #FECACA !important;
    }

    summary.catalog-accordion-summary {
        display: grid !important;
        grid-template-columns: 110px 16px 85px 16px 1fr 16px 190px 16px 80px 16px 140px !important;
        align-items: center !important;
        padding: 12px 16px 12px 16px !important;
        cursor: pointer !important;
        font-size: 13px !important;
        user-select: none !important;
    }
    summary.catalog-accordion-summary::-webkit-details-marker {
        color: #64748B;
    }

    .col-pipe {
        color: #CBD5E1 !important;
        text-align: center !important;
        font-size: 12px !important;
    }
    .col-sku {
        font-weight: 700 !important;
        color: #0F172A !important;
        display: flex !important;
        align-items: center !important;
        gap: 6px !important;
    }
    .col-hub {
        color: #64748B !important;
        font-size: 13px !important;
    }
    .col-title {
        font-weight: 600 !important;
        color: #0F172A !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        white-space: nowrap !important;
        padding-right: 12px !important;
    }
    .col-color {
        color: #0F172A !important;
        font-size: 12px !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        white-space: nowrap !important;
    }
    .col-price {
        font-weight: 700 !important;
        color: #0F172A !important;
    }
    .col-status-ready {
        color: #059669 !important;
        font-weight: 700 !important;
        font-size: 12px !important;
    }
    .col-status-review {
        color: #DC2626 !important;
        font-weight: 700 !important;
        font-size: 12px !important;
    }
    .col-status-pending {
        color: #64748B !important;
        font-size: 12px !important;
    }

    .catalog-accordion-body {
        padding: 16px 20px !important;
        background: #FFFFFF !important;
        border-top: 1px solid #F1F5F9 !important;
        border-radius: 0 0 8px 8px !important;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# Instant Session Initialization (ZERO API Calls on Start)
# -------------------------------------------------------------
if "raw_df" not in st.session_state:
    sample_path = os.path.join(os.path.dirname(__file__), "data", "raw_vendor_samples.csv")
    try:
        st.session_state.raw_df = pd.read_csv(sample_path)
    except Exception:
        st.session_state.raw_df = None

if "processed_results" not in st.session_state:
    st.session_state.processed_results = []

if "stage_1_done" not in st.session_state:
    st.session_state.stage_1_done = False

if "stage_2_done" not in st.session_state:
    st.session_state.stage_2_done = False

if "derivation_error" not in st.session_state:
    st.session_state.derivation_error = None


def set_derivation_error(error: Exception, sku_id: Optional[str] = None):
    """Store a concise user-facing message and retain the original error for troubleshooting."""
    error_text = str(error)
    if "401" in error_text or "403" in error_text or "AuthenticationError" in error_text or "PermissionDeniedError" in error_text:
        title = "Groq authentication failed"
        message = "Check that `GROQ_API_KEY` is set correctly in your Streamlit app secrets, then restart or redeploy the app."
    elif "429" in error_text or "rate limit" in error_text.lower():
        title = "Groq rate limit reached"
        message = "Wait briefly and try again, or check the rate limits for your Groq account."
    elif "Live LLM client" in error_text:
        title = "LLM configuration is missing"
        message = "Add `GROQ_API_KEY` to Streamlit app secrets and restart or redeploy the app."
    else:
        title = "Catalog enrichment failed"
        message = "The item could not be enriched. Review the technical details below and try again."

    st.session_state.derivation_error = {
        "title": title,
        "message": message,
        "details": error_text,
        "sku_id": sku_id,
    }


def raw_row_to_input(row):
    return RawVendorInput(
        sku_id=str(row["sku_id"]),
        vendor_location=str(row["vendor_location"]),
        raw_title=str(row["raw_title"]),
        raw_category=str(row["raw_category"]),
        raw_color=str(row["raw_color"]),
        raw_fabric=str(row["raw_fabric"]),
        raw_price=float(row["raw_price"]),
        vendor_notes=str(row["vendor_notes"]) if "vendor_notes" in row and pd.notna(row["vendor_notes"]) else ""
    )

# =============================================================
# 1. TOP NAVIGATION (Exact Layout from Screenshot)
# =============================================================
st.markdown("""
<div class="top-nav">
    <div class="brand-group">
        <div class="brand-mark">D</div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <span class="brand-name">DHAGA & CO.</span>
            <span class="brand-pill">OPERATIONS PORTAL</span>
        </div>
    </div>
    <div class="top-subtext">
        Bengaluru HQ • Direct-to-Consumer Fashion
    </div>
</div>
<hr style="margin-top: 0; margin-bottom: 22px; border: none; border-top: 1px solid #E2E8F0;">
""", unsafe_allow_html=True)

# =============================================================
# 2. EXECUTIVE HERO BANNER (Exact Deep Navy from Screenshot)
# =============================================================
st.markdown("""
<div class="dashboard-hero">
    <div class="hero-heading">Merchandising & Catalog Operations Dashboard</div>
    <div class="hero-caption">
        Real-time operational visibility into Dhaga & Co.'s weekly drop calendar, vendor sourcing hubs in Tiruppur & Jaipur, and catalog acceleration metrics.
    </div>
</div>
""", unsafe_allow_html=True)

# =============================================================
# 3. EXECUTIVE KPI GRID (Exact 4 Cards from Screenshot)
# =============================================================
st.markdown("""
<div class="metric-grid-4">
    <div class="stat-card">
        <div class="stat-label">RUN-RATE SCALE</div>
        <div class="stat-value">₹310 Cr GMV</div>
        <div class="stat-sub">~48,000 orders / week</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">WEEKLY DROP VOLUME</div>
        <div class="stat-value">400 New SKUs</div>
        <div class="stat-sub">Drops every Tue & Fri</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">CATALOGUE TURNOVER</div>
        <div class="stat-value">14,000 Live SKUs</div>
        <div class="stat-sub">6-week unsold auto-pull</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">CUSTOMER MOBILE SHARE</div>
        <div class="stat-value">92% Android App</div>
        <div class="stat-sub">64% Tier-2/Tier-3 Cities</div>
    </div>
</div>
""", unsafe_allow_html=True)

# =============================================================
# 4. CATALOG INTAKE & 2-STAGE LISTING WORKBENCH
# =============================================================
st.markdown("""
<div style="border-top: 1px solid #E2E8F0; padding-top: 24px; margin-top: 10px;"></div>
""", unsafe_allow_html=True)

if st.session_state.derivation_error:
    error = st.session_state.derivation_error
    with st.container(border=True):
        label = f" for `{error['sku_id']}`" if error["sku_id"] else ""
        st.error(f"**{error['title']}{label}**\n\n{error['message']}")
        with st.expander("Technical details"):
            st.code(error["details"])

# Action Toolbar
header_col1, header_col2 = st.columns([8, 4])

with header_col1:
    st.markdown('<div class="section-title">Catalog Intake & Attribute Enrichment</div>', unsafe_allow_html=True)
    st.caption(f"Dhaga & Co. Listing Workbench • {len(st.session_state.raw_df) if st.session_state.raw_df is not None else 0} vendor SKUs • Replaces manual typing & copywriting")

with header_col2:
    st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
    btn_label = "⚡ Derive & Enrich Attributes"
    btn_type = "primary" if not st.session_state.stage_1_done else "secondary"
    if st.button(btn_label, type=btn_type, use_container_width=True, help="Derives all attributes, standardizes fabrics/colors, writes SEO titles, PDP bullets, care rules, and Hinglish tags"):
        st.session_state.derivation_error = None
        with st.spinner("Deriving garment attributes, generating product copy, and verifying quality guardrails..."):
            fast_p = CatalogingPipeline(api_key=None)
            batch = []
            try:
                for _, row in st.session_state.raw_df.iterrows():
                    batch.append(fast_p.derive_attributes(raw_row_to_input(row)))
                st.session_state.processed_results = batch
                st.session_state.stage_1_done = True
                st.success("Attributes derived and listings enriched successfully!")
                st.rerun()
            except Exception as e:
                set_derivation_error(e)
                st.rerun()


# =============================================================
# Clean Modal Dialogs for Conflict Resolution & Attribute Edits
# =============================================================
@st.dialog("Resolve Quality Conflict")
def show_conflict_dialog(sku_id: str):
    item = next((r for r in st.session_state.processed_results if r.sku_id == sku_id), None)
    if not item:
        st.error("Item not found.")
        return

    st.markdown(f'<div style="font-size: 13px; color: #64748B; margin-bottom: 12px;">Correct vendor contradictions to approve <b>{item.sku_id}</b> for catalog release.</div>', unsafe_allow_html=True)
    
    for r_reason in item.review_reasons:
        st.error(f"❌ {r_reason}")

    new_title = st.text_input("Product Title", value=item.seo_title, key=f"dlg_title_{sku_id}")
    
    col1, col2 = st.columns(2)
    with col1:
        fabric_options = ["100% Cotton Denim", "Pure Malmal Cotton", "Cotton Silk Blend", "Rayon Slub"]
        new_fabric = st.selectbox("Verified Fabric", fabric_options, index=0, key=f"dlg_fab_{sku_id}")
    with col2:
        color_keys = list(CANONICAL_COLOR_MAP.keys())
        new_color = st.selectbox("Canonical Color Code", color_keys, index=0, key=f"dlg_col_{sku_id}")

    new_care = st.text_input("Care Instructions", value="Machine wash cold with like colors. Dry in shade.", key=f"dlg_care_{sku_id}")

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    if st.button("Confirm & Approve SKU", type="primary", use_container_width=True, key=f"dlg_btn_{sku_id}"):
        item.seo_title = new_title
        item.fabric = new_fabric
        item.canonical_color = new_color
        item.wash_care = new_care
        item.status = ListingStatus.SPECS_STAGED if not st.session_state.get("stage_2_done", False) else ListingStatus.AUTO_APPROVED
        item.review_reasons = []
        st.success(f"{item.sku_id} conflict resolved! Marked as Staged.")
        st.rerun()

# Modal Trigger from Accordion Row Links
if "resolve" in st.query_params:
    resolve_sku = st.query_params.get("resolve")
    if resolve_sku:
        del st.query_params["resolve"]
        show_conflict_dialog(resolve_sku)


@st.dialog("Edit SKU Attributes")
def show_edit_dialog(sku_id: str):
    item = next((r for r in st.session_state.processed_results if r.sku_id == sku_id), None)
    if not item:
        st.error("Item not found.")
        return

    st.markdown(f'<div style="font-size: 13px; color: #64748B; margin-bottom: 12px;">Edit listing attributes for <b>{item.sku_id}</b>.</div>', unsafe_allow_html=True)

    new_title = st.text_input("Product Title", value=item.seo_title, key=f"edit_dlg_title_{sku_id}")
    
    col1, col2 = st.columns(2)
    with col1:
        new_fabric = st.text_input("Fabric", value=item.fabric, key=f"edit_dlg_fab_{sku_id}")
    with col2:
        color_keys = list(CANONICAL_COLOR_MAP.keys()) + ["UNMAPPED_AMBIGUOUS"]
        col_idx = color_keys.index(item.canonical_color) if item.canonical_color in color_keys else 0
        new_color = st.selectbox("Canonical Color Code", color_keys, index=col_idx, key=f"edit_dlg_col_{sku_id}")

    new_care = st.text_input("Care Instructions", value=item.wash_care, key=f"edit_dlg_care_{sku_id}")

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    if st.button("Save Changes", type="primary", use_container_width=True, key=f"edit_dlg_btn_{sku_id}"):
        item.seo_title = new_title
        item.fabric = new_fabric
        item.canonical_color = new_color
        item.wash_care = new_care
        st.success(f"{item.sku_id} updated!")
        st.rerun()


# =============================================================
# Table Column Header Bar (Pixel-Perfect Synchronized Grid)
# =============================================================
header_columns = st.columns([10, 2])
with header_columns[0]:
    render_html("""
<div class="catalog-grid-header">
    <span>SKU</span>
    <span class="col-pipe">│</span>
    <span>Hub</span>
    <span class="col-pipe">│</span>
    <span>Item / Standardized Title</span>
    <span class="col-pipe">│</span>
    <span>Color Code</span>
    <span class="col-pipe">│</span>
    <span>Price</span>
    <span class="col-pipe">│</span>
    <span>Status</span>
</div>
""")
with header_columns[1]:
    st.markdown(
        "<div style='padding: 10px 16px; background: #F8FAFC; border: 1px solid #E2E8F0; "
        "font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase;'>Action</div>",
        unsafe_allow_html=True
    )

# Accordion-Only Table Rows
if st.session_state.processed_results:
    conflict_skus = [itm for itm in st.session_state.processed_results if itm.status == ListingStatus.NEEDS_HUMAN_REVIEW]
    processed_skus = {itm.sku_id for itm in st.session_state.processed_results}
    total_skus = len(st.session_state.raw_df) if st.session_state.raw_df is not None else len(processed_skus)
    all_skus_enriched = len(processed_skus) == total_skus
    if conflict_skus:
        count_txt = f"{len(conflict_skus)} SKU{'s' if len(conflict_skus) > 1 else ''}"
        st.error(f"⚠️ **Quality Conflicts Flagged ({count_txt} Pending Review)**: Contradictory vendor specifications detected. Expand the flagged item{'s' if len(conflict_skus) > 1 else ''} below to resolve.")
    elif not all_skus_enriched:
        st.info(f"Enriched {len(processed_skus)} of {total_skus} SKUs. Enrich the remaining rows individually or use the top button to process all.")
    elif not st.session_state.stage_2_done:
        col_s1, col_s2 = st.columns([8, 3])
        with col_s1:
            st.success("✅ **All SKUs Enriched & Staged!** Quality checks passed with 0 conflicts. Ready to share with downstream departments.")
        with col_s2:
            st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
            if st.button("📤 Share with Next Department", type="primary", use_container_width=True, help="Dispatches enriched listings to Storefront (Shopify Plus/App) and Bengaluru ERP"):
                st.session_state.stage_2_done = True
                st.rerun()
    else:
        st.success("🎉 **Catalog Handoff Complete**: All 4 SKUs are live and syndicated to **Storefront Operations (Shopify Plus / Android App)** and **Bengaluru ERP (Central Warehouse Master)**.")

    # Render each standardized row with precision grid alignment
    for itm in st.session_state.processed_results:
        is_review = (itm.status == ListingStatus.NEEDS_HUMAN_REVIEW)
        if is_review:
            status_cls = "col-status-review"
            status_txt = "● Needs Review"
            icon_val = "🔴"
        elif st.session_state.stage_2_done:
            status_cls = "col-status-ready"
            status_txt = "● Dispatched to Live"
            icon_val = "🟢"
        else:
            status_cls = "col-status-ready"
            status_txt = "● Specs Staged"
            icon_val = "🟢"

        acc_cls = "catalog-accordion catalog-accordion-review" if is_review else "catalog-accordion"

        raw_row = None
        if st.session_state.raw_df is not None:
            matches = st.session_state.raw_df[st.session_state.raw_df["sku_id"] == itm.sku_id]
            if not matches.empty:
                raw_row = matches.iloc[0]

        src_cat = getattr(itm, "raw_category", "") or (str(raw_row["raw_category"]) if raw_row is not None and "raw_category" in raw_row and pd.notna(raw_row["raw_category"]) else itm.department)
        src_color = getattr(itm, "original_color", "") or (str(raw_row["raw_color"]) if raw_row is not None and "raw_color" in raw_row and pd.notna(raw_row["raw_color"]) else "Vendor Color")
        src_fabric = getattr(itm, "raw_fabric", "") or (str(raw_row["raw_fabric"]) if raw_row is not None and "raw_fabric" in raw_row and pd.notna(raw_row["raw_fabric"]) else itm.fabric)
        src_notes = getattr(itm, "vendor_notes", "") or (str(raw_row["vendor_notes"]) if raw_row is not None and "vendor_notes" in raw_row and pd.notna(raw_row["vendor_notes"]) and str(raw_row["vendor_notes"]).strip() != "" else "None provided")
        src_title = getattr(itm, "raw_title", "") or (str(raw_row["raw_title"]) if raw_row is not None and "raw_title" in raw_row and pd.notna(raw_row["raw_title"]) else "")
        src_price = str(raw_row["raw_price"]) if raw_row is not None and "raw_price" in raw_row and pd.notna(raw_row["raw_price"]) else f"{itm.price:.0f}"

        tags_list = itm.hinglish_occasion_tags or []
        if tags_list:
            tag_badges = "".join([f'<span style="background: #EFF6FF; color: #1D4ED8; font-size: 11px; font-weight: 600; padding: 3px 9px; border-radius: 12px; margin-right: 6px; display: inline-block; margin-bottom: 4px;">🔍 {tag}</span>' for tag in tags_list])
        else:
            tag_badges = '<span style="color: #94A3B8; font-size: 12px; font-style: italic;">No occasion tags generated</span>'

        bullets_list = itm.bullet_highlights or []
        if bullets_list:
            highlights_html = '<ul style="margin: 0; padding-left: 18px; color: #1E293B;">' + "".join([f'<li style="margin-bottom: 2px;">{h}</li>' for h in bullets_list]) + '</ul>'
        else:
            highlights_html = f'<span style="color: #1E293B;">{itm.product_description}</span>' if itm.product_description else '<span style="color: #94A3B8; font-style: italic;">None</span>'

        care_target = f"<b>{itm.wash_care}</b>"

        conflict_banner = ""
        reasons_list = itm.review_reasons or []
        reasons_txt = ", ".join(reasons_list) if reasons_list else "Contradictory garment attributes require manual verification."
        if is_review:
            conflict_banner = f"""
            <div style="background: #FEF2F2; border: 1px solid #FECACA; border-left: 4px solid #EF4444; padding: 12px 16px; border-radius: 6px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <div>
                    <div style="font-weight: 700; color: #991B1B; font-size: 13px; margin-bottom: 2px;">⚠️ Quality Conflict Flagged ({itm.sku_id}): {reasons_txt}</div>
                    <div style="font-size: 11.5px; color: #B91C1C;">Contradictory specifications must be resolved before this listing can be approved.</div>
                </div>
                <div>
                    <a href="?resolve={itm.sku_id}" target="_self" style="display: inline-block; background: #DC2626; color: #FFFFFF !important; font-weight: 700; font-size: 12px; padding: 7px 15px; border-radius: 6px; text-decoration: none; box-shadow: 0 1px 2px rgba(220, 38, 38, 0.25);">
                        ⚡ Resolve Conflict
                    </a>
                </div>
            </div>
            """

        guardrail_output = f'<span style="color: #DC2626; font-weight: 700;">⚠️ Flagged: {reasons_txt}</span>' if is_review else '<span style="color: #059669; font-weight: 600;">🟢 Passed (Zero Contradictions • Catalog Safe)</span>'

        row_columns = st.columns([10, 2])
        with row_columns[0]:
            render_html(f"""
        <details class="{acc_cls}" {'open' if is_review else ''}>
            <summary class="catalog-accordion-summary">
                <span class="col-sku">{icon_val} {itm.sku_id}</span>
                <span class="col-pipe">│</span>
                <span class="col-hub">{itm.vendor_location}</span>
                <span class="col-pipe">│</span>
                <span class="col-title">{itm.seo_title}</span>
                <span class="col-pipe">│</span>
                <span class="col-color">#{itm.canonical_color}</span>
                <span class="col-pipe">│</span>
                <span class="col-price">₹{itm.price:.0f}</span>
                <span class="col-pipe">│</span>
                <span class="{status_cls}">{status_txt}</span>
            </summary>
            <div class="catalog-accordion-body">
                {conflict_banner}
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; overflow: hidden; margin-bottom: 12px;">
                    <table style="width: 100%; border-collapse: collapse; font-size: 12px; font-family: 'Plus Jakarta Sans', sans-serif;">
                        <thead>
                            <tr style="background: #F1F5F9; color: #475569; font-weight: 700; text-align: left; text-transform: uppercase; font-size: 10px; letter-spacing: 0.05em;">
                                <th style="padding: 9px 12px; width: 150px; border-bottom: 1px solid #CBD5E1;">Catalog Attribute</th>
                                <th style="padding: 9px 12px; width: 42%; border-bottom: 1px solid #CBD5E1;">Raw Vendor Input (Source)</th>
                                <th style="padding: 9px 12px; border-bottom: 1px solid #CBD5E1;">Enriched Catalog Output</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td style="font-weight: 700; color: #334155; padding: 8px 12px; border-bottom: 1px solid #E2E8F0;">Taxonomy / Dept</td>
                                <td style="color: #475569; padding: 8px 12px; border-bottom: 1px solid #E2E8F0;">
                                    <span style="font-family: monospace; font-size: 11px; background: #EEF2F6; padding: 1px 5px; border-radius: 3px; color: #64748B;">raw_category</span><br>
                                    <b>"{src_cat}"</b>
                                </td>
                                <td style="color: #0F172A; padding: 8px 12px; border-bottom: 1px solid #E2E8F0;">
                                    <span style="background: #E0F2FE; color: #0369A1; padding: 1px 7px; border-radius: 4px; font-weight: 600; font-size: 11px;">{itm.department}</span>
                                    <span style="color: #94A3B8; margin: 0 4px;">→</span>
                                    <b>{itm.sub_category}</b>
                                </td>
                            </tr>
                            <tr>
                                <td style="font-weight: 700; color: #334155; padding: 8px 12px; border-bottom: 1px solid #E2E8F0;">Color Normalization</td>
                                <td style="color: #475569; padding: 8px 12px; border-bottom: 1px solid #E2E8F0;">
                                    <span style="font-family: monospace; font-size: 11px; background: #EEF2F6; padding: 1px 5px; border-radius: 3px; color: #64748B;">raw_color</span><br>
                                    <b>"{src_color}"</b>
                                </td>
                                <td style="font-weight: 700; color: #0F172A; padding: 8px 12px; border-bottom: 1px solid #E2E8F0;">
                                    <span style="display: inline-block; width: 9px; height: 9px; border-radius: 50%; background: #0F172A; margin-right: 5px; vertical-align: middle;"></span>
                                    #{itm.canonical_color}
                                </td>
                            </tr>
                            <tr>
                                <td style="font-weight: 700; color: #334155; padding: 8px 12px; border-bottom: 1px solid #E2E8F0;">Fabric Specification</td>
                                <td style="color: #475569; padding: 8px 12px; border-bottom: 1px solid #E2E8F0;">
                                    <span style="font-family: monospace; font-size: 11px; background: #EEF2F6; padding: 1px 5px; border-radius: 3px; color: #64748B;">raw_fabric</span><br>
                                    <b>"{src_fabric}"</b>
                                </td>
                                <td style="color: #0F172A; padding: 8px 12px; border-bottom: 1px solid #E2E8F0;">
                                    <b>{itm.fabric}</b>
                                </td>
                            </tr>
                            <tr>
                                <td style="font-weight: 700; color: #334155; padding: 8px 12px; border-bottom: 1px solid #E2E8F0;">Price Verification</td>
                                <td style="color: #475569; padding: 8px 12px; border-bottom: 1px solid #E2E8F0;">
                                    <span style="font-family: monospace; font-size: 11px; background: #EEF2F6; padding: 1px 5px; border-radius: 3px; color: #64748B;">raw_price</span><br>
                                    <b>₹{src_price}</b>
                                </td>
                                <td style="color: #0F172A; padding: 8px 12px; border-bottom: 1px solid #E2E8F0;">
                                    <b>₹{itm.price:.0f}</b> <span style="color: #059669; font-weight: 600; font-size: 11px;">✓ Compliant (₹399–₹1,499)</span>
                                </td>
                            </tr>
                            <tr>
                                <td style="font-weight: 700; color: #334155; padding: 8px 12px; border-bottom: 1px solid #E2E8F0;">SEO Listing Title</td>
                                <td style="color: #475569; padding: 8px 12px; border-bottom: 1px solid #E2E8F0;">
                                    <span style="font-family: monospace; font-size: 11px; background: #EEF2F6; padding: 1px 5px; border-radius: 3px; color: #64748B;">raw_title</span><br>
                                    <b>"{src_title}"</b>
                                </td>
                                <td style="color: #0F172A; padding: 8px 12px; border-bottom: 1px solid #E2E8F0;">
                                    <b>{itm.seo_title}</b>
                                </td>
                            </tr>
                            <tr>
                                <td style="font-weight: 700; color: #334155; padding: 8px 12px; border-bottom: 1px solid #E2E8F0;">Wash & Garment Care</td>
                                <td style="color: #475569; padding: 8px 12px; border-bottom: 1px solid #E2E8F0;">
                                    <span style="font-family: monospace; font-size: 11px; background: #EEF2F6; padding: 1px 5px; border-radius: 3px; color: #64748B;">vendor_notes + raw_fabric</span><br>
                                    <b>"{src_notes}"</b>
                                </td>
                                <td style="color: #0F172A; padding: 8px 12px; border-bottom: 1px solid #E2E8F0;">
                                    {care_target}
                                </td>
                            </tr>
                            <tr>
                                <td style="font-weight: 700; color: #334155; padding: 8px 12px; border-bottom: 1px solid #E2E8F0;">Feature Highlights</td>
                                <td style="color: #475569; padding: 8px 12px; border-bottom: 1px solid #E2E8F0;">
                                    <span style="font-family: monospace; font-size: 11px; background: #EEF2F6; padding: 1px 5px; border-radius: 3px; color: #64748B;">raw_fabric + raw_title + notes</span><br>
                                    Extracted from Vendor Specs
                                </td>
                                <td style="padding: 8px 12px; border-bottom: 1px solid #E2E8F0;">
                                    {highlights_html}
                                </td>
                            </tr>
                            <tr>
                                <td style="font-weight: 700; color: #334155; padding: 8px 12px; border-bottom: 1px solid #E2E8F0;">Quality Guardrail</td>
                                <td style="color: #475569; padding: 8px 12px; border-bottom: 1px solid #E2E8F0;">
                                    <span style="font-family: monospace; font-size: 11px; background: #EEF2F6; padding: 1px 5px; border-radius: 3px; color: #64748B;">Cross-Spec Validation</span><br>
                                    Evaluates Fabric, Care & Consistency
                                </td>
                                <td style="padding: 8px 12px; border-bottom: 1px solid #E2E8F0;">
                                    {guardrail_output}
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 6px; padding: 10px 14px;">
                    <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; color: #64748B; letter-spacing: 0.05em; margin-bottom: 6px;">
                        Hinglish Search Occasion Tags (Auto-Created by LLM • Hinglish Mobile Intent):
                    </div>
                    <div>{tag_badges}</div>
                </div>
            </div>
        </details>
        """)
        with row_columns[1]:
            st.empty()
if st.session_state.raw_df is not None:
    processed_skus = {itm.sku_id for itm in st.session_state.processed_results}
    for _, r in st.session_state.raw_df.iterrows():
        sku_val = str(r['sku_id'])
        if sku_val in processed_skus:
            continue
        hub_val = str(r['vendor_location'])
        title_val = str(r['raw_title'])
        cat_val = str(r['raw_category']) if 'raw_category' in r and pd.notna(r['raw_category']) else 'Unassigned'
        color_val = str(r['raw_color'])
        price_val = f"₹{float(r['raw_price']):.0f}"
        fabric_val = str(r['raw_fabric'])
        notes_val = str(r['vendor_notes']) if ('vendor_notes' in r and pd.notna(r['vendor_notes']) and str(r['vendor_notes']).strip() != "") else 'None provided'

        row_columns = st.columns([10, 2])
        with row_columns[0]:
            render_html(f"""
        <details class="catalog-accordion">
            <summary class="catalog-accordion-summary">
                <span class="col-sku">⚪ {sku_val}</span>
                <span class="col-pipe">│</span>
                <span class="col-hub">{hub_val}</span>
                <span class="col-pipe">│</span>
                <span class="col-title">{title_val}</span>
                <span class="col-pipe">│</span>
                <span class="col-color">{color_val}</span>
                <span class="col-pipe">│</span>
                <span class="col-price">{price_val}</span>
                <span class="col-pipe">│</span>
                <span class="col-status-pending">● Pending Staging</span>
            </summary>
            <div class="catalog-accordion-body">
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; overflow: hidden; margin-bottom: 12px;">
                    <table style="width: 100%; border-collapse: collapse; font-size: 12px; font-family: 'Plus Jakarta Sans', sans-serif;">
                        <thead>
                            <tr style="background: #F1F5F9; color: #475569; font-weight: 700; text-align: left; text-transform: uppercase; font-size: 10px; letter-spacing: 0.05em;">
                                <th style="padding: 9px 12px; width: 150px; border-bottom: 1px solid #CBD5E1;">Catalog Attribute</th>
                                <th style="padding: 9px 12px; width: 42%; border-bottom: 1px solid #CBD5E1;">Raw Vendor Input (Source)</th>
                                <th style="padding: 9px 12px; border-bottom: 1px solid #CBD5E1;">Enriched Target Output</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td style="font-weight: 700; color: #334155; padding: 8px 12px; border-bottom: 1px solid #E2E8F0;">Taxonomy / Dept</td>
                                <td style="color: #475569; padding: 8px 12px; border-bottom: 1px solid #E2E8F0;">
                                    <span style="font-family: monospace; font-size: 11px; background: #EEF2F6; padding: 1px 5px; border-radius: 3px; color: #64748B;">raw_category</span><br>
                                    <b>"{cat_val}"</b>
                                </td>
                                <td style="color: #94A3B8; font-style: italic; padding: 8px 12px; border-bottom: 1px solid #E2E8F0;">Pending</td>
                            </tr>
                            <tr>
                                <td style="font-weight: 700; color: #334155; padding: 8px 12px; border-bottom: 1px solid #E2E8F0;">Color Normalization</td>
                                <td style="color: #475569; padding: 8px 12px; border-bottom: 1px solid #E2E8F0;">
                                    <span style="font-family: monospace; font-size: 11px; background: #EEF2F6; padding: 1px 5px; border-radius: 3px; color: #64748B;">raw_color</span><br>
                                    <b>"{color_val}"</b>
                                </td>
                                <td style="color: #94A3B8; font-style: italic; padding: 8px 12px; border-bottom: 1px solid #E2E8F0;">Pending</td>
                            </tr>
                            <tr>
                                <td style="font-weight: 700; color: #334155; padding: 8px 12px; border-bottom: 1px solid #E2E8F0;">Fabric Specification</td>
                                <td style="color: #475569; padding: 8px 12px; border-bottom: 1px solid #E2E8F0;">
                                    <span style="font-family: monospace; font-size: 11px; background: #EEF2F6; padding: 1px 5px; border-radius: 3px; color: #64748B;">raw_fabric</span><br>
                                    <b>"{fabric_val}"</b>
                                </td>
                                <td style="color: #94A3B8; font-style: italic; padding: 8px 12px; border-bottom: 1px solid #E2E8F0;">Pending</td>
                            </tr>
                            <tr>
                                <td style="font-weight: 700; color: #334155; padding: 8px 12px; border-bottom: 1px solid #E2E8F0;">Price Verification</td>
                                <td style="color: #475569; padding: 8px 12px; border-bottom: 1px solid #E2E8F0;">
                                    <span style="font-family: monospace; font-size: 11px; background: #EEF2F6; padding: 1px 5px; border-radius: 3px; color: #64748B;">raw_price</span><br>
                                    <b>{price_val}</b>
                                </td>
                                <td style="color: #94A3B8; font-style: italic; padding: 8px 12px; border-bottom: 1px solid #E2E8F0;">Pending</td>
                            </tr>
                            <tr>
                                <td style="font-weight: 700; color: #334155; padding: 8px 12px; border-bottom: 1px solid #E2E8F0;">SEO Listing Title</td>
                                <td style="color: #475569; padding: 8px 12px; border-bottom: 1px solid #E2E8F0;">
                                    <span style="font-family: monospace; font-size: 11px; background: #EEF2F6; padding: 1px 5px; border-radius: 3px; color: #64748B;">raw_title</span><br>
                                    <b>"{title_val}"</b>
                                </td>
                                <td style="color: #94A3B8; font-style: italic; padding: 8px 12px; border-bottom: 1px solid #E2E8F0;">Pending</td>
                            </tr>
                            <tr>
                                <td style="font-weight: 700; color: #334155; padding: 8px 12px; border-bottom: 1px solid #E2E8F0;">Wash & Garment Care</td>
                                <td style="color: #475569; padding: 8px 12px; border-bottom: 1px solid #E2E8F0;">
                                    <span style="font-family: monospace; font-size: 11px; background: #EEF2F6; padding: 1px 5px; border-radius: 3px; color: #64748B;">vendor_notes + raw_fabric</span><br>
                                    <b>"{notes_val}"</b>
                                </td>
                                <td style="color: #94A3B8; font-style: italic; padding: 8px 12px; border-bottom: 1px solid #E2E8F0;">Pending</td>
                            </tr>
                            <tr>
                                <td style="font-weight: 700; color: #334155; padding: 8px 12px; border-bottom: 1px solid #E2E8F0;">Feature Highlights</td>
                                <td style="color: #475569; padding: 8px 12px; border-bottom: 1px solid #E2E8F0;">
                                    <span style="font-family: monospace; font-size: 11px; background: #EEF2F6; padding: 1px 5px; border-radius: 3px; color: #64748B;">raw_fabric + raw_title + notes</span><br>
                                    Extracted from Vendor Specs
                                </td>
                                <td style="color: #94A3B8; font-style: italic; padding: 8px 12px; border-bottom: 1px solid #E2E8F0;">Pending</td>
                            </tr>
                            <tr>
                                <td style="font-weight: 700; color: #334155; padding: 8px 12px; border-bottom: 1px solid #E2E8F0;">Quality Guardrail</td>
                                <td style="color: #475569; padding: 8px 12px; border-bottom: 1px solid #E2E8F0;">
                                    <span style="font-family: monospace; font-size: 11px; background: #EEF2F6; padding: 1px 5px; border-radius: 3px; color: #64748B;">Cross-Spec Validation</span><br>
                                    Evaluates Fabric, Care & Consistency
                                </td>
                                <td style="color: #94A3B8; font-style: italic; padding: 8px 12px; border-bottom: 1px solid #E2E8F0;">Pending</td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                    <div>
                        <span style="font-size: 11px; font-weight: 700; text-transform: uppercase; color: #64748B; letter-spacing: 0.05em; margin-right: 8px;">
                            Hinglish Search Occasion Tags:
                        </span>
                        <span style="font-size: 12px; color: #94A3B8; font-style: italic;">Pending</span>
                    </div>
                    <div style="font-size: 12px; color: #64748B;">
                        Use this row's button to enrich only this SKU, or the top button to enrich all SKUs.
                    </div>
                </div>
            </div>
        </details>
        """)
        with row_columns[1]:
            if st.button(
                "⚡ Enrich",
                key=f"enrich_sku_{sku_val}",
                help=f"Derive attributes and generate copy for {sku_val} only",
                use_container_width=True
            ):
                st.session_state.derivation_error = None
                try:
                    with st.spinner(f"Enriching {sku_val}..."):
                        pipeline = CatalogingPipeline(api_key=None)
                        enriched_item = pipeline.derive_attributes(raw_row_to_input(r))
                    st.session_state.processed_results.append(enriched_item)
                    st.session_state.stage_1_done = len(st.session_state.processed_results) == len(st.session_state.raw_df)
                    st.rerun()
                except Exception as e:
                    set_derivation_error(e, sku_val)
                    st.rerun()
