import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skill/project-interview-skill/scripts/validate_output.py"
spec = importlib.util.spec_from_file_location("validate_output", SCRIPT)
validate_output = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(validate_output)


class ValidateOutputTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.interview = self.root / "项目" / "面经.md"
        self.guide = self.interview.with_name("导学.md")
        self.lesson = self.root / "guide-fullstack" / "03-查询.md"
        self.interview.parent.mkdir()
        self.lesson.parent.mkdir()
        (self.root / "service.go").write_text("package service\n", encoding="utf-8")
        self.interview.write_text(
            "## 简历 bullet\n- **查询聚合：** 聚合资料，向调用方提供完整读模型。\n"
            "## 简历 → 面试展开\n"
            "| B2 | 查询聚合 | 完整读模型 | 为什么后端聚合？ | Q4 | [C03](../guide-fullstack/03-查询.md) |\n"
            "## 面试问题\n### Q4 查询聚合\n"
            "- 对应支柱：B2\n- 触发依据：完整读模型\n- 考查目标：查询边界\n"
            "- 学习入口：[C03](../guide-fullstack/03-查询.md)\n"
            "**面试官问题**：为什么后端聚合？\n"
            "**口播版**：后端聚合后提供统一响应。\n",
            encoding="utf-8",
        )
        self.guide.write_text(
            "## 核心学习路线\n"
            "| C03 | [查询](../guide-fullstack/03-查询.md) | 无 | 解释查询流程 | B2、Q4 |\n",
            encoding="utf-8",
        )
        self.lesson.write_text(
            "# C03 查询\n[总览](../项目/导学.md) [面经](../项目/面经.md#q4)\n"
            "## 源码阅读\n先看 [服务](../service.go)，再沿调用追踪数据组装。\n"
            "## 需要懂什么\n后端将用户资料组装进读模型，调用方不必逐条请求。\n"
            "## 需要记住什么\n先查业务列表，再批量取资料，最后按 ID 关联返回。\n",
            encoding="utf-8",
        )

    def replace(self, path, old, new):
        path.write_text(path.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")

    def test_accepts_linked_delivery_without_exercises_and_preserves_ids(self):
        self.assertEqual(validate_output.check_delivery(self.interview, self.guide), [])

    def test_delivery_keeps_bqc_links_with_english_or_mixed_bullet_titles(self):
        original = self.interview.read_text(encoding="utf-8")
        for title in ("Middleware Chain", "SSE 流式恢复"):
            with self.subTest(title=title):
                self.interview.write_text(
                    original.replace("查询聚合", title), encoding="utf-8"
                )
                self.assertEqual(
                    validate_output.check_delivery(self.interview, self.guide), []
                )

    def test_english_title_still_requires_matching_bullet_mapping(self):
        self.replace(self.interview, "**查询聚合：**", "**Middleware Chain：**")
        errors = validate_output.check_delivery(self.interview, self.guide)
        self.assertTrue(any("B mapping" in error for error in errors))

    def test_rejects_bullet_without_question_and_course_mapping(self):
        self.replace(self.interview, "## 简历 →", "- **会话隔离：** 分离用户会话。\n## 简历 →")
        errors = validate_output.check_delivery(self.interview, self.guide)
        self.assertTrue(any("cover every resume bullet" in error for error in errors))

    def test_rejects_mapped_question_without_body(self):
        self.replace(self.interview, "### Q4", "### Q5")
        errors = validate_output.check_delivery(self.interview, self.guide)
        self.assertTrue(any("Q4: mapped question has no body" in error for error in errors))

    def test_rejects_missing_question_trigger(self):
        self.replace(self.interview, "- 触发依据：完整读模型\n", "")
        with self.interview.open("a", encoding="utf-8") as stream:
            stream.write("**追问 1**：如何优化？\n**触发依据**：统一响应\n")
        errors = validate_output.check_delivery(self.interview, self.guide)
        self.assertTrue(any("Q4: missing 触发依据" in error for error in errors))

    def test_rejects_question_with_conflicting_bullet_id(self):
        self.replace(self.interview, "对应支柱：B2", "对应支柱：B8")
        errors = validate_output.check_delivery(self.interview, self.guide)
        self.assertTrue(any("B IDs differ" in error for error in errors))

    def test_rejects_course_not_in_guide_index(self):
        other = self.lesson.with_name("04-其他.md")
        other.write_text("# C04 其他\n", encoding="utf-8")
        self.replace(self.interview, "03-查询.md", "04-其他.md")
        errors = validate_output.check_delivery(self.interview, self.guide)
        self.assertTrue(any("indexed core courses" in error for error in errors))

    def test_rejects_empty_course_and_missing_backlinks(self):
        self.lesson.write_text("# C03 查询\n", encoding="utf-8")
        errors = validate_output.check_delivery(self.interview, self.guide)
        self.assertTrue(any("源码阅读" in error for error in errors))
        self.assertTrue(any("需要懂什么" in error for error in errors))
        self.assertTrue(any("需要记住什么" in error for error in errors))
        self.assertTrue(any("missing backlink" in error for error in errors))

    def test_experiment_section_does_not_replace_knowledge_content(self):
        self.replace(self.lesson, "## 需要懂什么", "## 动手验证")
        errors = validate_output.check_delivery(self.interview, self.guide)
        self.assertTrue(any("需要懂什么" in error for error in errors))

    def test_rejects_broken_source_link_in_lesson(self):
        (self.root / "service.go").unlink()
        errors = validate_output.check_delivery(self.interview, self.guide)
        self.assertTrue(any("broken local file link" in error for error in errors))

    def test_ignores_fenced_examples_and_external_links(self):
        with self.lesson.open("a", encoding="utf-8") as stream:
            stream.write("\n[文档](https://example.org)\n```markdown\n[示例](missing.md)\n```\n")
        self.assertEqual(validate_output.check_delivery(self.interview, self.guide), [])

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
