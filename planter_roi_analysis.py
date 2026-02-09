#!/usr/bin/env python3
"""
High-ROI Planter Performance Upgrades Analysis

Analyzes aftermarket planter products (closing wheels, seed firmers, meters,
downforce systems, etc.) to rank them by return on investment for planting
performance — yield gain per dollar spent.

ROI is calculated from:
  - Estimated yield gain (bu/ac) from field trial data
  - Corn price assumption for revenue per bushel
  - Product cost (per-row or per-planter)
  - Payback acreage — how many acres before the upgrade pays for itself
  - Planter compatibility breadth

Outputs:
  products/planter_high_roi_report.csv  - ranked upgrades by ROI %
  (stdout summary with tier breakdown)
"""

import csv
import os
import sys
from collections import defaultdict

PRODUCTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "products")
UPGRADES_CSV = os.path.join(PRODUCTS_DIR, "planter_performance_upgrades.csv")

# Assumption for revenue calculation
CORN_PRICE_PER_BU = 4.50


def load_upgrades(csv_path):
    """Load planter performance upgrades CSV."""
    upgrades = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            upgrades.append({
                "product_name": row["product_name"].strip(),
                "manufacturer": row["manufacturer"].strip(),
                "category": row["category"].strip(),
                "description": row["description"].strip(),
                "approx_price_usd": float(row["approx_price_usd"]),
                "price_basis": row["price_basis"].strip(),
                "planter_compatibility": row["planter_compatibility"].strip(),
                "performance_benefit": row["performance_benefit"].strip(),
                "estimated_yield_gain_bu_ac": float(row["estimated_yield_gain_bu_ac"]),
                "estimated_roi_percent": float(row["estimated_roi_percent"]),
                "payback_acres": float(row["payback_acres"]),
                "source_notes": row["source_notes"].strip(),
            })
    return upgrades


def count_compatible_models(compat_str):
    """Count how many planter models a product fits."""
    return len([m.strip() for m in compat_str.replace("/", ",").split(",") if m.strip()])


def compute_performance_roi(upgrades):
    """
    Rank upgrades by planting performance ROI.

    Score factors:
      - estimated_roi_percent (from CSV, based on field data)
      - yield_gain_bu_ac * corn price = revenue per acre
      - payback_acres (lower = faster payback = better)
      - compatibility_bonus (fits more planters = more useful)

    Composite score weights the farmer's return:
      score = (roi_pct * 0.4) + (revenue_per_ac / max_rev * 100 * 0.3)
              + (inverse_payback * 0.2) + (compat_bonus * 0.1)
    """
    # Pre-compute normalizers
    max_revenue = max(
        u["estimated_yield_gain_bu_ac"] * CORN_PRICE_PER_BU for u in upgrades
    )
    max_payback = max(u["payback_acres"] for u in upgrades)

    results = []
    for u in upgrades:
        revenue_per_ac = u["estimated_yield_gain_bu_ac"] * CORN_PRICE_PER_BU
        inverse_payback = (1 - u["payback_acres"] / max_payback) * 100
        compat_count = count_compatible_models(u["planter_compatibility"])
        compat_bonus = min(compat_count * 8, 100)  # cap at 100

        composite_score = (
            u["estimated_roi_percent"] * 0.4
            + (revenue_per_ac / max_revenue) * 100 * 0.3
            + inverse_payback * 0.2
            + compat_bonus * 0.1
        )

        results.append({
            "product_name": u["product_name"],
            "manufacturer": u["manufacturer"],
            "category": u["category"],
            "approx_price_usd": u["approx_price_usd"],
            "price_basis": u["price_basis"],
            "yield_gain_bu_ac": u["estimated_yield_gain_bu_ac"],
            "revenue_per_ac": round(revenue_per_ac, 2),
            "roi_percent": u["estimated_roi_percent"],
            "payback_acres": u["payback_acres"],
            "planter_compatibility": u["planter_compatibility"],
            "composite_score": round(composite_score, 1),
            "performance_benefit": u["performance_benefit"],
            "source_notes": u["source_notes"],
        })

    results.sort(key=lambda r: r["composite_score"], reverse=True)
    return results


def assign_tiers(results):
    """Assign ROI tiers based on composite score."""
    for r in results:
        score = r["composite_score"]
        if score >= 70:
            r["roi_tier"] = "Top Tier"
        elif score >= 50:
            r["roi_tier"] = "Strong"
        elif score >= 30:
            r["roi_tier"] = "Moderate"
        else:
            r["roi_tier"] = "Situational"
    return results


def write_report_csv(results, out_path):
    """Write the ranked ROI report to CSV."""
    fieldnames = [
        "rank", "roi_tier", "product_name", "manufacturer", "category",
        "approx_price_usd", "price_basis", "yield_gain_bu_ac",
        "revenue_per_ac", "roi_percent", "payback_acres",
        "composite_score", "planter_compatibility",
        "performance_benefit", "source_notes",
    ]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for i, row in enumerate(results, 1):
            row["rank"] = i
            writer.writerow(row)


def print_summary(results):
    """Print a human-readable summary."""
    print("=" * 100)
    print("  HIGH-ROI PLANTER PERFORMANCE UPGRADES")
    print(f"  (corn @ ${CORN_PRICE_PER_BU:.2f}/bu)")
    print("=" * 100)
    print(
        f"{'Rank':<5} {'Tier':<12} {'Product':<32} {'Mfg':<22} "
        f"{'Price':>8} {'Yield':>7} {'$/ac':>7} {'ROI%':>6} "
        f"{'Payback':>8} {'Score':>6}"
    )
    print("-" * 100)

    for i, r in enumerate(results, 1):
        print(
            f"{i:<5} {r['roi_tier']:<12} {r['product_name']:<32} "
            f"{r['manufacturer']:<22} "
            f"${r['approx_price_usd']:>7.0f} "
            f"{r['yield_gain_bu_ac']:>5.1f}bu "
            f"${r['revenue_per_ac']:>5.2f} "
            f"{r['roi_percent']:>5.0f}% "
            f"{r['payback_acres']:>6.0f}ac "
            f"{r['composite_score']:>5.1f}"
        )

    print("-" * 100)

    # Category summary
    cat_scores = defaultdict(list)
    for r in results:
        cat_scores[r["category"]].append(r)

    print("\n  BEST UPGRADE BY CATEGORY")
    print(f"  {'Category':<28} {'Best Product':<32} {'ROI%':>6} {'Score':>6}")
    print("  " + "-" * 75)
    for cat in sorted(cat_scores, key=lambda c: max(r["composite_score"] for r in cat_scores[c]), reverse=True):
        best = max(cat_scores[cat], key=lambda r: r["composite_score"])
        print(
            f"  {cat:<28} {best['product_name']:<32} "
            f"{best['roi_percent']:>5.0f}% {best['composite_score']:>5.1f}"
        )

    # Tier summary
    tier_counts = defaultdict(int)
    for r in results:
        tier_counts[r["roi_tier"]] += 1

    print(f"\n  TIER BREAKDOWN")
    for tier in ["Top Tier", "Strong", "Moderate", "Situational"]:
        if tier_counts[tier]:
            names = [r["product_name"] for r in results if r["roi_tier"] == tier]
            print(f"  {tier:<14} ({tier_counts[tier]}) - {', '.join(names)}")

    print()


def main():
    if not os.path.exists(UPGRADES_CSV):
        print(f"Error: {UPGRADES_CSV} not found.", file=sys.stderr)
        sys.exit(1)

    upgrades = load_upgrades(UPGRADES_CSV)
    print(f"Loaded {len(upgrades)} planter performance upgrades\n")

    results = compute_performance_roi(upgrades)
    results = assign_tiers(results)

    out_csv = os.path.join(PRODUCTS_DIR, "planter_high_roi_report.csv")
    write_report_csv(results, out_csv)
    print(f"Report written to: {out_csv}\n")

    print_summary(results)


if __name__ == "__main__":
    main()
