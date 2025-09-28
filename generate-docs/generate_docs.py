#!/usr/bin/env python3
"""
Generate documentation from JSON schema files.
"""

import argparse
import shutil
import sys
from pathlib import Path

from json_schema_for_humans.generate import generate_from_filename


def main():
    parser = argparse.ArgumentParser(description="Generate documentation from JSON schema files")
    parser.add_argument("schema_files", nargs="+", help="JSON schema files to process")
    parser.add_argument("--output-dir", default="docs", help="Output directory for documentation (default: docs)")

    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    schema_files = args.schema_files

    if not schema_files:
        print("No schema files provided")
        sys.exit(1)

    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    for schema_file in schema_files:
        schema_path = Path(schema_file)

        if not schema_path.exists():
            print(f"Schema file not found: {schema_file}")
            sys.exit(1)

        folder_name = schema_path.stem
        schema_dir = output_dir / folder_name
        schema_dir.mkdir(exist_ok=True)
        output_path = schema_dir / "index.html"

        try:
            generate_from_filename(str(schema_path), str(output_path))

            schema_out_filename = schema_path.name
            shutil.copy2(schema_path, schema_dir / schema_out_filename)

            html_content = output_path.read_text()

            link_html = f'<p><a href="{schema_out_filename}" target="_blank">View schema</a></p>'
            html_content = html_content.replace('</h1>', f'</h1>\n{link_html}', 1)

            output_path.write_text(html_content)
        except Exception as e:
            print(f"Error generating documentation for {schema_file}: {e}")
            sys.exit(1)

    print(f"\nDocumentation generated successfully in {output_dir}")


if __name__ == "__main__":
    main()