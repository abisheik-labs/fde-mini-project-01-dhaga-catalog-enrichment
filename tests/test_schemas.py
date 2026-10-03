"""Unit tests for Pydantic schema validation."""

import pytest
from core.schemas import RawVendorInput, CategoryRoutingResult, DepartmentEnum, ListingStatus


def test_raw_vendor_input_valid():
    raw = RawVendorInput(
        sku_id="DHG-101",
        vendor_location="Jaipur",
        raw_title="Anarkali Kurti",
        raw_category="kurtis",
        raw_color="dusty gulabi",
        raw_fabric="100% Rayon",
        raw_price=799.0
    )
    assert raw.sku_id == "DHG-101"
    assert raw.raw_price == 799.0


def test_category_routing_valid():
    routing = CategoryRoutingResult(
        department=DepartmentEnum.WOMENSWEAR,
        sub_category="Kurti",
        clean_fabric="Rayon",
        extracted_raw_color="dusty gulabi"
    )
    assert routing.department == DepartmentEnum.WOMENSWEAR
    assert routing.sub_category == "Kurti"
