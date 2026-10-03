"""
Cost Accounting and Token Tracker for Dhaga & Co.
Calculates the exact cost line arithmetic per SKU and scaled to Dhaga's weekly volume (400 SKUs/week).
Answers the CTO's direct question: 'What does this cost to run on Monday morning?'
"""

from typing import Dict, Any
from config import (
    CHEAP_MODEL_INPUT_PRICE_PER_M,
    CHEAP_MODEL_OUTPUT_PRICE_PER_M,
    STRONG_MODEL_INPUT_PRICE_PER_M,
    STRONG_MODEL_OUTPUT_PRICE_PER_M,
    USD_TO_INR,
    WEEKLY_NEW_SKUS,
    MONTHLY_NEW_SKUS,
    HOURS_PER_MANUAL_SKU,
    EST_MANUAL_HOURLY_COST_INR
)


class CostTracker:
    @staticmethod
    def calculate_sku_cost(
        cheap_input_tokens: int,
        cheap_output_tokens: int,
        strong_input_tokens: int,
        strong_output_tokens: int
    ) -> Dict[str, Any]:
        """
        Calculates exact API cost for one SKU run in USD and INR.
        """
        # Cheap model cost (USD)
        cheap_cost_usd = (
            (cheap_input_tokens / 1_000_000.0) * CHEAP_MODEL_INPUT_PRICE_PER_M +
            (cheap_output_tokens / 1_000_000.0) * CHEAP_MODEL_OUTPUT_PRICE_PER_M
        )

        # Strong model cost (USD)
        strong_cost_usd = (
            (strong_input_tokens / 1_000_000.0) * STRONG_MODEL_INPUT_PRICE_PER_M +
            (strong_output_tokens / 1_000_000.0) * STRONG_MODEL_OUTPUT_PRICE_PER_M
        )

        total_cost_usd = cheap_cost_usd + strong_cost_usd
        total_cost_inr = total_cost_usd * USD_TO_INR
        total_tokens = cheap_input_tokens + cheap_output_tokens + strong_input_tokens + strong_output_tokens

        return {
            "cheap_tokens": cheap_input_tokens + cheap_output_tokens,
            "strong_tokens": strong_input_tokens + strong_output_tokens,
            "total_tokens": total_tokens,
            "cheap_cost_usd": cheap_cost_usd,
            "strong_cost_usd": strong_cost_usd,
            "total_cost_usd": total_cost_usd,
            "total_cost_inr": total_cost_inr
        }

    @staticmethod
    def calculate_volume_projections(avg_cost_inr_per_sku: float) -> Dict[str, Any]:
        """
        Calculates weekly and monthly financial projections at Dhaga's actual catalog volume.
        Volume: 400 new SKUs/week (~1,600 new SKUs/month).
        """
        weekly_api_cost_inr = avg_cost_inr_per_sku * WEEKLY_NEW_SKUS
        monthly_api_cost_inr = avg_cost_inr_per_sku * MONTHLY_NEW_SKUS

        # Human listing time comparisons
        # Current: 6 listing agents spend ~15 mins (0.25 hrs) typing 60 attributes per SKU
        weekly_manual_hours = WEEKLY_NEW_SKUS * HOURS_PER_MANUAL_SKU # 100 hours/week
        weekly_manual_labor_inr = weekly_manual_hours * EST_MANUAL_HOURLY_COST_INR # ₹25,000/week

        # With MVP: Listing staff only review flagged or drafted items (~2 mins per SKU = 0.033 hrs)
        weekly_review_hours = WEEKLY_NEW_SKUS * (2.0 / 60.0) # ~13.3 hours/week
        weekly_review_labor_inr = weekly_review_hours * EST_MANUAL_HOURLY_COST_INR # ~₹3,333/week

        weekly_net_savings_inr = weekly_manual_labor_inr - (weekly_review_labor_inr + weekly_api_cost_inr)
        monthly_net_savings_inr = weekly_net_savings_inr * 4.0

        return {
            "avg_cost_per_sku_inr": round(avg_cost_inr_per_sku, 3),
            "weekly_skus": WEEKLY_NEW_SKUS,
            "weekly_api_cost_inr": round(weekly_api_cost_inr, 2),
            "monthly_api_cost_inr": round(monthly_api_cost_inr, 2),
            "weekly_manual_hours": round(weekly_manual_hours, 1),
            "weekly_review_hours": round(weekly_review_hours, 1),
            "weekly_hours_saved": round(weekly_manual_hours - weekly_review_hours, 1),
            "weekly_labor_saved_inr": round(weekly_net_savings_inr, 2),
            "monthly_labor_saved_inr": round(monthly_net_savings_inr, 2),
        }
