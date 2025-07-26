"""CLI tool to convert between PDF and Markdown."""

from __future__ import annotations

import argparse
import os
import sys


def convert(input_path: str, output_path: str | None = None) -> None:
    """Convert between PDF and Markdown using pypandoc.

    If ``input_path`` ends with ``.pdf``, the output will be Markdown.
    If ``input_path`` ends with ``.md`` or ``.markdown``, the output will be PDF.
    The ``output_path`` defaults to the same basename with the appropriate
    extension.
    """
    ext = os.path.splitext(input_path)[1].lower()
    if ext == ".pdf":
        fmt = "md"
        output_path = output_path or os.path.splitext(input_path)[0] + ".md"
        extra_args = []
    elif ext in {".md", ".markdown"}:
        fmt = "pdf"
        output_path = output_path or os.path.splitext(input_path)[0] + ".pdf"
        extra_args = [
            "--pdf-engine=xelatex",
            "-V",
            "CJKmainfont=Noto Serif CJK TC",
        ]
    else:
        raise ValueError("Input must be a .pdf or .md/.markdown file")

    try:
        import pypandoc

        pypandoc.convert_file(
            input_path, fmt, outputfile=output_path, extra_args=extra_args
        )
    except Exception as exc:  # pragma: no cover - error path depends on env
        print(f"Conversion failed: {exc}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert between PDF and Markdown formats"
    )
    parser.add_argument("input", help="Path to input file (.pdf or .md)")
    parser.add_argument("-o", "--output", help="Output file path")
    args = parser.parse_args()

    try:
        convert(args.input, args.output)
    except ValueError as exc:
        print(f"Error: {exc}")
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover - manual execution
    main()
