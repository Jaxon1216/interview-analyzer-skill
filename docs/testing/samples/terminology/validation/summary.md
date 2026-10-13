# 自动验证结果

工作目录：`/Users/bytedance/code/Easton/interview-analyzer-skill`

所有命令均在上述目录实际运行；设置 `PYTHONDONTWRITEBYTECODE=1` 防止验证产生 Python 字节码文件。完整 stdout/stderr 分别存放于 `logs/`。

| 实际命令 | 退出码 | 结果 | 完整日志 |
| --- | --- | --- | --- |
| `npm test` | 0 | PASS | [stdout](logs/npm-test.stdout.log) / [stderr](logs/npm-test.stderr.log) |
| `npm run pack:check` | 0 | PASS | [stdout](logs/npm-pack-check.stdout.log) / [stderr](logs/npm-pack-check.stderr.log) |
| `git diff --check` | 0 | PASS | [stdout](logs/git-diff-check.stdout.log) / [stderr](logs/git-diff-check.stderr.log) |
| `/Users/bytedance/code/Easton/mma/deer-flow/backend/.venv/bin/python /Users/bytedance/.codex/skills/.system/skill-creator/scripts/quick_validate.py /Users/bytedance/code/Easton/interview-analyzer-skill/skill/project-interview-skill` | 0 | PASS | [stdout](logs/skill-quick-validate.stdout.log) / [stderr](logs/skill-quick-validate.stderr.log) |

## B/Q/C 测试执行证据

本轮 `npm test` 实际执行 29 项测试。以下两项均在 unittest 的逐项执行日志中出现并显示 `ok`：

- `test_delivery_keeps_bqc_links_with_english_or_mixed_bullet_titles`：通过

```text
test_delivery_keeps_bqc_links_with_english_or_mixed_bullet_titles (test_validate_output.ValidateOutputTests.test_delivery_keeps_bqc_links_with_english_or_mixed_bullet_titles) ... ok
```

- `test_english_title_still_requires_matching_bullet_mapping`：通过

```text
test_english_title_still_requires_matching_bullet_mapping (test_validate_output.ValidateOutputTests.test_english_title_still_requires_matching_bullet_mapping) ... ok
```

第一项测试在测试源码中分别以 `Middleware Chain`（英文）和 `SSE 流式恢复`（中英混合）为 subTest，调用实际 `check_delivery` 并断言无错误；第二项测试将英文 bullet 标题与映射标题设为不一致并断言检出 `B mapping` 错误。该说明以实际测试源码和执行日志为依据，没有用文字检查替代测试。

`pack:check` 对应 `npm pack --dry-run`，未执行发布。

Git 状态验证：验证前后 porcelain 状态、未暂存 diff 和已暂存 diff 均一致。

整体结果：全部通过。

提交版日志仅整理文末空行；逐字原始日志及 SHA256 保留在本地 `.test-runs/technical-terminology-2026-10-13/validation-final/` 与 manifest 中。
