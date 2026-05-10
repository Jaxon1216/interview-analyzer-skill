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

Generate two practical interview-prep docs from a real codebase (written to your **target project root**):

- `导学-{short-name}.md`: key highlights, code-reading path, and study checklist
- `面经-{short-name}.md`: resume-ready summary + STAR speaking answers

## Demo

This merged screenshot shows both trigger input and interview output:

![Demo](demo.jpg)

## Outputs

| File | Purpose |
|------|---------|
| `导学-{short-name}.md` | Prerequisites, checklist, reading guide (repo-relative paths), design decisions; optional end section **「量化与验证（含待测）」** (recommended; see [SKILL.md](SKILL.md)) |
| `面经-{short-name}.md` | 1–2 sentence resume summary, project bullets, 15–25 interview questions; **no mandatory** separate measurement section |

## Quick Start

Installation is **clone + install.sh** (not `npx`).

### Two things to understand first

1. **Where the skill is installed**: `install.sh` **copies** this repo into your tool’s convention folder (e.g. `~/.cursor/rules/` or `./.cursor/rules/` in one project). The agent loads rules from **that** path.
2. **Where the two Markdown files are written**: Depends on **which folder you open** in the IDE. Open your **application project root**, trigger the skill, and `导学-*.md` / `面经-*.md` appear in **that project’s root**. This is **not** the same path as the skill install.

### 1) Clone

```bash
git clone https://github.com/Jaxon1216/interview-analyzer-skill.git
cd interview-analyzer-skill
chmod +x install.sh
```

### 2) Install: pick a row, then run the command

**Check “current working directory” carefully.** User-level installs usually run `./install.sh` from the **cloned skill repo root**. Project-only installs run from the **application project root** using the **absolute path** to this repo’s `install.sh`.

| Scenario | Run from | Command | Typical skill location after install |
|----------|----------|---------|--------------------------------------|
| Cursor, all projects | **Skill repo root** | `./install.sh --platform cursor` | `~/.cursor/rules/interview-analyzer-skill/` with `SKILL.md` and `interview-analyzer-skill.mdc` |
| Cursor, **one** app only | **App project root** | `/path/to/interview-analyzer-skill/install.sh --platform cursor --project` | `your-app/.cursor/rules/interview-analyzer-skill/` (includes `.mdc`) |
| VS Code + Copilot, project only | **App project root** | `/path/to/interview-analyzer-skill/install.sh --platform copilot --project` | `your-app/.github/skills/interview-analyzer-skill/` |
| Codex / `.agents/skills` tools | **App project root** | `/path/to/interview-analyzer-skill/install.sh --platform codex --project` | `your-app/.agents/skills/interview-analyzer-skill/` |

Replace `/path/to/interview-analyzer-skill` with your local clone path.

**Auto-detect (optional)**: from the **skill repo root**, run `./install.sh` with no args. The script guesses the platform from folders on your machine (e.g. `~/.cursor` → Cursor). If you use **multiple** tools, pass **`--platform` explicitly**.

More flags:

```bash
./install.sh --help
```

Supported `--platform` values (see `--help` for full list): `claude-code`, `copilot`, `cursor`, `windsurf`, `cline`, `codex`, `gemini`, `kiro`, `trae`, `goose`, `opencode`, `roo-code`, `antigravity`, `universal`

### 3) Verify the install

- Open the **“Typical skill location”** folder from the table: you should see **`SKILL.md`**; with Cursor you should also see **`interview-analyzer-skill.mdc`**.
- **Behavior check**: open your **app project root** in the IDE, start a **new** chat, and send `/interview-analyzer-skill` (or ask for 导学/面经). When the rule loads, the agent should write two `.md` files to the **app root** per [SKILL.md](SKILL.md), or paste two Markdown blocks if the environment cannot write files.

### Optional: preview without writing

From **app project root**:

```bash
cd /path/to/your-project
/path/to/interview-analyzer-skill/install.sh --platform cursor --project --dry-run
```

Review the printed paths, then rerun without `--dry-run`.

### 4) Trigger in the app project

```text
/interview-analyzer-skill 简称：电商；项目描述：...；技术栈：Vue3、Pinia、Vite；求职方向：前端
```

Files such as `导学-电商.md` and `面经-电商.md` are created under **that app’s root** (short name as you provide).

## Repository Structure

```text
interview-analyzer-skill/
|-- SKILL.md
|-- install.sh
|-- README.md
|-- README_EN.md
|-- demo.jpg
|-- donate.jpg
|-- LICENSE
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
cd interview-analyzer-skill
git pull
./install.sh --platform <your-platform> [--project]
```

## FAQ

### How detailed should the input be?

Include at least: background, your role, one hard problem, and outcome. More detail yields better questions.

### Which doc should I read first?

`导学` for the learning path, then `面经` for spoken answers and follow-ups.

### Is the measurement section mandatory?

No. Same as [SKILL.md](SKILL.md): **导学** may end with 「量化与验证（含待测）」 as a **recommendation**; **面经** does not require a separate measurement section.

### Do updates apply automatically?

No. `git pull` and run `install.sh` again.

## Support

If this project helps you:

- **buy me a coffee** (WeChat): scan the QR below—any amount is appreciated.

![WeChat tip QR](donate.jpg)

- **Contact** (feedback, commercial use, derivatives): **jiangxu05@outlook.com**
- **Star**, **Fork**, **Issues / PRs** are welcome.

## License

Licensed under the **[MIT License](LICENSE)**. The file includes the **English legal text** plus an **unofficial Chinese translation** for convenience; if they disagree, the **English** section controls.

When you redistribute (including commercial use or forks): **keep** the copyright and license notices, and **credit the source** (e.g. link to this repo).
