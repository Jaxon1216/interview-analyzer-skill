<div align="center">
  <h1>project-interview-skill</h1>
  <p><a href="https://github.com/Jaxon1216/interview-analyzer-skill/blob/main/README_EN.md">English</a></p>
  <p><em>把你的项目经历，变成可复述、可追问、可上场的面试战斗手册。</em></p>
  <p>
    <a href="SKILL.md"><img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-yellow.svg"></a>
    <img alt="Type: Agent Skill" src="https://img.shields.io/badge/Type-Agent%20Skill-7c3aed">
    <img alt="Trae Compatible" src="https://img.shields.io/badge/Trae-Compatible-111827">
    <img alt="Cursor Compatible" src="https://img.shields.io/badge/Cursor-Compatible-00B8D9">
    <img alt="VS Code Compatible" src="https://img.shields.io/badge/VS%20Code-Compatible-007ACC?logo=visual-studio-code&logoColor=white">
    <img alt="Claude Code Compatible" src="https://img.shields.io/badge/Claude%20Code-Compatible-7c3aed">
    <img alt="Codex Compatible" src="https://img.shields.io/badge/Codex-Compatible-0A66C2">
  </p>
</div>

把真实项目快速整理成两份可直接用于面试准备的文档（输出到目标项目根目录）：

- `导学-{简称}.md`：重点亮点、代码阅读路径、学习顺序与必备知识点
- `面经-{简称}.md`：简历可用摘要 + 面试题口播（第一人称 STAR）

## 效果演示

下面这张合并图展示了触发输入与面经输出示例：

![Demo](https://raw.githubusercontent.com/Jaxon1216/interview-analyzer-skill/main/demo.jpg)

## 安装方式

推荐使用 `npx`，不需要 clone 仓库：

```bash
npx project-interview-skill install
```

默认安装到用户级通用 Agent 目录：

```text
~/.agents/skills/project-interview-skill/
```

如果你明确使用某个编辑器或 Agent，建议显式指定产品：

| 目标 | 用户级安装 | 安装位置 |
|------|------------|----------|
| 通用 Agent / Codex | `npx project-interview-skill install --agents` | `~/.agents/skills/project-interview-skill/` |
| Trae | `npx project-interview-skill install --trae` | `~/.trae/skills/project-interview-skill/` |
| Cursor | `npx project-interview-skill install --cursor` | `~/.cursor/rules/project-interview-skill/` |
| VS Code | `npx project-interview-skill install --vscode` | `~/.copilot/instructions/project-interview-skill.instructions.md` |
| Claude Code | `npx project-interview-skill install --claude-code` | `~/.claude/skills/project-interview-skill/` |
| Codex | `npx project-interview-skill install --codex` | `~/.agents/skills/project-interview-skill/` |

也可以一次安装到全部支持目标：

```bash
npx project-interview-skill install --all
```

只查看会安装到哪里，不写入文件：

```bash
npx project-interview-skill install --trae --dry-run
npx project-interview-skill doctor
```

## 项目级安装

如果你只想让某个业务项目使用这个 skill，进入业务项目根目录后执行：

```bash
cd /path/to/your-project
npx project-interview-skill install --project --trae
```

支持的项目级目标：

| 目标 | 项目级安装 | 安装位置 |
|------|------------|----------|
| 通用 Agent / Codex | `npx project-interview-skill install --project --agents` | `.agents/skills/project-interview-skill/` |
| Trae | `npx project-interview-skill install --project --trae` | `.trae/rules/project-interview-skill/` |
| Cursor | `npx project-interview-skill install --project --cursor` | `.cursor/rules/project-interview-skill/` |
| VS Code | `npx project-interview-skill install --project --vscode` | `.github/instructions/project-interview-skill.instructions.md` |
| Claude Code | `npx project-interview-skill install --project --claude-code` | `.claude/skills/project-interview-skill/` |
| Codex | `npx project-interview-skill install --project --codex` | `.agents/skills/project-interview-skill/` |

安装完成后，重启对应 IDE / Agent，开启新对话。

## 使用方式

在被分析项目的工作区开启新对话，例如：

```text
/project-interview-skill 简称：电商；项目描述：......（背景/职责/难点/结果）；技术栈：Vue3、Pinia、Vite；求职方向：前端
```

随后在该业务项目根目录生成：

| 文件 | 用途 |
|------|------|
| `导学-{简称}.md` | 前置知识、必备知识点、推荐阅读（含仓库相对路径）、原理与设计决策；文末可含「量化与验证（含待测）」 |
| `面经-{简称}.md` | 1～2 句简历摘要、架构向 bullets、按简历支柱展开的面试题（主问/追问口播） |

也可以不写 slash 命令，直接描述“请基于这个项目生成导学和面经”。

## 源码安装兼容入口

`install.sh` 仍保留给 clone 仓库的用户使用，但它只是 Node CLI 的兼容包装器：

```bash
git clone https://github.com/Jaxon1216/interview-analyzer-skill.git
cd interview-analyzer-skill
./install.sh --trae
./install.sh --project --cursor
```

npm 包不会打包 `install.sh`；对普通用户优先推荐 `npx project-interview-skill ...`。

## 仓库结构

```text
interview-analyzer-skill/
|-- bin/
|   `-- project-interview-skill.js
|-- SKILL.md
|-- install.sh
|-- package.json
|-- README.md
|-- README_EN.md
|-- demo.jpg
|-- LICENSE
|-- references/
|   |-- interview-rubric.md
|   |-- star-framework.md
|   |-- output-templates.md
|   |-- oral-and-resume-patterns.md
|   |-- oral-style-samples.md
|   `-- excellent-resumes/
|-- scripts/
|   |-- check_inputs.py
|   `-- build_prompt.py
`-- tests/
```

## 维护与发布

本项目作为 npm CLI 包发布，不需要编译。npm 包会按 `package.json` 的 `files` 白名单打包：

```bash
npm pack --dry-run
npm publish --access public
```

本地验证：

```bash
npm test
npm run pack:check
node bin/project-interview-skill.js install --trae --dry-run
```

## 常见问题

### `.npmrc` 是必要的吗？

不是 npm 包必须文件。它只用于本仓库开发时指定 registry。真正发布到公网 npm 的关键配置是 `package.json` 里的 `publishConfig.registry`。

### 为什么默认安装到 `.agents/skills`？

这是最稳的用户级默认值，不依赖猜测用户正在使用哪个产品。如果你明确使用 Trae、Cursor、VS Code 或 Claude Code，使用对应参数即可。

### `install` 会自动探测产品吗？

不会。当前设计刻意收敛：默认只装到通用 `.agents/skills`，分产品安装必须显式指定 `--trae`、`--cursor`、`--vscode`、`--claude-code` 或 `--codex`。`doctor` 只展示路径，不安装。

### 更新后会自动生效吗？

不会。已安装目录是拷贝产物，需要重新执行安装命令：

```bash
npx project-interview-skill install --trae
```

## 反馈与支持

- 需求 / 建议 / 商用 / 二开：**jiangxu05@outlook.com**
- 欢迎 **Star**、**Fork** 按场景定制、**Issue / PR** 一起改进

## License

本项目采用 **MIT License**，完整条款见 **[LICENSE](LICENSE)**（英文正文 + 中文参考译文；若理解有出入，以英文为准）。
