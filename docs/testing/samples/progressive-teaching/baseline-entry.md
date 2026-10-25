# C03 重试与状态：学习入口

复制到新聊天：

```text
读取 /Users/eastonjiang/code/ideas/interview-analyzer-skill/skill/project-interview-skill/SKILL.md，仅为 C03「重试与状态」生成离线单文件 HTML 教学页。事实：状态 queued/running/failed/done；消费者失败保留任务 ID 并有限重试。无源码、个人经历、指标。讲清机制、边界、必懂与必记；未给出的转换、重试上限、退避策略标为未知。保留 ID 不等于幂等。只做本课，不生成面经或其他课。
```

以上学习入口共 293 字符（含 Markdown 标记与换行），可独立复制，不依赖本聊天历史。

## HTML 深化流程从哪里读取

当前 skill 没有专门的 HTML 深化流程。可以读取以下已有规则作为课程内容依据，但不能把它们说成现成的 HTML 模式：

- [SKILL.md](/Users/eastonjiang/code/ideas/interview-analyzer-skill/skill/project-interview-skill/SKILL.md) 的“默认范围”“输入与参考”“交付目录与增量更新”：允许只处理指定课程，只有描述时不虚构源码；课程设计和文件骨架分别按下列两个文件读取。
- [课程设计与质量分层](/Users/eastonjiang/code/ideas/interview-analyzer-skill/skill/project-interview-skill/references/rules/course-design.md) 的“单课内容”“代码引用与可移植性”“更新与质量检查”：提供课程重点、主链、机制与异常边界、必懂与必记等要求；默认不布置预测、实验或作业。
- [输出骨架](/Users/eastonjiang/code/ideas/interview-analyzer-skill/skill/project-interview-skill/references/templates/output-templates.md) 的“核心课程 C01…”：现有骨架是 Markdown，未定义 HTML 骨架或生成步骤。

离线单文件 HTML 是本次请求附加的交付要求，并非已从 skill 读取到的能力契约。

## 当前契约与缺口

**明确 HTML 模式：没有。** 主流程、模板和校验器面向 Markdown 导学、面经与课程，没有 HTML 模式入口、资源内联要求、离线验收、页面质量检查或 HTML 专用校验。

**可跨聊天定位的入口契约：没有。** 现有 C01…稳定编号、相对文件链接和导航便于在一套材料内阅读，但未规定新聊天请求必须携带项目根目录、课程文件路径、课程内容或源码基线，也未规定 Agent 如何解析 C03。本次入口手动携带 skill 绝对路径和全部已知事实，只能用于当前可访问该路径的环境；它无法定位未提供的既有 C03 文档，也不代表 skill 已有标准入口。

**已有事实边界：** 四种状态及“失败保留 ID、有限重试”可用于教学。具体状态转移、failed 是单次失败还是最终失败、重试上限、调度方式、退避、幂等和终止条件尚未提供，不能写成项目已实现行为；也没有个人经历或指标可供扩写。
