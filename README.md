<div align="center">
  <h1>project-interview-skill</h1>
  <p><strong>把真实项目整理成简历 bullet、源码课程和递进面经。</strong></p>
  <p>先读懂项目怎样工作，再准备怎样讲清楚。</p>
  <p>
    <a href="README_EN.md">English</a> ·
    <a href="https://www.npmjs.com/package/project-interview-skill">npm</a> ·
    <a href="LICENSE">MIT License</a>
  </p>
</div>

适合已经有项目、希望理解核心设计并准备面试的开发者。向 Agent 提供可访问的仓库或项目材料，它会查证机制、提炼技术支柱，把每条简历主张关联到问题、课程和源码。

支持通用 Agent、Codex、Claude Code、Cursor、Trae 和 VS Code Copilot；安装器需要 **Node.js 18+**，内容生成由你使用的 Agent 完成。

[快速开始](#快速开始) · [成品示例](#成品示例) · [常用请求](#常用请求) · [安装与更新](#安装与更新) · [准确性与验证](#准确性与验证)

## 快速开始

**1. 安装已发布版本**

```bash
npx project-interview-skill@latest install
```

默认安装到 `~/.agents/skills/project-interview-skill/`。其他产品使用[对应安装参数](#安装与更新)；要使用 GitHub 当前源码，见[源码安装](#源码安装)。

**2. 打开你的项目根目录，重启 Agent / 编辑器并开启新对话**

复制下面的请求，替换项目简称与岗位即可；技术栈会从源码识别。

```text
使用 project-interview-skill，分析当前仓库。
项目简称：商城
目标岗位：后端研发
请生成导学、全部核心源码课程和面经，写入 interview-prep/。
```

也可以用 `/project-interview-skill` 调用，并在后面附上上述信息。只有项目描述时，直接粘贴材料即可。

**3. 从导学开始，按课程理解机制，再练面经**

下面是单项目、后端方向的目录示意：

```text
interview-prep/
├── 商城/
│   ├── 导学.md                 # 项目地图、学习路线与导航
│   └── 面经.md                 # 简历 bullet、主问、追问与口播
└── guide-backend/
    ├── 01-主题.md              # 完整核心课程
    └── 02-主题.md
```

| 产物 | 你能看到什么 | 怎么用 |
| --- | --- | --- |
| 导学 | 模块职责、代表性链路、课程前置依赖和导航 | 先建立项目全貌，确定学习顺序 |
| 核心课程 | 真实源码、运行机制、异常边界、需要懂什么与需要记住什么 | 沿场景读代码，讲清机制和取舍 |
| 面经 | 项目简介、技术支柱、简历触发词、主问与递进追问、第一人称回答 | 对照简历练习，让每个主张都有展开依据 |

未指定方向时默认全栈，课程目录为 `guide-fullstack/`；明确前端时为 `guide-frontend/`。多个项目共用输出根目录时，课程放在各自的 `{简称}/guide-{方向}/` 下。首次默认完整展开全部核心课程，选读内容按需展开。

## 学到某一课，再生成 HTML

每课末尾会提供一段已经填写项目、课程路径、范围与源码基线的提示词。复制到能访问同一项目的新聊天即可生成整课 HTML；也可以追加自己不懂的小节。已有旧课程没有这个入口时，直接指定文件同样可以使用，例如：

```text
使用 project-interview-skill 的 HTML 深化模式。
读取 interview-prep/guide-backend/03-任务状态.md，课程 C03。
只讲“机制与边界 / 有限重试”：我不懂失败后为什么还是同一任务。
请生成单文件离线 HTML，保留原文与我的笔记。
```

这里的路径和主题是示例，替换为你的课程。页面会用状态变化、关键代码和正常/异常分支解释机制，按需要加入步骤切换等互动，默认不加测验或答题解锁。HTML 按需写入该文档同目录的 `html/`，成功生成后在原 Markdown 尾部登记入口；首轮仍完整交付 Markdown，不提前生成全部 HTML。普通追问直接在对话回答。

表达规则适配自 [Humanizer](https://github.com/blader/humanizer)，教学方法适配自 Matt Pocock 的 [/teach](https://github.com/mattpocock/skills/tree/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/productivity/teach)。本 Bundle 已包含适配规则，无需再安装它们，也没有新增 `/tech` 或 `/teach` 命令；[来源、版本与许可](skill/project-interview-skill/references/upstream/sources.md)可供核对。

[合成课程 HTML 首稿](docs/testing/samples/progressive-teaching/H2-first/interview-prep/guide-backend/html/03-任务状态--有限重试-455e7796.html)与[验证记录](docs/testing/2026-10-25-progressive-teaching.md)保留实际生成结果、笔记更新检查和浏览器验证限制。

## 成品示例

下面节选自 **DeerFlow 源码补稿的审读修订版**，展示如何用具体机制组织正文；完整输出和证据可在[原始记录](docs/testing/samples/bullet-quality/deerflow-primary-revised.md)与[源码索引](docs/testing/samples/bullet-quality/deerflow-primary-evidence.md)中查看。

> - **Skill 渐进加载与工具授权：** 技能以含 SKILL.md 的目录包组织，默认提示提供元数据，正文由显式选择或 read_file 按需加载；会话状态保留已加载技能的轻量引用。
>   - 活跃技能的 allowed-tools 同时过滤模型可见工具并拦截越权调用，权限声明参与实际执行控制。
> - **上下文压缩与跨会话记忆：** 达到配置阈值后，将较早历史压成摘要并保留近期消息；摘要生成成功才替换历史，摘要、委派记录与技能引用独立保存并注入后续模型请求。
>   - 过大的工具结果写入文件，以摘要和文件引用进入上下文；文件持久化不可用时退回首尾截断。
>   - 启用被动记忆模式时，对话在执行结束后入队处理，入队时捕获用户身份，后台抽取持久记忆，后续会话按用户与 Agent 作用域加载。

标题让同行识别设计，正文解释职责、协作和改变行为的条件；重要子机制可以展开，不强行补收益句。支柱由项目核心职责和真实机制决定，数量与标题不套金样。英文有辨识价值时保留，中文更自然时使用中文。

完整交付还会建立以下关联，便于回到源码复习：

```text
B1 简历支柱
 └─ Q1 面试主问 → 根据回答递进追问
     └─ C01 核心课程 → 源码路径与关键符号
```

不同领域的例子可看 [EdgeMetric 存储引擎首稿](docs/testing/samples/bullet-quality/edgemetric-first.md)。

<details>
<summary>展开历史界面截图：面经与学习路线</summary>

以下截图展示早期版本的阅读界面，内容和文件名以当前文字示例及输出契约为准。

![早期版本的简历 bullet 与 Agent 对话](https://raw.githubusercontent.com/Jaxon1216/interview-analyzer-skill/main/docs/images/bullet-output.png)

![早期版本的主问、追问与口播](https://raw.githubusercontent.com/Jaxon1216/interview-analyzer-skill/main/docs/images/interview-questions.png)

![早期版本的源码学习路线](https://raw.githubusercontent.com/Jaxon1216/interview-analyzer-skill/main/docs/images/learning-path.png)

</details>

## 常用请求

默认交付可以直接用快速开始中的请求；需要缩小范围或增量更新时，把要求写清楚。

| 需要什么 | 可直接复制的请求 |
| --- | --- |
| 先看简历表达 | `使用 project-interview-skill，面向后端岗位分析当前完整仓库，只生成项目简介和简历 bullet，另附源码证据。` |
| 深入一个机制 | `使用 project-interview-skill，只展开上下文压缩这节源码课程，讲清主链、失败边界、需要懂什么与需要记住什么。` |
| 整理实际贡献 | `使用 project-interview-skill，仅整理我的实际贡献。参与范围：……；已有证据：……；目标岗位：……。` |
| 更新已有材料 | `使用 project-interview-skill，基于最新源码更新 interview-prep/，保留我的笔记、未请求章节和既有 B/Q/C 编号。` |

默认是**目标简历与学习模式**：仓库已实现机制可以入选，供掌握后选用；不主动审核提交作者。需要描述本人实际经历时，明确使用“仅整理实际贡献”并给出参与范围。

## 安装与更新

通用安装命令为 `npx project-interview-skill@latest install`。选择产品时，在后面添加对应参数：

| 产品 | 参数 | 用户级位置 | 加 `--project` 后的位置 |
| --- | --- | --- | --- |
| 通用 Agent / Codex | `--agents` 或 `--codex` | `~/.agents/skills/project-interview-skill/` | `.agents/skills/project-interview-skill/` |
| Claude Code | `--claude-code` | `~/.claude/skills/project-interview-skill/` | `.claude/skills/project-interview-skill/` |
| Cursor | `--cursor` | `~/.cursor/rules/project-interview-skill/` | `.cursor/rules/project-interview-skill/` |
| Trae | `--trae` | `~/.trae/skills/project-interview-skill/` | `.trae/rules/project-interview-skill/` |
| VS Code Copilot | `--vscode` | `~/.copilot/instructions/project-interview-skill.instructions.md` | `.github/instructions/project-interview-skill.instructions.md` |

例如：

```bash
# 用户级：供 Cursor 使用
npx project-interview-skill@latest install --cursor

# 项目级：在你的业务项目根目录执行
npx project-interview-skill@latest install --project --trae

# 先查看安装位置
npx project-interview-skill@latest install --trae --dry-run
```

`--project` 以**执行命令时所在目录**为项目根目录。默认不会自动探测产品；`--all` 安装到全部支持目标，`doctor` 只显示路径。

VS Code 的 instructions 是入口，完整 Bundle 安装在其同目录的 `project-interview-skill/`，保留 `references/` 与 `scripts/`；迁移时一并复制。`doctor` 和 `--dry-run` 会同时显示两个位置。

**更新已安装的 Skill**：重新运行原安装命令，保留相同产品参数和作用域。例如，更新用户级通用 Agent / Codex：

```bash
npx project-interview-skill@latest install --agents
```

安装会替换目标 Skill 目录；更新后重启 Agent / 编辑器并开启新对话。已有 `interview-prep/` 材料在再次调用 Skill 后才会更新。固定 npm 版本时，将 `@latest` 换为具体版本号。

### 源码安装

GitHub 当前源码和 npm 已发布版本可能不同。使用仓库当前内容时：

```bash
git clone https://github.com/Jaxon1216/interview-analyzer-skill.git
cd interview-analyzer-skill
./install.sh --agents
```

`install.sh` 是 Node CLI 的包装器，支持相同安装参数；它不包含在 npm 包内。已有 clone 时，更新源码后重新安装。

也可以直接复制完整的 `skill/project-interview-skill/` 目录，其中包含 `SKILL.md`、`references/` 和 `scripts/`；迁移 Skill 无需复制 CLI 或测试工程。

## 准确性与验证

源码用于支持技术事实，历史演进、个人身份与收益数字需要各自的证据。未实现增强另列进阶；没有可支持的效果就直接结束，不用待测尾注填充简历。

对生成的完整导学与面经，可检查交付结构（将路径替换为实际安装目录）：

```bash
python3 ~/.agents/skills/project-interview-skill/scripts/validate_output.py interview-prep/商城/面经.md --guide interview-prep/商城/导学.md
```

校验覆盖 bullet 格式、B/Q/C 关联、核心课程章节和本地链接。**整组选材、事实准确性、术语和成稿质量仍需分别审读。**

HTML 单独检查本地链接、离线依赖、正文和交互；上述脚本不解析 HTML 或执行 JavaScript。Agent 会报告可执行检查的结果与未验证项，生成页面不代表已经掌握该课。

开发仓库的检查入口：

```bash
npm test
npm run pack:check
```

[测试说明](tests/README.md)列出自动回归与人工行为评测。[最近的选材与成稿记录](docs/testing/2026-10-13-bullet-quality.md)保留首次输出、修订和限制：DeerFlow 独立生成因额度中断，展示稿来自主 agent 补稿及修订；跨领域存储材料完成了一次独立生成。自动检查通过不代表内容质量已被证明。

## 反馈与许可

欢迎通过 [Issue](https://github.com/Jaxon1216/interview-analyzer-skill/issues) 反馈使用问题或提交 PR。联系：**jiangxu05@outlook.com**。

采用 [MIT License](LICENSE)。许可证附中文参考译文，英文正文为准。
