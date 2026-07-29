# Hugo voting statistics schemas

JSON schemas for Hugo Awards voting statistics data.

## Versions

 * [2026-08](https://ajanuary.github.io/hugo-nomination-stats-schema/nominations-2026-08/) [DRAFT]

## Goal

The goal of this project is to establish a common format that can be used to consume the nomination statistics for
analysis and alternative presentations.

## Examples

The `examples/` directory contains nomination statistics for past Hugo Awards, transcribed from the official
statistics packets into this schema (2017 to 2025, i.e. every year EPH has been in use). They're intended as
realistic sample data for trying out the schema and the tools below.

**These files are not authoritative.** They were transcribed by hand and by script from PDFs of varying quality,
and almost certainly contain mistakes. Where the schema couldn't represent something exactly, judgement calls were
made. Always refer to the official statistics published by the relevant Worldcon for the real numbers.

## Tools

The `tools/` directory contains example scripts showing how to consume nomination statistics data conforming to
these schemas. They are not part of the schema itself, and aren't required to use the data — they're a starting
point for writing your own consumers. Each script is a [PEP 723](https://peps.python.org/pep-0723/) single-file
script and can be run with [uv](https://docs.astral.sh/uv/), which handles dependencies automatically:

 * `generate_csv.py` — converts one or more nomination statistics files into CSV tables (`categories.csv`,
   `nominees.csv`, `rounds.csv`), for consumption by R, pandas, or similar data analysis tools.

   ```
   uv run tools/generate_csv.py examples/hugo-nominations-2024.json --output-dir csv
   ```

 * `generate_html.py` — renders a single nomination statistics file as a standalone HTML table.

   ```
   uv run tools/generate_html.py examples/hugo-nominations-2024.json --output nominations-2024.html
   ```

 * `generate_xlsx.py` — renders a single nomination statistics file as an Excel workbook, with one sheet per
   category.

   ```
   uv run tools/generate_xlsx.py examples/hugo-nominations-2024.json --output nominations-2024.xlsx
   ```

 * `generate_docs.py` — generates browsable HTML documentation from the JSON schema files themselves (used to
   build the version docs linked above).

   ```
   uv run tools/generate_docs.py nominations-2026-08.json --output-dir docs
   ```

## Community project

 Note, this is a community project, and is in no way connected or officially endoreced by [WSFS](https://www.wsfs.org/)
 or any Hugo administration team.