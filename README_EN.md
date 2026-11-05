# Project Interview Skill · Source code walkthroughs and interview prep

[简体中文](README.md) · **English** · [npm](https://www.npmjs.com/package/project-interview-skill) · [Preview a lesson and resume bullets](#deerflow-example)

Give your coding agent a project repository and a target role. It builds a linked study guide with source code lessons, resume bullets, and interview questions and answers, so you can trace each claim back to the code that supports it.

## Installation

Requires **Node.js 18+**. To make the skill available across projects in Codex or another agent that reads `.agents/skills/`, run this from any directory. The skill goes in `~/.agents/skills/project-interview-skill/`.

```bash
npx project-interview-skill@latest install
```

To install only for the current project, run this from its root. The skill goes in `.agents/skills/project-interview-skill/`.

```bash
npx project-interview-skill@latest install --project
```

<details>
<summary>Install for Claude Code, Cursor, Trae, or VS Code Copilot</summary>

Append the flag for your editor to either command above. Each parent directory below receives a `project-interview-skill/` bundle.

| Editor | Flag | User-wide parent directory | Project parent directory |
| --- | --- | --- | --- |
| Claude Code | `--claude-code` | `~/.claude/skills/` | `.claude/skills/` |
| Cursor | `--cursor` | `~/.cursor/rules/` | `.cursor/rules/` |
| Trae | `--trae` | `~/.trae/skills/` | `.trae/rules/` |
| VS Code Copilot | `--vscode` | `~/.copilot/instructions/` | `.github/instructions/` |

For VS Code Copilot, the installer also writes `project-interview-skill.instructions.md` next to the bundle.

</details>

Add `--dry-run` to preview the destination. To install from a source checkout, run `./install.sh` at the root of this repository. The script accepts the same flags. [Source installer](install.sh)

## Update to the latest version

Repeat the original install command with `@latest`, keeping the same scope and editor flag. This command updates a user-wide Codex installation.

```bash
npx project-interview-skill@latest install
```

For a project-only Claude Code installation, run this from the same project root.

```bash
npx project-interview-skill@latest install --project --claude-code
```

The installer replaces the installed skill directory. To refresh existing study notes, ask the agent to update the files in `interview-prep/` in a new chat.

## First run

After installation, restart your agent, open the project, and start a new chat. Copy this request and change the project name or target role as needed.

```text
Use project-interview-skill to help me prepare for a backend engineering interview.
Analyze the repository in this directory and use “shop” as the project name.
Write the study guide, all core source code lessons, resume bullets, and interview Q&A
to interview-prep/. Link the interview answers to the lessons and supporting code.
```

If you only have project materials, paste them into the chat. The agent identifies which details still need source verification. To describe your own contributions on a resume, give it your scope and supporting evidence, and ask it to cover only the work you did.

| Where to start | What you'll find |
| --- | --- |
| `interview-prep/shop/导学.md` | A project map and the order in which to read the lessons. |
| `interview-prep/guide-backend/` | Markdown lessons that follow a request through real code, including failure paths. |
| `interview-prep/guide-backend/topics/` | One to three offline HTML pages where changing a condition helps explain a mechanism. Agents that support delegation can assign one topic per subagent. If no topic fits, the Markdown lessons stand on their own. |
| `interview-prep/shop/面经.md` | Resume bullets, opening questions, follow-ups, and first-person answers linked back to the relevant lessons. |

<a name="deerflow-example"></a>

## DeerFlow sample lesson and resume bullets

One run on the DeerFlow repository produced eight source code lessons, two interactive HTML topics, and six resume bullets. Here are excerpts from the same run. The sample materials are in Chinese.

### An HTML lesson

What can a browser recover after it loses its connection to a running task? Switch between a cursor that is still in the event window and one that has expired. The lesson shows which events the server can replay and when the client needs to reload the thread.

![An excerpt from the DeerFlow HTML lesson on connection recovery, with the event window and replay cursor.](https://raw.githubusercontent.com/Jaxon1216/interview-analyzer-skill/main/docs/images/deerflow-course-preview.png)

[Download the offline HTML lesson](https://raw.githubusercontent.com/Jaxon1216/interview-analyzer-skill/main/docs/examples/deerflow/deerflow-c04.zip) · [Read the study guide](docs/examples/deerflow/导学.md). Unzip the download and open the HTML file in a browser to try the different cursors.

### Resume bullets

The same mechanism appears in the generated resume under “Stream replay and session recovery.” The image shows two bullets from the original Chinese output.

![Two DeerFlow resume bullets covering stream replay and session recovery, and concurrent artifact editing.](https://raw.githubusercontent.com/Jaxon1216/interview-analyzer-skill/main/docs/images/deerflow-resume-preview.png)

[Read and copy all six resume bullets](docs/examples/deerflow/resume-bullets.md)

[Evaluation record](docs/testing/2026-10-13-bullet-quality.md) · [Tests](tests/README.md) · [Report an issue](https://github.com/Jaxon1216/interview-analyzer-skill/issues) · [Email the maintainer](mailto:jiangxu05@outlook.com) · [MIT License](LICENSE)
