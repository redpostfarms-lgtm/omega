# MEMORY.md — Project Truth (READ FIRST)

You are Cursor AI working inside THIS repository. This file is the source of truth.
Before answering, editing, refactoring, generating new files, or running commands:
1) Read this entire file.
2) Read `WORKFLOW_STATE.md` for current task context.
3) Follow the rules exactly.
4) If anything conflicts, MEMORY.md wins.

---

## Project Identity
- Project name: <PROJECT_NAME>
- Goal: <ONE_SENTENCE_GOAL>
- Non-goals: <WHAT_WE_ARE_NOT_DOING>

## Current State
- Status: <active / paused / broken / needs refactor>
- What works:
  - <bullets>
- What is broken / risky:
  - <bullets>

## Architecture (Short)
- Entry points:
  - <paths>
- Key modules:
  - <paths + what they do>
- Data flow:
  - <1–3 bullets>
- External dependencies:
  - <APIs, DBs, services>

## Operating Rules (Hard Constraints)
- Do NOT delete files unless explicitly instructed.
- Do NOT rename public functions, routes, CLI commands, or exported APIs unless explicitly instructed.
- Do NOT rewrite large sections "for style" or "cleanup".
- Prefer minimal diffs. Target the smallest change that solves the problem.
- If you must change behavior, explain why and list side effects.

## Session Start Protocol
**At the start of every new Cursor session, use this prompt:**

```text
Read MEMORY.md and WORKFLOW_STATE.md. 
Summarize: (1) project goal, (2) current task, (3) files allowed to edit.
Do not propose code changes yet.
```text

**If Cursor summarizes wrong → fix MEMORY/WORKFLOW immediately.**
**If it summarizes right → proceed.**

## Violation Response
If Cursor edits outside Files in Play: "Stop. Revert. Propose plan first."
If Cursor refactors: "Not requested. Minimal diff only. Revert."
If Cursor renames public API: "Disallowed. Revert and patch locally."
If Cursor touches Protected Zone: "Disallowed unless asked. Revert."

## Coding Standards (Repo-Specific)
- Language/runtime: <e.g., Node 20 / Python 3.11>
- Formatting: <prettier/black/etc>
- Linting: <eslint/ruff/etc>
- Test command: <command>
- Build command: <command>
- Run command: <command>

## Verification Commands
- Test command: `<command>`
- Lint command: `<command>`
- Typecheck command: `<command>`
- Done means: tests pass + no new warnings + minimal diff

## Change Protocol (MANDATORY)
When making changes:
1) State the intent in 1 sentence.
2) List the files you will change (exact paths).
3) Make the change with minimal diff.
4) Provide a brief verification plan (how we'd confirm it works).
If you are missing info, ask BEFORE changing files.

## "Never Do" List
- Never remove error handling to "simplify".
- Never replace working code with stubs/placeholders.
- Never change config defaults silently.
- Never introduce new frameworks without permission.
- Never edit generated files unless explicitly told.
- Never edit protected zones (marked with `// === CURSOR: PROTECTED ZONE ===`) unless explicitly asked.
- Never change formatting/whitespace unless required for the requested change.

**Protected Zones Usage:** Only mark 3–10 critical places max (config loaders, auth logic, serialization formats, protocol parsers, DB schema/migrations, payment/VA/USDA logic). Overuse reduces effectiveness.

## Work Log (Keep Recent Only)
- Last successful milestone:
  - <date> — <what>
- Last changes made:
  - <date> — <summary>
- Next 3 tasks:
  1) <task>
  2) <task>
  3) <task>

## Glossary (Project Terms)
- <term>: <meaning>

