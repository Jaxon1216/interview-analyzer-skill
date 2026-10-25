# VS Code installer implementation

Scope: only `bin/project-interview-skill.js` and new `tests/test_installer.py` in `/Users/eastonjiang/code/ideas/interview-analyzer-skill`. No commit was created. No actual user-level installation was run; all writing installation tests used a temporary project directory. The real HOME was not changed.

## Root cause and change

The VS Code branch previously wrote the expanded Skill body to its `.instructions.md` file without copying `references/` or `scripts/`. Those relative dependencies therefore could not resolve from the shared instructions directory.

The VS Code target now includes a companion Bundle in `.github/instructions/project-interview-skill/` for project installation and `.copilot/instructions/project-interview-skill/` for user installation. The `.instructions.md` file retains `applyTo: '**'` and becomes a thin relative Markdown link to the adjacent Bundle's `SKILL.md`, with an explicit statement that the Skill's relative paths resolve from its directory. Only the product-owned Bundle directory is replaced on reinstall. Shared sibling instructions and support directories remain intact. Both paths appear in install output, dry-run output, and doctor. `--path` still selects a standalone full Bundle, and other product adapters retain their existing behavior.

## Red evidence (before production change)

Command: `python3 -m unittest discover -s tests -p test_installer.py -v`

Result: exit 1, 8 tests, 5 failures and 3 passes.

- `test_vscode_project_entry_reaches_a_complete_adjacent_bundle`: expected a link to `SKILL.md`, found 0 links.
- `test_vscode_reinstall_refreshes_only_its_bundle_and_entry`: expected a link to `SKILL.md`, found 0 links.
- `test_all_project_targets_include_vscode_bundle_and_existing_adapters`: missing `.github/instructions/project-interview-skill/SKILL.md`.
- `test_vscode_project_dry_run_reports_entry_and_bundle_without_writing`: companion Bundle path was absent.
- `test_doctor_and_user_dry_run_report_vscode_companion_bundle`: user companion Bundle path was absent.

These failures were caused by the missing requested behavior, rather than fixture or command errors. Default project Bundle, custom standalone Bundle, and custom dry-run tests passed before the change.

## Green and full verification

- `python3 -m unittest discover -s tests -p test_installer.py -v`: exit 0, 8/8 pass.
- `npm test`: exit 0, 37/37 pass at this stage of the concurrent parent work.
- `node --check bin/project-interview-skill.js`: exit 0.
- `git diff --check -- bin/project-interview-skill.js tests/test_installer.py`: exit 0.

The tests run the actual Node CLI and inspect installed files. They resolve the actual thin-entry Markdown link, compare every published Bundle file against its source, traverse installed local Markdown links, verify `applyTo`, check repeat installation refresh and neighbor preservation, check both dry-run modes without writes, inspect user paths via read-only doctor/dry-run, preserve default/custom Bundle semantics, and cover all existing project product targets.

Independent read-only review found no blocker. Its suggested explicit relative-link assertion was added, and `npm test` was rerun successfully (37/37) together with the whitespace check. This prevents a future absolute entry link from passing merely because it currently resolves on the installing machine.

## Limits and self-review

No VS Code/Copilot runtime session was launched. File-level discovery, path resolution, and Bundle completeness are verified; model behavior after loading the instructions is outside these regression tests. User-level paths were checked without writing to the user's installation. No new dependency or package publishing rule was necessary because the existing Bundle copy and npm files entries already include `SKILL.md`, `references/`, and Python scripts.
