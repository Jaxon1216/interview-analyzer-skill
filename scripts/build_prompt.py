#!/usr/bin/env python3
"""
Build a single consolidated prompt block for generating 导学 + 面经 Markdown files.

Reads fields from CLI flags or a JSON file and prints UTF-8 Markdown for agent consumption.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ILLEGAL_SHORT_NAME_CHARS = {"/", "\\", ":", "*", "?", '"', "<", ">", "|"}


def _escape_md(text: str) -> str:
    """Avoid accidental markdown break when embedding user text."""
    return text.replace("```", "``\u200b`")


def _validate_short_name(short_name: str) -> str:
    """
    Validate filename-safe short name used in 导学-{简称}.md / 面经-{简称}.md.
    """
    cleaned = short_name.strip()
    if not cleaned:
        return ""
    if cleaned in {".", ".."}:
        raise ValueError("short name cannot be '.' or '..'.")
    if any(ch in cleaned for ch in ILLEGAL_SHORT_NAME_CHARS):
        chars = "".join(sorted(ILLEGAL_SHORT_NAME_CHARS))
        raise ValueError(f"short name contains illegal path chars. disallowed: {chars}")
    if len(cleaned) > 24:
        raise ValueError("short name is too long (max 24 characters).")
    return cleaned


def build_prompt(
    description: str,
    tech_stack: str | None,
    role_focus: str | None,
    short_name: str | None,
    extra: str | None,
) -> str:
    """
    Compose the master prompt for the analyzing agent.

    Args:
        description: Required project description.
        tech_stack: Optional stack string.
        role_focus: Optional frontend/backend/AI.
        short_name: Optional short name for `导学-{简称}.md` / `面经-{简称}.md`.
        extra: Optional free-form notes.

    Returns:
        Markdown string to paste into a chat or pipe to an LLM.
    """
    lines: list[str] = [
        "请严格按 `interview-analyzer-skill` 执行：在**工作区根目录**写入两个文件：",
        "`导学-{简称}.md` 与 `面经-{简称}.md`；量化与验证仅作为导学中的可选建议项。",
        "",
        "## 已确认输入",
        "",
        "### 项目简称（用于文件名）",
        "",
    ]
    if short_name and short_name.strip():
        lines.append(short_name.strip())
    else:
        lines.append("_（未提供，请从描述提炼并在写入前写明）_")
    lines.extend(["", "### 项目描述（必须）", "", "```text", _escape_md(description.strip()), "```", ""])

    lines.append("### 技术栈（可选）")
    lines.append("")
    if tech_stack and tech_stack.strip():
        lines.append("```text")
        lines.append(_escape_md(tech_stack.strip()))
        lines.append("```")
    else:
        lines.append("_（未提供，请合理推断并列出假设）_")
    lines.append("")

    lines.append("### 求职方向（可选）")
    lines.append("")
    if role_focus and role_focus.strip():
        lines.append(role_focus.strip())
    else:
        lines.append("_（未提供，请从描述推断或给出交叉标签）_")
    lines.append("")

    if extra and extra.strip():
        lines.append("### 补充说明")
        lines.append("")
        lines.append(extra.strip())
        lines.append("")

    lines.extend(
        [
            "## 输出要求（摘要）",
            "",
            "- 面经：项目简介 1～2 句（简历向）；面试题 15～25；建议按 3～6 个主题组织，每主题至少 1 主问 + 2 追问。",
            "- 面经：正文重心放在面试题口播，不单独输出「亮点拆解」章节。",
            "- 口播：第一人称；主问与每个追问口播均 **≥150 字**，完整 STAR（场景→归因→动作→结果/兜底）。",
            "- 导学：必须包含「重点亮点与学习顺序」和「推荐阅读」表，含 **仓库相对路径**。",
            "- 导学：加一条固定自学提醒——看不懂继续问 AI，本 skill 不做逐行讲解。",
            "- 量化与验证：仅导学可选添加（建议语气）；面经不强制该章节。",
            "",
        ]
    )
    return "\n".join(lines)


def _load_json(path: Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("JSON root must be an object")
    return data


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Build consolidated prompt for interview-analyzer-skill."
    )
    parser.add_argument(
        "--description",
        "-d",
        help="Project description text.",
    )
    parser.add_argument(
        "--short-name",
        "-s",
        default="",
        help="Short name for filenames: 导学-{简称}.md / 面经-{简称}.md",
    )
    parser.add_argument("--tech", default="", help="Technology stack string.")
    parser.add_argument(
        "--role",
        default="",
        help="Job direction, e.g. 前端 / 后端 / AI.",
    )
    parser.add_argument(
        "--extra",
        default="",
        help="Additional notes appended under 补充说明.",
    )
    parser.add_argument(
        "--json-file",
        help="Path to JSON with keys: description, short_name?, tech_stack?, role_focus?, extra?.",
    )
    args = parser.parse_args(argv)

    description = args.description or ""
    tech = args.tech or ""
    role = args.role or ""
    short_name = args.short_name or ""
    extra = args.extra or ""

    if args.json_file:
        try:
            payload = _load_json(Path(args.json_file))
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            print(f"Error loading JSON: {exc}", file=sys.stderr)
            return 1
        description = str(payload.get("description", "")).strip()
        tech = str(payload.get("tech_stack", payload.get("tech", ""))).strip()
        role = str(payload.get("role_focus", payload.get("role", ""))).strip()
        short_name = str(payload.get("short_name", payload.get("简称", ""))).strip()
        extra = str(payload.get("extra", "")).strip()

    try:
        short_name = _validate_short_name(short_name)
    except ValueError as exc:
        print(f"Error: invalid --short-name: {exc}", file=sys.stderr)
        return 1

    if not description:
        print(
            "Error: missing description. Use -d, or --json-file with description field.",
            file=sys.stderr,
        )
        return 1

    prompt = build_prompt(
        description,
        tech or None,
        role or None,
        short_name or None,
        extra or None,
    )
    sys.stdout.write(prompt)
    if not prompt.endswith("\n"):
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
