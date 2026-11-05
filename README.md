# Project Interview Skill · 项目源码导学与面试准备

**简体中文** · [English](README_EN.md) · [npm](https://www.npmjs.com/package/project-interview-skill) · [看 DeerFlow 实例](#deerflow-example)

把项目仓库交给 Codex 等 AI 编程助手，生成项目导学、源码课程、简历要点和面试问答。顺着一条简历要点，你能看到面试官可能怎么追问，再沿课程链接找到支撑回答的代码。

## 安装：跨项目使用，还是只给当前项目用？

安装器需要 **Node.js 18 或更高版本**。选下面一种即可：

**跨项目使用（默认，适用于 Codex 和读取 `.agents/skills/` 的助手）**。在任意目录运行：

```bash
npx project-interview-skill@latest install
```

安装到 `~/.agents/skills/project-interview-skill/`。这里的 `~` 是你的用户主目录；使用 Codex 不需要另加参数。

**仅当前项目使用**。在你要分析的**项目根目录**运行：

```bash
npx project-interview-skill@latest install --project
```

安装到该项目的 `.agents/skills/project-interview-skill/`。如果想和队友共用，可以把这个目录提交到项目仓库。

<details>
<summary>Claude Code、Cursor、Trae、VS Code Copilot 装到哪里？</summary>

在安装命令末尾加对应参数，例如 `npx project-interview-skill@latest install --claude-code`。下表列出**父目录**；安装器会在其下创建 `project-interview-skill/`。

| 助手 | 参数 | 用户级父目录 | 加 `--project` 后的父目录 |
| --- | --- | --- | --- |
| Claude Code | `--claude-code` | `~/.claude/skills/` | `.claude/skills/` |
| Cursor | `--cursor` | `~/.cursor/rules/` | `.cursor/rules/` |
| Trae | `--trae` | `~/.trae/skills/` | `.trae/rules/` |
| VS Code Copilot | `--vscode` | `~/.copilot/instructions/` | `.github/instructions/` |

VS Code Copilot 还会在同一父目录生成 `project-interview-skill.instructions.md`。想先看实际路径，可在安装命令后加 `--dry-run`。若要使用 GitHub 当前源码，克隆本仓库后在仓库根目录运行 [`./install.sh --agents`](install.sh)。

</details>

## 如何更新到最新版？

**重跑最初的安装命令**，保留 `@latest`、客户端参数和安装范围。默认安装的用户，在任意目录运行：

```bash
npx project-interview-skill@latest install
```

如果当初只为某个项目的 Claude Code 安装，则回到那个项目根目录运行 `npx project-interview-skill@latest install --project --claude-code`。安装器会替换目标 skill 目录；已经生成的 `interview-prep/` 不会随之改写。安装或更新后，重启助手并开启新对话。

## 第一次使用：从导学开始

用助手打开目标仓库，把这句话发给它：

```text
使用 project-interview-skill 分析当前仓库。我准备面试后端研发岗位，
请把项目导学、核心源码课程和面经写到 interview-prep/，给适合演示的难点配上 HTML 专题。
```

只有项目描述时也可以直接粘贴材料；缺少源码的部分会标明。生成后，从 `interview-prep/<项目简称>/导学.md` 开始：

| 想做什么 | 打开哪里 |
| --- | --- |
| 先弄清项目怎么跑 | **导学.md**：看模块、调用链和推荐学习顺序。 |
| 读懂一个机制 | **核心课程 Markdown**：沿场景读源码，看正常路径、异常分支和设计取舍。 |
| 比较条件变化后的结果 | **HTML 专题**：从导学或对应课程点进去，离线切换条件。主会话通常选 1～3 个难点；支持子 agent 时按专题分工，没有合适题材时保留 Markdown 即可。 |
| 准备面试 | **面经.md**：从简历要点练主问、追问和第一人称回答。若只想写本人做过的工作，说明参与范围并要求“仅整理实际贡献”。 |

<a name="deerflow-example"></a>

## DeerFlow 实例：为什么同一次保存会先遇到 409？

在 DeerFlow 仓库的一次实际生成中，8 节核心课程配了 2 个 HTML 专题：**事件回放的游标**与**两个标签页保存同一份文件**。下图来自第二个专题。

![DeerFlow 文件保存专题：选中「运行中」和「基线过期」，页面显示先返回 409，尚未检查文件版本。](https://raw.githubusercontent.com/Jaxon1216/interview-analyzer-skill/main/docs/images/deerflow-artifact-save.png)

两个标签页读到了同一版文件。甲先保存，乙拿着旧版本再保存：如果线程正忙，乙先收到 **409**；等线程空闲后用旧版本重试，才会收到 **412**。可以对照 [DeerFlow 保存请求的处理代码](https://github.com/bytedance/deer-flow/blob/5ecc1c2ac2de624af354bc515d5cb04f80df226c/backend/app/gateway/routers/artifacts.py#L533) 看这两个检查的顺序。

想看简历要点的写法，可以对照 [DeerFlow 简历节选（审读修订版）](docs/testing/samples/bullet-quality/deerflow-primary-revised.md) 和[对应的源码证据](docs/testing/samples/bullet-quality/deerflow-primary-evidence.md)。

[测试与验证](tests/README.md) · [反馈问题](https://github.com/Jaxon1216/interview-analyzer-skill/issues) · [联系维护者](mailto:jiangxu05@outlook.com) · [MIT 许可证](LICENSE)
