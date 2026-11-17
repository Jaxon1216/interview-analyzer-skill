# Bullet 动机、做法与变化：规则修订及验证

日期：2026-11-17。修改仓库内 Skill，并同步本机已安装副本；未发布或提交。自动回归与实际生成内容分别验收。

## 修改内容

原规则在事实归档和交付检查中提到目标、障碍，但控制成文的规则、模板及 few-shot 多次强调直接讲运行机制、背景按需，导致成稿容易只剩源码流程。本次修改生成过程及示范正文，不只增加末尾检查项。

| 文件（相对 `skill/project-interview-skill/`） | 调整 |
| --- | --- |
| `SKILL.md` | 组织支柱及正文时连起设计动机、关键做法和具体变化；职责与协作服务于因果解释。 |
| `references/rules/oral-and-resume-patterns.md` | 成稿前从事实卡提取目标或障碍、可见变化，再选择能解释联系的关键机制；项目简介不替代各条工程动机。 |
| `references/rules/repository-investigation.md` | 区分材料明说的问题、从实现分析的目的和已验证结果，不把目的分析当历史事故或收益。 |
| `references/excellent-resumes/susu-bullet-template.md` | 保留金样原文，补回金样中的需求与因果；改写说明、可迁移句形和示范正文。 |
| `references/excellent-resumes/README.md` | 默认模板索引同步为动机、做法与变化相连。 |
| `references/examples/bullet-few-shots.md` | 更新机制起笔、真实演进、复杂分层和 SSE 示例；新增同一事实下“流程说明→有因果成稿”的对照。 |
| `references/templates/output-templates.md` | 面经骨架要求正文表达设计必要性、做法与具体变化，句式和位置保持灵活。 |
| `scripts/build_prompt.py` | 同步生成摘要、内嵌 few-shot 与改写原则，移除与新规则相冲突的机制优先表达。CLI 参数和逻辑不变。 |

工程目的可以由当前机制分析，例如限制重复调用、分离受理与执行；历史事故、版本演进、当时选型和实测收益仍需来源。动机可以融入场景、约束、条件或作用，不要求统一痛点前缀、固定三句或完整 STAR。没有指标时写可见能力，作用已经融入动作时不重复总结。

## 测试方式与自动结果

仓库已有两类相关入口：`npm test` 检查脚本与结构；`tests/evals/` 的请求交给独立生成者，再由另一位审读者做语义判断。前者不会调用模型，不能据此判断 bullet 是否讲清动机。

| 实际执行 | 结果 |
| --- | --- |
| `npm test` | 57/57 通过，退出 0。覆盖提示词、输入、Bundle 链接、B/Q/C、课程和文件关联；约 57.9 秒。 |
| `npm run pack:check` | 退出 0，24 个发布文件；测试请求及评测产物未进入运行时包。 |
| skill-creator `quick_validate.py` | 隔离 uv 环境中退出 0，`Skill is valid!`。系统 Python 首次执行因缺 PyYAML 失败，原记录保留；未修改项目依赖。 |
| `python3 -m py_compile skill/project-interview-skill/scripts/build_prompt.py` | 退出 0。另实际执行 CLI 保存生成提示词。 |
| `git diff --check` | 退出 0。 |

skill-creator 校验命令（路径归一化）：

```bash
uv run --isolated --no-project --with pyyaml python <SKILL_CREATOR>/scripts/quick_validate.py skill/project-interview-skill
```

本次没有为生成措辞添加关键词匹配测试，也没有改变原有结构断言。HTML 没有本轮改动，未重跑浏览器回归或生成课程。

## 实际生成流程与基线

1. 保存修改前 Skill 和原工作区 diff；修改后冻结完整 Skill 到独立 `.test-runs/` 目录。
2. DeerFlow 使用已有准备脚本，离线复用固定源码缓存。准备命令如下，`RUN_DIR` 为本轮独立目录：

   ```bash
   python3 tests/prepare_deerflow_eval.py --case bullet-quality --offline --skill-root "$RUN_DIR/after/project-interview-skill" --output-dir "$RUN_DIR/deerflow"
   ```

3. EdgeMetric 使用已有请求，E4/E5/E6 仅提取原 JSON 的 `request`；GenBI 使用新增的参数化后端请求。生成者不获得 `checks`、诊断、旧 bullet 或另一用例的结果。
4. 六例各由一个新上下文的子 agent 执行，仅读取原材料、指定 Skill 及所需引用。首次完整输出保留，未在生成后修稿。
5. 独立审读者读取原请求、首次产物及审读标准，分别判定选材、动机、机制、变化、事实边界与术语；源码例另按证据抽查。DeerFlow 的后四条再由其只读子审查并行核对。

环境：macOS 26.4.1 arm64、Python 3.14.4、Node.js v24.15.0、npm 11.12.1。

- 待测 Skill SHA-256：`bdc4a6b621f86da76b8f3314274f5d36657c6c01fbe267679aeb3b9000ba55b1`。采用排序相对路径、NUL、文件内容、NUL 的整树摘要，排除 Python 缓存；生成前后与当前源码一致。
- DeerFlow：`6783073a39f2de19b11d952d87f55e3fa67601f9`，前后工作区干净，符合固定源码清单。生成者另核对已跟踪源码内容指纹前后一致。
- GenBI：HEAD `8bc3edf984d1419e9f2f16d4d72d990d48ca7ad9`，分析当前已有未提交修改的工作树，不等同于该提交的干净快照；HEAD 与工作区状态前后相同。生成任务只读后端及必要的前端接口契约，未读取旧面经作为事实来源。
- 本机安装副本中本轮修改的 8 个文件均与修改前基线一致后才同步，并保存原文件备份。同步后完整副本与受测冻结 Skill 的指纹一致。

## 首次输出及独立审读结果

| 用例 | 首次产物 | 成稿 | 事实与术语 | 关键判断 |
| --- | --- | --- | --- | --- |
| DeerFlow | [简介与 6 条 bullet](samples/bullet-causality/deerflow-first.md)、[源码证据](samples/bullet-causality/deerflow-evidence.md) | 通过 | 通过 | 能力按需发现、委派容量、上下文恢复和共享沙箱均有动机及可见变化；保留开关、恢复方式和回放窗口条件。 |
| GenBI | [简介与 5 条 bullet](samples/bullet-causality/genbi-first.md)、[源码证据](samples/bullet-causality/genbi-evidence.md) | 通过 | 通过 | 说明受理不等待生成、补发下的重复调用风险、跨进程终态通知；未宣称消息必达或执行中断后自动恢复。 |
| EdgeMetric | [简介与 5 条 bullet](samples/bullet-causality/edgemetric-first.md)、[事实记录](samples/bullet-causality/edgemetric-evidence.md) | 通过 | 通过 | fsync 后确认、冻结换表、查询版本和回收时机分别联系工程目标；未编造旧版事故、性能或通用事务保证。 |
| E4：只有当前实现 | [一条 bullet 与递进口播](samples/bullet-causality/E4-first.md) | 通过 | 通过 | 解释队列分离提交与执行；不把两个运行环节写成两期改造，也不补造接口立即返回等未知能力。 |
| E5：有明确历史陈述 | [一条 bullet 与方案口播](samples/bullet-causality/E5-first.md) | 通过 | 通过 | 保留验收网关超时、当时两方案比较和两版演进；结果限定于返回受理及后台生成。 |
| E6：未知业务背景 | [简介与一条 bullet](samples/bullet-causality/E6-first.md) | 通过 | 通过 | 围绕插件统一接入与调度表达工程目的；没有编造旧系统耦合、运营目标、热插拔或收益。 |

例如，GenBI 首稿中的 CAS 条目直接以“面对事务消息补发可能产生的重复投递”交代必要性，再解释条件更新、未命中确认及避免重复调用；E5 则基于明确陈述写出验收痛点与真实演进。两种表达均成立，不要求统一起笔。

独立审读没有发现必须修订项，完整理由见[审读记录](samples/bullet-causality/review.md)。GenBI 入口限流不能扩大成消费端执行频率硬上限，CAS 不能扩大成运行态恢复，Pub/Sub 不能扩大成可靠事件通道；DeerFlow 的显式恢复、进程内容量及有限窗口回放也保留对应范围。

归档仅归一化本机绝对路径和证据链接，没有编辑首稿正文；[manifest](samples/bullet-causality/manifest.json) 保存请求、原始输出及归档输出摘要。完整原始产物、日志、修改前副本和安装备份留在被忽略的运行目录。

六例通过说明本次首次生成符合所审读的内容要求，未证明多次生成稳定优于旧版。源码项目采用静态查证，未启动应用、调用其模型或运行其业务测试；本轮也没有重跑完整 E1 课程交付。
