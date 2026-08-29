import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "skill" / "project-interview-skill"


class BundleLayoutTests(unittest.TestCase):
    def test_runtime_bundle_has_expected_layers(self):
        self.assertTrue((BUNDLE / "SKILL.md").is_file())
        self.assertTrue((BUNDLE / "references").is_dir())
        self.assertTrue((BUNDLE / "scripts").is_dir())
        self.assertFalse((ROOT / "SKILL.md").exists())
        self.assertFalse((ROOT / "references").exists())
        self.assertFalse((ROOT / "scripts").exists())

    def test_package_files_publish_bundle(self):
        package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
        self.assertIn("skill/", package["files"])
        self.assertNotIn("SKILL.md", package["files"])
        self.assertNotIn("references/", package["files"])
        self.assertNotIn("scripts/", package["files"])

    def test_bundle_relative_markdown_links_resolve(self):
        link_pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
        for markdown_file in BUNDLE.rglob("*.md"):
            content = markdown_file.read_text(encoding="utf-8")
            for target in link_pattern.findall(content):
                if target.startswith(("http://", "https://", "#", "mailto:")):
                    continue
                path_target = target.split("#", 1)[0]
                self.assertTrue(
                    (markdown_file.parent / path_target).exists(),
                    f"Broken link in {markdown_file.relative_to(ROOT)}: {target}",
                )


if __name__ == "__main__":
    unittest.main()
