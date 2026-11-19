# Backlog

Working list of bugs, fixes and ideas for BIM Nexus. Product direction lives in `Roadmap.md`; this file is the day-to-day list.

Format: `area | item | type (bug / small fix / feature / UI) | status (open / in progress / done)`

Small fixes go straight to Claude Code. Features and schema changes go through a superpowers spec, then a plan.

## Decisions

- 2026-11-19 Any list row that opens a detail page uses the shared `ClickableRow` (real link on the record number, whole row clickable, Enter key, clicks on controls inside ignored); names of products, units, suppliers, clients and records link to their pages wherever one exists. Why: only some lists linked anything, and consistency matters more than per-page choices.

## Items

- Inventory | example: describe the problem or idea here | bug | open
- UI | Records and references not clickable everywhere | UI | done
