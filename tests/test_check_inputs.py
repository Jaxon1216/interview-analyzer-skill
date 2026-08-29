import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, relative_path: str):
    module_path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


check_inputs = load_module(
    "check_inputs_module",
    "skill/project-interview-skill/scripts/check_inputs.py",
)


class CheckInputsTests(unittest.TestCase):
    def test_analyze_short_description_requires_more_input(self):
        result = check_inputs.analyze("太短了", None, None)

        self.assertFalse(result.ok)
        self.assertTrue(result.missing)
        self.assertTrue(any("技术栈未提供" in item for item in result.suggestions))
        self.assertTrue(any("求职方向未指定" in item for item in result.suggestions))

    def test_analyze_complete_description_has_note(self):
        result = check_inputs.analyze(
            "负责交易链路项目分析，覆盖职责拆解、难点梳理、结果复盘，并整理线上数据和指标口径。",
            "Python, Markdown",
            "AI",
        )

        self.assertTrue(result.ok)
        self.assertEqual(result.missing, [])
        self.assertTrue(any("长度达标" in item for item in result.notes))

    def test_main_prints_json_output(self):
        description = (
            "这是一个用于简历和面试准备的项目分析技能，负责根据仓库和项目描述"
            "生成导学与面经文档，包含职责、难点和结果。"
        )
        stdout = io.StringIO()
        stderr = io.StringIO()

        with mock.patch("sys.stdin", io.StringIO(description)):
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                exit_code = check_inputs.main(["--json"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(stderr.getvalue(), "")
        payload = json.loads(stdout.getvalue())
        self.assertTrue(payload["ok"])
        self.assertIn("notes", payload)

    def test_main_reads_file_input(self):
        description = (
            "负责项目分析技能的设计与生成流程，覆盖职责拆解、难点梳理、结果复盘、线上问题和数据规模口径。"
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            input_file = Path(temp_dir) / "description.txt"
            input_file.write_text(description, encoding="utf-8")

            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                exit_code = check_inputs.main(
                    ["--file", str(input_file), "--tech", "Python", "--role", "AI"]
                )

        self.assertEqual(exit_code, 0)
        self.assertEqual(stderr.getvalue(), "")
        self.assertIn("[PASS]", stdout.getvalue())
        self.assertIn("建议追问：", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
