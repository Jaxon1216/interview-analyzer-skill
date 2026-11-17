# 测试集与复跑

按检查类型分别记录结果，不把结构通过当作内容正确。`npm test` 不调用大模型，也不启动 DeerFlow。

| 层次 | 入口 | 验证范围 |
| --- | --- | --- |
| 自动回归 | `npm test` | 输入与提示词脚本、Bundle 链接、简介下的技术栈、bullet 格式、B/Q/C 关联、课程与文件链接 |
| HTML 模板回归 | `npm run test:html` | 连续状态示例的无头交互、即时反馈、重置、键盘和打印；桌面/手机截图基线比较 |
| 生成 HTML 冒烟 | `npm run test:html -- --topic-root <topics目录>` | 另对真实生成页检查运行、交互与布局，保存截图供审阅；不与随机生成的内容做像素回归 |
| 行为评测 | [business-narrative.json](evals/business-narrative.json) | 业务选材、指标口径与归属、责任模式、历史决策和材料不足时的行为 |
| 术语行为评测 | [technical-terminology.json](evals/technical-terminology.json) | 事实匹配、目标岗位熟悉度、中英比较、标题与正文一致性；不按英文数量评分 |
| 支柱与成稿评测 | [bullet-quality/](evals/bullet-quality/README.md) | 从完整项目选材，讲清设计动机、关键做法与具体变化；事实、术语和成稿分别判定 |

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

## 可迁移的 DeerFlow 准备入口

DeerFlow 作为独立测试来源，不复制进本仓库版本历史或 Skill Bundle。[源码清单](evals/deerflow-source.json)固定用户 fork 的 URL 与提交 SHA。本次基线为 `6783073a39f2de19b11d952d87f55e3fa67601f9`，与 2026-10-13 归档评测的 `5ecc1c2a…` 不同，不能混为同一轮复跑。

新电脑无需先手动克隆 DeerFlow。未指定外部源码路径时，以下命令会在被忽略的 `.test-repos/deer-flow/` 缺失时，读取源码清单的 `repository_url` 与完整 `commit`，自动 clone 并以 **detached HEAD** 检出固定提交，再准备完整交付用例：

```bash
python3 tests/prepare_deerflow_eval.py --case e1 --output-dir .test-runs/deerflow-e1-first
```

首次准备需要能访问清单中的 Git 仓库。clone 在同级临时目录完成并核验后才放入缓存；失败不会留下可被误用的半成品缓存。已有缓存直接复用并校验 SHA 与工作区，不联网更新、不跟随分支最新版本，也不自动切换或清理已有缓存。离线运行可加 `--offline`；缓存缺失时会明确失败，不尝试联网。

准备仅简介与 bullet 的用例，或使用已有源码和冻结 Skill：

```bash
python3 tests/prepare_deerflow_eval.py --case bullet-quality --source-root /path/to/deer-flow --skill-root /path/to/frozen/project-interview-skill --output-dir .test-runs/deerflow-bullets-first
```

源码路径优先级是 `--source-root`、`DEERFLOW_ROOT` 环境变量、仓库内 `.test-repos/deer-flow/`。显式参数或环境变量指定的外部源码始终只读：路径缺失即报错，不自动 clone、切换提交或创建分支。`--output-dir` 必填，必须不存在或为空，并位于源码和待测 Skill 目录之外；首次产物不会被覆盖。默认 Skill 为本仓库 `skill/project-interview-skill/`，对比两个版本时分别指定冻结副本。

缓存就绪后，准备脚本以只读 Git 命令核验仓库根目录、实际 SHA 和工作区，记录 Skill 内容指纹、原始请求与请求指纹。SHA 不匹配或工作区 dirty 时默认退出；确需检查当前开发版本时显式使用 `--allow-source-drift`，元信息会将其标为不可直接与固定源码基线比较。当前源码里已有未追踪的教学产物也属于 dirty。升级测试源码时应显式更新并评审源码清单，再准备与新清单匹配的专用缓存；不在测试中偷偷更新基线。

成功后输出三份文件：`agent-input.md` 是给执行子 agent 的完整输入；`request.md` 保存替换路径后的请求；`manifest.json` 保存本次基线与指纹。实际交付写到该评测目录内的 `delivery/`。准备脚本不会把源码或 Skill 复制到交付目录，不调用模型、不生成课程、不启动应用，也不会把评测 `checks` 写进执行者输入。准备成功只代表测试输入就绪，仍需执行与验收。

## 分支与测试结果留存

测试默认不创建分支，也不自动切换当前主仓库分支。Skill 开发可以按正常开发流程使用 `codex/...` 分支；自动创建的 DeerFlow 缓存固定在清单 SHA 的 detached HEAD，不需要另建测试源码分支。生成任务只读源码，所有生成产物写到独立的 `.test-runs/`，不会写入 DeerFlow 缓存或日常开发 checkout。

不是每次测试都需要产生 Git 提交，按材料用途留存：

| 材料 | 留存方式 |
| --- | --- |
| 测试代码、用例、依赖锁文件、源码 URL 与 SHA 清单 | 随相关改动进入本仓库版本历史，供其他机器复跑。 |
| 稳定模板的截图基线 | 经审阅后随预期视觉变化提交；失败时不自动更新或接受新基线。 |
| 日常运行日志、完整生成课程、浏览器 trace 和临时截图 | 留在被忽略的 `.test-runs/`；CI 可保存为有保留期限的 artifacts。 |
| 重要行为回归、发布验收或失败修复记录 | 挑选可复核的摘要与必要证据归档到 `docs/testing/`，保留首次失败与修复后结果。 |
| DeerFlow 源码缓存 | 保持被忽略；通过清单与准备流程重建。 |

归档摘要应记录用例、源码 SHA、Skill 指纹、执行命令、运行环境和各项通过/失败结果；生成任务还需标明实际产物与审读结论。归档前移除机器绝对路径、凭据及私有信息，不直接提交原始本机 manifest 或全量日志。测试命令和准备脚本都不自动执行 `git add` 或 `git commit`。

## 执行与验收

1. 将 `agent-input.md` 的内容交给新的子 agent，只提供指定 Skill、源码和请求。执行者不读取评分标准、历史输出或诊断；保留首次完整产物，修订另存。执行期间保持源码只读与 Skill 版本不变，结束后再次核对实际 SHA、工作区与 Skill 指纹；发生变化就记录并重新准备，不能沿用原 manifest 声称同一基线。
2. E1 完成后运行结构校验：`python3 skill/project-interview-skill/scripts/validate_output.py <面经路径> --guide <导学路径>`。使用其他冻结 Skill 时，改为该副本内的校验器。bullet-only 用例按交付范围验收，不强制补课程。

   完整交付要求 `## 项目简介` 下有非空的 `### 技术栈`，代码示例里的标题或同级章节不能替代。单独校验旧版 bullet 时不传 `--guide`，仍只检查 bullet 格式；技术栈内容是否属实由源码与语义审读确认。
3. 有 HTML 专题时运行 `npm run test:html -- --topic-root <delivery内的topics目录>`。HTML 开发回归需 Node.js 20 或更高版本（Skill 安装器仍支持 Node.js 18）；首次安装需 `npm ci` 和 `npx playwright install chromium`。检查结果与截图保存到 `.test-runs/html/`，全程无头运行，不弹出用户可见预览。技能来源与共享租约示例有各自的操作路径断言：检查保留其他条件后的结果变化、两种完成顺序、最终结局、反事实恢复与重置；旧 radio 页面保留兼容适配器。新机制应补对应的交互断言，不要求页面为通用测试器套固定控件。
4. 由另一位审读者对照对应 `checks` 或 [bullet 审读标准](evals/bullet-quality/README.md)核对正文与证据。HTML 另按 [教学规则](../skill/project-interview-skill/references/rules/html-teaching.md)审查单一学习成果、完整工作示例、每步因果反馈及判定方法，实际操作并看截图。结构、运行呈现、事实和教学分别记录；不能由技术通过或条件覆盖推导好学。修复后保留首次失败与复跑结果。准备成功只代表输入准备完成，不能报告生成或验收已通过。

模板截图基线按平台命名，当前提供的基线是 macOS（darwin）环境。迁移后应使用相同环境，或明确审阅新平台截图再建立基线。`npm run test:html:update` **仅用于显式更新稳定模板夹具的基线**；更新后必须审阅差异，不能自动接受失败截图。真实生成页的截图冒烟与人工审阅不等于已有基线的视觉回归。

## 其他行为用例

E2–E6 直接将对应 `request` 与冻结 Skill 交给独立生成者；输出使用各自的干净临时目录，不强制生成课程。另由审读者对照每例 `checks` 检查事实与表达，不用结构校验替代语义判断。

一次生成通过只证明本次样本的行为。没有运行大模型的 `npm test` 不会执行这六个用例，不能宣称自动覆盖业务语义。

bullet 动机表达回归可组合 DeerFlow、EdgeMetric 与 GenBI 后端请求，再用 E4/E6 检查是否编造历史问题，用 E5 检查真实演进是否保留。GenBI 请求中的 `${GENBI_ROOT}` 与 `${OUTPUT_DIR}` 由运行者替换；与合成用例一样，记录源码基线、工作区和冻结 Skill 指纹，再把请求与 Skill 交给新生成者。审读按设计动机、运行机制、具体变化和事实边界逐项记录，接受不同句式；不增加“包含痛点关键词”一类自动措辞断言。

## 记录

- [2026-11-17 技术栈与完整 E1](../docs/testing/2026-11-17-terms-stack-e1.md)：技术栈层级、具体术语保留、60 项自动回归，以及真实 DeerFlow 的 9 课、两页 HTML、首次问题与最终复核。
- [2026-11-17 Bullet 动机、做法与变化](../docs/testing/2026-11-17-bullet-causality.md)：规则、模板、few-shot 与提示词同步修订；57 项自动回归、六例独立首次生成及独立语义审读。
- [2026-11-08 HTML 教学品质修订](../docs/testing/2026-11-08-teaching-quality.md)：用户反馈后的教学生成契约重做、两页样课、独立教学审读与第三案例验证；与事实和功能检查分开报告。
- [2026-11-08 DeerFlow 自动缓存与教学 HTML 回归](../docs/testing/2026-11-08-deerflow-html-regression.md)：真实首次 clone、离线复用、57 项单测、一次完整 E1 生成及首次失败与修订记录。
- [2026-10-13 改造与 DeerFlow 验证](../docs/testing/2026-10-13-business-narrative.md)
- [2026-10-13 常见技术英文选择验证](../docs/testing/2026-10-13-technical-terminology.md)
- [2026-10-13 支柱与成稿验证](../docs/testing/2026-10-13-bullet-quality.md)：包含首次补稿、修订和跨领域独立首稿；DeerFlow 独立生成未完成，限制单独记录。

## 术语评测复跑

T1–T5 是合成材料，T6 使用[已核验的 DeerFlow 事实](evals/deerflow-terminology-facts.md)。六例均只生成 bullet，不需要重新生成课程或启动应用。

`supplemental_cases` 中的 T7/T8 是首轮审读发现 worker 译名过度具体化后加入的定向验证：分别检查执行载体未知和明确为独立进程的材料。它们单独报告，不计入原六例的首次结果。

将保存版与新版 Skill 分别冻结到独立目录，用同一 `request` 执行。执行者不读取 `checks`、另一版本输出或预期答案；每例保存第一次完整的 `output.md`，并把英文/中文取舍说明单独保存为 `terminology-notes.md`。审读者对照事实与 `checks` 评估，若修改正文，保留初稿并记录原因。接受零英文、合法同义表达与不同标题，不用指定词匹配代替语义判断。

自动回归另覆盖英文、中英混合标题的 B/Q/C 关联，以及标题与映射表不一致时的拒绝行为。`npm test` 不运行大模型，也不证明同行熟悉度。
