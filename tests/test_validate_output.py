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

    def add_topic(self, name="C03-查询边界.html", *, route=True, lesson=True):
        page = self.lesson.parent / "topics" / name
        page.parent.mkdir(exist_ok=True)
        page.write_text(
            '<nav><a href="../../项目/导学.md">导学</a> '
            '<a href="../03-查询.md#需要懂什么">回到课程</a></nav>'
            '<main>为什么先批量查再关联？</main>', encoding="utf-8",
        )
        if route:
            md = "[查询](../guide-fullstack/03-查询.md)"
            self.replace(self.guide, md, md + f" [专题](<../guide-fullstack/topics/{name}>)")
        if lesson:
            with self.lesson.open("a", encoding="utf-8") as stream:
                stream.write(f"\n[专题](<topics/{name}>)\n")
        return page

    def test_multiple_linked_topics_leave_ordinary_html_sources_and_other_projects_alone(self):
        self.add_topic()
        self.add_topic("C03-异常 分支.html")
        for path in (self.root / "src" / "C03-源码页面.html",
                     self.lesson.parent / "topics" / "diagram.html",
                     self.root / "另一个项目" / "guide-fullstack" / "topics" / "C03-别的课.html"):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("", encoding="utf-8")
        with self.lesson.open("a", encoding="utf-8") as stream:
            stream.write("\n[源码](../src/C03-源码页面.html) [示意图](topics/diagram.html)\n")
        self.replace(self.guide, " | 无 |", " [源码](../src/C03-源码页面.html) | 无 |")
        self.assertEqual(validate_output.check_delivery(self.interview, self.guide), [])

    def test_topic_named_without_course_id_in_route_is_an_error(self):
        self.add_topic("wrong.html")
        errors = validate_output.check_delivery(self.interview, self.guide)
        self.assertTrue(any("invalid topic filename" in error and "wrong.html" in error for error in errors))

    def test_topic_must_be_linked_in_both_route_and_course_even_if_both_omit_it(self):
        for route, lesson in ((False, True), (True, False), (False, False)):
            with self.subTest(route=route, lesson=lesson):
                page = self.add_topic(f"C03-边界-{route}-{lesson}.html", route=route, lesson=lesson)
                errors = validate_output.check_delivery(self.interview, self.guide)
                relevant = [error for error in errors if page.name in error]
                self.assertEqual(any("in guide route" in error for error in relevant), not route)
                self.assertEqual(any("in course" in error for error in relevant), not lesson)

    def test_rejects_topic_linked_under_another_course_id_or_directory(self):
        self.add_topic("C04-其他课.html")
        other = self.root / "另一个项目" / "topics" / "C03-同号.html"
        other.parent.mkdir(parents=True)
        other.write_text("另一项目的专题", encoding="utf-8")
        self.replace(self.guide, " | 无 |", " [错误](../另一个项目/topics/C03-同号.html) | 无 |")
        errors = validate_output.check_delivery(self.interview, self.guide)
        for name in ("C04-其他课.html", "C03-同号.html"):
            self.assertTrue(any(name in error and "outside its course" in error for error in errors))

    def test_rejects_missing_or_empty_topic(self):
        self.add_topic("C03-空专题.html").write_text(" \n", encoding="utf-8")
        self.add_topic("C03-断链.html").unlink()
        errors = validate_output.check_delivery(self.interview, self.guide)
        self.assertTrue(any("empty topic" in error and "空专题" in error for error in errors))
        self.assertTrue(any("cannot read topic" in error and "断链" in error for error in errors))

    def test_requires_relative_links_and_html_backlinks(self):
        page = self.add_topic()
        self.replace(self.guide, f"../guide-fullstack/topics/{page.name}", str(page))
        # Absolute, external and fragment-only hrefs cannot stand in for the
        # two portable backlinks. A Markdown example is only text inside HTML.
        page.write_text(
            f'<a href="{self.guide}">导学</a><a href="#lesson">课</a>'
            '<a href="https://example.org/03-查询.md">外部</a> '
            '[课](../03-查询.md) [示例](missing.md)', encoding="utf-8",
        )
        errors = validate_output.check_delivery(self.interview, self.guide)
        self.assertTrue(any("needs a relative topic link" in error for error in errors))
        for target in (self.guide, self.lesson):
            self.assertTrue(any("missing relative backlink to " + target.name in error for error in errors))
        self.assertFalse(any("missing.md" in error for error in errors))

    def test_topic_checks_local_source_links_without_checking_fragments_or_external_urls(self):
        page = self.add_topic()
        with page.open("a", encoding="utf-8") as stream:
            stream.write(
                '<a href="../../service.go#read">源码</a><a href="#read">本页章节</a>'
                '<a href="https://example.org/missing">文档</a>'
                '<a href="../../removed.go">旧版证据</a>'
            )
        errors = validate_output.check_delivery(self.interview, self.guide)
        self.assertEqual(errors, [f"broken local file link in {page.name}: {(self.root / 'removed.go').resolve()}"])

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
