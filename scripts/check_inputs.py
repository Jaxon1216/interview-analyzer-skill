#!/usr/bin/env python3
"""
Validate project narrative inputs for interview-analyzer-skill.

Reads UTF-8 text from stdin or a file, checks for minimum signal,
and prints suggested follow-up questions in Chinese.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable


MIN_DESCRIPTION_CHARS = 40
KEYWORD_HINTS = (
    "指标",
    "qps",
    "延迟",
    "用户",
    "线上",
    "数据",
    "规模",
    "难点",
    "结果",
    "职责",
)


@dataclass
class CheckResult:
    """Outcome of input validation."""

    ok: bool
    missing: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def _text_length(text: str) -> int:
    """Character count after strip."""
    return len(text.strip())


def _has_any_keyword(text: str, keywords: Iterable[str]) -> bool:
    lower = text.lower()
    for kw in keywords:
        if kw.lower() in lower:
            return True
    return False


def analyze(description: str, tech_stack: str | None, role_focus: str | None) -> CheckResult:
    """
    Analyze user-provided fields and return gaps plus follow-up suggestions.

    Args:
        description: Required project description.
        tech_stack: Optional technology list or sentence.
        role_focus: Optional job direction (frontend/backend/AI).

    Returns:
        CheckResult with ok flag, missing topics, and concrete questions.
    """
    missing: list[str] = []
    suggestions: list[str] = []
    notes: list[str] = []

    desc_len = _text_length(description)
    if desc_len < MIN_DESCRIPTION_CHARS:
        missing.append(
            f"项目描述过短（当前约 {desc_len} 字符，建议至少 {MIN_DESCRIPTION_CHARS}+ "
            "并包含职责、难点或结果线索）"
        )

    if not _has_any_keyword(description, KEYWORD_HINTS) and desc_len < MIN_DESCRIPTION_CHARS * 2:
        suggestions.append(
            "请补充：你在项目中的**具体职责**（独立负责模块 / 协作边界）？"
        )
        suggestions.append(
            "请补充：一个**技术或业务难点**，以及你如何验证「已解决」？"
        )

    if not tech_stack or not tech_stack.strip():
        suggestions.append(
            "技术栈未提供：若补充语言/框架/存储/消息/观测栈，面试题会更准。"
        )

    if not role_focus or not role_focus.strip():
        suggestions.append(
            "求职方向未指定：目标是 **前端 / 后端 / AI** 中的哪些？会影响题目权重与标签。"
        )

    suggestions.extend(
        [
            "请描述一次**线上问题或惊险排障**：现象、定位手段、修复、复盘项？",
            "若重新做一遍，你会在哪个**设计决策**上改变？为什么？",
            "项目中**如何发布与回滚**（灰度、特性开关、数据迁移）？",
        ]
    )

    if desc_len >= MIN_DESCRIPTION_CHARS:
        notes.append("项目描述长度达标；可按追问补齐量化与线上证据。")

    ok = len(missing) == 0
    return CheckResult(ok=ok, missing=missing, suggestions=suggestions, notes=notes)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Check project description completeness for interview-analyzer-skill."
    )
    parser.add_argument(
        "-f",
        "--file",
        help="Read project description from file (UTF-8).",
    )
    parser.add_argument(
        "--tech",
        default="",
        help="Optional tech stack string.",
    )
    parser.add_argument(
        "--role",
        default="",
        help="Optional job focus: frontend, backend, AI, etc.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON.",
    )
    args = parser.parse_args(argv)

    if args.file:
        try:
            description = Path(args.file).read_text(encoding="utf-8").strip()
        except OSError as exc:
            print(f"Error reading file: {exc}", file=sys.stderr)
            return 1
    else:
        description = sys.stdin.read().strip()

    if not description:
        print("Error: empty description. Pipe text or use --file.", file=sys.stderr)
        return 1

    tech = args.tech.strip() or None
    role = args.role.strip() or None
    result = analyze(description, tech, role)

    if args.json:
        print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
        return 0

    status = "PASS" if result.ok else "NEEDS_INPUT"
    print(f"[{status}] interview-analyzer-skill input check\n")
    if result.missing:
        print("必须补齐：")
        for item in result.missing:
            print(f"  - {item}")
        print()
    print("建议追问：")
    for q in result.suggestions:
        print(f"  - {q}")
    if result.notes:
        print("\n备注：")
        for n in result.notes:
            print(f"  - {n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
