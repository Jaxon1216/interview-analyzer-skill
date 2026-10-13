# DeerFlow 主 agent 补稿证据与边界

源码基线：`5ecc1c2ac2de624af354bc515d5cb04f80df226c`。范围为完整本机项目，按 README / 根与模块 AGENTS 的职责地图识别候选，再按需查证下列核心链路；并非逐文件穷举。源码只读，未启动应用、生成课程、运行 DeerFlow 测试或核验作者。以下路径相对 DeerFlow 根目录。

| 条目 | 关键源码与位置 | 支持的事实和限制 |
| --- | --- | --- |
| 简介 / B1 | `backend/packages/harness/deerflow/agents/lead_agent/agent.py`：`assemble_lead_agent`、`_assemble_lead_agent`；`tools/builtins/task_tool.py:966–1060`；`subagents/executor.py:1406–1570,2129–2207` | Lead Agent 装配并调用 task；子任务新建状态，可带 context_snapshot，继承工作目录/沙箱；持久独立事件循环；执行 ID 与工具消息 ID 分开。不能照搬金样双线程池，也不能说子任务永远只看到任务描述。 |
| B1 额度 | `backend/packages/harness/deerflow/agents/middlewares/subagent_limit_middleware.py:95–180` | 限制单响应 task 调用与 run_id 归属账本累计委派；不是全进程实际并发控制器。未复制金样并发/超时数。 |
| B2 | `backend/packages/harness/deerflow/agents/middlewares/tool_error_handling_middleware.py:360–528,566–658`；`agents/lead_agent/agent.py:544–648` | 主子 Agent 共享基础执行层；净化与预算顺序、句柄解析在策略前；授权及读后写等检查受配置控制，不声称所有部署默认开启全部策略或存在固定层数。 |
| B3 | `backend/packages/harness/deerflow/agents/lead_agent/prompt.py:940–980`；`agents/middlewares/skill_tool_policy_middleware.py:305–343,431–507`；`agents/middlewares/durable_context_middleware.py:389–430` | 默认元数据，正文按需加载，轻量引用；活跃技能策略在模型列表与工具调用两处处理。不复制“默认只注入名称索引”，不承诺完整安全隔离。 |
| B4 压缩 | `backend/packages/harness/deerflow/agents/middlewares/summarization_middleware.py:779–902,1082–1189`；`agents/middlewares/durable_context_middleware.py:400–430`；`agents/middlewares/tool_output_budget_middleware.py:1–24` | 按配置阈值压缩历史，生成成功才替换；独立状态通道重注入；大工具结果外置，失败退回首尾预算。没有断点 exactly-once 或无损摘要保证。 |
| B4 记忆 | `backend/packages/harness/deerflow/agents/middlewares/memory_middleware.py:157–228`；`agents/middlewares/dynamic_context_middleware.py:389–443`；`agents/lead_agent/prompt.py:822–875` | 被动模式入队捕获身份、后台更新，后续按用户/Agent 作用域取上下文；并非所有记忆模式都全量自动注入。 |
| B5 | `backend/packages/harness/deerflow/agents/middlewares/thread_data_middleware.py:52–100`；`sandbox/middleware.py:129–225`；`sandbox/lease.py:151–191`；`subagents/executor.py:1627,1793–1794,2027–2033` | 用户/线程目录与共享客户端执行租约；最后持有者处理待释放请求。provider release 不等于销毁容器，不把本地路径映射说成容器隔离。 |
| B5 产物 | `backend/packages/harness/deerflow/tools/builtins/present_file_tool.py`；`agents/thread_state.py`：`merge_artifacts`；`backend/app/gateway/routers/artifacts.py`：`get_artifact` | 状态中的去重引用与受权内容读取；登记不证明内容存在、正确或完整。 |
| B6 | `backend/app/gateway/services.py:1745,2259,2465–2540`；`frontend/src/core/api/api-client.ts:337–424,446–498` | asyncio 后台任务与 SSE 消费分开；创建不自动重试，GET 恢复；gap 重载状态再订阅；创建与观察连接的断开语义不同。不承诺每个事件补回或活跃任务跨进程重启续跑。 |

## 选材和修订

在完整职责地图中比较调度、执行层、技能、上下文/记忆、线程资源与运行/事件状态；接口、文件读取和权限检查均归入所服务机制。不是先将旧评测的五类材料扩写成同数目的条目，也没有照搬金样四标题。

主 agent 已读本轮诊断与旧评测，不能承担“生成者未获预写答案”的独立验证。`primary-first.md` 是其首次完整补稿，保留原样；`primary-revised.md` 为编辑修订，未改 Skill 后再独立重跑。

首稿 B2 与 B3 重复技能双处授权，B2 仍有“在调用链上落实执行约束”空泛尾句，B3 末尾又复述权限生效两处；修订删除重复、将 B2 收束为有顺序意义的参数还原与策略检查。B1 的“单轮并行委派数”改为实际约束的 task 调用数，B4 补明摘要成功才替换历史。修订有上述源码支持；不将该主 agent 稿的前后变化作为独立 Skill 改善证明。
