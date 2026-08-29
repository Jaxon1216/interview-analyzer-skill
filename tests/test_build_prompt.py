import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, relative_path: str):
    module_path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


build_prompt = load_module(
    "build_prompt_module",
    "skill/project-interview-skill/scripts/build_prompt.py",
)


class BuildPromptTests(unittest.TestCase):
    def test_validate_short_name_accepts_valid_value(self):
        self.assertEqual(build_prompt._validate_short_name("电商"), "电商")

    def test_validate_short_name_rejects_illegal_chars(self):
        with self.assertRaises(ValueError):
            build_prompt._validate_short_name("bad/name")

    def test_validate_short_name_rejects_reserved_names(self):
        with self.assertRaises(ValueError):
            build_prompt._validate_short_name("..")

    def test_build_prompt_escapes_markdown_fences(self):
        prompt = build_prompt.build_prompt(
            description="第一段```第二段",
            tech_stack="Python",
            role_focus="AI",
            short_name="电商",
            extra="补充信息",
        )

        self.assertIn("``\u200b`", prompt)
        self.assertIn("### 技术栈（可选）", prompt)
        self.assertIn("### 求职方向（可选）", prompt)
        self.assertIn("### 补充说明", prompt)

    def test_build_prompt_clarifies_main_question_counting(self):
        prompt = build_prompt.build_prompt(
            description="负责交易链路项目分析与面试题生成",
            tech_stack="Python",
            role_focus="AI",
            short_name="交易",
            extra="补充信息",
        )

        self.assertIn("主问合计 8～12", prompt)
        self.assertIn("追问不计入总数", prompt)
        self.assertIn("简历 → 面试展开", prompt)

    def test_build_prompt_includes_domain_neutral_bullet_few_shot(self):
        prompt = build_prompt.build_prompt(
            description="负责一个需要治理异常和扩展性的业务系统",
            tech_stack="Python",
            role_focus="后端",
            short_name="系统",
            extra="",
        )

        self.assertIn("Bullet few-shot（仅学习结构，不复制素材）", prompt)
        self.assertIn("针对异常处理逻辑散落", prompt)
        self.assertIn("接入缓存和重试，优化接口请求", prompt)
        self.assertIn("结果写可验证的架构变化或真实指标", prompt)

    def test_main_reads_json_file(self):
        payload = {
            "description": "负责交易链路项目分析与面试题生成",
            "short_name": "交易",
            "tech_stack": "Python, Markdown",
            "role_focus": "AI",
            "extra": "补充说明",
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            json_file = Path(temp_dir) / "input.json"
            json_file.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                exit_code = build_prompt.main(["--json-file", str(json_file)])

        self.assertEqual(exit_code, 0)
        self.assertEqual(stderr.getvalue(), "")
        output = stdout.getvalue()
        self.assertIn("### 项目简称（用于文件名）", output)
        self.assertIn("交易", output)
        self.assertIn("Python, Markdown", output)

    def test_main_rejects_invalid_short_name(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            exit_code = build_prompt.main(
                ["-d", "负责交易链路项目分析与面试题生成", "-s", "bad/name"]
            )

        self.assertEqual(exit_code, 1)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("invalid --short-name", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
