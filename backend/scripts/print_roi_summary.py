#!/usr/bin/env python3
"""Run and display the Saathi AI ROI and Business Impact summary.

Uses SBI's public retail customer scale (approx. 500 million customers) to model
the potential financial uplift and efficiency gains.
"""
from __future__ import annotations

import os
import sys

# Allow import from app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.analytics.roi_model import estimate_impact

# Cited Figure: State Bank of India (SBI) has approximately 480M to 500M customers.
# We use a conservative estimate of 500,000,000 retail customers.
SBI_RETAIL_BASE = 500_000_000

# Average product net interest income (NII) + fee value: e.g., ₹25,000 per loan/SIP lifetime
AVG_PRODUCT_VALUE = 25000.0

# Mass marketing conversion rate: 0.5%
BASELINE_CONVERSION = 0.005

# Targeted relative uplift: 4.0 (400% uplift, matching typical targeted ML benchmarks)
UPLIFT_PCT = 4.0


def main():
    res = estimate_impact(
        customer_base=SBI_RETAIL_BASE,
        baseline_conversion=BASELINE_CONVERSION,
        uplift_pct=UPLIFT_PCT,
        avg_product_value=AVG_PRODUCT_VALUE,
    )

    print("=" * 80)
    print("                      SAATHI AI - BUSINESS ROI & IMPACT MODEL           ")
    print(f"       Scale Reference: SBI Public Retail Customer Base (~{SBI_RETAIL_BASE / 1e6:.0f} Million)")
    print("=" * 80)
    print(f"Conservative Modeled Assumptions:")
    print(f"  - Total Retail Customer Base: {SBI_RETAIL_BASE:,}")
    print(f"  - Mass Marketing Baseline Conversion: {BASELINE_CONVERSION * 100:.2f}%")
    print(f"  - Saathi AI Targeted Fraction (Outreach): {res['assumptions']['targeted_fraction'] * 100:.1f}%")
    print(f"  - Saathi AI Segment Conversion Rate: {res['assumptions']['targeted_conversion'] * 100:.2f}%")
    print(f"  - Average Product Value (NII/Fees per acquisition): ₹{AVG_PRODUCT_VALUE:,.2f}")
    print(f"  - Baseline Outreach Cost per Contact: ₹{res['assumptions']['baseline_contact_cost']:.2f}")
    print("-" * 80)
    print("CAMPAIGN METRICS COMPARISON (10% Target Subsegment Example)")
    print("-" * 80)
    print(f"{'Metric':<30} | {'Baseline Mass-Mkt':<20} | {'Saathi AI Targeted':<20}")
    print("-" * 80)
    base_cost_str = f"₹{res['baseline']['total_cost']:,.2f}"
    saathi_cost_str = f"₹{res['saathi']['total_cost']:,.2f}"
    base_conv_str = f"{res['baseline']['conversions']:,.2f}"
    saathi_conv_str = f"{res['saathi']['conversions']:,.2f}"
    base_cpa_str = f"₹{res['baseline']['cpa']:,.2f}"
    saathi_cpa_str = f"₹{res['saathi']['cpa']:,.2f}"
    base_rev_str = f"₹{res['baseline']['revenue']:,.2f}"
    saathi_rev_str = f"₹{res['saathi']['revenue']:,.2f}"

    print(f"{'Outreach Contact Base':<30} | {f'{SBI_RETAIL_BASE:,}':<20} | {f'{int(SBI_RETAIL_BASE * 0.10):,}':<20}")
    print(f"{'Campaign Cost':<30} | {base_cost_str:<20} | {saathi_cost_str:<20}")
    print(f"{'Acquired Conversions':<30} | {base_conv_str:<20} | {saathi_conv_str:<20}")
    print(f"{'Cost Per Acquisition (CPA)':<30} | {base_cpa_str:<20} | {saathi_cpa_str:<20}")
    print(f"{'Gross Revenue / Yield':<30} | {base_rev_str:<20} | {saathi_rev_str:<20}")
    print("-" * 80)
    print("INCREMENTAL VALUE ADDED BY SAATHI AI")
    print("-" * 80)
    print(f"  * Incremental Conversions:  {res['incremental']['conversions']:,.0f} accounts")
    print(f"  * Incremental Revenue/NII:  ₹{res['incremental']['revenue']:,.2f}")
    print(f"  * CPA Reduction Delta:      ₹{res['incremental']['cpa_savings_per_acq']:,.2f} lower per customer")
    print(f"  * Campaign Cost Reduction:  ₹{res['incremental']['campaign_cost_savings']:,.2f}")
    print(f"  * Campaign ROI Multiple:    {res['incremental']['roi_multiple']}x yield on spend")
    print("=" * 80)
    print("Disclaimer: Modeled estimates based on retail banking averages, not measured SBI performance.")
    print("=" * 80)


if __name__ == "__main__":
    main()
