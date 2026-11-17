# GenBI 源码证据记录

## 范围与事实等级

- 分析日期：2026-11-17；源码根目录：`<GENBI_ROOT>/backend`。
- 采用目标简历模式，选材覆盖完整 Go 后端；未用提交作者或个人职责证据筛选机制。用户未提供个人职责、部署验收、线上收益或性能数据。
- 只读查看指定 Skill、其本阶段引用与给定源码。未读取已有 interview-prep、旧交付、评分标准或其他运行目录；未修改源码与 Skill，未启动应用、执行测试或调用真实模型/中间件。
- 前端仅查看 `frontend/src/services/yubi/chartController.ts` 与 `frontend/src/hooks/useChartEvents.ts`，用于确认 HTTP 参数、返回值使用声明及 SSE 消息契约；不据此前端材料扩写页面、看板等能力。
- 下列“效果”均是静态源码能支持的行为与结构，目的为依据当前实现作出的工程分析，不代表已验证的历史事故、选型过程或生产收益。

## 完整后端地图与选材

| 范围 | 实际职责与已核验落点 | 简历取舍 |
| --- | --- | --- |
| HTTP 与依赖装配 | `cmd/server/main.go:18` 显式组装 MySQL、Redis、Session、服务、生产者、relay 与 SSE；`internal/bootstrap/router.go:25` 注册登录、用户管理、图表管理、同步/异步生成与订阅路由。 | 作为各机制入口与技术栈依据，不把常规接口数量独立包装成亮点。 |
| 图表与模型服务 | `internal/handler/chart_handler.go:139` 解析上传和生成请求；`internal/service/chart_service.go:166` 构造提示词、同步生成、异步受理、CAS 执行及结果落库；`internal/service/deepseek_service.go:56` 调用 DeepSeek。 | 核心产品能力，进入 B1。 |
| 数据转换与结果规范化 | `internal/util/excel.go:18` 支持 xlsx/csv；`internal/util/echarts.go:22` 清洗配置并校验 JSON。 | 服务于生成链路，合入 B1，不单列文件处理。 |
| 异步投递与执行 | `internal/model/outbox.go:19` 保存投递记录；`internal/outbox/relay.go:123` 扫描补发；`internal/mq/client.go:39` 声明主队列与死信拓扑；`internal/mq/consumer.go:59` 消费处理。 | B2 解释受理与投递分离，B3 解释重复投递下的执行权。 |
| 任务通知 | `internal/event/redis_publisher.go:33` 尽力发布，`internal/handler/sse_handler.go:42` 鉴权、过滤、推送并清理订阅；`cmd/consumer/main.go:41` 注入发布器。 | B4 解释跨进程结果通知与主流程边界。 |
| 外部调用资源边界 | `internal/ratelimit/limiter.go:23` 用户维度 Redis 限流；`internal/mq/consumer.go:71` 设置期限；`internal/service/deepseek_service.go:76` 绑定 HTTP 请求 Context。 | B5 将入口频率与模型等待时间组织为同一资源约束。 |
| 用户、权限与通用能力 | `internal/service/user_service.go` 实现注册、登录、用户管理、分页及 VO 转换；`internal/handler/user_handler.go` 维护会话；`internal/bootstrap/session.go:12` 使用 Redis Session；`internal/middleware/auth.go:16` 登录鉴权、`:36` 管理员校验；`internal/common` 提供统一响应、错误和分页。 | 已核验但不独立成一级 bullet，避免用户 CRUD 挤占生成任务主线。 |
| 数据模型与基础设施 | `internal/bootstrap/db.go:NewDB`、`redis.go:NewRedis` 完成初始化及连通性检查；`internal/model` 与 `sql/create_table.sql`、`sql/02_outbox.sql` 描述用户、图表、事务消息表和软删除。 | 支撑持久化、状态与技术栈，不宣称连接池调优或自动迁移。 |

## 简介与 B1—B5 证据

### 简介与技术栈

- go.mod（`backend/go.mod:3`）：声明 Go 1.25；直接依赖包含 Gin、GORM/MySQL、Redis、redis_rate、RabbitMQ 客户端、Excelize 和 Session 库。
- 路由装配（`backend/internal/bootstrap/router.go:55`）：生成和 SSE 均为登录后的图表接口。后端范围为 HTTP 服务与独立消费者，没有从模型调用推断 RAG、Agent 或 SQL 查询能力。
- 图表模型（`backend/internal/model/chart.go:9`）：任务状态包含 wait/running/succeed/failed；同一实体保存输入数据、生成配置、分析文本和执行信息。

### B1：AI 图表生成链路

- 工程目的：上传数据格式与模型响应格式都需要适配；当前实现将它们归一到同一图表持久化结构，供同步返回或异步查询使用。
- ExcelToCSV（`backend/internal/util/excel.go:18`）：xlsx 使用 Excelize 读取首个 sheet，过滤空行并对逗号、引号、换行作 CSV 转义；csv 直接读取文本。未实现 xls、多 sheet 分析或全量 CSV 内容校验。
- parseGenRequest（`backend/internal/handler/chart_handler.go:208`）：接收 multipart 文件，名称、分析目标和图表类型可来自 form 或 query，并校验必填项。
- BuildPrompt / GenSync（`backend/internal/service/chart_service.go:166`）：按目标、图表类型与 CSV 构造提示词，调用模型、清洗配置并保存成功记录；ProcessChart（`backend/internal/service/chart_service.go:276`） 复用提示词与配置清洗。
- AnalyzeCsv（`backend/internal/service/deepseek_service.go:56`）：使用 deepseek-chat，通过 `/v1/chat/completions` 请求，解析外层 choices 与内层 genChart/genResult；数组或字符串形式的分析结果统一为字符串。
- CleanEchartsJSON（`backend/internal/util/echarts.go:22`）：移除部分赋值/标点并校验 JSON；非法配置回退为 `{}`。这是格式容错，不能证明图表语义正确或分析结论真实，空对象仍可能随成功状态入库。模型系统提示词中的“不编造”是要求，不是准确率证据。

### B2：Transactional Outbox

- 工程目的：请求受理不等待模型生成；同时将业务任务与待投递意图置于同一数据库事务，避免两次独立写入只完成一半。
- SaveWait（`backend/internal/service/chart_service.go:208`）：GORM Transaction 内先创建 wait 图表，再创建以 chartId 为 payload 的 pending outbox；任一写入失败即返回事务错误。
- GenAsync（`backend/internal/handler/chart_handler.go:171`）：producer 为 nil 时拒绝异步请求；调用 SaveWait 后返回 chartId，handler 不直接发布 MQ。
- Relay.runOnce（`backend/internal/outbox/relay.go:123`）：按 id 升序取 pending，单批上限 100；Publish 报错时 retryCount 加一并保留 pending，成功后置 sent。启动即扫描，随后按配置周期继续，单条报错不终止整批。
- Producer.Publish（`backend/internal/mq/producer.go:21`）：通过 amqp091-go 发消息，设置 Persistent；拓扑（`backend/internal/mq/client.go:39`） 声明 durable exchange、主队列和死信队列。
- 保证范围：本地事务只保证“图表与待投递记录”一起提交。发布成功后、sent 落库前失败会重发；没有看到 publisher confirm，mandatory=false，也没有连接重建流程，不能宣称 broker 已确认送达、绝不丢消息或端到端 exactly-once。关闭 relay 配置仍可受理任务，是否持续投递取决于启用状态与进程可用性。源码注释中的强保证没有直接搬入简历。

### B3：CAS 幂等消费

- 工程目的：事务消息补发允许重复，同一任务需要在调用昂贵模型前决定唯一执行者。
- ProcessChart（`backend/internal/service/chart_service.go:260`）：先查图表，再执行带 id 与 wait 条件的 UPDATE，将状态改为 running；classifyCASResult（`backend/internal/service/chart_service.go:244`） 将零行更新归类为 ErrAlreadyProcessed。
- Consumer.handle（`backend/internal/mq/consumer.go:59`）：识别该哨兵后直接 Ack 并 return，不继续重试、MarkFailed 或发事件。消费者 Start（`backend/internal/mq/consumer.go:42`） 设置 Qos(1) 和手动确认，并逐条处理。
- 关键限制：CAS 成功后没有租约、恢复扫描或状态回退。如果第一次模型调用失败，任务仍为 running；第二次应用层尝试再次执行 CAS 会得到零行更新，被当成“已处理”而 Ack。崩溃发生在抢占后也可能留下 running。因此 B3 只主张重复执行抑制，不主张自动恢复或恰好成功一次。
- 失败分支确实存在：onExhausted（`backend/internal/mq/consumer.go:114`） 写失败、发事件并 Nack(requeue=false)，主队列已绑定死信交换机。但上述 CAS 交互使模型调用失败不一定抵达该分支，不能写成所有失败均重试后收敛到失败/死信；MarkFailed 也未检查持久化错误。

### B4：Redis Pub/Sub 与 SSE

- 工程目的：消费者独立于 HTTP 进程运行，通过任务标识把处理结果送回订阅者；通知失败不反向改变消费主流程。
- 消费者装配（`backend/cmd/consumer/main.go:41`）：Redis Ping 失败回退 NoopPublisher，消费继续；RedisPublisher（`backend/internal/event/redis_publisher.go:33`） 发布 `{chartId,status}`，序列化或 Publish 错误仅记录日志。
- 消费完成事件（`backend/internal/mq/consumer.go:103`）：生成成功后发 succeed，耗尽分支发 failed，随后执行消息确认/拒绝；没有观察到 wait/running 进度事件发布。
- SSEHandler.Stream（`backend/internal/handler/sse_handler.go:42`）：先校验登录用户与图表归属；订阅 Redis 后按 chartId 过滤，设置 text/event-stream 和关闭代理缓冲响应头；每 15 秒发注释心跳，收到终态或请求断开时退出，defer 关闭订阅与 ticker。
- useChartEvents（`frontend/src/hooks/useChartEvents.ts:89`）：同源 EventSource 订阅 `/api/chart/sse?id=...`，按 chartId/status 解析，终态关闭连接，建连超时或 error 发出轮询降级信号。仅核验这一客户端契约，未据此声称实际轮询整体行为已验收。
- 保证范围：Redis Pub/Sub 是即时通知分支，当前服务没有事件持久化、Last-Event-ID 回放或订阅后当前状态补发；事件早于订阅时可能错过，通知不能替代数据库状态查询，也不能宣称无遗漏实时推送。

### B5：模型调用限流与取消

- 工程目的：限制单用户发起模型生成的频率，以及异步生成时本地外部调用的等待时间。
- 同步入口（`backend/internal/handler/chart_handler.go:148`） 与 异步入口（`backend/internal/handler/chart_handler.go:186`） 使用同一个 `gen_chart:{userId}` key；Limiter.Allow（`backend/internal/ratelimit/limiter.go:23`） 调用 redis_rate.PerSecond(3)，Redis 调用自身设置 2 秒 Context。3 次/秒属于源码配置策略，不是吞吐测试结果；未核验依赖内部算法，不按本地注释扩大为某种算法实现。
- 消费者期限（`backend/internal/mq/consumer.go:70`）：单条消息建立 context.WithTimeout，再传给 ProcessChart；AnalyzeCsv（`backend/internal/service/deepseek_service.go:76`） 将其绑定到 http.NewRequestWithContext，并在请求/读体错误时保留可被 errors.Is 识别的超时与取消原因。客户端另有 60 秒 timeout；配置默认生成期限为 30 秒，可配置。
- 同步路径使用请求本身的 Context。取消只支持本地 HTTP 请求等待的中断，不能推断远端模型计算或计费停止；任务 DB 操作没有统一使用同一 Context，重试间隔用 time.Sleep，不能宣称整个任务严格在配置期限内返回。
- 限流发生在文件解析之后，无法据此声称上传解析资源也受频率保护；频率额度并非并发数或费用硬预算。

## 附属能力与契约边界

- Redis Session 与管理员角色有实现依据，但用户/管理员二级判断不是完整 RBAC。图表编辑、删除及 SSE 有归属或角色校验，通用 get/list 未逐项强制归属，不能写成全接口租户隔离。
- 用户密码实现为固定盐 MD5；注册使用查询后插入且 SQL 账号索引非唯一。不将这些现状写成高强度密码保护或并发注册幂等。
- 后端同步返回 BiResponse；异步实际返回 chartId 数值。前端生成服务文件的异步泛型仍写 BiResponse，存在声明与实现差异，简介仅表述“返回任务标识”，不宣称类型契约完全一致。
- 分页、错误码、VO 和软删除支撑管理能力；无证据说明微服务治理、高可用集群、分布式事务或数据库性能调优已落地。

## 验证状态

- 已完成：只读沿生成、异步受理/投递/消费、通知、限流与取消链路的静态查证；独立只读补查用户、通用基础设施与 SQL；逐条核对简介、技术栈和 B1—B5 的主张。
- 已查看相关测试源码：`internal/outbox/relay_test.go` 使用 fakePublisher/fakeStore 覆盖正常补发、发布失败后保留 pending 并在后续轮次补发、无待投递记录；`internal/service/chart_service_cas_test.go` 包含 CAS 结果分类测试；`internal/service/deepseek_service_test.go` 包含超时与取消测试。测试源码的存在不等于已执行通过，也不证明真实 MySQL/RabbitMQ 集成行为。
- 未执行：应用、测试、压测、浏览器或生产验收；无线上收益、并发规模、延迟或准确率结论。未生成课程、面经或 HTML，未对本次限定的简介/bullet 交付套用要求完整 B/Q/C 文档的校验器。
