#!/usr/bin/env python3
"""Prepare isolated DeerFlow generation inputs without running a model or app."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_MANIFEST = ROOT / "tests/evals/deerflow-source.json"
DEFAULT_SOURCE = ROOT / ".test-repos/deer-flow"
DEFAULT_SKILL = ROOT / "skill/project-interview-skill"


def git(source: Path, *args: str, required: bool = True) -> str:
    result = subprocess.run(
        ["git", "--no-optional-locks", "-C", str(source), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if required and result.returncode:
        raise ValueError(f"Git 检查失败：{result.stderr.strip()}")
    return result.stdout.rstrip("\n") if result.returncode == 0 else ""


def skill_fingerprint(skill: Path) -> str:
    if not (skill / "SKILL.md").is_file():
        raise ValueError(f"Skill 目录缺少 SKILL.md：{skill}")
    digest = hashlib.sha256()
    for path in sorted(skill.rglob("*")):
        relative = path.relative_to(skill)
        if not path.is_file() or "__pycache__" in relative.parts or path.suffix in {".pyc", ".pyo"}:
            continue
        digest.update(relative.as_posix().encode("utf-8") + b"\0")
        digest.update(path.read_bytes() + b"\0")
    return digest.hexdigest()


def request_template(case: str) -> str:
    if case == "e1":
        suite = json.loads((ROOT / "tests/evals/business-narrative.json").read_text(encoding="utf-8"))
        return next(item["request"] for item in suite["cases"] if item["id"] == "E1")
    return (ROOT / "tests/evals/bullet-quality/deerflow-request.md").read_text(encoding="utf-8").strip()


def load_baseline() -> dict:
    baseline = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    if not re.fullmatch(r"[0-9a-f]{40}", baseline.get("commit", "")):
        raise ValueError("源码清单必须指定完整的 40 位提交 SHA，不能使用分支或 latest。")
    if not isinstance(baseline.get("repository_url"), str) or not baseline["repository_url"].strip():
        raise ValueError("源码清单缺少 repository_url。")
    return baseline


def validate_output(source: Path, output: Path, skill: Path) -> None:
    if output.is_relative_to(source):
        raise ValueError("输出目录必须位于源码目录之外，避免污染源码。")
    if output.is_relative_to(skill):
        raise ValueError("输出目录必须位于待测 Skill 目录之外。")
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise ValueError(f"输出目录必须不存在或为空，首次输出不会被覆盖：{output}")


def ensure_managed_source(source: Path, baseline: dict, *, offline: bool = False) -> None:
    """Create only an absent managed cache; existing checkouts remain untouched."""
    if source.exists() or source.is_symlink():
        return
    if offline:
        raise ValueError(f"离线模式下测试缓存不存在：{source}。先联网运行一次以获取固定版本。")
    source.parent.mkdir(parents=True, exist_ok=True)
    lock = source.parent / f".{source.name}.clone.lock"
    try:
        lock.mkdir()
    except FileExistsError as exc:
        raise ValueError(f"另一次源码准备正在占用 {lock}，请等其完成后重试。") from exc
    try:
        # A second caller may have published a complete checkout before the lock.
        if source.exists() or source.is_symlink():
            return
        print(f"[SOURCE] 测试缓存不存在，正在获取固定提交 {baseline['commit']}（detached HEAD）…", flush=True)
        with tempfile.TemporaryDirectory(prefix=f".{source.name}-clone-", dir=source.parent) as temporary:
            checkout = Path(temporary) / "checkout"
            clone = subprocess.run(
                ["git", "clone", "--filter=blob:none", "--depth=1", "--no-checkout", "--",
                 baseline["repository_url"], str(checkout)],
                capture_output=True, text=True, encoding="utf-8",
            )
            if clone.returncode:
                raise ValueError(f"克隆固定源码失败：{clone.stderr.strip()}")
            git(checkout, "fetch", "--depth=1", "origin", baseline["commit"])
            git(checkout, "checkout", "--detach", baseline["commit"])
            if git(checkout, "rev-parse", "HEAD") != baseline["commit"]:
                raise ValueError("克隆后的提交与固定 SHA 不一致。")
            if git(checkout, "status", "--porcelain=v1", "--untracked-files=all", "--ignore-submodules=none"):
                raise ValueError("新克隆的源码工作区不干净，未发布为测试缓存。")
            if source.exists() or source.is_symlink():
                raise ValueError(f"测试缓存路径在克隆期间被创建，未覆盖：{source}")
            checkout.rename(source)
    finally:
        lock.rmdir()


def prepare(case: str, source: Path, output: Path, skill: Path, *, allow_source_drift: bool = False,
            managed_source: bool = False, offline: bool = False) -> dict:
    source = source.expanduser()
    if managed_source and any(path.is_symlink() and not path.exists() for path in (source, *source.parents)):
        raise ValueError(f"测试缓存路径包含断裂符号链接，未克隆或创建其目标：{source}")
    source, output, skill = source.resolve(), output.expanduser().resolve(), skill.expanduser().resolve()
    # Reject invalid deliveries and skills before a potentially expensive clone.
    validate_output(source, output, skill)
    fingerprint = skill_fingerprint(skill)
    template = request_template(case)
    baseline = load_baseline()
    if managed_source:
        ensure_managed_source(source, baseline, offline=offline)
    if not source.is_dir():
        raise ValueError(f"源码目录不存在：{source}。外部 --source-root / DEERFLOW_ROOT 不会被自动克隆或修改。")
    repository_root = Path(git(source, "rev-parse", "--show-toplevel")).resolve()
    if repository_root != source:
        raise ValueError(f"--source-root 必须是 Git 仓库根目录：{repository_root}")
    commit = git(source, "rev-parse", "--verify", "HEAD")
    status = git(source, "status", "--porcelain=v1", "--untracked-files=all", "--ignore-submodules=none")
    drift = []
    if commit != baseline["commit"]:
        drift.append("commit_mismatch")
    if status:
        drift.append("dirty_worktree")
    if drift and not allow_source_drift:
        raise ValueError(
            f"源码偏离固定基线（{', '.join(drift)}；实际 {commit}，预期 {baseline['commit']}）。"
            "如需单独检查当前源码，显式加 --allow-source-drift；结果不可直接与固定基线比较。"
        )

    delivery = output / "delivery"
    request = template.replace("${DEERFLOW_ROOT}", str(source)).replace("${OUTPUT_DIR}", str(delivery))
    metadata = {
        "case": case,
        "prepared_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_root": str(source),
        "managed_source": managed_source,
        "source_branch": git(source, "symbolic-ref", "--short", "-q", "HEAD", required=False) or None,
        "baseline": baseline,
        "actual_commit": commit,
        "origin_url": git(source, "remote", "get-url", "origin", required=False),
        "dirty": bool(status),
        "git_status_porcelain": status,
        "source_drift": drift,
        "allow_source_drift": allow_source_drift,
        "comparable_to_pinned_source": not drift,
        "skill_root": str(skill),
        "skill_sha256": fingerprint,
        "fingerprint_method": "Sorted POSIX relative path + NUL + bytes + NUL; exclude __pycache__, .pyc, .pyo",
        "delivery_root": str(delivery),
        "request": request,
        "request_sha256": hashlib.sha256(request.encode("utf-8")).hexdigest(),
    }
    agent_input = (
        f"使用本次指定的 Skill：<{skill / 'SKILL.md'}>。\n\n"
        f"源码只读：<{source}>。仅将本次交付写入 <{delivery}>，保留首次完整输出；"
        "不修改源码、不启动项目应用或调用真实模型应用链路、不打开用户可见预览。"
        "HTML 验收可用无头浏览器。\n\n"
        "只读取本次 Skill、源码和以下请求，不读取评测 checks、评分标准、旧输出或其他版本结果。"
        "源码或 Skill 在执行中变化时应记录变化，不能继续声称使用同一基线。\n\n"
        + request + "\n"
    )
    # The initial preflight may precede a long clone; reject intervening output.
    validate_output(source, output, skill)
    output.mkdir(parents=True, exist_ok=True)
    contents = {
        "request.md": request + "\n",
        "agent-input.md": agent_input,
        "manifest.json": json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
    }
    for name, content in contents.items():
        # Also protect against a writer racing after the second directory check.
        with (output / name).open("x", encoding="utf-8") as destination:
            destination.write(content)
    return metadata


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", type=str.lower, choices=("e1", "bullet-quality"), default="e1")
    parser.add_argument("--source-root", type=Path, help="源码根目录；优先于 DEERFLOW_ROOT 和 .test-repos/deer-flow")
    parser.add_argument("--output-dir", type=Path, required=True, help="独立且不存在或为空的评测目录")
    parser.add_argument("--skill-root", type=Path, default=DEFAULT_SKILL, help="待测或已冻结的 Skill 目录")
    parser.add_argument("--allow-source-drift", action="store_true", help="允许 SHA 或工作区漂移，并标记不可直接对比")
    parser.add_argument("--offline", action="store_true", help="禁止自动联网克隆；默认缓存缺失时退出")
    args = parser.parse_args(argv)
    environment_source = os.environ.get("DEERFLOW_ROOT")
    source = args.source_root or Path(environment_source or DEFAULT_SOURCE)
    try:
        metadata = prepare(args.case, source, args.output_dir, args.skill_root,
                           allow_source_drift=args.allow_source_drift,
                           managed_source=args.source_root is None and not environment_source,
                           offline=args.offline)
    except (OSError, ValueError) as exc:
        print(f"[FAIL] {exc}", file=sys.stderr)
        return 1
    print(f"[READY] {args.output_dir.expanduser().resolve() / 'agent-input.md'}")
    print(f"源码：{metadata['actual_commit']}；dirty={metadata['dirty']}；基线可比={metadata['comparable_to_pinned_source']}")
    print("仅准备执行输入与元信息；尚未生成、验收或启动应用。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
