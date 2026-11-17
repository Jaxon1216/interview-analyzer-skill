# GenBI 源码证据记录

## 分析范围与基线

- 分析日期：2026-11-17；目标岗位：后端研发；模式：目标简历。
- 源码根目录：`<GENBI_ROOT>/backend`。盘点完整后端的入口、装配、业务、模型、HTTP 处理、消息消费、事务消息表、事件、限流、会话、工具、SQL 与测试，再沿候选机制查证。未按个人提交筛选。
- Git HEAD：`8bc3edf984d1419e9f2f16d4d72d990d48ca7ad9`。本次分析的是当前工作区文件，不能等同于该提交的纯净快照；后端范围内已有未提交修改：`.env.example`、`README.md`、`cmd/consumer/main.go`、`cmd/server/main.go`、`internal/config/config.go`。未改动这些文件，也未读取环境密钥。
- 技术栈依据：go.mod（`backend/go.mod:1`） 声明 Go 模块及 Gin、GORM、MySQL、Redis、RabbitMQ 和 Excelize 依赖；项目目标参考 README（`backend/README.md:3`），行为以实际源码为准。
- 前端只读取生成接口封装、异步受理响应使用及状态事件接收相关代码，核对 HTTP 与通知边界；未将前端渲染、看板等功能纳入后端简历。
- 没有提供个人职责、上线记录、流量、压测或线上收益材料；不声称独立负责、历史选型、线上事故修复或量化提升。
- 验证方式：只读源码与已有测试代码，未启动服务，未运行测试、联调或压测。测试存在只证明仓库包含相应断言，不能作为测试已通过的结论。
- 本次仅交付简介、bullet 和本证据记录，未生成课程、面经、HTML 或应用产物。B1—B5 对应 output.md 中一级 bullet 的顺序。

## 系统职责与代表链路

服务对象是上传表格并希望取得图表配置、分析结论及处理状态的用户。这个目标由 HTTP 接口、图表业务、DeepSeek 调用、MySQL、RabbitMQ 消费者和事件通路协作完成。下列设计目的均是依据当前实现作出的工程分析，不代表已经核实的历史需求、团队 OKR 或方案演进。

| 组件 | 当前职责与证据 |
| --- | --- |
| HTTP 服务 | server/main.go（`backend/cmd/server/main.go:28`） 显式装配数据库、Redis、会话、业务、限流、生产者、事务消息 relay 与 SSE；router.go（`backend/internal/bootstrap/router.go:55`） 注册图表接口及登录校验。 |
| 图表业务与存储 | ChartService（`backend/internal/service/chart_service.go:25`） 负责图表查询、编辑、生成和状态写入；Chart（`backend/internal/model/chart.go:9`） 定义 wait、running、succeed、failed 及输入、输出、执行信息字段。 |
| 异步执行 | consumer/main.go（`backend/cmd/consumer/main.go:29`） 独立启动消费进程，装配图表业务及事件发布器；Consumer.Start（`backend/internal/mq/consumer.go:41`） 预取 1、手动确认、逐条处理当前消费流。 |
| 投递与通知 | Relay.runOnce（`backend/internal/outbox/relay.go:123`） 扫描待发送记录并尝试投递；EventPublisher（`backend/internal/event/publisher.go:10`） 定义尽力通知接口，Redis 实现供 consumer 发布，server 订阅后输出 SSE。 |
| 账户与访问边界 | UserHandler.Login（`backend/internal/handler/user_handler.go:38`） 保存用户 ID 会话；session.go（`backend/internal/bootstrap/session.go:11`） 使用 Redis 会话；Auth/Admin（`backend/internal/middleware/auth.go:14`） 校验登录、当前用户和管理员角色。用户与图表 CRUD 作为支撑能力，不单独堆成一级 bullet。 |

1. 同步生成：上传文件与参数 → 解析为 CSV → 用户限流 → 拼接提示并调用 DeepSeek → 解析结果、清洗配置 → 保存成功态图表 → 返回图表 ID、配置及结论。
2. 异步生成：上传与限流 → 同一数据库事务保存等待态图表和 pending 消息 → 返回图表 ID → server relay 轮询消息并投递 RabbitMQ → consumer 按 ID 读取任务，CAS 抢占后调用模型，写成功结果。
3. 终态通知：consumer 成功处理分支或失败兜底分支 → 发布图表 ID、状态 → Redis Pub/Sub → server 校验归属并按 ID 过滤 → SSE → 客户端据事件刷新查询。通知不是完整结果载体。
4. 当前异步失败路径：一般错误进入最多两次调用循环；未抢到 CAS 的消息直接 Ack；循环耗尽分支尝试写失败状态并 Nack 到死信拓扑。CAS 后出错的实际组合边界见 B3，不能用注释中的意图替代运行逻辑。

## B1｜模型输入与结果归一化

**目标与问题（实现分析）**：上传格式与模型输出形态不同，需要把文件内容送入同一模型调用，并把生成结果整理为后续存储、HTTP 返回可以使用的字段。这不是已核实的旧版兼容事故。

**实现与可定位证据**：

- ChartHandler.parseGenRequest（`backend/internal/handler/chart_handler.go:208`） 从 multipart/form 或 query 获取名称、分析目标和图表类型，校验必填参数并读取上传文件。
- ExcelToCSV（`backend/internal/util/excel.go:18`） 按扩展名接收 XLSX 或 CSV；xlsxToCSV（`backend/internal/util/excel.go:31`） 读取首个 sheet、跳过空行、转义逗号/引号/换行；CSV 直接读取文本。
- BuildPrompt/GenSync（`backend/internal/service/chart_service.go:166`） 将目标、类型与 CSV 构成模型输入，同步生成保存输入、清洗后配置和结论；ProcessChart（`backend/internal/service/chart_service.go:276`） 异步复用相同提示构造与清洗逻辑。
- DeepSeekService.AnalyzeCsv（`backend/internal/service/deepseek_service.go:56`） 调用 Chat Completions，解析 choices 中 JSON 内容的 genChart 与 genResult；rawToString（`backend/internal/service/deepseek_service.go:133`） 将结论字符串或数组表示归一为字符串。
- CleanEchartsJSON（`backend/internal/util/echarts.go:22`） 去除赋值前缀、部分尾部符号，替换单引号与换行，经 json.Valid 校验，非法内容返回 `{}`。
- BiResponse（`backend/internal/dto/chart.go:51`） 与 前端同步生成封装（`frontend/src/services/yubi/chartController.ts:50`） 确认生成接口字段与上传契约。

**代码可见变化**：同步与异步处理使用同一提示构造和配置清洗函数，图表配置、分析结论进入相同模型字段；非法配置字符串可被替换为合法 JSON 空对象。不是图表质量或结论正确率的量化成果。

**边界**：只处理 XLSX 首个工作表；CSV 原文直读，没有完整 CSV 语义校验。JSON 合法性不等于 ECharts schema 正确或配置一定可渲染；空对象仍可能随成功态保存。系统提示要求基于输入数据，不构成分析事实正确性的保证。未见上传体量、行数或模型输入 token 的显式限制；没有将其描述为大文件或超大上下文方案。已有 清洗测试（`backend/internal/util/echarts_test.go:8`） 和 提示构造测试（`backend/internal/service/chart_service_test.go:8`），本次未执行。

## B2｜异步生成与事务消息表

**目标与问题（实现分析）**：调用方提交任务时无需等待外部模型完成；同时，已保存的任务应有持久化投递依据，避免把数据库任务写入与立即发消息当作一个原子操作。

**实现与可定位证据**：

- GenAsync（`backend/internal/handler/chart_handler.go:171`） 校验异步服务可用、执行限流，调用 SaveWait 后直接返回 chartID，没有在接口内调用模型或直接 Publish。
- SaveWait（`backend/internal/service/chart_service.go:208`） 在 GORM Transaction 中依次创建 wait 图表、pending outbox 记录；第二次写入出错会使事务返回错误。
- Outbox 模型（`backend/internal/model/outbox.go:19`） 记录 aggregateId、payload、status 和 retryCount；outbox SQL（`backend/sql/02_outbox.sql:11`） 定义表与 status 索引。
- gormStore.fetchPending（`backend/internal/outbox/relay.go:59`） 按 ID 升序取 pending；Relay 构造与轮询（`backend/internal/outbox/relay.go:88`） 默认每批 100 条，启动即扫一次，随后周期扫描；runOnce（`backend/internal/outbox/relay.go:123`） 发布失败保留 pending、增加 retryCount，成功后尝试标记 sent。
- Producer.Publish（`backend/internal/mq/producer.go:21`） 以图表 ID 字符串作为消息体、使用持久化消息投递配置；consumer/main.go（`backend/cmd/consumer/main.go:60`） 启动独立消费入口。
- GetByID（`backend/internal/service/chart_service.go:55`） 返回包含状态与生成结果的图表；前端异步受理使用（`frontend/src/pages/AddChartAsync/index.tsx:22`） 在有响应数据时提示提交成功并跳转到我的图表。

**代码可见变化**：接口返回受理标识与生成执行分离；任务及投递意图受同一数据库事务保护；应用观察到的发送失败保留补发记录。没有声称模型生成更快或端到端零丢失。

**边界**：relay 只有在配置启用且 server 启动时获得生产者后才启动，见 server 装配（`backend/cmd/server/main.go:45`）。关闭 relay 但仍有 producer 时，接口依然可以创建 pending，不能写成所有已受理任务自动执行。Producer 未启用 publisher confirms，mandatory 为 false；Publish 返回 nil 不是消息已经被消费者处理或必达的证明。发送后标记 sent 失败会重发，多个 relay 也未见租约或抢占，因此补发允许重复。没有清理、重连、自愈或最终送达的运行证据。源码注释使用的“不丢”“exactly-once 效果”没有作为正文保证继承。已有 relay 内存 fake 测试（`backend/internal/outbox/relay_test.go:77`） 覆盖发送、失败保留与下轮补发，没有实际事务回滚或 RabbitMQ 端到端结果，本次未运行。

## B3｜状态 CAS 幂等消费

**目标与问题（实现分析）**：relay 的发送与 sent 标记存在间隔，可能对同一图表产生重复投递，需要限制重复消息重复调用模型。与 B2 的事务范围不同，这里约束的是消费执行入口。

**实现与可定位证据**：

- ProcessChart（`backend/internal/service/chart_service.go:260`） 在模型调用前执行 `UPDATE chart SET status=running WHERE id=? AND status=wait`。
- classifyCASResult（`backend/internal/service/chart_service.go:244`） 先区分数据库错误，再将零影响行返回为 ErrAlreadyProcessed；只有命中更新才继续。
- Consumer.handle（`backend/internal/mq/consumer.go:78`） 对该错误直接 Ack 并 return，不进入重试、MarkFailed 或通知发布分支。

**代码可见变化**：同一图表一旦离开 wait，后续重复消息不会再次进入模型调用，也不会由重复消息分支执行失败回写。这不证明任务最终成功、外部副作用恰好一次或执行中断后可以恢复。

**关键限制**：当前 CAS 与重试组合存在明确窗口：首次抢到任务后已持久化 running，随后模型调用、超时或成功回写出错，第二次 ProcessChart 将因非 wait 返回 ErrAlreadyProcessed，Consumer 随即 Ack，可能保留 running 而没有 failed 终态。进程在抢占后崩溃，重投也会命中同类跳过路径。未见运行态租约、回收扫描或重置等待态机制。故正文不写“失败自动恢复”“超时必定落失败”或“全链路恰好一次”。CAS 测试（`backend/internal/service/chart_service_cas_test.go:13`） 只覆盖结果分类函数，不能证明真实数据库并发消费或重试闭环。

**关联失败拓扑**：源码确有 onExhausted（`backend/internal/mq/consumer.go:114`） 的失败回写、通知与 Nack(requeue=false)，并由 declareTopology（`backend/internal/mq/client.go:39`） 定义持久化死信交换机和队列；但只有执行到耗尽分支才成立，不能据此宣称所有生成失败都会进入死信。MarkFailed 未返回数据库更新错误，亦不能保证失败状态与事件一致。这些边界保留在证据中，不把失败处理意图写成一级成果。

## B4｜生成限流与调用取消

**目标与问题（实现分析）**：外部模型调用需要限制单用户发起频率，并允许在请求取消或超时时停止等待。目的来自当前限流键与上下文传递链，不是已核实的历史拥塞事故。

**实现与可定位证据**：

- 同步 Gen（`backend/internal/handler/chart_handler.go:139`） 与 异步 GenAsync（`backend/internal/handler/chart_handler.go:186`） 使用相同的用户限流键；超额返回业务限流错误，Redis 检查错误则返回系统错误。
- Limiter.Allow（`backend/internal/ratelimit/limiter.go:22`） 使用 Redis 及 redis_rate.PerSecond(3)，单次限流访问上下文为 2 秒。这里的每秒 3 次是代码配置，不是实测吞吐量。
- Consumer.handle（`backend/internal/mq/consumer.go:70`） 创建可配置时限的 context，传入 ProcessChart；配置（`backend/internal/config/config.go:70`） 默认 30 秒；Gen（`backend/internal/handler/chart_handler.go:159`） 同步传递请求上下文。
- AnalyzeCsv（`backend/internal/service/deepseek_service.go:76`） 用 NewRequestWithContext 发请求；HTTP client 另有 60 秒超时；wrapCtxError（`backend/internal/service/deepseek_service.go:150`） 保留 DeadlineExceeded/Canceled 的可识别错误。

**代码可见变化**：同一用户两种生成入口共享限流配置，超额时不会从该请求继续发起模型调用；取消与超时能够传递至模型 HTTP 调用，调用方可以识别超时、取消错误。没有据此声称 API 延迟下降、成本下降或最大并发受控。

**边界**：上传解析发生在限流之前，因此限流没有覆盖上传接收和 XLSX 解析开销。配置的异步 context 被重试循环共享，数据库操作未普遍使用 WithContext，循环中的 Sleep 也不响应取消；30 秒不能描述为整个任务、数据库写入或消费确认的严格完成上限。同步没有套用这个 30 秒 context。超时后的状态处理仍受 B3 限制。已有 超时测试（`backend/internal/service/deepseek_service_test.go:17`） 与 主动取消测试（`backend/internal/service/deepseek_service_test.go:52`），使用 httptest 模拟慢响应，本次未执行；不是线上生成耗时数据。

## B5｜跨进程终态通知

**目标与问题（实现分析）**：生成执行与 HTTP 服务属于独立进程，需要将后台的处理终态送至仍在等待该图表的调用方，同时限制订阅者看到的任务范围，并让通知失败不改变消费分支的既定处理。

**实现与可定位证据**：

- Consumer 成功分支（`backend/internal/mq/consumer.go:103`） 发布 succeed 后 Ack；耗尽分支（`backend/internal/mq/consumer.go:114`） 尝试失败回写、发布 failed 后 Nack。
- RedisPublisher（`backend/internal/event/redis_publisher.go:33`） 发布 `{chartId,status}`，错误仅记录日志；consumer 装配（`backend/cmd/consumer/main.go:41`） 在启动时 Redis 不可用则注入 NoopPublisher。
- SSEHandler.Stream（`backend/internal/handler/sse_handler.go:42`） 先查图表并校验归属，再订阅配置频道；按图表 ID 过滤事件，使用 text/event-stream 写出，遇终态结束流。订阅生命周期（`backend/internal/handler/sse_handler.go:68`） 跟随请求上下文关闭，心跳 15 秒一次，defer 关闭订阅和定时器。
- 前端 useChartEvents（`frontend/src/hooks/useChartEvents.ts:89`） 建立同源 EventSource 并解析 chartId/status，终态关闭；我的图表接口消费（`frontend/src/pages/myChart/index.tsx:69`） 在通知回调中刷新列表，连接不可用时启用轮询。此处只核对事件与 HTTP 契约，未将前端实现写成后端个人职责。

**代码可见变化**：消费者与 HTTP 服务之间通过事件传递终态信号，已登录归属用户可以订阅对应图表，事件触发查询刷新；通知发布返回错误不会转成消费者处理错误。不是所有状态的实时进度流，也不是持久化可靠事件通道。

**边界**：当前实际发布 succeed/failed，未发布 wait/running。Pub/Sub 没有事件持久化、游标回放或服务端重放；建连没有先发当前状态快照，订阅前发生的终态可以错过，不能承诺终态必达或完全取消轮询。前端轮询是在 SSE 不可用时启用，不能证明连接正常但错过事件时一定恢复。SSE 订阅校验归属不等于所有图表读接口都有同等归属校验：GetByID 与通用 Page 不能据此包装成完整多租户隔离。

## 结果、责任与历史证据的使用边界

| 证据类型 | 本次可支持的范围 | 未支持的表达 |
| --- | --- | --- |
| 当前实现 | 同库事务、补发记录、条件更新、共享用户限流键、可取消 HTTP 调用、按归属过滤的 SSE 终态事件。 | 消息必达、恰好一次、运行中任务自动恢复、所有失败必落库、完整多租户隔离。 |
| 已有测试源码 | 纯函数与 fake/httptest 覆盖意图，可定位具体断言。 | 本次测试已通过、真实 MySQL/RabbitMQ 联调通过或生产验证。 |
| 代码参数 | 批量上限、每秒限流配置、默认超时、轮询周期和心跳。 | 吞吐量、P95、成功率、成本或人效提升。 |
| 个人职责 | 用户只指定目标简历模式，允许从已有机制选材。 | 个人主导、独立从零建设、推动上线、承担全仓 owner。 |
| 历史演进 | README 和注释给出重写/改造背景，但本次未查旧版与历史决策材料。 | 将当前机制叙述为本人经历过的故障、评估过程或已验证前后收益。 |

成稿审读已按“目标—机制—具体变化”核对：B1 对应输入输出契约，B2 对应受理与执行分离及事务投递依据，B3 对应补发下的执行入口去重，B4 对应频率和外部等待约束，B5 对应跨进程通知与订阅生命周期。账户 CRUD、普通列表和参数读取未单独冒充系统支柱；未将测试中时间断言、示例数字或注释中的绝对保证移入简历成果。
