#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""
Generate CSV files from Hugo nomination statistics JSON files, for
consumption by R, pandas, or similar data analysis tools.
"""

import argparse
import csv
import json
import sys
from pathlib import Path


def load_documents(input_files):
    documents = []
    seen_years = {}
    for input_file in input_files:
        path = Path(input_file)
        with path.open(encoding="utf-8") as f:
            document = json.load(f)
        year = document["year"]
        if year in seen_years:
            print(
                f"Duplicate year {year} in {path} (already seen in {seen_years[year]})",
                file=sys.stderr,
            )
            sys.exit(1)
        seen_years[year] = path
        documents.append(document)
    return documents


def max_name_fields(documents):
    max_fields = 1
    for document in documents:
        for category in document["categories"]:
            max_fields = max(max_fields, len(category["nameFields"]))
    return max_fields


def write_csv(path, fieldnames, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
            quoting=csv.QUOTE_MINIMAL,
            lineterminator="\n",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def bool_str(value):
    return "TRUE" if value else "FALSE"


def build_categories_rows(documents, max_fields):
    fieldnames = [
        "year",
        "category",
        "category_order",
        "num_ballots",
        "total_num_ballots",
        "num_nominees",
    ] + [f"name_field_{i}" for i in range(1, max_fields + 1)]

    rows = []
    for document in documents:
        year = document["year"]
        total_num_ballots = document["numBallots"]
        for order, category in enumerate(document["categories"], start=1):
            row = {
                "year": year,
                "category": category["name"],
                "category_order": order,
                "num_ballots": category["numBallots"],
                "total_num_ballots": total_num_ballots,
                "num_nominees": category["numNominees"],
            }
            for i in range(max_fields):
                row[f"name_field_{i + 1}"] = (
                    category["nameFields"][i] if i < len(category["nameFields"]) else ""
                )
            rows.append(row)
    return fieldnames, rows


def build_nominees_rows(documents, max_fields):
    fieldnames = [
        "year",
        "category",
        "nominee_index",
        "name",
    ] + [f"name_{i}" for i in range(1, max_fields + 1)] + [
        "num_nominations",
        "rank",
        "finalist",
        "removed",
        "removed_reason",
    ]

    rows = []
    for document in documents:
        year = document["year"]
        for category in document["categories"]:
            category_name = category["name"]
            for index, nominee in enumerate(category["nominees"]):
                name_parts = nominee["name"]
                row = {
                    "year": year,
                    "category": category_name,
                    "nominee_index": index,
                    "name": " - ".join(name_parts),
                    "num_nominations": nominee["numNominations"],
                    "rank": nominee["rank"],
                    "finalist": bool_str(nominee.get("finalist", False)),
                    "removed": bool_str(nominee.get("removed", False)),
                    "removed_reason": nominee.get("removedReason", ""),
                }
                for i in range(max_fields):
                    row[f"name_{i + 1}"] = name_parts[i] if i < len(name_parts) else ""
                rows.append(row)
    return fieldnames, rows


def build_rounds_rows(documents):
    fieldnames = [
        "year",
        "category",
        "nominee_index",
        "round",
        "points",
        "status",
    ]

    rows = []
    for document in documents:
        year = document["year"]
        for category in document["categories"]:
            category_name = category["name"]
            for round_ in category["rounds"]:
                round_number = round_["number"]
                for active in round_["activeNominees"]:
                    rows.append(
                        {
                            "year": year,
                            "category": category_name,
                            "nominee_index": active["nomineeIndex"],
                            "round": round_number,
                            "points": active["scaledPoints"] / 60,
                            "status": active.get("status", ""),
                        }
                    )
    return fieldnames, rows


def main():
    parser = argparse.ArgumentParser(
        description="Generate CSV files from Hugo nomination statistics JSON files"
    )
    parser.add_argument("input_files", nargs="+", help="Nomination statistics JSON files")
    parser.add_argument(
        "--output-dir", required=True, help="Output directory for CSV files"
    )

    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    documents = load_documents(args.input_files)
    max_fields = max_name_fields(documents)

    categories_fieldnames, categories_rows = build_categories_rows(documents, max_fields)
    nominees_fieldnames, nominees_rows = build_nominees_rows(documents, max_fields)
    rounds_fieldnames, rounds_rows = build_rounds_rows(documents)

    write_csv(output_dir / "categories.csv", categories_fieldnames, categories_rows)
    write_csv(output_dir / "nominees.csv", nominees_fieldnames, nominees_rows)
    write_csv(output_dir / "rounds.csv", rounds_fieldnames, rounds_rows)


if __name__ == "__main__":
    main()
