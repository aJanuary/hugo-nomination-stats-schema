#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""
Generate an HTML nomination-statistics table
"""

import argparse
import html
import json
import sys
from pathlib import Path


def render_nominee_name_cells(nominee, name_fields, footnotes):
    cells = []

    marker = ""
    if nominee.get("removed") and nominee.get("removedReason"):
        footnotes.append(nominee["removedReason"])
        marker = f' <sup>{len(footnotes)}</sup>'

    for i, _field in enumerate(name_fields):
        text = html.escape(nominee["name"][i])
        if i == 0:
            cells.append(f'<td><span>{text}</span>{marker}</td>')
        else:
            cells.append(f'<td>{text}</td>')
    return cells


def render_category_table(category):
    name_fields = category["nameFields"]
    nominees = category["nominees"]
    rounds = category["rounds"]

    footnotes = []

    lines = []
    lines.append("<table>")
    lines.append("<thead><tr>")
    for field in name_fields:
        lines.append(f"<th>{html.escape(field)}</th>")
    lines.append("<th>N</th>")
    for round_ in rounds:
        lines.append(f'<th>R{round_["number"]}</th>')
    lines.append("</tr></thead>")

    last_finalist_index = max(
        (index for index, nominee in enumerate(nominees) if nominee.get("finalist")),
        default=None,
    )

    rounds_by_index = [
        {entry["nomineeIndex"]: entry for entry in round_["activeNominees"]}
        for round_ in rounds
    ]

    lines.append("<tbody>")
    for index, nominee in enumerate(nominees):
        row_classes = []
        if nominee.get("finalist"):
            row_classes.append("finalist")
        if nominee.get("removed"):
            row_classes.append("removed")
        if index == last_finalist_index:
            row_classes.append("last-finalist")
        row_class = f' class="{" ".join(row_classes)}"' if row_classes else ""
        lines.append(f"<tr{row_class}>")
        lines.extend(render_nominee_name_cells(nominee, name_fields, footnotes))
        lines.append(f'<td>{nominee["numNominations"]}</td>')
        for active_by_index in rounds_by_index:
            entry = active_by_index.get(index)
            if entry is None:
                lines.append('<td class="blank"></td>')
            else:
                cell_class = ' class="elimination-candidate"' if "status" in entry else ""
                lines.append(f'<td{cell_class}>{entry["scaledPoints"] / 60:.2f}</td>')
        lines.append("</tr>")
    lines.append("</tbody>")
    lines.append("</table>")

    if footnotes:
        lines.append('<ol class="footnotes">')
        for reason in footnotes:
            lines.append(f"<li>{html.escape(reason)}</li>")
        lines.append("</ol>")

    return "\n".join(lines)


STYLE = """
body { font-family: sans-serif; }
table { border-collapse: collapse; margin-bottom: 1em; }
th, td { border: 1px solid #999; padding: 0.25em 0.5em; text-align: right; white-space: nowrap; }
th:first-child, th:nth-child(2), td:first-child, td:nth-child(2) { text-align: left; white-space: normal; }
thead th { background-color: #333; color: #fff; }
tbody tr:nth-child(even) td:not(.blank) { background-color: #f0f0f0; }
tr.finalist td { font-weight: bold; }
tr.removed td { text-decoration: line-through; }
tr.removed td sup { text-decoration: none; display: inline-block; }
td.elimination-candidate,
tbody tr:nth-child(even) td.elimination-candidate { background-color: #fdd; color: #900; }
td.blank { border: none; }
tr.last-finalist td:not(.blank) { border-bottom: 1px solid #111; }
.footnotes { font-size: 0.9em; }
"""


def render_document(data):
    lines = []
    lines.append("<!doctype html>")
    lines.append("<html lang=\"en\"><head><meta charset=\"utf-8\">")
    lines.append(f"<title>{data['year']} Hugo Award Nomination Statistics</title>")
    lines.append(f"<style>{STYLE}</style>")
    lines.append("</head><body>")
    lines.append(f"<h1>{data['year']} Hugo Award Nomination Statistics</h1>")
    lines.append(f"<p>{data['numBallots']} ballots cast.</p>")
    for category in data["categories"]:
        lines.append(f"<h2>{html.escape(category['name'])}</h2>")
        lines.append(
            f"<p>{category['numBallots']} ballots cast, "
            f"{category['numNominees']} nominees.</p>"
        )
        lines.append(render_category_table(category))
    lines.append("</body></html>")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="Path to a nominations JSON file")
    parser.add_argument("--output", required=True, help="Path to write the HTML file")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(input_path.read_text())
    html_out = render_document(data)

    Path(args.output).write_text(html_out)


if __name__ == "__main__":
    main()
