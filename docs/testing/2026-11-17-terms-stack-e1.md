# 技术栈、具体术语与 DeerFlow 完整 E1 回归

日期：2026-11-17。按本仓库既有测试流程，在真实 DeerFlow 源码上完成 E1 生成、结构检查、实际 HTML 验收和独立内容审读；同时复跑 GenBI 简介与 bullet。首次完整输出和修订结果分别保留。修改已同步本机安装的 Skill，未提交或发布。

## 既有约束在哪里

- [测试说明](../../tests/README.md) 已区分自动回归、完整 E1、bullet-only 和 HTML 验收；完整 E1 不是只准备输入或只生成 bullet。
- [2026-11-08 回归记录](2026-11-08-deerflow-html-regression.md) 已记录真实首次 clone、固定 SHA、离线缓存复用、完整 E1、首次失败及修订。
- 当前工作区为 `main`。测试说明是已跟踪文件；自动准备脚本、固定源码清单及 11 月 8 日回归记录在当前工作区，尚未提交。检查本地已知的 `origin/codex/humanized-progressive-teaching` 时，该分支也有 E1 说明，但不含这批自动准备文件；本轮没有切换分支。
- 上一轮 [bullet 因果回归](2026-11-17-bullet-causality.md) 使用真实源码缓存，但只执行 `bullet-quality`。本轮补跑完整 E1。

源码来自 [固定来源清单](../../tests/evals/deerflow-source.json)：`https://github.com/Jaxon1216/deer-flow.git`，提交 `6783073a39f2de19b11d952d87f55e3fa67601f9`。本次复用已存在的干净 clone，准备脚本核对固定提交和工作区；没有重新联网 clone。既有流程只在托管缓存缺失时自动 clone，不要求每次重建。完整 E1 按准备输入保持源码只读，不启动 DeerFlow 业务应用或调用其真实模型链路。

## Skill 修改

| 位置（相对 `skill/project-interview-skill/`） | 调整 |
| --- | --- |
| `SKILL.md` | 项目简介下增加 `### 技术栈`；正文保留解释关键做法的框架、库、协议和通用机制名称。 |
| `references/rules/oral-and-resume-patterns.md` | 技术栈集中展示，bullet 解释技术作用；具体库不必人人熟悉，不能因普通中文替代词而抹掉已验证技术。仍不设英文数量或术语配额。 |
| `references/templates/output-templates.md` | 明确简介、技术栈小标题和 bullet 的层级及各自职责。 |
| `references/excellent-resumes/susu-bullet-template.md` | 补充关键技术参与机制解释的正向成文要求。 |
| `references/examples/bullet-few-shots.md` | 用 Go Context / `http.NewRequestWithContext` 对照过度泛化的“传递上下文”，说明真实名称如何服务因果表达。 |
| `scripts/build_prompt.py` | 提示词同步技术栈及具体技术保留要求，CLI 参数不变。 |
| `scripts/validate_output.py` | 完整交付要求简介下有非空技术栈；代码围栏里的示例标题或同级章节不能代替。旧 bullet-only 校验保持兼容。 |

技术名词的观察有项目差异：上一轮 DeerFlow 已保留 LangChain/LangGraph、MCP、checkpoint、SSE 等；GenBI 的 Excelize、Go Context 等有局部泛化。本轮 [GenBI 首稿](samples/terms-stack-e1/genbi-first.md) 在技术栈中集中列示，也在相应做法中自然使用 Excelize、GORM 事务、Transactional Outbox、CAS、Ack、Redis Pub/Sub、redis_rate、Go Context 和 net/http；[证据记录](samples/terms-stack-e1/genbi-evidence.md)区分源码配置、静态能力、未运行测试及可靠性限制。

## 如何实际执行

1. 保存修改前 Skill 与当前工作区 diff；修改后冻结完整 Skill，供生成者与校验器使用。
2. 用既有入口准备 E1。以下为实际命令的路径归一化形式，`RUN_DIR` 是本轮新建的独立运行目录：

   ```bash
   python3 tests/prepare_deerflow_eval.py --case e1 --skill-root "$RUN_DIR/frozen/project-interview-skill" --output-dir "$RUN_DIR/e1"
   ```

3. 新上下文执行者只接收该 `agent-input.md`、冻结 Skill 和真实源码，不读旧输出、checks 或本轮诊断。完整请求覆盖 Web 提交、Gateway/Agent、工具/沙箱、技能加载、流式展示和产物；不扩展定时、IM、长期记忆。
4. 生成主会话实际分别委派 C05/C06 HTML 作者，回填导学与课程。封存 `first-delivery`，后续修订仅写 `delivery`。另一个新上下文独立生成 GenBI 简介与 bullet。
5. root 独立运行结构、浏览器与版面检查；另一位审读者独立全文审读，按原始源码抽查，另委派只读课程审查。首稿问题修订后定向复核，不把自动通过当作内容或教学通过。

本轮冻结 Skill 指纹为 `b12585db6d9055db37ab13a9095b2c7db03a386bae3c554e03b2d705125485a1`。正式算法按排序相对路径和内容计算，排除 `__pycache__`、`.pyc`、`.pyo`。root 动态加载校验器产生过冻结目录编译缓存，新增缓存及其来源已记录；规则、模板和脚本正文始终未变。DeerFlow 全源码内容及干净工作区前后不变；GenBI 采用原有 dirty 工作树，只读使用，HEAD 和工作区状态前后相同。

## 实际结果

E1 完整产物包含导学、面经、9 节完整核心课、5 条 bullet、6 组主问和递进追问，以及 C05 沙箱租约、C06 技能加载两个单文件离线 HTML。课程和 HTML 全部保存在本轮独立运行目录，未写入源码缓存或运行时发布包。

| 检查 | 首次结果 | 最终结果 |
| --- | --- | --- |
| `npm test` | 60/60 通过；新增 3 项结构/兼容回归 | 同一运行时版本，之后未改规则或脚本正文，无须重复 Python 回归 |
| `npm run pack:check` | 通过，24 个发布文件 | 受测运行时指纹不变，评测文件未进入包 |
| skill-creator `quick_validate.py` | 隔离 uv + PyYAML 环境通过 | 运行时内容不变 |
| HTML 稳定模板 | 4/4 通过，既有截图基线未更新 | 与实际页面检查一起复跑通过 |
| GenBI 简介/技术栈层级及 bullet 格式 | 通过 | 首稿未改；独立成稿、事实与术语审读通过 |
| E1 独立结构校验 | 通过 | 修订后再跑，`Delivery structure: OK` |
| 两页实际 HTML + 模板 | 8/8 通过 | 加入首屏入口断言，修订后 8/8 通过 |
| E1 独立内容审读 | F1 恢复边界需修订，其余主线/课程/教学通过 | F1 定向复核通过，E1 五项 checks 满足 |
| root 手机首屏检查 | C05 按钮 y=1033.90625，低于 844 高视口 | y=461.125，完整进入首屏；桌面也通过 |
| 本机安装副本 | 修改前文件逐一匹配后才同步 | 完整副本指纹与受测冻结 Skill 一致 |

结构与实际页面检查的命令：

```bash
python3 "$RUN_DIR/frozen/project-interview-skill/scripts/validate_output.py" "$RUN_DIR/e1/delivery/interview-prep/DeerFlow/面经.md" --guide "$RUN_DIR/e1/delivery/interview-prep/DeerFlow/导学.md"
npm run test:html -- --topic-root "$RUN_DIR/e1/delivery/interview-prep/guide-fullstack/topics"
```

两页采用连续状态操作，本轮给浏览器测试器新增 `sandbox-leases` 和 `skill-loading` 专用适配。断言覆盖同一沙箱对象、两种结束顺序、最后持有者释放、被动读取的声明并集、slash 来源优先、deferred 先描述再读取、键盘重置、离线、本地链接、打印及两种视口，保存 24 张独立阶段截图（附件副本另计）。root 实际查看了首稿两页的桌面/手机代表截图，以及修订后 C05 手机首屏；没有自动接受新截图基线。

## 首次问题及修订

- **F1：SSE 恢复条件泛化。** C07 和 Q6 曾把“游标太旧或日志不存在”都概括成 gap。原始源码区分桥报告 `StreamGap`、普通终态缺流默认 `end`、本次线程范围幂等创建重试显式缺流 `gap`，以及不可跨进程观察的 store-only join `409`。修订课程的总结/图示/正文、Q6 和关联触发词，明确只有实际收到 gap 才进入前端持久状态重读；最后再次明确终态条件同时限定普通 join 与无状态创建入口。
- **惰性获取范围。** B3 与相关解释补上默认共享技能视图条件，保留受限投影等 eager 路径，避免将首次工具使用时机推广到所有执行。
- **技术栈成稿。** 将私有实现类型改为真实技术与通用职责，依赖版本和部署核验说明移到交付说明，保持正文可以贴入简历。
- **手机入口。** C05 控件移到主图之前并精简手机前言，状态对象、图形、反馈和顺序比较不变。root 复测入口位置并加入对应回归断言。
- **首交前教学审读。** C06 曾在仅知名称时允许直接读取未知路径，生成主会话在封存完整首稿前已修正为先 describe 元信息再读取，并保留默认与 slash 两条主链。这是草稿审读修正，未冒充成完整首稿后的自动测试失败。

首稿与最终[简历摘录对照](samples/terms-stack-e1/deerflow-resume-first.md)、[最终简介与 bullet](samples/terms-stack-e1/deerflow-resume-final.md)；[独立首稿审读](samples/terms-stack-e1/review-first.md)、[逐课审查](samples/terms-stack-e1/course-audit-first.md)、[定向最终复核](samples/terms-stack-e1/review-final.md)；[主会话首稿补充检查](samples/terms-stack-e1/root-review-first.md)与[修订记录](samples/terms-stack-e1/revisions.md)。原始完整首稿的 19 个文件逐一核对未变。

## 留存与范围

[归档 manifest](samples/terms-stack-e1/manifest.json) 保存运行环境、源码基线、Skill 指纹、命令和退出码、首次/最终状态、版面测量及归档摘要。归档移除本机绝对路径；简历只摘录简介和 bullet，不把摘录冒充完整面经。完整首稿、最终导学/面经/9 课/2 页、原始审读、日志、截图与安装备份保存在被忽略的 `.test-runs/terms-stack-e1-2026-11-17-a88u4e_9/`。

本次验证的是 Skill 的完整真实源码交付；没有启动 DeerFlow 业务应用、调用它的模型服务或跑其业务测试套件。一次生成及修订通过不代表多次生成稳定优于旧版，首稿内容缺陷没有被自动通过结果抵消。

## 后续用户验收：技术栈摘要密度

用户指出技术栈长列表不符合金样。重新核对两份 OCR 及历史版本：酥神金样没有独立技术栈行，DeerFlow 是在版本总标题中使用 `Agent Teams Harness + Middleware Chain + Skill System + Context Engineering`，再逐项展开。此前“简介下技术栈集中展示”是新增输出规则，不能反过来当作金样证据。

保留用户要求的 `### 技术栈`，将默认正文收紧为一行核心技术组合；版本、客户端包、标准库 API 和可选配置不展开为盘点。关键库和 API 的作用仍在相关 bullet 中解释。同步修改主 Skill、表达规则、输出模板、默认金样说明、领域中立 few-shot 和提示词脚本，未改变标题层级、B/Q/C 或 HTML 机制。

两个项目的摘要由新的独立执行者只读核实并生成，执行者不读旧结果或预期答案：

- [GenBI 简介与技术栈](samples/stack-summary/genbi.md)：`Go + Gin + GORM + MySQL + Redis + RabbitMQ + DeepSeek`。
- [DeerFlow 简介与技术栈](samples/stack-summary/deerflow.md)：`TypeScript + Next.js + Python + FastAPI + LangChain + LangGraph + MCP`。
- [简短源码证据](samples/stack-summary/evidence.md)、[更新后的 GenBI 简历片段](samples/stack-summary/genbi-resume-revised.md)、[更新后的 DeerFlow 简历片段](samples/stack-summary/deerflow-resume-revised.md)。简历片段仅替换原技术栈正文，保留原简介与 bullet；此前首稿及归档不改。

该摘要候选指纹为 `384cfbffe7979e450c4f66a4df50d04a4d4fb57115637b501803bf83e6b2534c`。`npm test` 60/60、打包和 skill 格式校验通过，并同步本机安装副本；命令和结果见[本轮 manifest](samples/stack-summary/manifest.json)。本轮针对简介/技术栈生成与既有完整交付的摘要替换作复核，前文完整 E1 的首次生成与浏览器结果仍属于原候选版本，不混称为本轮重跑。
