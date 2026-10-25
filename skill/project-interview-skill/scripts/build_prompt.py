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
    Validate directory-safe short name used in interview-prep/{简称}/.
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
        role_focus: Optional direction; omitted means fullstack.
        short_name: Optional short name for `interview-prep/{简称}/`.
        extra: Optional free-form notes.

    Returns:
        Markdown string to paste into a chat or pipe to an LLM.
    """
    lines: list[str] = [
        "请按 `project-interview-skill` 执行：写入 `interview-prep/{简称}/导学.md`、`面经.md` 与全部核心课程；单项目课程使用 `interview-prep/guide-{方向}/`，多项目输出根目录使用各项目子目录。",
        "",
        "## 已确认输入",
        "",
        "### 项目简称（用于目录名）",
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
        lines.append("_（未提供，默认全栈；课程目录 guide-fullstack，按真实源码调整比重）_")
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
            "- 表达：先读 references/rules/writing-style.md，直接讲机制，删无信息铺垫和重复总结；保留事实、条件、指标口径、必要教学解释、代码、链接与 B/Q/C，不为口语化编造本人经历。默认只交付成稿。",
            "- 选材：按 references/rules/repository-investigation.md 从完整范围识别核心职责、主要状态和组件分工，查证系统机制后再按系统重要性、目标相关性和设计辨识度组织支柱；不把材料分组、目录或接口数量直接当成 bullet 结构。文件读取、权限校验等细节归入所服务的机制，保留解释设计的实现；课程仍覆盖必要核心机制。",
            "- 先探索仓库：确认入口与实际技术范围，追踪 2～4 条核心链路，逐条记录问题/演进、已实现机制、失败边界、具体效果、源码/测试相对路径与验证状态；只有用户描述时标明证据限制，不虚构源码、实测指标或旧架构。",
            "- 面经：先写目标简介与 bullet；每条一级 bullet 独立成行，格式为 `- **具体支柱名：** 正文`，讲清谁负责什么、如何协作、什么条件改变行为，复杂机制可分二级。具体作用有依据且增加信息时写，已讲清就结束，不机械填四槽。最后填「简历 → 面试展开」表并按表出题。证据不足时少写。",
            "- 默认目标简历：仓库已有机制均可入选，不主动核验 commit author；用户明确参与在同等含金量下优先。未实现增强另列进阶，只有明确要求实际贡献时才限制职责。",
            "- 证据边界：实现、责任与结果分别归档，责任仅在贡献模式限制入选；有指标时按仓库探索规则保留基线、统计对象、时间窗口、环境/负载、来源与归属，不跨口径计算改善或把工程效果推成业务收益。证据缺口留在索引或相关回答，不塞进简历尾注。",
            "- 决策叙述：当前实现不能证明当时比较过方案；历史选型、阶段演进与本人推进过程须有来源，事后替代方案用“现在回看/如果重新设计”表述。第一人称学习口播不补造实验、上线或个人经历。",
            "- 面经 bullet：先读 references/excellent-resumes/susu-bullet-template.md 的原文片段，再对照领域中立 few-shot；默认以酥神简历的具体动词、机制说明和信息分层对齐语言，禁止复制样例的项目事实、身份或数字。",
            "- Bullet 术语：按 references/rules/oral-and-resume-patterns.md 的技术术语选择，先核对事实，再判断目标岗位同行熟悉度，最后比较中英文；英文能提高设计辨识度或表达精度时保留，中文更自然时用中文，存在中文译法不是删除英文的理由。标题概括核心机制，正文术语参与解释；不设英文数量、不固定括号翻译、不用可搜索的私有类名冒充通用概念，取舍理由不进入简历正文。",
            "",
            "## Bullet few-shot（仅学习结构，不复制素材）",
            "",
            "**合格**：- **分层容错：** 将错误处理集中到统一入口，按错误类型选择有限重试、降级或快速失败；重试仅用于幂等操作，各分支统一返回处理结果，调用方无需分别判断底层异常。",
            "",
            "**不合格**：接入缓存和重试，优化接口请求。",
            "",
            "**改写原则**：标题点名具体机制，正文说明职责、协作与行为条件；背景与历史演进有证据且必要时才写；结果写可验证的架构变化或真实指标，没有可支持的新效果就结束，不编造数字，不把待测或测量计划塞进简历。",
            "",
            "- 面经 bullet 成稿审读：先看整组是否抓住项目核心，再看每条是否让同行识别设计、读懂机制并自然追问；保留关键实现，删除源码动作清单、重复条件与不增加信息的总结句。未实现计划、待测尾注放证据记录或相关回答。",
            "- 面经 bullet 事实与术语审读：另行核对主张和名称；不可验证的收益直接删除。支柱名使用目标领域熟悉的机制或架构概念；`RunManager`、`Stream Bridge`、`execution id` 等项目实现名与私有函数、路径、内部枚举下沉到源码证据索引。结构或术语通过不能替代成稿审读。",
            "- 面经：每条 bullet 至少一组 Q&A，通常 1 主问与 2～4 个递进追问；主问通常 4～10 道，按实际主张调整，追问不计入总数。每题记录 B 编号、简历触发依据、考查目标与 C 课程链接；追问来自简历或前序回答。",
            "- 面经：正文重心放在面试题口播，不单独输出「亮点拆解」章节。",
            "- 口播：先正面回答，按方案/原理/故障/演进题选择结构；项目口播第一人称，不设统一最低字数，不强制每道追问完整 STAR。",
            "- 默认读者能写 CRUD；方向未指定用全栈。基础按需补齐，核心精力用于数据流、特色机制、运行原理、工程质量和设计取舍。",
            "- 导学：总览含项目地图、核心课程路线与 B/Q/C 导航；首次完整展开全部核心课程，选读只列入口；课程直接写本课重点、主链、源码阅读、机制边界、需要懂什么、需要记住什么。默认不生成预测、动手验证、实验任务或理解题；用户明确要求时再补充。",
            "- 源码引用：相对文件链接＋符号名＋必要片段，链接相对当前文档计算；课程反向链接主导学和面经，保留用户笔记。",
            "- 后续 HTML：本次仍完整交付 Markdown，不提前生成 HTML。每课末尾按 output-templates.md 附可跨聊天复制的提示词，填入真实项目根定位、文档路径、C 编号、整课范围和源码基线；用户选课或小节后，按 references/rules/interactive-teaching.md 只生成对应离线 HTML，保留笔记并在独立尾部登记有效链接。普通追问直接回答。",
            "- 源码查证是生成者职责，不转成读者作业；用户明确要求验证材料时才提供测量方法，未执行不写已通过。",
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
        help="Short name for output directory: interview-prep/{简称}/",
    )
    parser.add_argument("--tech", default="", help="Technology stack string.")
    parser.add_argument(
        "--role",
        default="",
        help="Job direction, e.g. 前端 / 后端 / 全栈 / AI; default 全栈.",
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
