#!/usr/bin/env python3
"""Extract plain paragraph text from Word .docx files for question review."""

from __future__ import annotations

import argparse
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile


WORD_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def extract_docx_text(path: Path) -> list[str]:
    with ZipFile(path) as archive:
        document = archive.read("word/document.xml")

    root = ET.fromstring(document)
    paragraphs = []
    for para in root.iter(WORD_NS + "p"):
        text = "".join(node.text or "" for node in para.iter(WORD_NS + "t")).strip()
        if text:
            paragraphs.append(text)
    return paragraphs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path, help=".docx files to extract")
    parser.add_argument("--limit", type=int, default=0, help="maximum paragraphs per file; 0 means all")
    args = parser.parse_args()

    for path in args.paths:
        print(f"==== {path}")
        paragraphs = extract_docx_text(path)
        if args.limit:
            paragraphs = paragraphs[: args.limit]
        for paragraph in paragraphs:
            print(paragraph)


if __name__ == "__main__":
    main()
