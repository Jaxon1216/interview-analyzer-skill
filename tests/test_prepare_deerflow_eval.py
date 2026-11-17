import contextlib
import hashlib
import importlib.util
import io
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("prepare_deerflow_eval", ROOT / "tests/prepare_deerflow_eval.py")
prepare_eval = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(prepare_eval)


class PrepareDeerflowEvalTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.source = self.root / "source"
        self.source.mkdir()
        self.git("init", "-q")
        (self.source / "source.txt").write_text("original\n", encoding="utf-8")
        self.git("add", "source.txt")
        self.git("-c", "user.name=Eval Test", "-c", "user.email=eval@example.invalid", "commit", "-qm", "fixture")
        self.commit = self.git("rev-parse", "HEAD").strip()
        self.manifest = self.root / "baseline.json"
        self.manifest.write_text(json.dumps({"repository_url": self.source.as_uri(), "commit": self.commit}), encoding="utf-8")
        manifest_patch = patch.object(prepare_eval, "SOURCE_MANIFEST", self.manifest)
        manifest_patch.start()
        self.addCleanup(manifest_patch.stop)
        self.skill = self.root / "skill"
        self.skill.mkdir()
        (self.skill / "SKILL.md").write_text("# Fixture Skill\n", encoding="utf-8")
        self.output = self.root / "run"

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.source), *args], capture_output=True, check=True, text=True).stdout

    def prepare(self, case="e1", **kwargs):
        return prepare_eval.prepare(case, self.source, self.output, self.skill, **kwargs)

    def test_prepares_only_request_and_metadata_without_changing_source_or_exposing_checks(self):
        index = self.source / ".git/index"
        before = (index.read_bytes(), index.stat().st_mtime_ns, (self.source / "source.txt").read_bytes())
        metadata = self.prepare()
        after = (index.read_bytes(), index.stat().st_mtime_ns, (self.source / "source.txt").read_bytes())
        self.assertEqual(before, after)
        self.assertEqual(self.git("status", "--porcelain"), "")
        self.assertEqual({path.name for path in self.output.iterdir()}, {"manifest.json", "request.md", "agent-input.md"})
        self.assertEqual(metadata["actual_commit"], self.commit)
        self.assertFalse(metadata["dirty"])
        self.assertTrue(metadata["comparable_to_pinned_source"])
        request = (self.output / "request.md").read_text(encoding="utf-8").strip()
        self.assertIn(str(self.source), request)
        self.assertIn(str(self.output / "delivery"), request)
        self.assertNotIn("${", request)
        self.assertEqual(metadata["request_sha256"], hashlib.sha256(request.encode("utf-8")).hexdigest())
        agent_input = (self.output / "agent-input.md").read_text(encoding="utf-8")
        self.assertIn(str(self.skill / "SKILL.md"), agent_input)
        suite = json.loads((ROOT / "tests/evals/business-narrative.json").read_text(encoding="utf-8"))
        for check in suite["cases"][0]["checks"]:
            self.assertNotIn(check, agent_input)

    def test_bullet_case_uses_portable_request_and_separate_output_files(self):
        metadata = self.prepare("bullet-quality")
        self.assertIn(str(self.output / "delivery/output.md"), metadata["request"])
        self.assertIn(str(self.output / "delivery/evidence.md"), metadata["request"])
        self.assertNotIn("${", metadata["request"])

    def test_dirty_source_requires_explicit_override_and_is_not_comparable(self):
        (self.source / "untracked.txt").write_text("keep me", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "dirty_worktree"):
            self.prepare()
        self.assertFalse(self.output.exists())
        metadata = self.prepare(allow_source_drift=True)
        self.assertTrue(metadata["dirty"])
        self.assertEqual(metadata["source_drift"], ["dirty_worktree"])
        self.assertFalse(metadata["comparable_to_pinned_source"])
        self.assertIn("untracked.txt", metadata["git_status_porcelain"])
        self.assertEqual((self.source / "untracked.txt").read_text(encoding="utf-8"), "keep me")

    def test_commit_drift_requires_explicit_override_and_is_recorded(self):
        baseline = json.loads(self.manifest.read_text(encoding="utf-8"))
        baseline["commit"] = "0" * 40
        self.manifest.write_text(json.dumps(baseline), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "commit_mismatch"):
            self.prepare()
        self.assertFalse(self.output.exists())
        metadata = self.prepare(allow_source_drift=True)
        self.assertEqual(metadata["actual_commit"], self.commit)
        self.assertEqual(metadata["source_drift"], ["commit_mismatch"])
        self.assertFalse(metadata["comparable_to_pinned_source"])

    def test_rejects_non_repository_and_nested_source_directory(self):
        plain = self.root / "plain"
        plain.mkdir()
        with self.assertRaisesRegex(ValueError, "Git 检查失败"):
            prepare_eval.prepare("e1", plain, self.output, self.skill)
        nested = self.source / "nested"
        nested.mkdir()
        with self.assertRaisesRegex(ValueError, "仓库根目录"):
            prepare_eval.prepare("e1", nested, self.output, self.skill)
        self.assertFalse(self.output.exists())

    def test_rejects_source_output_and_symlink_alias_before_writing(self):
        alias = self.root / "source-alias"
        alias.symlink_to(self.source, target_is_directory=True)
        for output in (self.source, self.source / "generated", alias / "generated"):
            with self.subTest(output=output):
                with self.assertRaisesRegex(ValueError, "源码目录之外"):
                    prepare_eval.prepare("e1", self.source, output, self.skill)
        self.assertFalse((self.source / "generated").exists())

    def test_existing_first_output_and_skill_directory_are_preserved(self):
        self.output.mkdir()
        first = self.output / "first.md"
        first.write_text("first output", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "不会被覆盖"):
            self.prepare()
        self.assertEqual(first.read_text(encoding="utf-8"), "first output")
        with self.assertRaisesRegex(ValueError, "Skill 目录之外"):
            prepare_eval.prepare("e1", self.source, self.skill / "run", self.skill)

    def test_skill_fingerprint_changes_with_resources_and_ignores_bytecode(self):
        initial = prepare_eval.skill_fingerprint(self.skill)
        cache = self.skill / "__pycache__"
        cache.mkdir()
        (cache / "script.pyc").write_bytes(b"cache")
        self.assertEqual(initial, prepare_eval.skill_fingerprint(self.skill))
        (self.skill / "reference.md").write_text("new evidence", encoding="utf-8")
        self.assertNotEqual(initial, prepare_eval.skill_fingerprint(self.skill))

    def test_cli_source_precedence_and_explicit_output_requirement(self):
        cases = (({}, [], "default"), ({"DEERFLOW_ROOT": str(self.source)}, [], "environment"),
                 ({"DEERFLOW_ROOT": str(self.root / "missing")}, ["--source-root", str(self.source)], "argument"))
        for environment, source_args, name in cases:
            with self.subTest(source=name), patch.dict(os.environ, environment, clear=True), patch.object(prepare_eval, "DEFAULT_SOURCE", self.source):
                with contextlib.redirect_stdout(io.StringIO()):
                    result = prepare_eval.main(["--output-dir", str(self.root / name), "--skill-root", str(self.skill), *source_args])
                self.assertEqual(result, 0)
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
            prepare_eval.main([])
        self.assertEqual(error.exception.code, 2)

    def test_default_cache_is_cloned_at_pinned_commit_with_detached_head(self):
        # The remote's default branch has moved; the manifest still pins the first commit.
        (self.source / "source.txt").write_text("new remote tip\n", encoding="utf-8")
        self.git("add", "source.txt")
        self.git("-c", "user.name=Eval Test", "-c", "user.email=eval@example.invalid", "commit", "-qm", "new tip")
        remote_tip = self.git("rev-parse", "HEAD").strip()
        cache = self.root / "cache/deer-flow"
        with patch.dict(os.environ, {}, clear=True), patch.object(prepare_eval, "DEFAULT_SOURCE", cache):
            with contextlib.redirect_stdout(io.StringIO()):
                result = prepare_eval.main(["--output-dir", str(self.output), "--skill-root", str(self.skill)])
        self.assertEqual(result, 0)
        self.assertEqual(prepare_eval.git(cache, "rev-parse", "HEAD"), self.commit)
        self.assertEqual(prepare_eval.git(cache, "symbolic-ref", "--short", "-q", "HEAD", required=False), "")
        self.assertEqual((cache / "source.txt").read_text(encoding="utf-8"), "original\n")
        self.assertEqual(self.git("rev-parse", "HEAD").strip(), remote_tip)
        self.assertEqual([item.name for item in cache.parent.iterdir()], ["deer-flow"])
        metadata = json.loads((self.output / "manifest.json").read_text(encoding="utf-8"))
        self.assertTrue(metadata["managed_source"])
        self.assertIsNone(metadata["source_branch"])
        self.assertTrue(metadata["comparable_to_pinned_source"])

    def test_existing_cache_is_reused_offline_without_fetch_or_branch_changes(self):
        cache = self.root / "cache/deer-flow"
        prepare_eval.prepare("e1", cache, self.output, self.skill, managed_source=True)
        index = cache / ".git/index"
        before = (index.read_bytes(), index.stat().st_mtime_ns)
        original_run = subprocess.run
        with patch.object(prepare_eval.subprocess, "run", wraps=original_run) as run:
            metadata = prepare_eval.prepare("e1", cache, self.root / "second", self.skill,
                                            managed_source=True, offline=True)
        self.assertFalse(any(call.args[0][:2] == ["git", "clone"] or "fetch" in call.args[0] for call in run.call_args_list))
        self.assertEqual(before, (index.read_bytes(), index.stat().st_mtime_ns))
        self.assertTrue(metadata["comparable_to_pinned_source"])
        self.assertIsNone(metadata["source_branch"])

    def test_offline_missing_cache_fails_without_network(self):
        cache = self.root / "cache/deer-flow"
        with patch.object(prepare_eval.subprocess, "run", side_effect=AssertionError("must not run Git")):
            with self.assertRaisesRegex(ValueError, "离线模式"):
                prepare_eval.prepare("e1", cache, self.output, self.skill, managed_source=True, offline=True)
        self.assertFalse(cache.exists())
        self.assertFalse(self.output.exists())

    def test_failed_clone_cleans_staging_directory_without_publishing_cache(self):
        baseline = json.loads(self.manifest.read_text(encoding="utf-8"))
        baseline["repository_url"] = (self.root / "missing-remote").as_uri()
        self.manifest.write_text(json.dumps(baseline), encoding="utf-8")
        cache = self.root / "cache/deer-flow"
        with self.assertRaisesRegex(ValueError, "克隆固定源码失败"):
            prepare_eval.prepare("e1", cache, self.output, self.skill, managed_source=True)
        self.assertFalse(cache.exists())
        self.assertEqual(list(cache.parent.iterdir()), [])
        self.assertFalse(self.output.exists())

    def test_failed_pinned_fetch_does_not_publish_partial_clone(self):
        baseline = json.loads(self.manifest.read_text(encoding="utf-8"))
        baseline["commit"] = "0" * 40
        self.manifest.write_text(json.dumps(baseline), encoding="utf-8")
        cache = self.root / "cache/deer-flow"
        with self.assertRaisesRegex(ValueError, "Git 检查失败"):
            prepare_eval.prepare("e1", cache, self.output, self.skill, managed_source=True)
        self.assertFalse(cache.exists())
        self.assertEqual(list(cache.parent.iterdir()), [])
        self.assertFalse(self.output.exists())

    def test_concurrent_clone_lock_is_preserved_and_cache_is_not_touched(self):
        cache = self.root / "cache/deer-flow"
        cache.parent.mkdir()
        lock = cache.parent / ".deer-flow.clone.lock"
        lock.mkdir()
        with patch.object(prepare_eval.subprocess, "run", side_effect=AssertionError("another clone owns the lock")):
            with self.assertRaisesRegex(ValueError, "另一次源码准备"):
                prepare_eval.prepare("e1", cache, self.output, self.skill, managed_source=True)
        self.assertTrue(lock.is_dir())
        self.assertFalse(cache.exists())
        self.assertFalse(self.output.exists())

    def test_external_missing_source_is_never_cloned(self):
        missing = self.root / "missing-source"
        with patch.object(prepare_eval, "ensure_managed_source", side_effect=AssertionError("external source is read-only")):
            for source_args, environment in ((["--source-root", str(missing)], {}),
                                             ([], {"DEERFLOW_ROOT": str(missing)})):
                with self.subTest(source=source_args or "environment"), patch.dict(os.environ, environment, clear=True):
                    with contextlib.redirect_stderr(io.StringIO()):
                        result = prepare_eval.main(["--output-dir", str(self.output), "--skill-root", str(self.skill), *source_args])
                self.assertEqual(result, 1)
        self.assertFalse(missing.exists())

    def test_dirty_existing_managed_cache_is_not_cleaned_or_reset(self):
        untracked = self.source / "keep.txt"
        untracked.write_text("preserve", encoding="utf-8")
        branch = self.git("symbolic-ref", "--short", "HEAD")
        with self.assertRaisesRegex(ValueError, "dirty_worktree"):
            self.prepare(managed_source=True)
        self.assertEqual(untracked.read_text(encoding="utf-8"), "preserve")
        self.assertEqual(self.git("symbolic-ref", "--short", "HEAD"), branch)
        self.assertFalse(self.output.exists())

    def test_invalid_output_and_non_sha_pin_fail_before_clone(self):
        cache = self.root / "cache/deer-flow"
        self.output.mkdir()
        (self.output / "first.md").write_text("preserve", encoding="utf-8")
        with patch.object(prepare_eval, "ensure_managed_source", side_effect=AssertionError("invalid preflight must not clone")):
            with self.assertRaisesRegex(ValueError, "不会被覆盖"):
                prepare_eval.prepare("e1", cache, self.output, self.skill, managed_source=True)
            baseline = json.loads(self.manifest.read_text(encoding="utf-8"))
            baseline["commit"] = "main"
            self.manifest.write_text(json.dumps(baseline), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "40 位"):
                prepare_eval.prepare("e1", cache, self.root / "new-output", self.skill, managed_source=True)
        self.assertFalse(cache.parent.exists())

    def test_output_created_during_clone_or_final_write_is_preserved(self):
        cache = self.root / "cache/deer-flow"
        original_ensure = prepare_eval.ensure_managed_source

        def clone_with_concurrent_output(*args, **kwargs):
            original_ensure(*args, **kwargs)
            self.output.mkdir()
            (self.output / "request.md").write_text("other request", encoding="utf-8")
            (self.output / "manifest.json").write_text("other manifest", encoding="utf-8")

        with patch.object(prepare_eval, "ensure_managed_source", side_effect=clone_with_concurrent_output):
            with self.assertRaisesRegex(ValueError, "不会被覆盖"):
                prepare_eval.prepare("e1", cache, self.output, self.skill, managed_source=True)
        self.assertEqual((self.output / "request.md").read_text(encoding="utf-8"), "other request")
        self.assertEqual((self.output / "manifest.json").read_text(encoding="utf-8"), "other manifest")
        self.assertFalse((self.output / "agent-input.md").exists())

        # A writer arriving just after the final preflight must also be preserved.
        late_output = self.root / "late-output"
        original_validate = prepare_eval.validate_output
        checks = 0

        def check_then_race(source, output, skill):
            nonlocal checks
            original_validate(source, output, skill)
            checks += 1
            if checks == 2:
                output.mkdir()
                (output / "request.md").write_text("late request", encoding="utf-8")

        with patch.object(prepare_eval, "validate_output", side_effect=check_then_race):
            with self.assertRaises(FileExistsError):
                prepare_eval.prepare("e1", cache, late_output, self.skill, managed_source=True, offline=True)
        self.assertEqual((late_output / "request.md").read_text(encoding="utf-8"), "late request")
        self.assertEqual({item.name for item in late_output.iterdir()}, {"request.md"})

    def test_dangling_managed_cache_symlink_never_clones_outside_target(self):
        target = self.root / "outside/missing-cache"
        link = self.root / "cache-link"
        link.symlink_to(target, target_is_directory=True)
        parent_target = self.root / "missing-parent"
        parent_link = self.root / "parent-link"
        parent_link.symlink_to(parent_target, target_is_directory=True)
        with patch.object(prepare_eval.subprocess, "run", side_effect=AssertionError("must not clone through dangling symlink")):
            for source in (link, parent_link / "deer-flow"):
                with self.subTest(source=source), self.assertRaisesRegex(ValueError, "断裂符号链接"):
                    prepare_eval.prepare("e1", source, self.output, self.skill, managed_source=True)
        self.assertTrue(link.is_symlink())
        self.assertTrue(parent_link.is_symlink())
        self.assertFalse(target.parent.exists())
        self.assertFalse(parent_target.exists())
        self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()
