# DeerFlow 源码证据记录

## 分析边界与基线

- 目标岗位：AI Agent 后端研发；模式：目标简历。仅交付项目简介、六条完整 bullet 与本证据记录，不生成课程、面经或 HTML。
- 源码根目录：<DEERFLOW_ROOT>。完整范围包括 Harness、Gateway、前端、工具/Skill、沙箱、记忆、运行持久化及外围接入；从该范围选择对目标岗位最有辨识度的机制，未逐行审计全仓。
- 指定 Skill：project-interview-skill/SKILL.md（`SKILL.md`），版本 1.4.3。读取了该 Skill 内的仓库探索、表达规则、默认 bullet 模板、领域中立 few-shot 和输出模板；没有读取其他运行结果、评分材料或其他版本 Skill。
- 源码 Git HEAD：`6783073a39f2de19b11d952d87f55e3fa67601f9`；分析日期：2026-11-17。首次和落盘前检查均为干净工作区。
- 源码内容指纹：3899 个已跟踪且实际存在的文件，SHA-256 为 `0c00ac31b09535b4424c25dc2d85d37901f6e9fc47069f0346f9ed103019773f`。
- 指定 Skill 内容指纹：19 个文件，SHA-256 为 `bdc4a6b621f86da76b8f3314274f5d36657c6c01fbe267679aeb3b9000ba55b1`。
- 指纹算法：按文件相对路径排序，将每项的“UTF-8 相对路径、NUL、原始文件内容、NUL”依次送入 SHA-256。两次比对一致，未观察到基线变化；源码指纹不覆盖未跟踪文件或外部服务。

本次验证为静态源码查证，没有启动应用、调用真实模型、执行仓库测试或压测，也没有打开预览。已有实现、测试文件或 README 均不作为上线与实测收益证明。无个人职责、历史升级过程和收益数字材料，因而没有声明本人 owner、版本改造经历或性能提升比例。

## 项目职责与代表性链路

项目目标是让用户通过对话完成需要多次推理、工具操作和文件产出的任务；这一产品定位来自 README 与 Agent/工具入口。下列工程动机是依据当前机制作出的分析，不代表团队历史事故、正式 OKR 或当时选型过程。

| 组件 | 已查明的职责 | 入口依据 |
| --- | --- | --- |
| Gateway | 请求规范化、运行受理、后台 worker 与 SSE 订阅 | services.py / start_run（`backend/app/gateway/services.py:1885`） |
| Harness | 组装模型、工具、中间件和状态 schema，构成 Agent 图 | agent.py / create_agent（`backend/packages/harness/deerflow/agents/lead_agent/agent.py:1402`） |
| 子任务运行时 | 委派执行、独立状态、容量准入、状态与结果回传 | task_tool.py / executor 调用（`backend/packages/harness/deerflow/tools/builtins/task_tool.py:993`） |
| 状态与流桥 | checkpoint、运行记录、实时事件与限窗回放 | worker.py / 绑定 checkpointer（`backend/packages/harness/deerflow/runtime/runs/worker.py:1372`）；MemoryStreamBridge（`backend/packages/harness/deerflow/runtime/stream_bridge/memory.py:27`） |
| 沙箱与文件交付 | 命令/文件接口、线程目录、执行租约与产物引用 | SandboxMiddleware（`backend/packages/harness/deerflow/sandbox/middleware.py:54`）；present_file_tool（`backend/packages/harness/deerflow/tools/builtins/present_file_tool.py:83`） |
| Web 工作台 | Next.js/React 对话与工作区应用，消费后端能力 | frontend/package.json（`frontend/package.json:1`）；workspace-content.tsx（`frontend/src/app/workspace/workspace-content.tsx:1`） |

代表链路：

1. 用户请求由 Gateway 规范化并受理运行，RunManager 约束线程并发，后台 worker 组装 Agent 并绑定 checkpoint；图执行事件经流桥交给 SSE 消费者。
2. Agent 组装时按能力配置建立 Skill/MCP 发现工具，模型按需获取说明或工具定义；模型可见列表与工具执行分别经过策略约束。
3. 主 Agent 调用委派工具，后端创建子任务执行器并取得共享容量；子任务使用新状态运行，后端汇集进度与最终结果回到父 Agent。
4. 模型调用前先捕获委派和 Skill 引用，再判断是否摘要；摘要成功后改写活跃消息，后续模型请求从独立状态通道重建持久上下文。主 Agent 的 checkpoint 支持显式恢复，沙箱租约独立保护并发执行期间的资源。

## 按简历顺序核对主张

### B1 中间件编排与扩展点

**目的分析：** 推理请求加工、工具执行与跨步骤状态维护需要不同生命周期钩子；共享基础链可以让主、子 Agent 应用共同的运行约束，扩展顺序也需要在最终组合后成立。

**实现证据：**

- tool_error_handling_middleware.py / _build_runtime_middlewares（`backend/packages/harness/deerflow/agents/middlewares/tool_error_handling_middleware.py:346`） 组合模型包装器、线程钩子和工具包装器；`build_lead_runtime_middlewares` 与 `build_subagent_runtime_middlewares` 复用该基础构建器。
- agent.py / build_middlewares（`backend/packages/harness/deerflow/agents/lead_agent/agent.py:485`） 追加动态上下文、Skill 策略、持久上下文、摘要等能力，最终传入 `create_agent`。
- stack.py / compose_with_extensions（`backend/packages/harness/deerflow/extensions/stack.py:134`） 在完整链上按 placement anchors 注入贡献并调用 `assert_ordering`，不是仅凭目录分层推断可扩展。

**代码直接支持的变化：** 具有现有钩子可表达的横切行为可通过独立中间件与扩展贡献接入，组装期检查已声明的顺序约束。

**限制：** 没有断言固定“11 层”，也没有宣称所有能力零改动接入；涉及 Agent 主循环、缺失钩子或核心状态契约的变更仍可能需要修改核心。没有据当前结构编造旧架构散落或重构历史。

### B2 Skill 与 MCP 渐进发现

**目的分析：** 能力目录增长时，按需展示说明与定义可以让单次请求无需携带所有能力正文；工具被发现与是否允许执行必须分别处理。

**实现证据：**

- agent.py / skill_search_enabled（`backend/packages/harness/deerflow/agents/lead_agent/agent.py:1158`） 从 `skills.deferred_discovery` 读取开关；describe.py / build_skill_search_setup（`backend/packages/harness/deerflow/skills/describe.py:169`） 建立描述工具与名称集合，get_skill_index_prompt_section（`backend/packages/harness/deerflow/skills/describe.py:214`） 渲染名称索引，指导先查询元数据、再读 Skill 正文。
- tool_search.py / build_tool_search_tool（`backend/packages/harness/deerflow/tools/builtins/tool_search.py:233`） 返回命中工具定义并写入目录哈希范围内的 `promoted` 状态；DeferredToolFilterMiddleware（`backend/packages/harness/deerflow/agents/middlewares/deferred_tool_filter_middleware.py:29`） 同时隐藏未提升定义并拒绝直接调用。agent.py / MCP routing 安装顺序（`backend/packages/harness/deerflow/agents/lead_agent/agent.py:704`） 将自动路由置于延迟过滤之前。
- SkillToolPolicyMiddleware / _filter_model_request（`backend/packages/harness/deerflow/agents/middlewares/skill_tool_policy_middleware.py:334`） 过滤模型工具；同文件 `_filter_tool_search_result`、`wrap_tool_call` 同时约束发现结果和执行入口。
- ToolSearchConfig（`backend/packages/harness/deerflow/config/tool_search_config.py:15`） 的 MCP 延迟发现默认关闭；prompt.py / get_skills_prompt_section（`backend/packages/harness/deerflow/agents/lead_agent/prompt.py:939`） 保留未启用名称索引时的兼容渲染路径。

**代码直接支持的变化：** 启用相应发现机制后，Skill 正文按需加载，MCP 未提升定义不会绑定到模型；工具策略继续影响已发现能力。正文明确保留了“启用延迟发现时”的条件。

**限制：** Skill 和 MCP 的开关、加载单位不同；没有把它们描述成同一注册器。Skill 未声明 `allowed-tools` 与显式空列表含义不同，不能宣称所有 Skill 默认限制全部工具。调用拦截是逻辑策略，不等于 OS 沙箱隔离。没有测量 token、成本或任务质量收益。

### B3 多 Agent 委派与容量控制

**目的分析：** 将复杂任务交给独立子 Agent，需要同时限制模型展开任务的数量和进程实际可承载的执行数；只限制一次模型响应不足以约束跨轮、跨会话委派。

**实现证据：**

- task_tool.py / context_snapshot（`backend/packages/harness/deerflow/tools/builtins/task_tool.py:820`） 仅在 `context_mode=snapshot` 时捕获父会话；ParentContextSnapshot（`backend/packages/harness/deerflow/subagents/context_snapshot.py:91`） 序列化保留的会话与摘要，转为新的背景消息，不共享父会话消息容器。
- executor.py / _build_initial_state（`backend/packages/harness/deerflow/subagents/executor.py:1543`） 构造子任务的新消息状态；_aexecute（`backend/packages/harness/deerflow/subagents/executor.py:1572`） 在共享容量槽中执行。execute_async（`backend/packages/harness/deerflow/subagents/executor.py:2129`） 使用服务端执行 ID，保留模型工具调用 ID 作为消息/进度关联标识。
- task_tool.py / 后端轮询与 task_* 事件（`backend/packages/harness/deerflow/tools/builtins/task_tool.py:993`） 后端等待子任务，推送开始、进展和结束事件并返回结果，模型无需自行循环查询。
- SubagentLimitMiddleware / _truncate_task_calls（`backend/packages/harness/deerflow/agents/middlewares/subagent_limit_middleware.py:124`） 结合当前运行的委派账本裁剪超过单轮及总额度的调用；SubagentExecutionCapacity（`backend/packages/harness/deerflow/subagents/capacity.py:36`） 提供运行槽、FIFO 有界等待、拒绝/等待超时及取消时归还容量。

**代码直接支持的变化：** 子任务分开维护消息状态，主任务能取得子任务结果和进度；调用数约束与实际容量准入分别发挥作用，队列不会无限积累。

**限制：** 父会话快照为可选模式，并非每个子任务自动继承全历史；子 Agent 仍可共享同线程沙箱文件，不等于独立机器。普通子任务配置 `checkpointer=False`，不能把主 Agent 的恢复能力扩大为普通子任务自动续跑。队列可配置为直接拒绝；“双层”指委派策略与执行准入，不是声称两层分布式调度。没有并行加速比或成功率实测。

### B4 长上下文与断点恢复

**目的分析：** 长任务的模型输入预算与执行状态保留是不同约束；删除旧消息时仍需要让后续调用看到摘要、已完成委派与加载过的能力引用。

**实现证据：**

- SummarizationConfig（`backend/packages/harness/deerflow/config/summarization_config.py:63`） 定义摘要启用、触发和保留策略，支持消息数、token 或模型输入比例等口径；默认 `enabled=False`，没有使用样例阈值替代项目事实。
- _prepare_compaction（`backend/packages/harness/deerflow/agents/middlewares/summarization_middleware.py:646`） 选择待摘要区间并保留当前用户请求；acompact_state（`backend/packages/harness/deerflow/agents/middlewares/summarization_middleware.py:829`） 在摘要失败时不替换状态；`_amaybe_summarize` 成功后清除旧活跃消息、放回保留消息并更新摘要。
- agent.py / 持久上下文先于摘要安装（`backend/packages/harness/deerflow/agents/lead_agent/agent.py:625`） 明确捕获顺序；DurableContextMiddleware / _capture、_inject（`backend/packages/harness/deerflow/agents/middlewares/durable_context_middleware.py:389`） 捕获委派与 Skill 引用并只在模型请求视图注入；ThreadState（`backend/packages/harness/deerflow/agents/thread_state.py:362`） 为摘要、账本与引用提供独立状态通道。
- _async_checkpointer（`backend/packages/harness/deerflow/runtime/checkpointer/async_provider.py:113`） 支持 memory/SQLite/PostgreSQL；worker.py / 绑定 checkpointer（`backend/packages/harness/deerflow/runtime/runs/worker.py:1372`） 将 saver 绑定主 Agent；services.py / Command(resume=...)（`backend/app/gateway/services.py:1966`） 接受显式恢复输入。

**代码直接支持的变化：** 摘要成功后减少活跃原始消息，持久上下文在后续模型请求中可见；配置持久 saver 时可恢复主 Agent 状态与中断点，客户端无需重新构造全部会话。

**限制：** 摘要是有损模型输出，不能保证所有细节完整保留；Skill 通道保存的是引用，不是正文永久驻留。memory saver 不提供跨进程持久化。显式恢复不等于进程崩溃后自动恢复所有后台任务，更不保证外部工具副作用 exactly-once；没有宣称已完成步骤绝不会重放。未测量压缩率、上下文容量或恢复耗时。

### B5 线程沙箱与执行租约

**目的分析：** 并发主、子 Agent 需要协作访问同线程文件，但某个持有者先结束时不能提前回收其他持有者仍在使用的 Provider 客户端；用户/线程数据归属与执行资源生命周期分别管理。

**实现证据：**

- ThreadDataMiddleware / _get_thread_paths（`backend/packages/harness/deerflow/agents/middlewares/thread_data_middleware.py:51`） 将工作区、上传和输出落在当前用户线程路径；LocalSandboxProvider / _build_thread_path_mappings（`backend/packages/harness/deerflow/sandbox/local/local_sandbox_provider.py:334`） 建立对应虚拟路径映射。
- SandboxMiddleware（`backend/packages/harness/deerflow/sandbox/middleware.py:54`） 管理获取、复用和释放，支持延迟初始化，并让并发执行持有独立租约；SandboxLeaseManager / _remove_binding_locked（`backend/packages/harness/deerflow/sandbox/lease.py:197`） 记录待释放请求和持有者集合，仅最后一个持有者退出时允许交还 Provider；release / release_async（`backend/packages/harness/deerflow/sandbox/lease.py:646`） 等命令作用域清理结束再移除持有者。
- present_file_tool（`backend/packages/harness/deerflow/tools/builtins/present_file_tool.py:83`） 将输出目录中的文件写为产物引用，是简介“文件交付”的实现入口。

**代码直接支持的变化：** 工具通过一致的线程文件路径协作，单个执行结束不会使共享环境立即被回收；用户可取得已呈现的产物引用。

**限制：** 本条租约是单进程的执行持有关系，不是跨实例的 Provider 所有权租约。实际隔离强度随 Provider 而变；LocalSandboxProvider 类说明（`backend/packages/harness/deerflow/sandbox/local/local_sandbox_provider.py:36`） 明确本地路径视图并非主机安全边界，启用主机 bash 时尤甚。未声称所有命令均在容器内、恶意代码绝对安全或子任务文件互不可见。没有 VM 复用率或启动耗时结果。

### B6 长任务受理与流式重连

**目的分析：** 长 Agent 运行时间与一次 HTTP/SSE 连接寿命不同；连接重试需要关联同一运行，并在事件窗口丢失后回到持久状态，避免重复受理或误认为事件已完整回放。

**实现证据：**

- start_run / 运行受理与幂等复用（`backend/app/gateway/services.py:2324`） 调用 RunManager，幂等重用时核对输入、助手及恢复请求等身份，不一致返回 HTTP 409；新受理后附加后台 task，复用分支直接返回已有运行。
- RunManager / create_or_reject（`backend/packages/harness/deerflow/runtime/runs/manager.py:1562`） 统一受理；`_admit_thread_operation` 使用本地锁并委托存储原子创建；RunRepository / create_thread_operation_atomic（`backend/packages/harness/deerflow/persistence/run/sql.py:840`） 在事务中创建或报告冲突；RunRow / uq_runs_thread_active（`backend/packages/harness/deerflow/persistence/run/model.py:74`） 用 SQL 部分唯一索引约束 pending/running。
- sse_consumer（`backend/app/gateway/services.py:2590`） 读取 Last-Event-ID，消费事件/心跳/终止标记，区分创建者与观察者断连；仅符合创建者断连条件才按策略取消。缺口事件携带 `reload_durable_state` 恢复指引。
- MemoryStreamBridge / _resolve_start_offset（`backend/packages/harness/deerflow/runtime/stream_bridge/memory.py:75`） 处理保留窗口；RedisStreamBridge / subscribe（`backend/packages/harness/deerflow/runtime/stream_bridge/redis.py:241`） 提供 Redis 事件流回放与缺口检测。

**代码直接支持的变化：** 对带键的匹配重试复用已受理运行，限制线程并发活跃运行；保留窗口内衔接事件，窗口外显式告知重新加载持久状态。连接断开是否保留后台执行由策略决定。

**限制：** 幂等键是条件，不是所有请求天然去重；唯一索引约束运行记录，并非所有工具副作用的全局 exactly-once。流桥有保留与清理边界，内存模式不能跨进程保存事件；Redis 模式依赖外部服务和配置。没有宣称 SSE 无损永久回放或所有断连默认继续。

## 选材与验证结论

六条按简介后的实际顺序标为 B1—B6，分别覆盖扩展结构、能力发现、任务展开、上下文与状态持续、执行资源以及长任务交付契约。目录与接口数量未直接变成 bullet 数量；上传/产物路径归到沙箱与文件交付，策略校验归到能力发现及运行受理，没有独立凑成接口工单。

长期记忆及其多后端、定时任务、IM 通道、项目资料与知识检索也在仓库范围内。本次从 Agent 组装中的记忆接入、MemoryMiddleware 与相关目录确认其存在，但未展开独立主张；这不表示项目没有这些能力，也不据目录名称推断其质量或收益。

- 实现证据：已沿上述代表链路静态核对调用、状态及失败条件。
- 目的与风险：均为基于当前职责/分支的工程分析，未冒充真实历史痛点。
- 责任证据：未提供；目标模式未据此过滤仓库机制，也未核查作者统计。
- 结果证据：限于实现直接支持的行为；没有执行测试、应用验收、线上监控或性能实验。
- 首次交付：只创建 `output.md` 和 `evidence.md`，不覆盖既有完整结果。按用户本次范围，未运行要求课程与 Q&A 的全套结构校验；仅核对六条一级 bullet 格式、证据路径及本次输出文件范围。
