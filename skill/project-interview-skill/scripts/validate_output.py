#!/usr/bin/env python3
"""Check that every top-level resume bullet has a visible title prefix."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


TITLE_PATTERN = re.compile(r"^- \*\*[^*：\s][^*：]*：\*\*\s+\S")


def check_resume_bullets(markdown: str) -> list[str]:
    in_section = False
    found = 0
    errors: list[str] = []

    for number, line in enumerate(markdown.splitlines(), 1):
        if line.startswith("## 简历 bullet"):
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section and line.startswith("- "):
            found += 1
            if not TITLE_PATTERN.match(line):
                errors.append(f"line {number}: use '- **具体支柱名：** 正文'")

    if not in_section:
        errors.append("missing '## 简历 bullet' section")
    elif not found:
        errors.append("no top-level resume bullets found")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="Path to generated 面经.md")
    args = parser.parse_args()
    try:
        markdown = args.path.read_text(encoding="utf-8")
    except OSError as exc:
        parser.error(str(exc))
    errors = check_resume_bullets(markdown)
    if errors:
        for error in errors:
            print(error)
        return 1
    print("Resume bullet titles: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
