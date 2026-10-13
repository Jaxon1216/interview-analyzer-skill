# 金样：DeerFlow Agent Harness（图 1 OCR）

来源：用户提供的优秀简历截图（开源项目 `github.com/bytedance/deer-flow`）。下文是按截图整理的全文，供对照结构，**禁止把本页的 star 数、层名、超时数字写进其他项目**。

---

## OCR 正文

**github.com/bytedance/deer-flow** · 76k stars · 10.3k forks · GitHub Trending #1 Repository Of The Day

### 项目简介

字节跳动排名第一的开源 Long-Horizon Agent Harness 项目，能做研究、编码与创作；内置 AIOSandBox 执行环境、可插拔 Skill 系统、跨会话长期记忆、动态 Sub-agent 调度与系统性 Context Engineering，可处理多层 long-horizon 任务。

### 我的职责

作为项目 owner、核心作者之一，主导从 1.0 到 2.0 的架构升级与迭代。

- **1.0（Multi-Agent + ReAct-style Sub-Agent）**
  - 工作流：Coordinator（意图识别）→ Planner → Research Team（Researcher / Coder 支持 MCP 动态扩展外部工具）→ Reporter（汇总上下文生成最终报告）。Prompt 由 OpenAI Meta Prompt 生成。

- **2.0（Agent Teams Harness + Middleware Chain + Skill System + Context Engineering）**
  - **Agent Teams Harness：** 相比 1.0 固定 5 节点流水线，2.0 改为单一 Lead Agent 统一决策。`system_prompt` 动态写入——按当前启用的 Skill 列表、跨会话持久记忆、Sub-agent 并发规则组装。Lead Agent 通过 `task` 工具触发 SubagentExecutor 启动独立 Agent 实例。调度与执行分离为双线程池，最大 3 并发 / 900s 单任务超时。Sub-agent 继承父线程目录 + 复用父沙箱，实时流式步骤到前端，完成后向 Lead Agent 返回压缩摘要。
  - **Middleware Chain：** 1.0 中上下文压缩 / 沙箱 / 记忆逻辑散落，改一处要改很多。2.0 抽成 11 层有序 pipeline；增改能力只动对应层，Agent 推理代码零改动。（顺序：ThreadData → Uploads → Sandbox → DanglingToolCall → Summarization → Todo → Title → Memory → ViewImage → SubagentLimit → Clarification）
  - **Skill System：** 每个 Skill 是含 `SKILL.md` 的目录。`system_prompt` 只注入索引；Agent 按需通过 `read_file` 渐进加载，避免全量注入导致 token 爆炸。支持自定义 skill，在 `custom/` 下加目录即可。
  - **Context Engineering：**
    - **Write：** 中间结果写入文件系统；每轮把索引 / 规则注入 `system_prompt`
    - **Select：** 按 token 预算从 `memory.json` 剪枝注入；Skills 按需读全文
    - **Compress：** 超限时用轻量 LLM 压缩历史 + 异步抽取持久记忆
    - **Isolate：** Sub-agent 只看到任务描述；结果摘要回传；沙箱按 `thread_id` 隔离

---

## 点评（生成时只复用这些，不复用上文专有名词当素材）

### 可复用结构

1. **简介先定形态**：产品是什么（Long-Horizon Agent Harness）+ 能力清单（沙箱 / Skill / 长记忆 / 子 Agent / 上下文工程）。有真实影响力再写 star / Trending；没有就省略，禁止编。
2. **职责与事实分开**：原文的 owner / 核心作者是该作者的身份，不是提升表达质量所需的前提；分析其他项目按实际证据写职责与机制。
3. **组织围绕系统职责**：原文用真实演进串联核心机制；只有当前实现证据时直接讲协作关系，不复制升级历史、固定层数或技术组合。
4. **机制直接、约束相关**：各条分别从版本演进、运行方式或能力分解起笔；并发/超时跟着调度，索引/按需加载跟着 Skill，效果紧随机制。问题、机制、约束、结果可用于事实归档，不要求每条四槽齐全或同一顺序。
5. **允许嵌套**：一级概括系统机制，二级展开协作、条件和关键实现；标题与条数由待分析项目决定。
6. **相关常用技术名可留在简历上**：本例中的 Middleware Chain、Context Engineering、MCP 等承担架构或机制解释。复用时仍按[技术术语选择](../rules/oral-and-resume-patterns.md#技术术语选择)核对事实、目标岗位熟悉度和中英文表达优势；截图出现或能搜索到不意味着其他项目也应照用英文。

### 面试官只看简历会问什么（正例题干）

- 1.0 固定五段流水线和 2.0 单一 Lead Agent，取舍是什么？
- 为什么压缩 / 沙箱 / 记忆要做成中间件，而不是写进 Agent 循环？
- Skill 只注入索引、按需读全文，怎么避免该用时找不到？
- 上下文工程的 Write / Select / Compress / Isolate 各自解决什么失败模式？
- 子 Agent 并发 3、超时 900s 是怎么定的？超时之后 Lead Agent 看到什么？

### 不要写成什么样（同一仓库的一次失败生成）

本 skill 曾把该仓写成前端工单清单（对照规则见 `oral-and-resume-patterns.md` 的「功能工单型」）：

- 主 O Web 会话流式协议对接；断流重放；（重连成功率待测）
- 收敛消息时序两类竞态
- 接入子 Agent 进度卡片
- 开发人机确认卡片与协议降级
- 两级合帧 + 产物预览字节上限；（Long Task 待测）
- 接入技能斜杠、MCP 开关与能力门控

这组条目没有先解释项目怎样完成主要任务。交互与接口细节应归入它们服务的系统机制，有辨识价值的保留在正文或二级。生成时从完整项目重新选材；本金样的四个标题不是任何项目（包括另一源码基线的 DeerFlow）的固定答案。
