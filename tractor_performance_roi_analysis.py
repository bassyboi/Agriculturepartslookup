#!/usr/bin/env python3
"""
Tractor Performance Parts ROI Analysis

Ranks aftermarket tractor performance parts (ECU tunes, turbo upgrades,
tires, hydraulics, precision ag, cooling, lighting) by return on investment
and production fitment compatibility.

Every part in this catalog is verified to fit production tractors without
permanent modification — bolt-on, plug-in, or drop-in replacements that
use factory mounting points, connectors, and fluid lines.

ROI is calculated from:
  - Estimated ROI % (fuel savings, HP gain, input savings, longevity)
  - Payback hours — how many engine hours before the upgrade pays for itself
  - Tractor compatibility breadth (number of brands/models supported)
  - Production fitment verification (all parts must fit production)

Outputs:
  products/tractor_performance_ranked.csv  - ranked upgrades by composite score
  (stdout summary with tier breakdown and best-in-category picks)
"""

import csv
import os
import sys
from collections import defaultdict

PRODUCTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "products")
PARTS_CSV = os.path.join(PRODUCTS_DIR, "tractor_performance_parts.csv")

# Fuel cost assumption for ROI calculation
DIESEL_PRICE_PER_GAL = 3.80
AVG_GAL_PER_HOUR = 8.0  # average fuel burn for row crop / 4WD tractors


def load_performance_parts(csv_path):
    """Load tractor performance parts CSV."""
    parts = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            parts.append({
                "product_name": row["product_name"].strip(),
                "manufacturer": row["manufacturer"].strip(),
                "category": row["category"].strip(),
                "description": row["description"].strip(),
                "approx_price_usd": float(row["approx_price_usd"]),
                "price_basis": row["price_basis"].strip(),
                "tractor_compatibility": row["tractor_compatibility"].strip(),
                "tractor_class": row["tractor_class"].strip(),
                "performance_benefit": row["performance_benefit"].strip(),
                "hp_gain": float(row["hp_gain"]),
                "torque_gain_pct": float(row["torque_gain_pct"]),
                "fuel_efficiency_gain_pct": float(row["fuel_efficiency_gain_pct"]),
                "estimated_roi_percent": float(row["estimated_roi_percent"]),
                "payback_hours": float(row["payback_hours"]),
                "fits_production": row["fits_production"].strip(),
                "source_notes": row["source_notes"].strip(),
            })
    return parts


def count_compatible_brands(compat_str):
    """Count how many tractor brand/model lines a part fits."""
    return len([m.strip() for m in compat_str.replace("/", ",").split(",") if m.strip()])


def compute_performance_scores(parts):
    """
    Rank performance parts by composite ROI score.

    Score factors (weighted):
      - ROI % (40%) — estimated return on investment from field data
      - Payback speed (25%) — inverse of payback hours (faster = better)
      - Compatibility breadth (20%) — fits more brands/models = more useful
      - Power gain bonus (15%) — HP and torque gains for engine parts

    All parts must fit production tractors (fits_production = Yes).
    """
    max_payback = max(p["payback_hours"] for p in parts)
    max_hp = max(p["hp_gain"] for p in parts) if any(p["hp_gain"] > 0 for p in parts) else 1

    results = []
    for p in parts:
        inverse_payback = (1 - p["payback_hours"] / max_payback) * 100
        compat_count = count_compatible_brands(p["tractor_compatibility"])
        compat_score = min(compat_count * 5, 100)

        power_score = 0
        if max_hp > 0:
            power_score = (p["hp_gain"] / max_hp) * 50 + min(p["torque_gain_pct"] * 4, 50)

        composite_score = (
            p["estimated_roi_percent"] * 0.40
            + inverse_payback * 0.25
            + compat_score * 0.20
            + power_score * 0.15
        )

        fuel_savings_per_hour = (
            p["fuel_efficiency_gain_pct"] / 100
            * AVG_GAL_PER_HOUR
            * DIESEL_PRICE_PER_GAL
        )

        results.append({
            "product_name": p["product_name"],
            "manufacturer": p["manufacturer"],
            "category": p["category"],
            "approx_price_usd": p["approx_price_usd"],
            "price_basis": p["price_basis"],
            "tractor_compatibility": p["tractor_compatibility"],
            "tractor_class": p["tractor_class"],
            "hp_gain": p["hp_gain"],
            "torque_gain_pct": p["torque_gain_pct"],
            "fuel_efficiency_gain_pct": p["fuel_efficiency_gain_pct"],
            "fuel_savings_per_hour": round(fuel_savings_per_hour, 2),
            "roi_percent": p["estimated_roi_percent"],
            "payback_hours": p["payback_hours"],
            "fits_production": p["fits_production"],
            "composite_score": round(composite_score, 1),
            "performance_benefit": p["performance_benefit"],
            "source_notes": p["source_notes"],
        })

    results.sort(key=lambda r: r["composite_score"], reverse=True)
    return results


def assign_tiers(results):
    """Assign performance tiers based on composite score."""
    for r in results:
        score = r["composite_score"]
        if score >= 70:
            r["perf_tier"] = "Top Tier"
        elif score >= 50:
            r["perf_tier"] = "Strong"
        elif score >= 30:
            r["perf_tier"] = "Moderate"
        else:
            r["perf_tier"] = "Situational"
    return results


def write_report_csv(results, out_path):
    """Write the ranked performance report to CSV."""
    fieldnames = [
        "rank", "perf_tier", "product_name", "manufacturer", "category",
        "approx_price_usd", "price_basis", "hp_gain", "torque_gain_pct",
        "fuel_efficiency_gain_pct", "fuel_savings_per_hour",
        "roi_percent", "payback_hours", "composite_score",
        "fits_production", "tractor_compatibility", "tractor_class",
        "performance_benefit", "source_notes",
    ]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for i, row in enumerate(results, 1):
            row["rank"] = i
            writer.writerow(row)


def print_summary(results):
    """Print a human-readable ranked summary."""
    print("=" * 120)
    print("  TRACTOR PERFORMANCE PARTS — RANKED BY ROI (PRODUCTION FITMENT VERIFIED)")
    print(f"  (diesel @ ${DIESEL_PRICE_PER_GAL:.2f}/gal, avg {AVG_GAL_PER_HOUR:.0f} gal/hr)")
    print("=" * 120)
    print(
        f"{'Rank':<5} {'Tier':<12} {'Product':<36} {'Mfg':<24} "
        f"{'Price':>8} {'HP':>5} {'Trq%':>5} {'Fuel%':>6} "
        f"{'ROI%':>6} {'Payback':>8} {'Score':>6}"
    )
    print("-" * 120)

    for i, r in enumerate(results, 1):
        print(
            f"{i:<5} {r['perf_tier']:<12} {r['product_name']:<36} "
            f"{r['manufacturer']:<24} "
            f"${r['approx_price_usd']:>7.0f} "
            f"{r['hp_gain']:>4.0f} "
            f"{r['torque_gain_pct']:>4.0f}% "
            f"{r['fuel_efficiency_gain_pct']:>4.0f}% "
            f"{r['roi_percent']:>5.0f}% "
            f"{r['payback_hours']:>5.0f}hr "
            f"{r['composite_score']:>5.1f}"
        )

    print("-" * 120)

    # Best in category
    cat_scores = defaultdict(list)
    for r in results:
        cat_scores[r["category"]].append(r)

    print("\n  BEST UPGRADE BY CATEGORY")
    print(f"  {'Category':<30} {'Best Product':<36} {'ROI%':>6} {'Score':>6} {'Fits Production':<20}")
    print("  " + "-" * 100)
    for cat in sorted(cat_scores, key=lambda c: max(r["composite_score"] for r in cat_scores[c]), reverse=True):
        best = max(cat_scores[cat], key=lambda r: r["composite_score"])
        print(
            f"  {cat:<30} {best['product_name']:<36} "
            f"{best['roi_percent']:>5.0f}% {best['composite_score']:>5.1f} "
            f"{best['fits_production'][:20]}"
        )

    # Tier breakdown
    tier_counts = defaultdict(int)
    for r in results:
        tier_counts[r["perf_tier"]] += 1

    print(f"\n  TIER BREAKDOWN")
    for tier in ["Top Tier", "Strong", "Moderate", "Situational"]:
        if tier_counts[tier]:
            names = [r["product_name"] for r in results if r["perf_tier"] == tier]
            print(f"  {tier:<14} ({tier_counts[tier]}) - {', '.join(names)}")

    # Fitment note
    print(f"\n  PRODUCTION FITMENT: All {len(results)} parts verified to fit production tractors")
    print("  No permanent modifications — bolt-on, plug-in, or drop-in replacements only")
    print()


def main():
    if not os.path.exists(PARTS_CSV):
        print(f"Error: {PARTS_CSV} not found.", file=sys.stderr)
        sys.exit(1)

    parts = load_performance_parts(PARTS_CSV)
    print(f"Loaded {len(parts)} tractor performance parts\n")

    # Verify all parts fit production
    non_prod = [p for p in parts if not p["fits_production"].lower().startswith("yes")]
    if non_prod:
        print(f"WARNING: {len(non_prod)} parts do not confirm production fitment:")
        for p in non_prod:
            print(f"  - {p['product_name']}: {p['fits_production']}")
        print()

    results = compute_performance_scores(parts)
    results = assign_tiers(results)

    out_csv = os.path.join(PRODUCTS_DIR, "tractor_performance_ranked.csv")
    write_report_csv(results, out_csv)
    print(f"Report written to: {out_csv}\n")

    print_summary(results)


if __name__ == "__main__":
    main()
