"""ROI and Financial Impact Model for Saathi AI.

Calculates the incremental conversion, revenue, and cost-per-acquisition (CPA)
delta of Saathi AI's hyper-targeted recommendation engine vs. a baseline mass-marketing channel.

NOTE: All inputs are modeled estimates based on typical retail banking benchmarks
and do not represent confidential or measured SBI data.
"""
from __future__ import annotations


def estimate_impact(
    customer_base: int,
    baseline_conversion: float,
    uplift_pct: float,
    avg_product_value: float,
    baseline_contact_cost: float = 5.0,  # cost to contact a customer (SMS/email/banner)
    targeted_fraction: float = 0.10,     # only contact top 10% highest-prob prospects
    targeted_conversion: float = 0.025,  # conversion rate on targeted segment
) -> dict:
    """Estimate business impact of Saathi AI target marketing vs. baseline.

    Args:
        customer_base: Total number of retail customers.
        baseline_conversion: Conversion rate of broad mass marketing (e.g. 0.005 = 0.5%).
        uplift_pct: Relative conversion uplift in targeted campaigns (e.g. 4.0 = 400% uplift).
        avg_product_value: Net Interest Income (NII) or fee value per product (INR).
        baseline_contact_cost: Marketing outreach cost per customer (INR).
        targeted_fraction: Percentage of customer base recommended for outreach.
        targeted_conversion: Empirical conversion rate in the targeted group.

    Returns:
        dict containing business metrics.
    """
    # 1. Baseline Mass Marketing Campaign
    # Contacts the entire base
    baseline_cost = customer_base * baseline_contact_cost
    baseline_conversions = customer_base * baseline_conversion
    baseline_cpa = baseline_cost / baseline_conversions if baseline_conversions > 0 else 0.0
    baseline_revenue = baseline_conversions * avg_product_value

    # 2. Saathi AI Targeted Campaign
    # Contacts only the targeted high-probability segment
    targeted_contacts = customer_base * targeted_fraction
    saathi_cost = targeted_contacts * baseline_contact_cost
    saathi_conversions = targeted_contacts * targeted_conversion
    saathi_cpa = saathi_cost / saathi_conversions if saathi_conversions > 0 else 0.0
    saathi_revenue = saathi_conversions * avg_product_value

    # 3. Deltas & Incremental Metrics
    incremental_conversions = saathi_conversions - (baseline_conversions * targeted_fraction)
    incremental_revenue = incremental_conversions * avg_product_value
    cpa_delta = baseline_cpa - saathi_cpa
    marketing_cost_savings = baseline_cost - saathi_cost

    return {
        "assumptions": {
            "customer_base": customer_base,
            "baseline_conversion": baseline_conversion,
            "uplift_pct": uplift_pct,
            "avg_product_value": avg_product_value,
            "baseline_contact_cost": baseline_contact_cost,
            "targeted_fraction": targeted_fraction,
            "targeted_conversion": targeted_conversion,
        },
        "baseline": {
            "total_cost": round(baseline_cost, 2),
            "conversions": round(baseline_conversions, 2),
            "cpa": round(baseline_cpa, 2),
            "revenue": round(baseline_revenue, 2),
        },
        "saathi": {
            "total_cost": round(saathi_cost, 2),
            "conversions": round(saathi_conversions, 2),
            "cpa": round(saathi_cpa, 2),
            "revenue": round(saathi_revenue, 2),
        },
        "incremental": {
            "conversions": round(incremental_conversions, 2),
            "revenue": round(incremental_revenue, 2),
            "cpa_savings_per_acq": round(cpa_delta, 2),
            "campaign_cost_savings": round(marketing_cost_savings, 2),
            "roi_multiple": round(saathi_revenue / saathi_cost, 2) if saathi_cost > 0 else 0.0,
        },
    }
