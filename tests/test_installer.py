import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "bin" / "project-interview-skill.js"
BUNDLE = ROOT / "skill" / "project-interview-skill"
SKILL_NAME = "project-interview-skill"
LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


@unittest.skipUnless(shutil.which("node"), "Node.js is required for installer tests")
class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="skill-installer-")
        self.addCleanup(self.temporary.cleanup)
        self.project = Path(self.temporary.name).resolve()

    def run_cli(self, *args):
        result = subprocess.run(
            ["node", str(CLI), *args],
            cwd=self.project,
            env={**os.environ, "NO_COLOR": "1"},
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout

    def assert_complete_bundle(self, bundle):
        self.assertTrue((bundle / "SKILL.md").is_file(), f"Missing entry: {bundle}")
        for source in BUNDLE.rglob("*"):
            if not source.is_file() or "__pycache__" in source.parts:
                continue
            target = bundle / source.relative_to(BUNDLE)
            self.assertTrue(target.is_file(), f"Missing support file: {target}")
            self.assertEqual(target.read_bytes(), source.read_bytes(), str(target))
        for markdown in bundle.rglob("*.md"):
            for link in LINK_PATTERN.findall(markdown.read_text(encoding="utf-8")):
                if link.startswith(("https://", "http://", "#", "mailto:")):
                    continue
                self.assertTrue(
                    (markdown.parent / link.split("#", 1)[0]).exists(),
                    f"Broken installed link in {markdown}: {link}",
                )

    def assert_vscode_entry(self, instructions, bundle):
        self.assertTrue(instructions.is_file())
        text = instructions.read_text(encoding="utf-8")
        self.assertRegex(text, r"(?s)^---\n[^\n]*applyTo:\s*['\"]?\*\*['\"]?\n---\n")
        entry_links = [
            link for link in LINK_PATTERN.findall(text)
            if link.split("#", 1)[0].endswith("SKILL.md")
        ]
        self.assertEqual(len(entry_links), 1, "Instructions must link to the Skill entry")
        self.assertFalse(Path(entry_links[0]).is_absolute(), "The entry link must stay portable")
        self.assertEqual(
            (instructions.parent / entry_links[0]).resolve(),
            bundle / "SKILL.md",
        )
        # The adapter delegates to the bundle instead of duplicating its body.
        self.assertNotIn("references/rules/", text)
        self.assert_complete_bundle(bundle)

    def test_vscode_project_entry_reaches_a_complete_adjacent_bundle(self):
        self.run_cli("install", "--vscode", "--project")

        instructions_dir = self.project / ".github" / "instructions"
        self.assert_vscode_entry(
            instructions_dir / f"{SKILL_NAME}.instructions.md",
            instructions_dir / SKILL_NAME,
        )
        self.assertFalse((instructions_dir / "references").exists())
        self.assertFalse((instructions_dir / "scripts").exists())

    def test_vscode_reinstall_refreshes_only_its_bundle_and_entry(self):
        instructions_dir = self.project / ".github" / "instructions"
        neighbors = {
            instructions_dir / "team.instructions.md": "team instructions\n",
            instructions_dir / "references" / "notes.md": "shared references\n",
            instructions_dir / "scripts" / "helper.py": "# shared script\n",
            instructions_dir / "another-skill" / "SKILL.md": "another skill\n",
        }
        for neighbor, content in neighbors.items():
            neighbor.parent.mkdir(parents=True, exist_ok=True)
            neighbor.write_text(content, encoding="utf-8")
        self.run_cli("--vscode", "--project")
        bundle = instructions_dir / SKILL_NAME
        bundle.mkdir(exist_ok=True)
        (bundle / "SKILL.md").write_text("outdated entry\n", encoding="utf-8")
        (bundle / "obsolete.txt").write_text("old bundled file\n", encoding="utf-8")

        self.run_cli("--vscode", "--project")

        self.assert_vscode_entry(instructions_dir / f"{SKILL_NAME}.instructions.md", bundle)
        self.assertFalse((bundle / "obsolete.txt").exists())
        for neighbor, content in neighbors.items():
            self.assertEqual(neighbor.read_text(encoding="utf-8"), content)

    def test_vscode_project_dry_run_reports_entry_and_bundle_without_writing(self):
        marker = self.project / "keep.txt"
        marker.write_text("untouched\n", encoding="utf-8")

        output = self.run_cli("--vscode", "--project", "--dry-run")

        instructions_dir = self.project / ".github" / "instructions"
        self.assertIn(str(instructions_dir / f"{SKILL_NAME}.instructions.md"), output)
        self.assertIn(str(instructions_dir / SKILL_NAME) + "\n", output)
        self.assertEqual(list(self.project.iterdir()), [marker])
        self.assertEqual(marker.read_text(encoding="utf-8"), "untouched\n")

    def test_doctor_and_user_dry_run_report_vscode_companion_bundle(self):
        user_dir = Path.home() / ".copilot" / "instructions"
        user_entry = user_dir / f"{SKILL_NAME}.instructions.md"
        user_bundle = user_dir / SKILL_NAME
        before = self.target_state(user_entry, user_bundle)

        doctor = self.run_cli("doctor", "--vscode")
        dry_run = self.run_cli("--vscode", "--dry-run")

        self.assertIn(str(user_entry), doctor)
        self.assertIn(str(user_bundle) + "\n", doctor)
        self.assertIn(str(self.project / ".github" / "instructions" / SKILL_NAME) + "\n", doctor)
        self.assertIn(str(user_entry), dry_run)
        self.assertIn(str(user_bundle) + "\n", dry_run)
        self.assertEqual(self.target_state(user_entry, user_bundle), before)
        self.assertEqual(list(self.project.iterdir()), [])

    def test_default_project_target_still_installs_the_complete_bundle(self):
        self.run_cli("--project")

        self.assert_complete_bundle(self.project / ".agents" / "skills" / SKILL_NAME)
        self.assertFalse((self.project / ".github").exists())

    def test_vscode_custom_path_remains_a_standalone_bundle(self):
        custom = self.project / "custom skill bundle"

        self.run_cli("--vscode", "--project", "--path", str(custom))

        self.assert_complete_bundle(custom)
        self.assertFalse((self.project / ".github").exists())
        self.assertFalse((custom / f"{SKILL_NAME}.instructions.md").exists())

    def test_custom_bundle_dry_run_does_not_create_the_target(self):
        custom = self.project / "custom skill bundle"

        output = self.run_cli("--vscode", "--path", str(custom), "--dry-run")

        self.assertIn(str(custom), output)
        self.assertFalse(custom.exists())
        self.assertEqual(list(self.project.iterdir()), [])

    def test_all_project_targets_include_vscode_bundle_and_existing_adapters(self):
        self.run_cli("--all", "--project")

        for relative in (
            ".agents/skills", ".claude/skills", ".trae/rules", ".cursor/rules",
            ".github/instructions",
        ):
            self.assert_complete_bundle(self.project / relative / SKILL_NAME)
        self.assertTrue((self.project / ".cursor" / "rules" / SKILL_NAME / f"{SKILL_NAME}.mdc").is_file())
        self.assertTrue((self.project / ".trae" / "rules" / SKILL_NAME / f"{SKILL_NAME}.md").is_file())
        self.assert_vscode_entry(
            self.project / ".github" / "instructions" / f"{SKILL_NAME}.instructions.md",
            self.project / ".github" / "instructions" / SKILL_NAME,
        )

    @staticmethod
    def target_state(*targets):
        state = {}
        for target in targets:
            candidates = [target, *target.rglob("*")] if target.is_dir() else [target]
            for candidate in candidates:
                state[str(candidate)] = candidate.read_bytes() if candidate.is_file() else candidate.exists()
        return state


if __name__ == "__main__":
    unittest.main()
