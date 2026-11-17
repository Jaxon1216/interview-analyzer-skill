# 简短源码证据

核实日期：2026-11-17。仅静态阅读指定 Skill 与给定源码，未启动应用、调用模型或运行测试。

## GenBI

范围：`<GENBI_ROOT>/backend`（后端）。

| 核实结论 | 源码证据 |
| --- | --- |
| Go、Gin、GORM 与基础设施依赖已声明，数据库实际连接 MySQL。 | go.mod（`<GENBI_ROOT>/backend/go.mod:3`）、db.go（`<GENBI_ROOT>/backend/internal/bootstrap/db.go:16`） |
| 接收 Excel/CSV，调用 DeepSeek，返回图表配置与分析结论。 | excel.go（`<GENBI_ROOT>/backend/internal/util/excel.go:18`）、deepseek_service.go（`<GENBI_ROOT>/backend/internal/service/deepseek_service.go:15`）、chart_service.go（`<GENBI_ROOT>/backend/internal/service/chart_service.go:173`） |
| 同步生成与异步提交分别提供接口，RabbitMQ 消费者执行后台生成，SSE 推送任务状态。 | chart_handler.go（`<GENBI_ROOT>/backend/internal/handler/chart_handler.go:139`）、consumer.go（`<GENBI_ROOT>/backend/internal/mq/consumer.go:42`）、sse_handler.go（`<GENBI_ROOT>/backend/internal/handler/sse_handler.go:40`） |
| Redis 用于会话与请求限流。 | session.go（`<GENBI_ROOT>/backend/internal/bootstrap/session.go:12`）、limiter.go（`<GENBI_ROOT>/backend/internal/ratelimit/limiter.go:23`） |

## DeerFlow

范围：`<DEERFLOW_ROOT>`（前端提交至 Agent、工具/技能及结果展示的全栈链路）。

| 核实结论 | 源码证据 |
| --- | --- |
| 前端采用 TypeScript/Next.js，后端采用 Python/FastAPI，Agent 框架依赖 LangChain/LangGraph。 | frontend/package.json（`<DEERFLOW_ROOT>/frontend/package.json:9`）、backend/pyproject.toml（`<DEERFLOW_ROOT>/backend/pyproject.toml:6`）、harness/pyproject.toml（`<DEERFLOW_ROOT>/backend/packages/harness/pyproject.toml:24`） |
| Web 端提交消息和运行上下文，Gateway 创建运行并返回事件流。 | hooks.ts（`<DEERFLOW_ROOT>/frontend/src/core/threads/hooks.ts:2753`）、thread_runs.py（`<DEERFLOW_ROOT>/backend/app/gateway/routers/thread_runs.py:991`） |
| Agent 装配模型与工具；工具集合包含 MCP 工具。 | agent.py（`<DEERFLOW_ROOT>/backend/packages/harness/deerflow/agents/lead_agent/agent.py:1402`）、tools.py（`<DEERFLOW_ROOT>/backend/packages/harness/deerflow/tools/tools.py:337`） |
| 技能支持先发现元数据再按需加载，沙箱工具负责命令执行。 | describe.py（`<DEERFLOW_ROOT>/backend/packages/harness/deerflow/skills/describe.py:120`）、sandbox/tools.py（`<DEERFLOW_ROOT>/backend/packages/harness/deerflow/sandbox/tools.py:2456`） |
| 前端渲染回复并展示、下载生成文件。 | message-list-item.tsx（`<DEERFLOW_ROOT>/frontend/src/components/workspace/messages/message-list-item.tsx:643`）、artifact-viewer.tsx（`<DEERFLOW_ROOT>/frontend/src/components/workspace/artifacts/artifact-viewer.tsx:118`） |
