# 测试集与复跑

测试分两层，结果分别记录，不把结构通过当作内容正确。

| 层次 | 入口 | 验证范围 |
| --- | --- | --- |
| 自动回归 | `npm test` | 输入与提示词脚本、Bundle 链接、bullet 格式、B/Q/C 关联、课程与文件链接 |
| 行为评测 | [business-narrative.json](evals/business-narrative.json) | 业务选材、指标口径与归属、责任模式、历史决策和材料不足时的行为 |
| 术语行为评测 | [technical-terminology.json](evals/technical-terminology.json) | 事实匹配、目标岗位熟悉度、中英比较、标题与正文一致性；不按英文数量评分 |
| 支柱与成稿评测 | [bullet-quality/](evals/bullet-quality/README.md) | 从完整项目选材、机制标题、职责与协作、约束与具体作用；术语和成稿分别判定 |

发布内容检查：`npm run pack:check`。测试数据和评测产物留在开发仓库，不进入运行时 Skill Bundle。

## 行为用例

| ID | 场景 | 核心判断 |
| --- | --- | --- |
| E1 | 本机 DeerFlow，默认完整交付 | 不要求职责或指标；业务主线有源码支持；全栈与 B/Q/C 交付完整 |
| E2 | 不同并发、P99 与 P50 | 不跨口径计算提升，不外推线上收益 |
| E3 | 团队验收结果，个人只做子模块 | 保留指标口径和团队归属，限制个人责任范围 |
| E4 | 只有当前代码，却要求选型与阶段 | 可以讲事后取舍，不能编造历史 |
| E5 | 用户明确陈述真实演进 | 可以据此写历史，不能误伤为一律禁止演进 |
| E6 | 没有运营资料的插件框架 | 使用工程目标，不强行编造业务增长 |

E2–E6 是合成材料，不代表 DeerFlow 的事实。JSON 中 `request` 是输入，`checks` 是审读标准；运行者只接收输入和待测 Skill，审读者再对照标准检查产物。

## 复跑方式

1. 指定待测 `skill/project-interview-skill/` 和干净的临时输出目录。E1 还需指定 DeerFlow 路径，记录其提交 SHA 与工作区状态。
2. 将对应 `request` 的 `${DEERFLOW_ROOT}`、`${OUTPUT_DIR}` 替换为实际路径；在独立对话中运行，保持源码只读。部分交付用例遵从请求，不强制生成课程。
3. E1 运行 `python3 skill/project-interview-skill/scripts/validate_output.py <面经路径> --guide <导学路径>`；其他用例审读输出，不用结构校验替代语义判断。
4. 对照每例 `checks`，核验实际正文、口播及证据。记录通过/失败、具体位置与原因；修复后保留首次失败及复跑结果。

一次生成通过只证明本次样本的行为。没有运行大模型的 `npm test` 不会执行这六个用例，不能宣称自动覆盖业务语义。

## 记录

- [2026-10-13 改造与 DeerFlow 验证](../docs/testing/2026-10-13-business-narrative.md)
- [2026-10-13 常见技术英文选择验证](../docs/testing/2026-10-13-technical-terminology.md)
- [2026-10-13 支柱与成稿验证](../docs/testing/2026-10-13-bullet-quality.md)：包含首次补稿、修订和跨领域独立首稿；DeerFlow 独立生成未完成，限制单独记录。

## 术语评测复跑

T1–T5 是合成材料，T6 使用[已核验的 DeerFlow 事实](evals/deerflow-terminology-facts.md)。六例均只生成 bullet，不需要重新生成课程或启动应用。

`supplemental_cases` 中的 T7/T8 是首轮审读发现 worker 译名过度具体化后加入的定向验证：分别检查执行载体未知和明确为独立进程的材料。它们单独报告，不计入原六例的首次结果。

将保存版与新版 Skill 分别冻结到独立目录，用同一 `request` 执行。执行者不读取 `checks`、另一版本输出或预期答案；每例保存第一次完整的 `output.md`，并把英文/中文取舍说明单独保存为 `terminology-notes.md`。审读者对照事实与 `checks` 评估，若修改正文，保留初稿并记录原因。接受零英文、合法同义表达与不同标题，不用指定词匹配代替语义判断。

自动回归另覆盖英文、中英混合标题的 B/Q/C 关联，以及标题与映射表不一致时的拒绝行为。`npm test` 不运行大模型，也不证明同行熟悉度。
