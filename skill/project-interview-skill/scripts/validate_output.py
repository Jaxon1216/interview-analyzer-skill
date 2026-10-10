#!/usr/bin/env python3
"""Check resume format, or linked B/Q/C delivery structure with --guide.

Only simple inline Markdown file links are checked. Semantic accuracy, anchors,
question relevance, and writing quality require content review.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

TITLE_PATTERN = re.compile(r"^- \*\*[^*：\s][^*：]*：\*\*\s+\S")
LINK_PATTERN = re.compile(r'(?<!!)\[[^\]]+\]\((<[^>]+>|[^\s)]+)(?:\s+"[^"]*")?\)')


def without_fences(markdown: str) -> str:
    lines = []
    fence = None
    for line in markdown.splitlines():
        match = re.match(r"^\s*(`{3,}|~{3,})", line)
        if fence is None and match:
            fence = match[1]
        elif fence is not None:
            if re.match(r"^\s*" + re.escape(fence[0]) + "{" + str(len(fence)) + r",}\s*$", line):
                fence = None
        else:
            lines.append(line)
    return "\n".join(lines)


def section(markdown: str, title: str) -> str:
    match = re.search(r"^## " + re.escape(title) + r"[^\n]*\n(.*?)(?=^## |\Z)", markdown, re.M | re.S)
    return match[1] if match else ""


def check_resume_bullets(markdown: str) -> list[str]:
    markdown = without_fences(markdown)
    body = section(markdown, "简历 bullet")
    if not body:
        return ["missing '## 简历 bullet' section"]
    bullets = [line for line in body.splitlines() if line.startswith("- ")]
    if not bullets:
        return ["no top-level resume bullets found"]
    return [f"use '- **具体支柱名：** 正文': {line}" for line in bullets if not TITLE_PATTERN.match(line)]


def local_links(markdown: str, owner: Path) -> list[Path]:
    result = []
    for raw in LINK_PATTERN.findall(without_fences(markdown)):
        target = raw.strip("<>")
        if target.startswith("#") or urlsplit(target).scheme or target.startswith("//"):
            continue
        path = unquote(target.split("#", 1)[0])
        if path:
            result.append((owner.parent / path).resolve())
    return result


def table_rows(markdown: str, prefix: str) -> list[list[str]]:
    rows = []
    for line in markdown.splitlines():
        if re.match(r"^\|\s*" + prefix + r"\d+\s*\|", line):
            rows.append([cell.strip() for cell in line.strip().strip("|").split("|")])
    return rows


def field(body: str, name: str) -> str:
    match = re.search(r"^(?:-\s*)?(?:\*\*)?" + re.escape(name) + r"(?:\*\*)?\s*[:：]\s*(.+)$", body, re.M)
    return match[1].strip() if match else ""


def check_delivery(interview: Path, guide: Path) -> list[str]:
    errors: list[str] = []
    docs: dict[Path, str] = {}

    def read(path: Path) -> str:
        path = path.resolve()
        if path in docs:
            return docs[path]
        try:
            value = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"cannot read {path}: {exc}")
            value = ""
        if not value.strip():
            errors.append(f"empty or missing document: {path}")
        docs[path] = value
        return value

    interview, guide = interview.resolve(), guide.resolve()
    text, overview = read(interview), read(guide)
    errors.extend(check_resume_bullets(text))
    clean = without_fences(text)
    titles = re.findall(r"^- \*\*([^*：]+)：\*\*", section(clean, "简历 bullet"), re.M)

    courses: dict[str, Path] = {}
    for row in table_rows(section(without_fences(overview), "核心学习路线"), "C"):
        if len(row) != 5:
            errors.append(f"{row[0]}: core course table needs 5 columns")
            continue
        links = [p for p in local_links(row[1], guide) if p.suffix.lower() == ".md"]
        if len(links) != 1:
            errors.append(f"{row[0]}: needs one course file link")
            continue
        if row[0] in courses or links[0] in courses.values():
            errors.append(f"duplicate course ID or file: {row[0]}")
        courses[row[0]] = links[0]
    if not courses:
        errors.append("missing core C course rows in '## 核心学习路线'")

    for cid, path in courses.items():
        lesson = read(path)
        content = without_fences(lesson)
        if not re.search(r"^# " + re.escape(cid) + r"\b", content, re.M):
            errors.append(f"{cid}: course heading does not match ID")
        for heading in ("源码阅读", "需要懂什么", "需要记住什么"):
            body = section(content, heading)
            if not body.strip():
                errors.append(f"{cid}: missing expanded '{heading}' section")
        backlinks = local_links(lesson, path)
        for target in (guide, interview):
            if target not in backlinks:
                errors.append(f"{cid}: missing backlink to {target.name}")

    mappings: dict[str, str] = {}
    mapped_q: dict[str, set[str]] = {}
    mapped_courses: dict[str, set[Path]] = {}
    for row in table_rows(section(clean, "简历 → 面试展开"), "B"):
        if len(row) != 6:
            errors.append(f"{row[0]}: B mapping table needs 6 columns")
            continue
        bid, title, trigger, question, qcell, ccell = row
        if bid in mappings and mappings[bid] != title:
            errors.append(f"{bid}: conflicting bullet titles")
        mappings[bid] = title
        if title not in titles:
            errors.append(f"{bid}: title does not match a resume bullet: {title}")
        qids = set(re.findall(r"\bQ\d+\b", qcell))
        linked_courses = set(local_links(ccell, interview))
        if not trigger or not question or not qids:
            errors.append(f"{bid}: missing trigger, main question or Q ID")
        if not linked_courses or not linked_courses.issubset(set(courses.values())):
            errors.append(f"{bid}: must link to indexed core courses")
        for qid in qids:
            mapped_q.setdefault(qid, set()).add(bid)
            mapped_courses.setdefault(qid, set()).update(linked_courses)
    if len(mappings) != len(titles) or set(mappings.values()) != set(titles):
        errors.append("B mapping must cover every resume bullet")

    blocks = re.findall(r"^### (Q\d+)\b[^\n]*\n(.*?)(?=^### Q\d+\b|^## |\Z)", clean, re.M | re.S)
    qids = [qid for qid, _ in blocks]
    if len(qids) != len(set(qids)):
        errors.append("duplicate Q IDs")
    if not qids:
        errors.append("missing Q question blocks")
    for qid in mapped_q.keys() - set(qids):
        errors.append(f"{qid}: mapped question has no body")
    for qid, body in blocks:
        metadata = body.split("**面试官问题**", 1)[0]
        values = {name: field(metadata, name) for name in ("对应支柱", "触发依据", "考查目标", "学习入口")}
        for name, value in values.items():
            if not value:
                errors.append(f"{qid}: missing {name}")
        bids = set(re.findall(r"\bB\d+\b", values["对应支柱"]))
        if bids:
            if bids != mapped_q.get(qid, set()):
                errors.append(f"{qid}: B IDs differ from mapping table")
        elif "简介" not in values["对应支柱"]:
            errors.append(f"{qid}: must reference B IDs or 简介")
        elif qid in mapped_q:
            errors.append(f"{qid}: mapped B question cannot be labeled 简介")
        links = set(local_links(values["学习入口"], interview))
        if not links or not links.issubset(set(courses.values())):
            errors.append(f"{qid}: learning entry must link to indexed core courses")
        if not mapped_courses.get(qid, set()).issubset(links):
            errors.append(f"{qid}: learning entry omits courses in mapping table")

    for owner, content in docs.items():
        for path in local_links(content, owner):
            if not path.is_file():
                errors.append(f"broken local file link in {owner.name}: {path}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="Generated 面经.md")
    parser.add_argument("--guide", type=Path, help="Check full linked delivery against 导学.md")
    args = parser.parse_args()
    if args.guide:
        errors = check_delivery(args.path, args.guide)
    else:
        try:
            errors = check_resume_bullets(args.path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError) as exc:
            parser.error(str(exc))
    if errors:
        for error in errors:
            print(error)
        return 1
    print("Delivery structure: OK" if args.guide else "Resume bullet titles: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
