# GenBI｜后端研发目标简历

> 以下为目标简历与学习口播，供掌握后选用。分析范围为 GenBI 完整 Go 后端，前端仅核对 HTTP 与事件通知契约。

## 项目简介

基于 Go、Gin 与 DeepSeek 的智能 BI 后端，用户上传 Excel/CSV 并指定分析目标后，系统生成 ECharts 图表配置与分析结论。支持同步生成及基于 RabbitMQ 的异步任务，通过事务消息表保存投递意图，并以 SSE 通知任务处理结果。

### 技术栈

Go 1.25、Gin、GORM / MySQL、RabbitMQ（amqp091-go）、Redis（会话、限流、Pub/Sub）、gin-contrib/sessions、redis_rate、Excelize、DeepSeek Chat Completions、net/http、SSE。

## 简历 bullet

- **AI 图表生成链路：** 为将上传的表格数据转成图表与分析结论，使用 Excelize 将 Excel 首个工作表归一为 CSV，与直接上传的 CSV 共用分析目标和图表类型的提示词构造；调用 DeepSeek Chat Completions，解析模型返回结构并清洗 ECharts 配置，同步与异步路径复用相同的数据转换及结果处理规则，持久化配置与分析文本供接口查询。
- **Transactional Outbox：** 为让异步请求提交后即可返回任务标识，同时将任务受理与待投递记录一起保存，使用 GORM 事务原子写入 MySQL 图表任务与事务消息表；后台按批扫描待投递记录并发布到 RabbitMQ，发布报错时保留记录、累加重试次数，后续扫描继续尝试，提交请求无需等待模型生成完成。
- **CAS 幂等消费：** 面向消息补发和并发消费带来的重复执行风险，以 MySQL 条件更新原子抢占任务，仅允许待执行状态推进到执行中后调用模型；RabbitMQ 消费者采用手动确认，未取得执行权的消息直接 Ack，跳过重复生成、失败标记与状态事件发布。
- **Redis Pub/Sub 与 SSE：** 为将独立消费者的处理结果通知 HTTP 客户端，消费者通过 Redis Pub/Sub 发布任务标识与终态，Gin 服务校验订阅者的图表归属后按任务过滤并转发 SSE；连接以心跳保活，终态或断连时释放订阅，事件发布失败仅记录日志，使通知分支不改变生成主流程的消费结果。
- **模型调用限流与取消：** 同步、异步入口通过 Redis 与 redis_rate 按用户共享每秒 3 次的限流策略，拒绝超额的模型生成请求；异步消费者以 Go Context 设置生成期限，并传递到 net/http 的 http.NewRequestWithContext，超时或取消时结束本地模型 HTTP 请求的等待，限制外部调用持续占用消费者。
