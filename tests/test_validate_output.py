import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skill/project-interview-skill/scripts/validate_output.py"
spec = importlib.util.spec_from_file_location("validate_output", SCRIPT)
validate_output = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(validate_output)


class ValidateOutputTests(unittest.TestCase):
    def test_accepts_titled_bullets_and_ignores_following_sections(self):
        markdown = (
            "## 简历 bullet（4 条一级）\n"
            "- **分层容错：** 按失败类型选择有限重试或降级。\n"
            "  - 失败路径有测试覆盖。\n"
            "- **可扩展编排：** 扩展点与调度逻辑分离。\n"
            "## 简历 → 面试展开\n"
            "- 这一节不用按简历格式写。\n"
        )
        self.assertEqual(validate_output.check_resume_bullets(markdown), [])

    def test_rejects_unlabeled_bullet(self):
        markdown = "## 简历 bullet\n- 接入缓存和重试，优化请求。\n## 面试问题\n"
        errors = validate_output.check_resume_bullets(markdown)
        self.assertEqual(len(errors), 1)
        self.assertIn("具体支柱名", errors[0])


if __name__ == "__main__":
    unittest.main()
