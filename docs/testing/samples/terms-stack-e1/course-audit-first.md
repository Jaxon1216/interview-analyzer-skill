# E1 九课独立内容审查

审查对象：当前 `e1/request.md`、`e1/delivery/interview-prep/guide-fullstack/` 的全部九课、当前冻结 Skill 课程规则及 E1 checks。全文阅读九课，沿高风险主张抽查原始源码；未读取旧结果，未以结构检查或浏览器结果代替内容判断。未运行业务服务、业务测试或模型，未修改交付、冻结 Skill 或源码。

## 判断

课程基本满足完整核心课要求：C01–C09 是围绕一次 CSV 分析任务编排的连续场景，覆盖提交/附件、服务端受理、图组装、工具执行、沙箱、技能、SSE、消息和产物呈现，以及持久化与故障边界。各课均有前置依赖、反向导航、实际源码阅读顺序、机制解释、异常边界和直接给出的必懂/必记内容，不是待填大纲。课程没有把源码查证转为学习者作业，也没有夹带未请求的练习。

本次发现一处明确需修订的事实范围，位于 C07。它不推翻全部九课的教学结构，但使当前课程稿不能作为“所有事实与失败边界均已通过”的结果。

## 需修订：C07 将日志缺失统一描述为 gap 恢复

- 产物：`e1/delivery/interview-prep/guide-fullstack/07-SSE增量状态与断线恢复.md:43`。
- 当前表述：“游标太旧或日志不存在，服务端用无事件 ID 的 gap 控制帧说明需要 durable state”。
- 问题：日志不存在并非统一进入 gap。终态 run 的 stream 已不存在时，普通 join 与 stateless stream 的默认行为是返回 `end`；只有本次 thread-scoped 创建重试复用已有记录时，创建路由才传 `emit_gap_on_missing_stream=True`，触发 gap。还有 store-only + 非跨进程 bridge 的 join 会直接 409。
- 源码依据：`.test-repos/deer-flow/backend/app/gateway/services.py:2613` 的注释明确划分创建重试和 join；`:2621`–`:2638` 对 terminal/missing 分支分别产生 gap 或 end。`.test-repos/deer-flow/backend/app/gateway/routers/thread_runs.py:1031` 仅按 `record.idempotency_reused` 开启该参数；`:1338`–`:1344` 的 join 分支保留 409 及默认参数。前端 `.test-repos/deer-flow/frontend/src/core/api/api-client.ts:364`–`:374` 只有实际读到 gap 才进入 durable reload 路径，普通 end 不会自动走这条恢复循环。
- 教学影响：本课目标包含失败边界与恢复作用域，读者会据当前概括误以为任意日志缺失均会自动重读 durable state，再有界 rejoin。应精确区分“保留窗口之外的游标产生 gap”“终态丢流的普通 join 返回 end”和“幂等创建重试丢流发 gap”，不必重写整课或扩展其他业务。

相关位置已逐一核对，应按同一问题同步处理：

| 位置 | 判断 |
| --- | --- |
| `DeerFlow/面经.md:181` | 需同步修订。“如果缓冲已淘汰，后端明确发送 gap”可被理解成缓存整段已不存在也必发 gap，与上述 terminal join 反例冲突。口播可以简短，但应限定仍存在的事件桥缓冲/被判定的重放缺口，不能扩大保证。 |
| `guide-fullstack/07-SSE增量状态与断线恢复.md:11` | 总结句“超出重放范围时发送 gap”应随第 43 行限定，避免把终态日志完全丢失也包括在统一保证里。不是第二个独立缺陷。 |
| `guide-fullstack/07-SSE增量状态与断线恢复.md:20` | 文本链只有 gap 分支；正文明确分支后，可把该链标为“收到 gap 的恢复路径”，或补普通重放/终态 end 的分支。它目前是同一过度概括的教学传播点，不单列为另一项事实错误。 |
| `DeerFlow/面经.md:19`、`:29` | “缺口时重读持久状态”作为真实 gap 分支的紧凑陈述可成立，没有独立宣称所有日志缺失都会产生 gap；不要求因本问题强行重写 B5。 |
| `DeerFlow/导学.md:27` | “gap 时读持久状态”明确以 gap 为条件，事实成立。 |
| C07 `:49`、`:53`；面经 `:187` | 都解释已经收到 gap 后的语义，未新增“任意缺失必 gap”主张；无需因本问题修改。 |

检索并阅读了当前导学、面经和九课的全部 gap/重放/恢复相关段落，未发现除以上传播位置外的同类过度保证。没有读取历史版本。

## 抽查与教学结论

| 课程 | 内容判断与源码抽查 |
| --- | --- |
| C01 | 用一个输入贯穿控制流、消息流与文件旁路，区分 thread/run/tool-call ID，明确乐观显示、HTTP 受理和后台执行不是一个状态。服务拆分没有沿旧架构臆造独立必经 LangGraph 服务。 |
| C02 | 附件先上传后 submit、同一个 humanMessageId、Hook ref 只覆盖本地重入、onSent 在上传成功后触发均与 `frontend/src/core/threads/hooks.ts:2598`、`:2620`、`:2708`、`:2752`、`:2753` 一致。正确区分创建 POST 的受理歧义和观察流断线。 |
| C03 | 区分幂等键、同 thread 活动 run 准入、跨实例共享存储，避免把本地锁称为全局唯一。`services.py:2325`、`:2379`、`:2384` 支持准入后无 await 附着 task 的因果；`:2600` 起的消费器支持创建者和只读观察者断开语义的区分。 |
| C04 | 将 schema、模型可见性、执行授权区分，middleware 次序用保护对象解释，没有只背层数。`tool_error_handling_middleware.py:375`–`:389` 支持先清理结果标签/PII、再预算外置的解释；`tools/tools.py:158`–`:160` 支持 LocalSandbox 默认抑制 host bash。 |
| C05 | 用 `{lead}` → `{lead, child}` → `{child}` → 空的持有集合说明释放，不把 process-local lease 写成分布式引用计数。`sandbox/lease.py:196`–`:218`、`:405`–`:453` 支持最后释放与取消 acquire 对账；`sandbox/middleware.py:112` 起支持 lead 拥有共享技能投影；LocalSandbox 的强隔离限制表述正确。 |
| C06 | 发现、正文加载与激活政策三层分清；默认完整元信息、可选 deferred 名称索引，describe 不等于激活。`skills/tool_policy.py` 支持显式声明并集、缺省与空集区别及框架名称保留；`skill_tool_policy_middleware.py:_active_policy` 支持 slash 优先于被动 skill_context。`skill_context.py:137` 起与读取中间件支持成功配对/可信标记，未把任意聊天文本当激活依据。 |
| C07 | `stream-mode.ts`、`stream-state.ts`、`api-client.ts` 支持主聊天三流、消息由 SDK 处理、非消息 reducer、五次恢复 rejoin 预算。子图 namespace 与主 Web 不请求 subgraph 的说明与 `hooks.ts:2766` 和 worker namespace 分支一致。仅上述“日志不存在一概 gap”边界需修订。 |
| C08 | 将消息、文件与生命周期分开，工具结果按调用 ID 配对。`artifacts/utils.ts:22`–`:30` 支持逐段原始路径编码，`:111` 起支持 Markdown 边界一次解码；`:139` 起支持唯一匹配相对图片。`routers/artifacts.py:413` 起支持 active content 强制附件，`:103` 支持 expected SHA-256 版本检查。没有把文件路径显示当下载成功。 |
| C09 | 四种状态（图/运行/事件/文件）及配置读取时点讲清，区分“恢复结果”“恢复事件”和“重启工作”。`checkpointer/async_provider.py` 明确支持 memory/sqlite/postgres，内存生命周期限制恰当。将测试文件作为行为证据入口，明确未执行项目测试，没有冒认测试通过、线上事故或性能数字。 |

## 术语和范围

课程保留必要的可定位技术名：Next.js App Router、FastAPI、LangChain/LangGraph、MCP、SSE、ToolMessage、Command、reducer、SHA-256。内部函数放在源码区解释，主链能读懂而不是靠私有符号堆砌。沙箱租约、渐进技能加载、幂等准入与重放窗口都有具体输入、状态变化和失败条件，没有被业务口号替代。

没有把当前实现写成个人历史、正式 OKR、上线收益或已执行测试。第一人称/目标模式所需责任边界由主文件负责；课程内容使用当前机制和事后分析语气，范围保持在用户指定代表性主链，长期记忆、IM、定时业务未进入核心课程。

本子审查不判定 HTML 浏览器运行或版式。C05/C06 课文即使不打开 HTML 也能独立解释机制，专题入口承担可视化补充；HTML 本身交由父审查独立判断。
