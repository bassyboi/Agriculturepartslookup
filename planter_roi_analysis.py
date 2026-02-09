#!/usr/bin/env python3
"""
High-ROI Planter Products Analysis

Analyzes planter parts and common issues data to identify which products
deliver the highest return on investment (ROI) for stocking and sales.

ROI scoring is based on:
  - Issue frequency: how many distinct issues reference the part
  - Severity weight: Critical=4, High=3, Medium=2, Low=1
  - Price tier: higher price parts generate more revenue per sale
  - Model reach: parts compatible with more models have a wider market

Outputs:
  products/planter_high_roi_report.csv  - ranked list of all planter parts
  (stdout summary of top products)
"""

import csv
import os
import sys
from collections import defaultdict

PRODUCTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "products")

PLANTER_FOLDERS = [
    "jd1720_planter",
    "maximerge_xp_planter",
]

SEVERITY_WEIGHTS = {
    "Critical": 4,
    "High": 3,
    "Medium": 2,
    "Low": 1,
}


def load_parts(csv_path):
    """Load parts CSV into a list of dicts."""
    parts = {}
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pn = row["part_number"].strip()
            parts[pn] = {
                "part_number": pn,
                "part_name": row["part_name"].strip(),
                "category": row["category"].strip(),
                "description": row["description"].strip(),
                "compatibility": row["compatibility"].strip(),
                "price_usd": float(row["price_usd"]),
            }
    return parts


def load_issues(csv_path):
    """Load common issues CSV into a list of dicts."""
    issues = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rec_parts = [
                p.strip()
                for p in row["recommended_part_numbers"].split(";")
                if p.strip()
            ]
            issues.append({
                "issue_id": row["issue_id"].strip(),
                "issue_category": row["issue_category"].strip(),
                "description": row["description"].strip(),
                "affected_parts": row["affected_parts"].strip(),
                "recommended_part_numbers": rec_parts,
                "severity": row["severity"].strip(),
            })
    return issues


def count_compatible_models(compat_str):
    """Estimate the number of compatible models from the compatibility field."""
    return len([m.strip() for m in compat_str.replace("/", ",").split(",") if m.strip()])


def compute_roi_scores(all_parts, all_issues):
    """
    Score every part based on:
      issue_frequency  - number of distinct issues that recommend this part
      severity_score   - sum of severity weights across those issues
      price_tier       - normalized price contribution (higher price = more revenue)
      model_reach      - number of compatible equipment models

    Final ROI score = issue_frequency * severity_score * price_factor * model_factor
    """
    # Map part_number -> list of issues that reference it
    part_issue_map = defaultdict(list)
    for issue in all_issues:
        for pn in issue["recommended_part_numbers"]:
            part_issue_map[pn].append(issue)

    # Find max price for normalization
    max_price = max((p["price_usd"] for p in all_parts.values()), default=1)

    results = []
    for pn, part in all_parts.items():
        linked_issues = part_issue_map.get(pn, [])
        issue_freq = len(linked_issues)
        severity_score = sum(
            SEVERITY_WEIGHTS.get(iss["severity"], 1) for iss in linked_issues
        )
        price_factor = 1 + (part["price_usd"] / max_price)  # range [1, 2]
        model_reach = count_compatible_models(part["compatibility"])
        model_factor = 1 + (model_reach - 1) * 0.15  # small bonus per extra model

        roi_score = issue_freq * severity_score * price_factor * model_factor

        # Collect the issue IDs and severities that reference this part
        issue_details = "; ".join(
            f"{iss['issue_id']}({iss['severity']})" for iss in linked_issues
        )

        results.append({
            "part_number": pn,
            "part_name": part["part_name"],
            "category": part["category"],
            "price_usd": part["price_usd"],
            "compatibility": part["compatibility"],
            "issue_frequency": issue_freq,
            "severity_score": severity_score,
            "model_reach": model_reach,
            "roi_score": round(roi_score, 2),
            "linked_issues": issue_details,
        })

    results.sort(key=lambda r: r["roi_score"], reverse=True)
    return results


def write_report_csv(results, out_path):
    """Write the ranked ROI report to CSV."""
    fieldnames = [
        "rank", "part_number", "part_name", "category", "price_usd",
        "compatibility", "issue_frequency", "severity_score", "model_reach",
        "roi_score", "linked_issues",
    ]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for i, row in enumerate(results, 1):
            row["rank"] = i
            writer.writerow(row)


def print_summary(results, top_n=15):
    """Print a human-readable summary of the top ROI parts."""
    print("=" * 80)
    print(f"  HIGH-ROI PLANTER PRODUCTS  (top {top_n})")
    print("=" * 80)
    print(
        f"{'Rank':<5} {'Part #':<12} {'Name':<30} {'Price':>8} "
        f"{'Issues':>7} {'Sev':>5} {'ROI':>8}"
    )
    print("-" * 80)

    for i, r in enumerate(results[:top_n], 1):
        print(
            f"{i:<5} {r['part_number']:<12} {r['part_name']:<30} "
            f"${r['price_usd']:>7.2f} {r['issue_frequency']:>7} "
            f"{r['severity_score']:>5} {r['roi_score']:>8.1f}"
        )

    print("-" * 80)

    # Category breakdown
    cat_scores = defaultdict(float)
    cat_counts = defaultdict(int)
    for r in results:
        if r["roi_score"] > 0:
            cat_scores[r["category"]] += r["roi_score"]
            cat_counts[r["category"]] += 1

    print("\n  ROI BY CATEGORY (parts with at least one linked issue)")
    print(f"  {'Category':<25} {'Parts':>6} {'Total ROI':>10} {'Avg ROI':>10}")
    print("  " + "-" * 55)
    for cat in sorted(cat_scores, key=cat_scores.get, reverse=True):
        avg = cat_scores[cat] / cat_counts[cat] if cat_counts[cat] else 0
        print(
            f"  {cat:<25} {cat_counts[cat]:>6} "
            f"{cat_scores[cat]:>10.1f} {avg:>10.1f}"
        )
    print()


def main():
    all_parts = {}
    all_issues = []

    for folder in PLANTER_FOLDERS:
        folder_path = os.path.join(PRODUCTS_DIR, folder)
        if not os.path.isdir(folder_path):
            print(f"Warning: folder not found: {folder_path}", file=sys.stderr)
            continue

        # Find CSV files
        for fname in os.listdir(folder_path):
            fpath = os.path.join(folder_path, fname)
            if fname.endswith("_parts.csv"):
                parts = load_parts(fpath)
                all_parts.update(parts)
                print(f"Loaded {len(parts)} parts from {folder}/{fname}")
            elif fname.endswith("_common_issues.csv"):
                issues = load_issues(fpath)
                all_issues.extend(issues)
                print(f"Loaded {len(issues)} issues from {folder}/{fname}")

    if not all_parts:
        print("No planter parts data found.", file=sys.stderr)
        sys.exit(1)

    print(f"\nTotal: {len(all_parts)} parts, {len(all_issues)} issues across "
          f"{len(PLANTER_FOLDERS)} planter product lines\n")

    results = compute_roi_scores(all_parts, all_issues)

    # Write CSV report
    out_csv = os.path.join(PRODUCTS_DIR, "planter_high_roi_report.csv")
    write_report_csv(results, out_csv)
    print(f"Report written to: {out_csv}\n")

    print_summary(results)


if __name__ == "__main__":
    main()
