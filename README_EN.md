<div align="center">
  <h1>interview-analyzer-skill</h1>
  <p><a href="README.md">简体中文</a></p>
  <p><em>Turn your project experience into interview-ready docs you can actually explain and defend.</em></p>
  <p>
    <a href="SKILL.md"><img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-yellow.svg"></a>
    <img alt="Type: Agent Skill" src="https://img.shields.io/badge/Type-Agent%20Skill-7c3aed">
    <img alt="Cursor Compatible" src="https://img.shields.io/badge/Cursor-Compatible-00B8D9">
    <img alt="VS Code Compatible" src="https://img.shields.io/badge/VS%20Code-Compatible-007ACC?logo=visual-studio-code&logoColor=white">
    <img alt="Copilot Compatible" src="https://img.shields.io/badge/Copilot-Compatible-222222?logo=githubcopilot&logoColor=white">
    <img alt="Codex Compatible" src="https://img.shields.io/badge/Codex-Compatible-0A66C2">
  </p>
</div>

Generate two practical interview-prep docs from a real codebase (written to your target project root):

- `导学-{short-name}.md`: key highlights, code-reading path, and study checklist
- `面经-{short-name}.md`: resume-ready summary + STAR speaking answers

## Demo

This merged screenshot shows both trigger input and interview output:

![Demo](demo.jpg)

## Outputs

| File | Purpose |
|------|---------|
| `导学-{short-name}.md` | Prerequisites, key highlights, reading order, repo paths, design decisions, optional measurement suggestions |
| `面经-{short-name}.md` | 1-2 sentence resume summary, project bullets, and 15-25 interview questions |

## Quick Start

### Installation mode

Current installation mode is **clone + install.sh** (not `npx`).

### 1) Clone

```bash
git clone https://github.com/Jaxon1216/interview-analyzer-skill.git
cd interview-analyzer-skill
chmod +x install.sh
```

### 2) Install skill

Run location matters:

- User-level install (global): run inside this `interview-analyzer-skill` repository.
- Project-level install (current project only): `cd` into your target project root first.

Auto-detect platform:

```bash
./install.sh
```

Common explicit installs:

```bash
./install.sh --platform cursor
./install.sh --platform cursor --project
./install.sh --platform copilot --project
./install.sh --platform codex --project
```

Install into a target project explicitly:

```bash
cd /path/to/your-project
/path/to/interview-analyzer-skill/install.sh --platform cursor --project
```

Need all options?

```bash
./install.sh --help
```

Supported `--platform` values:

`claude-code`, `copilot`, `cursor`, `windsurf`, `cline`, `codex`, `gemini`, `kiro`, `trae`, `goose`, `opencode`, `roo-code`, `antigravity`, `universal`

### 3) Trigger in your target project

```text
/interview-analyzer-skill 简称：电商；项目描述：...；技术栈：Vue3、Pinia、Vite；求职方向：前端
```

The skill writes output files to the target project's root.

## Repository Structure

```text
interview-analyzer-skill/
|-- SKILL.md
|-- install.sh
|-- README.md
|-- README_EN.md
|-- demo.jpg
|-- references/
|   |-- interview-rubric.md
|   |-- star-framework.md
|   |-- output-templates.md
|   `-- oral-and-resume-patterns.md
`-- scripts/
    |-- check_inputs.py
    `-- build_prompt.py
```

## Upgrade

Installed skill folders are copied artifacts and do not auto-update.

```bash
git pull
./install.sh --platform <your-platform> [--project]
```

## Support

If this project helps you, feel free to:

- Star the repo
- Fork and customize for your own interview workflow
- Open Issues / PRs to improve it together

## License

MIT
