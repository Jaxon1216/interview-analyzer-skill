<div align="center">
  <h1>project-interview-skill</h1>
  <p><a href="https://github.com/Jaxon1216/interview-analyzer-skill/blob/main/README.md">简体中文</a></p>
  <p><em>Turn your project experience into interview-ready docs you can actually explain and defend.</em></p>
  <p>
    <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-yellow.svg"></a>
    <img alt="Type: Agent Skill" src="https://img.shields.io/badge/Type-Agent%20Skill-7c3aed">
    <img alt="Trae Compatible" src="https://img.shields.io/badge/Trae-Compatible-111827">
    <img alt="Cursor Compatible" src="https://img.shields.io/badge/Cursor-Compatible-00B8D9">
    <img alt="VS Code Compatible" src="https://img.shields.io/badge/VS%20Code-Compatible-007ACC?logo=visual-studio-code&logoColor=white">
    <img alt="Claude Code Compatible" src="https://img.shields.io/badge/Claude%20Code-Compatible-7c3aed">
    <img alt="Codex Compatible" src="https://img.shields.io/badge/Codex-Compatible-0A66C2">
  </p>
</div>

Turn a real codebase into interview material you can explain, defend, and study, written to the target project root.

## Core Capabilities

- Full-project scan: trace structure, entry points, and key modules into real technical pillars
- Resume bullets: turn code facts into reusable resume language
- STAR speaking answers: generate primary questions, follow-ups, and first-person responses
- Explanation guardrails: translate internal implementation terms into interviewer-friendly language
- Study path: prioritize concepts, source reading, and verification tasks
- Frontend and backend examples: provide reference templates for depth and phrasing

## Quick Start

```bash
npx project-interview-skill install
```

After installation, open the target project root in a new chat and enter:

```text
/project-interview-skill Short name: ecommerce; project description: ...; stack: Vue3, Pinia, Vite; target role: frontend
```

## Generated Output

Starting from one natural-language request, the Skill turns a codebase into three practical preparation views:

<p align="center">
  <img src="https://raw.githubusercontent.com/Jaxon1216/interview-analyzer-skill/main/docs/images/bullet-output.png" alt="Resume bullets and prompt sidebar" width="100%">
</p>

<table>
  <tr>
    <td width="50%" align="center"><strong>Interview guide: resume-driven questions</strong></td>
    <td width="50%" align="center"><strong>Study guide: an ordered learning path</strong></td>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/Jaxon1216/interview-analyzer-skill/main/docs/images/interview-questions.png" alt="Interview questions and spoken answers" width="100%"></td>
    <td><img src="https://raw.githubusercontent.com/Jaxon1216/interview-analyzer-skill/main/docs/images/learning-path.png" alt="Learning order and recommended reading" width="100%"></td>
  </tr>
</table>

## Install

The default target is the user-level generic Agent directory:

```text
~/.agents/skills/project-interview-skill/
```

If you know which editor or Agent you use, specify it explicitly:

| Target | User-level command | Install location |
|--------|--------------------|------------------|
| Generic Agent / Codex | `npx project-interview-skill install --agents` | `~/.agents/skills/project-interview-skill/` |
| Trae | `npx project-interview-skill install --trae` | `~/.trae/skills/project-interview-skill/` |
| Cursor | `npx project-interview-skill install --cursor` | `~/.cursor/rules/project-interview-skill/` |
| VS Code | `npx project-interview-skill install --vscode` | `~/.copilot/instructions/project-interview-skill.instructions.md` |
| Claude Code | `npx project-interview-skill install --claude-code` | `~/.claude/skills/project-interview-skill/` |
| Codex | `npx project-interview-skill install --codex` | `~/.agents/skills/project-interview-skill/` |

Install every supported target:

```bash
npx project-interview-skill install --all
```

Preview paths without writing files:

```bash
npx project-interview-skill install --trae --dry-run
npx project-interview-skill doctor
```

## Project-Level Install

To install the skill only for one application repository, run the command from that repository root:

```bash
cd /path/to/your-project
npx project-interview-skill install --project --trae
```

Supported project-level targets:

| Target | Project-level command | Install location |
|--------|-----------------------|------------------|
| Generic Agent / Codex | `npx project-interview-skill install --project --agents` | `.agents/skills/project-interview-skill/` |
| Trae | `npx project-interview-skill install --project --trae` | `.trae/rules/project-interview-skill/` |
| Cursor | `npx project-interview-skill install --project --cursor` | `.cursor/rules/project-interview-skill/` |
| VS Code | `npx project-interview-skill install --project --vscode` | `.github/instructions/project-interview-skill.instructions.md` |
| Claude Code | `npx project-interview-skill install --project --claude-code` | `.claude/skills/project-interview-skill/` |
| Codex | `npx project-interview-skill install --project --codex` | `.agents/skills/project-interview-skill/` |

Restart the target IDE or Agent after installation.

## Usage

The skill creates these files under the target project root:

| File | Purpose |
|------|---------|
| `导学-{short-name}.md` | Prerequisites, key concepts, repo-relative reading guide, design decisions, and optional measurement notes |
| `面经-{short-name}.md` | 1-2 sentence resume summary, architecture-level bullets, and interview Q&A mapped to those bullets |

You can also invoke it naturally by asking for project interview preparation docs.

## Source Checkout Compatibility

`install.sh` is kept for users who clone the repository. It is only a wrapper around the Node CLI:

```bash
git clone https://github.com/Jaxon1216/interview-analyzer-skill.git
cd interview-analyzer-skill
./install.sh --trae
./install.sh --project --cursor
```

The npm package does not include `install.sh`; regular users should prefer `npx project-interview-skill ...`.

## Standalone Skill Bundle

The repository root contains the npm CLI and development files. The independently portable Skill bundle is:

```text
skill/project-interview-skill/
├── SKILL.md
├── references/
└── scripts/
```

Copy this directory to migrate the Skill; `bin/`, `tests/`, and `package.json` are not required. The npm CLI also builds installed targets from this directory only.

## Repository Structure

```text
interview-analyzer-skill/
|-- skill/
|   `-- project-interview-skill/
|       |-- SKILL.md
|       |-- references/
|       |   |-- rules/
|       |   |-- templates/
|       |   |-- examples/
|       |   `-- excellent-resumes/
|       `-- scripts/
|-- bin/
|   `-- project-interview-skill.js
|-- install.sh
|-- package.json
|-- .npmrc
|-- README.md
|-- README_EN.md
|-- docs/
|   |-- images/
|   `-- promo.md
|-- LICENSE
`-- tests/
```

## FAQ

### Why does the default install target `.agents/skills`?

It is the least surprising user-level default and avoids guessing which product the user wants. Use an explicit flag for Trae, Cursor, VS Code, Claude Code, or Codex.

### Does `install` auto-detect products?

No. The behavior is intentionally narrow: the default installs only to `.agents/skills`, product-specific installs require `--trae`, `--cursor`, `--vscode`, `--claude-code`, or `--codex`. `doctor` only prints paths.

### Do updates apply automatically?

No. Installed skill folders are copied artifacts. Re-run the install command:

```bash
npx project-interview-skill install --trae
```

## Support

- **Contact** (feedback, commercial use, derivatives): **jiangxu05@outlook.com**
- **Star**, **Fork**, **Issues / PRs** are welcome.

## License

Licensed under the **[MIT License](LICENSE)**. The file includes the English legal text plus an unofficial Chinese translation for convenience; if they disagree, the English section controls.
