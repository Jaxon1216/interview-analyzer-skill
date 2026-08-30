# README and Promo Documentation Design

## Goal

Improve the public-facing README so a first-time visitor can understand the value, see representative output, and install the package without reading a long maintenance document. Keep release slogans and campaign copy separate from the README.

## README Direction

Use the approved "results first" layout:

1. Project name and one-line positioning.
2. A compact list of core capabilities.
3. The primary `npx` install command.
4. The three generated-output screenshots:
   - resume bullets plus the prompt sidebar;
   - interview questions and spoken answers;
   - study order and recommended reading.
5. A short input/output example.
6. User-level and project-level installation details.
7. Supported agent targets, source-checkout compatibility, FAQ, support, and license.

The README should use short sections, compact tables only where they improve scanning, and the screenshots as the main visual break. Chinese and English versions must remain structurally aligned.

## Core Feature Language

Describe the product with verifiable capabilities:

- project-wide codebase scanning;
- resume bullet extraction;
- STAR-style spoken answers and follow-up questions;
- safeguards for internal terminology and external-facing explanations;
- frontend and backend reference examples;
- npm installation for Trae, Cursor, VS Code, Claude Code, and Codex.

Avoid claims about interview outcomes, guaranteed offers, or capabilities not present in the repository.

## Promo Record

Add `docs/promo.md` as an append-only, reverse-chronological record of public slogans. Each entry contains:

- release or campaign title;
- short slogan;
- core features;
- installation command;
- links or notes for the current output screenshots.

The first entry documents the current README refresh and npm installation. It may use the phrase "大酥化时代来临" and mention that a PR was submitted to `asu-skill` and merged. The copy should treat this as a light community joke and avoid repeating unverified claims about individuals or controversies.

## Files

- Update `README.md` and `README_EN.md` with the results-first structure and concise feature copy.
- Add `docs/promo.md`.
- Keep the existing screenshot assets under `docs/images/`.

## Validation

- Check Chinese and English README section parity.
- Check every local image and document link.
- Run `git diff --check`.
- Run `npm test`.
- Run `npm run pack:check` to ensure README assets remain in the package.
