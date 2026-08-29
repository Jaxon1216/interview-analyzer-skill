# 金样：AI4SE Agent 轨迹合成与评测（图 2 OCR）

来源：用户提供的优秀简历截图（抖音 AI 基建 · AI4SE）。本 skill **未**用该项目跑过生成；收录是为了第二套结构：背景与目标 → 职责 → 机制 → 指标。禁止把本页指标、脚手架名单、token 阈值抄到其他项目。

---

## OCR 正文

**抖音 AI 基建 - AI4SE 基座算法 & Infra** · 2025.12 – 2026.4

### AgentScaling for SFT & RL | MultiModel Relay + Multi-Scaffold Diverse Trajectory Synthesis Pipeline

**背景与目标**

- 单模型轨迹风格容易过拟合。借鉴 Mix Diverse GPTs，引入多种 scaffold 提供不同风格的轨迹；目标是把高质量、多样化轨迹规模化合成，供 SFT 使用。
- 针对困难题上 Claude Opus 4.6 连续失败 3 次以上的情况，用 relay 与定位策略提高通过率、降低重复推理成本。

**我的职责**（项目 owner，0 到 1 设计落地；CLI：`relay run` → `export`）

- **多 scaffold 统一适配：** 为 10+ scaffold（codex、claude_code、cline 等）做统一 Agent 接口。新 scaffold 只需实现 `run` / `get_answer`。
- **Relay run 执行引擎：** 同一 Docker 容器内多 LLM 顺序接力，共享环境状态。交接分三阶段：规则压缩历史（约 12k 结构化文本）→ LLM 以 gold patch 作静默顾问生成 RFC（review）→ 按 Plan A/B/C 裁剪对话作为下一模型输入。可选每轮 Test-in-Loop：成功则提前退出，失败则把失败报告注入下一模型。复现 SWE-Replay：归档历史轨迹、从中间步分叉、用 `git diff` 恢复现场再试。
- **效果：** SWE-Bench 系列困难题通过率提升约 25%+；单任务推理成本（API 与耗时）下降约 30%+；覆盖 10+ seed 风格。
- **上下文压缩 + Checkpoint 续跑：** 超过约 180k tokens 触发 Micro compact；超过约 250k 走 LLM fallback。每轮落 checkpoint，中断后可从上一模型状态续跑。

### Agent Tracer Evaluation for SFT & RL | Trajectory Diagnosis + Rubric Eval and Wash Pipeline

**背景与目标**

不同模型在 MultiSWEBench 上完成率接近，但 agentic 能力（规划、工具效率、错误恢复、补丁质量）差异大。目标：用 Rubric 打分并过滤高质量轨迹片段，供 SFT / RL 训练。

**我的职责**（项目 owner，0 到 1 设计；CLI：`evaluate run` → `wash` → `export`）

- **LLM-as-Judge 评测引擎：** 按检查类型分批，减少 API 调用；能用规则判定的不走 LLM；支持多模型投票；429 自动退避重试，并限制并发与请求频率。
- **Failure Onset 定位：** 识别 Evidence-to-Action Gap（已经定位到证据，却转不成正确动作）。逐步打分找到第一次错误决策，丢掉其后的连锁失败，只保留此前的高质量决策段。
- **轨迹压缩：** 按内容类型差异化裁剪；同样在约 180k / 250k tokens 触发 compact / LLM 摘要，保留首条 USER 与失败报告。
- **增量续跑 + wash / export：** 按 CSR / ISR / Score / Effective Action Ratio 等多维 Top-K 过滤。
- **效果：** Agentic Rubric 模型区分度约 35%。相对未清洗基线，高质量决策段占比明显上升，SFT / RL 的通过率与补丁质量更好。

### SWE 系列 Benchmark 评测服务改造 | 接入字节云 AIPaaS 容器平台

**我的职责**（项目 owner）

把分散的本地评测迁到 AIPaaS 容器平台统一入口。链路：spec 配置 → CreateSession（申请隔离容器）→ 恢复仓库 → Agent 修复 → 提交 diff → 异步轮询 → 返回结构化结果，供业务线调用。

---

## 点评（生成时只复用这些）

### 可复用结构

1. **先 Why 再 How：** 「背景与目标」点名过拟合、连续失败、完成率相近但 agentic 差，简历读者 10 秒知道你在解决什么行业问题。
2. **所有权 + 交付物：** owner、0 到 1、CLI 工作流（`relay run` → `export`）说明这是一条可运行的系统，不是一组脚本。
3. **给失败模式起能问出口的名字：** Evidence-to-Action Gap、Failure Onset。面试官会问「怎么定义、怎么定位、切掉连锁失败会不会误杀」。
4. **机制带阶段数字：** 三阶段交接、约 12k、180k / 250k，数字是设计约束，不是空「待测」。
5. **指标跟在机制后面：** 25%+ / 30%+ / 35% 出现在已经讲清怎么做之后。用户项目没有数就写架构结果（统一接口、可续跑、推理代码零改），禁止编百分比。

### 面试官只看简历会问什么（正例题干）

- 多 scaffold 统一接口，怎么保证轨迹还能保持风格差异、而不是被接口抹平？
- 接力交接为什么是「规则压缩 → RFC → Plan A/B/C」，而不是直接把上一模型对话原样喂给下一个？
- Evidence-to-Action Gap 怎么操作化？第一次错误决策怎么避免误标？
- 180k / 250k 两个阈值各自挡住什么失败？压缩丢的是什么、必须保住什么？
