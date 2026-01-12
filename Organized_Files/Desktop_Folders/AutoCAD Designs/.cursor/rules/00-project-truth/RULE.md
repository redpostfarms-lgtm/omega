---
rule_type: always
description: Persistent Brain Enforcement (Spiderweb Memory)
---

# Persistent Brain Rules (Always)

## Authority Order
1) MEMORY.md
2) WORKFLOW_STATE.md
3) This RULE.md

## Start-of-Task (Mandatory)
- Read MEMORY.md if present.
- Read WORKFLOW_STATE.md if present.
- Query MCP server "brain" for:
  - project identity & architecture
  - invariants / public API surface
  - prior decisions & gotchas
  - AutoCAD workflow constraints (if applicable)

## Allowed-File Gate
- Only edit files listed in WORKFLOW_STATE.md → Files in Play.
- If not listed, STOP and ask first.

## Editing Discipline
- Minimal diffs only.
- No refactors, renames, or formatting-only changes unless explicitly requested.
- Do not change public APIs unless explicitly instructed.
- Do not edit PROTECTED ZONES unless explicitly instructed.

## Before Editing
1) State intent
2) List files
3) Apply minimal diff
4) Provide verification plan

## End-of-Task (Mandatory Memory Write)
- Write to MCP "brain":
  - project
  - type: decision | constraint | architecture | gotcha | milestone
  - files changed + intent
  - decisions + why
  - new constraints
  - next steps
- Never store guesses as facts.

