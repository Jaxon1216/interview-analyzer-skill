# interview-analyzer-skill

[English](README_EN.md)

把真实项目快速整理成两份可直接用于面试准备的文档（生成在工作区根目录）：

- `导学-{简称}.md`：重点亮点、代码阅读路径、学习顺序与必备知识点
- `面经-{简称}.md`：简历可用摘要 + 面试题口播（第一人称 STAR）

本 skill 面向工程化面试场景，强调“可落地、可追问、可复述”。

## 效果演示（3 步）

### 1）触发

在对话中输入 `/interview-analyzer-skill`，并提供简称 + 项目描述。

![触发示例](image/trigger.png)

### 2）导学结果

生成导学文档：告诉你“先学什么、先看哪些文件、为什么重要”。

![导学示例](image/guidance.png)

### 3）面经结果

生成面经文档：聚焦面试题与第一人称口播答案。

![面经示例](image/interviewBible.png)

## 输出文件

| 文件 | 用途 |
|------|------|
| `导学-{简称}.md` | 前置知识、重点亮点与学习顺序、推荐阅读（含仓库相对路径）、关键设计决策、可选量化建议 |
| `面经-{简称}.md` | 1～2 句简历摘要、项目 bullets、15～25 道面试题（主问/追问口播） |

## 快速开始

### 1）克隆仓库

```bash
git clone https://github.com/Jaxon1216/interview-analyzer-skill.git
cd interview-analyzer-skill
chmod +x install.sh
```

### 2）安装 skill

自动探测平台：

```bash
./install.sh
```

常见显式安装：

```bash
./install.sh --platform cursor
./install.sh --platform cursor --project
./install.sh --platform copilot --project
./install.sh --platform codex --project
```

### 3）在目标项目里使用

在“被分析项目”的工作区开启新对话，输入：

```text
/interview-analyzer-skill 简称：电商；项目描述：......（背景/职责/难点/结果）；技术栈：Vue3、Pinia、Vite；求职方向：前端
```

随后会在目标项目根目录生成结果文件。

## 仓库结构

- `SKILL.md`：技能协议与输出约束
- `references/`：面试 rubric、STAR 规范、输出模板
- `scripts/`：输入校验与提示词构建脚本
- `install.sh`：跨平台安装脚本
- `image/`：README 演示截图

## 升级说明

已安装目录是“拷贝产物”，不会随 GitHub 自动更新。

升级方式：

```bash
cd interview-analyzer-skill
git pull
./install.sh --platform <你的平台> [--project]
```

## 常见问题

### 必须上传整个仓库吗？

是。`SKILL.md`、`references/`、`scripts/`、`install.sh` 需要一起分发。

### 量化与验证是强制的吗？

不是。当前规则里它是导学中的可选建议项，面经不强制独立量化章节。

### 支持 VS Code 系工具吗？

支持。可根据环境选择 `--platform copilot`、`--platform cline`、`--platform roo-code` 等。

## License

MIT
