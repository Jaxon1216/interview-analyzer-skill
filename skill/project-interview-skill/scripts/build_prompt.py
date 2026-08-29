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
        "请严格按 `project-interview-skill` 执行：在**工作区根目录**写入两个文件：",
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
            "- 面经：先抽取 4～6 个架构支柱，再写简介与 bullet；每条一级 bullet 必须以 `**通用支柱名：**` 开头，随后交代问题/演进和职责，再写机制、约束/边界、结果，最后填「简历 → 面试展开」表并按表出题。",
            "- 面经 bullet：对照领域中立 few-shot 的正例、反例和改写对照，只学习表达结构；禁止复制样例的项目名、数字、领域名词或指标。",
            "",
            "## Bullet few-shot（仅学习结构，不复制素材）",
            "",
            "**合格**：**分层容错：** 针对异常处理逻辑散落、改动容易波及主流程的问题，将错误处理收敛为分层容错机制：按错误类型区分有限重试、降级与快速失败，并统一输出可观测结果，降低新增场景对主链路的改动面；线上收益需通过基线对比验证。",
            "",
            "**不合格**：接入缓存和重试，优化接口请求。",
            "",
            "**改写原则**：把实现动作还原成问题/演进；说明机制如何工作及其边界；结果写可验证的架构变化或真实指标，没有证据就写测量计划，不得编造数字。",
            "",
            "- 面经 bullet 质检：每条只表达一个支柱，至少包含「问题或演进 + 机制 + 结果」；关键支柱尽量补充约束或数字。",
            "- 面经 bullet 质检：删除“提升性能/提高稳定性/优化体验”等不可验证结果；私有函数、路径、内部枚举只进入源码证据索引。",
            "- 面经 bullet 质检：支柱名必须是通用架构/工程能力；`RunManager`、`Stream Bridge`、`execution id` 等项目实现名改写为通用表达或下沉到源码证据索引。",
            "- 面经：每个一级 bullet 1 主问 + 2 追问；可另加 2～4 道简介级通用题；主问合计 8～12，追问不计入总数。题干须简历可读，禁止源码巡检型。",
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
        description="Build consolidated prompt for project-interview-skill."
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
