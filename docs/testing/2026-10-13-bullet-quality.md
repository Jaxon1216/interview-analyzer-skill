# Bullet 支柱提炼与成稿：改造及实际验证

日期：2026-10-13。直接修改本地 Skill，未提交、未推送。自动回归与人工内容审读分开。

本轮有一项明确缺口：DeerFlow 独立生成因账号用量限制失败，未交付完整输出；不能报告完整独立验证通过。提供主 agent 使用冻结新版 Skill 按需只读查证后的补稿与编辑修订，供立即审阅。跨领域 EdgeMetric 已完成一次独立生成。单次样本和非独立补稿不能证明稳定达到金样。

## 失效位置与最小修改

| 修改文件（相对 skill/project-interview-skill） | 原有问题 | 本次修改 |
| --- | --- | --- |
| `SKILL.md` | 先选支柱再归档；检查将术语与成稿放在一起 | 先识别完整范围的职责与机制，再组织支柱；独立判定整组选材、逐条成稿与术语。 |
| `references/rules/oral-and-resume-patterns.md` | “架构演进 > 系统机制”及细节一律下沉追问；反复要求具体效果 | 按系统职责组织，关键实现可留正文/二级；写职责、协作和行为条件，允许直接结束，审读句子新增信息。 |
| `references/rules/repository-investigation.md` | 代表性链路可能沿预先分类展开 | 先看完整职责/状态/分工，再选择链路查证，接口/目录分类不决定支柱。 |
| `references/excellent-resumes/susu-bullet-template.md` | 可迁移句形反复填具体效果 | 作用有支持且增加信息才写；调整句形，保留原始金样片段。 |
| `references/excellent-resumes/deer-flow-harness.md` | 点评将 owner、演进、四标题当可复用骨架；文末要求写金样四机制 | 重写点评，组织方式可学习，身份/历史/层数/组合不可迁移；当前源码自行选标题与数量。OCR 正文保留。 |
| `references/examples/bullet-few-shots.md` | 先按目标选 4～6 支柱；SSE 例子有复述尾句，缺少从未分组材料选材示范 | 调整先机制后支柱顺序，增加短小转码选材示范，删除 SSE 空泛尾句并明确局部例子不自动成为一级。 |
| `references/templates/output-templates.md` | 骨架仍要求末尾接效果/指标 | 同步职责、协作与行为条件，可支持的新作用才写。 |
| `scripts/build_prompt.py` | 摘要提示重复要求效果，通用工程能力标题过宽 | 同步选材、机制命名、中英选择及分开审读，合并重复质检提示。CLI 参数不变。 |

运行时共 8 个文件，40 行新增、34 行删除。目录、B/Q/C、课程和口播契约、校验器、CLI 均未重做；未改安装在 .agents 下的 Skill。

旧 T6 的 `technical-terminology.json` 请求固定“5 条”且要求对应给定机制，事实材料亦按五类预分组。其通过不能证明从完整项目选支柱或达到金样表达。本轮保留全部旧评测，新增未指定支柱和条数的[真实请求](../../tests/evals/bullet-quality/deerflow-request.md)与[跨领域材料](../../tests/evals/bullet-quality/edgemetric-request.md)，[审读标准](../../tests/evals/bullet-quality/README.md)不提供给生成者。

## 生成记录与最新结果

冻结包及请求指纹见[manifest](2026-10-13-bullet-quality-manifest.json)。冻结 Skill 与最终运行时 Skill 一致。本机 DeerFlow SHA 为 `5ecc1c2ac2de624af354bc515d5cb04f80df226c`，工作区开始与结束均干净。完整项目范围按职责地图探索、按需读源码，不代表逐文件穷举；没有启动应用、重生成课程或修改源码。

- DeerFlow 独立生成者：新上下文，只获冻结 Skill（含原有引用）、仓库与请求，不获诊断、旧评测或定制答案；[失败记录](samples/bullet-quality/deerflow-independent-failure.md)。无完整输出可保留，未伪造首稿。
- 主 agent 补稿：已知本轮背景，不满足独立性；[首次完整补稿](samples/bullet-quality/deerflow-primary-first.md)、[最新修订全文](samples/bullet-quality/deerflow-primary-revised.md)、[源码证据及限制](samples/bullet-quality/deerflow-primary-evidence.md)。首稿 B2/B3 重复双处授权，B2 有空泛总结，B1 将调用数概括成并行数；修订删除冗余、细化参数还原/策略顺序、缩小 B1 范围，并补明摘要成功条件。是同一 Skill 下的编辑修订，不是修正规则后独立重跑。
- EdgeMetric：另一新上下文，只获冻结 Skill 与未分组原始材料；[首次完整输出](samples/bullet-quality/edgemetric-first.md)、[生成者事实边界](samples/bullet-quality/edgemetric-evidence.md)。选出 WAL、内存表轮转、MVCC/回收、文件裁剪，未套 Agent 领域标题；本次审读未发现需修订缺陷，未另造修订稿。

[内容审读全文](samples/bullet-quality/review.md)分别记录事实、术语、整组选材与成稿。主 agent 修订稿和跨领域首稿在本次人工审读中通过；DeerFlow 独立内容验证仍未完成。与金样比较重点是职责与机制可识别、行为条件具体、作用可查证，没有复用身份、升级、数字、固定层数或技术组合；不以通过数量或英文数量证明改善。

## 自动检查实际结果

| 命令 | 实际结果 |
| --- | --- |
| `npm test` | 退出 0，29/29；原有 B/Q/C、课程及链接检查通过。未调用模型。 |
| `npm run pack:check` | 退出 0，22 文件；评测与生成产物未进入运行时包，未发布。 |
| skill-creator `quick_validate.py` | 退出 0，`Skill is valid!`。使用 DeerFlow 已有 .venv Python 的 PyYAML；系统 python3 无 PyYAML，未安装依赖。 |
| `git diff --check` | 退出 0；最终文档落盘后再次核对。 |

[命令、退出码与完整 stdout/stderr](samples/bullet-quality/validation/results.json)均保留。自动检查验证结构和包装，不代替内容审读。

本轮未推送远端、未覆盖旧评测或首次完整输出。独立生成的额度限制仍是验收缺项，不将主 agent 补稿改名为独立通过。
