<div align="center">
  <h1>project-interview-skill</h1>
  <p><a href="https://github.com/Jaxon1216/interview-analyzer-skill/blob/main/README.md">简体中文</a></p>
  <p><em>Turn your project experience into interview-ready docs you can actually explain and defend.</em></p>
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

Generate two practical interview-prep docs from a real codebase, written to the target project root:

- `导学-{short-name}.md`: key highlights, code-reading path, and study checklist
- `面经-{short-name}.md`: resume-ready summary plus first-person STAR speaking answers

## Demo

This merged screenshot shows both trigger input and interview output:

![Demo](https://raw.githubusercontent.com/Jaxon1216/interview-analyzer-skill/main/demo.jpg)

## Install

Use `npx`; cloning is not required:

```bash
npx project-interview-skill install
```

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

Open the target project root in your IDE or Agent, then start a new chat:

```text
/project-interview-skill 简称：电商；项目描述：...；技术栈：Vue3、Pinia、Vite；求职方向：前端
```

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

## Repository Structure

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

## Maintenance and Publishing

This npm CLI package does not need a build step. The package contents are controlled by the `files` allowlist in `package.json`:

```bash
npm pack --dry-run
npm publish --access public
```

Local checks:

```bash
npm test
npm run pack:check
node bin/project-interview-skill.js install --trae --dry-run
```

## FAQ

### Is `.npmrc` required?

No. It is only useful for this repository's development registry selection. Public npm publishing is controlled by `publishConfig.registry` in `package.json`.

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
