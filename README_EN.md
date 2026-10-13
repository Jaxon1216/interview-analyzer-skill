<div align="center">
  <h1>project-interview-skill</h1>
  <p><strong>Turn a real project into resume bullets, source-code lessons, and interview Q&amp;A.</strong></p>
  <p>Understand how the project works, then learn to explain its design.</p>
  <p>
    <a href="README.md">简体中文</a> ·
    <a href="https://www.npmjs.com/package/project-interview-skill">npm</a> ·
    <a href="LICENSE">MIT License</a>
  </p>
</div>

For developers who have a project and want to understand its core design and prepare for interviews. Give your Agent an accessible repository or project material. The skill investigates mechanisms, selects technical pillars, and connects each resume claim to questions, lessons, and source evidence.

Supports generic Agents, Codex, Claude Code, Cursor, Trae, and VS Code Copilot. The installer requires **Node.js 18+**; your Agent generates the content.

[Quick start](#quick-start) · [Output example](#output-example) · [Common requests](#common-requests) · [Install and update](#install-and-update) · [Accuracy and validation](#accuracy-and-validation)

## Quick start

**1. Install the published version**

```bash
npx project-interview-skill@latest install
```

The default location is `~/.agents/skills/project-interview-skill/`. Use the [product flags](#install-and-update) for another editor. For the current GitHub source, see [Install from source](#install-from-source).

**2. Open your project root, restart the Agent/editor, and start a new chat**

Copy this request and replace the short name and target role. The stack is identified from source.

```text
Use project-interview-skill to analyze the current repository.
Project short name: shop
Target role: backend engineering
Generate the study guide, all core source-code lessons, and interview Q&A under interview-prep/.
```

You can also invoke `/project-interview-skill` and append these details. If you only have a project description, paste it as the input.

**3. Start with the guide, study the mechanisms, then practice the Q&A**

Example layout for one project targeting backend engineering:

```text
interview-prep/
├── shop/
│   ├── 导学.md                 # Project map, study route, and navigation
│   └── 面经.md                 # Resume bullets, questions, and spoken answers
└── guide-backend/
    ├── 01-topic.md             # Complete core lessons
    └── 02-topic.md
```

| Output | What it contains | How to use it |
| --- | --- | --- |
| Study guide | Module responsibilities, representative flows, lesson prerequisites, and navigation | Build a project-wide view and choose a study order |
| Core lessons | Real source, runtime mechanisms, failure boundaries, what to understand and remember | Follow a scenario through code and explain the design |
| Interview guide | Project summary, technical pillars, resume triggers, primary questions, follow-ups, and first-person answers | Practice each claim with supporting explanations |

With no direction specified, the default is fullstack and lessons use `guide-fullstack/`; frontend requests use `guide-frontend/`. When several projects share an output root, lessons go under each `{short-name}/guide-{direction}/`. The first delivery expands all core lessons; optional topics expand on demand.

## Output example

This excerpt is from a **reviewed and revised DeerFlow source-based draft**. The [complete original output](docs/testing/samples/bullet-quality/deerflow-primary-revised.md) and [source evidence](docs/testing/samples/bullet-quality/deerflow-primary-evidence.md) are available in Chinese. The wording below is translated for this README.

> - **Progressive Skill loading and tool authorization:** Skills are directory packages containing SKILL.md. The default prompt provides metadata; explicit selection or read_file loads the body on demand, while session state retains lightweight references to loaded skills.
>   - An active skill's allowed-tools policy filters model-visible tools and blocks unauthorized calls at execution time.
> - **Context compaction and cross-session memory:** At the configured threshold, older history is summarized while recent messages are retained. History is replaced only after a summary is generated successfully; summaries, delegation records, and skill references are stored separately and injected into later model requests.
>   - Oversized tool results are written to files and represented by a synopsis and file reference; unavailable file persistence falls back to head-and-tail truncation.
>   - In passive memory mode, conversations are queued after execution. User identity is captured at enqueue time; background extraction updates durable memory, which later sessions load within user and Agent scopes.

Titles identify the design; the body explains responsibilities, collaboration, and conditions that change behavior. Important submechanisms can be expanded without forcing a benefit sentence. The project's actual responsibilities and mechanisms determine the pillars, titles, and count. Keep English when it improves recognition or precision; use natural Chinese where it communicates better.

A full delivery also connects the material for source-based revision:

```text
B1 Resume pillar
 └─ Q1 Primary question → Follow-ups based on preceding answers
     └─ C01 Core lesson → Source paths and key symbols
```

For a different domain, see the [EdgeMetric storage-engine first draft](docs/testing/samples/bullet-quality/edgemetric-first.md).

<details>
<summary>Historical interface screenshots: interview guide and study route</summary>

These screenshots show an earlier reading interface. Current wording and filenames follow the text examples and output contract above.

![Earlier resume bullets and Agent conversation](https://raw.githubusercontent.com/Jaxon1216/interview-analyzer-skill/main/docs/images/bullet-output.png)

![Earlier primary questions, follow-ups, and spoken answers](https://raw.githubusercontent.com/Jaxon1216/interview-analyzer-skill/main/docs/images/interview-questions.png)

![Earlier source-code study route](https://raw.githubusercontent.com/Jaxon1216/interview-analyzer-skill/main/docs/images/learning-path.png)

</details>

## Common requests

Use the quick-start request for a full delivery. Specify a narrower scope or an incremental update when needed.

| Need | Request to copy |
| --- | --- |
| Resume wording first | `Use project-interview-skill to analyze the entire current repository for a backend role. Generate only a project summary and resume bullets, with separate source evidence.` |
| One mechanism in depth | `Use project-interview-skill to expand only the context-compaction source-code lesson. Explain the flow, failure boundaries, what to understand, and what to remember.` |
| Actual contributions | `Use project-interview-skill to describe only my actual contributions. Scope: …; evidence: …; target role: ….` |
| Update existing docs | `Use project-interview-skill to update interview-prep/ against the latest source. Preserve my notes, unrelated sections, and existing B/Q/C IDs.` |

The default is **target-resume and learning mode**: implemented repository mechanisms may be selected for use after you understand them; commit authorship is not audited. For personal experience statements, explicitly request actual contributions and provide your participation scope.

## Install and update

The base command is `npx project-interview-skill@latest install`. Append a flag to select a product:

| Product | Flag | User-level location | Location with `--project` |
| --- | --- | --- | --- |
| Generic Agent / Codex | `--agents` or `--codex` | `~/.agents/skills/project-interview-skill/` | `.agents/skills/project-interview-skill/` |
| Claude Code | `--claude-code` | `~/.claude/skills/project-interview-skill/` | `.claude/skills/project-interview-skill/` |
| Cursor | `--cursor` | `~/.cursor/rules/project-interview-skill/` | `.cursor/rules/project-interview-skill/` |
| Trae | `--trae` | `~/.trae/skills/project-interview-skill/` | `.trae/rules/project-interview-skill/` |
| VS Code Copilot | `--vscode` | `~/.copilot/instructions/project-interview-skill.instructions.md` | `.github/instructions/project-interview-skill.instructions.md` |

Examples:

```bash
# User-level installation for Cursor
npx project-interview-skill@latest install --cursor

# Project-level installation: run from your application repository root
npx project-interview-skill@latest install --project --trae

# Preview the install location
npx project-interview-skill@latest install --trae --dry-run
```

`--project` uses the **current working directory** as the project root. Products are not auto-detected. `--all` installs all supported targets; `doctor` only displays paths.

**Update an installed skill** by repeating the original command with the same product flag and scope. For a user-level generic Agent / Codex installation:

```bash
npx project-interview-skill@latest install --agents
```

Installation replaces the selected Skill directory. Restart the Agent/editor and start a new chat afterward. Existing `interview-prep/` files change only when the skill is invoked again. Replace `@latest` with a specific npm version to pin a release.

### Install from source

Current GitHub source and the published npm version may differ. To install the repository's current content:

```bash
git clone https://github.com/Jaxon1216/interview-analyzer-skill.git
cd interview-analyzer-skill
./install.sh --agents
```

`install.sh` wraps the Node CLI and accepts the same installation flags; it is not included in the npm package. For an existing clone, update the source and reinstall.

You can also copy the complete `skill/project-interview-skill/` directory, containing `SKILL.md`, `references/`, and `scripts/`. Migrating the Skill does not require the CLI or test project.

## Accuracy and validation

Source supports technical facts. Historical evolution, personal ownership, and measured gains each need their own evidence. Unimplemented improvements remain separate; end a bullet when there is no supported additional effect.

Check the structure of a complete generated delivery with the following command, replacing the installation path as needed:

```bash
python3 ~/.agents/skills/project-interview-skill/scripts/validate_output.py interview-prep/shop/面经.md --guide interview-prep/shop/导学.md
```

The validator checks bullet format, B/Q/C links, core lesson sections, and local file links. **Pillar selection, factual accuracy, terminology, and final writing quality still require separate review.**

Development checks:

```bash
npm test
npm run pack:check
```

The [test guide](tests/README.md) covers automated regression and manual behavior evaluation. The [latest selection and writing record](docs/testing/2026-10-13-bullet-quality.md) preserves first drafts, revisions, and limitations: independent DeerFlow generation stopped at a usage limit, so the shown draft was generated and revised by the main agent; the cross-domain storage material completed one independent generation. Passing automated checks does not establish writing quality.

## Feedback and license

Report usage issues through [GitHub Issues](https://github.com/Jaxon1216/interview-analyzer-skill/issues), or contribute a PR. Contact: **jiangxu05@outlook.com**.

Licensed under the [MIT License](LICENSE). A Chinese reference translation is included; the English text controls.
