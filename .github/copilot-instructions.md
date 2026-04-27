# Copilot Instructions

## Single Source of Truth

`AGENTS.md` defines all conventions, structure, and workflows. **Read it at the start of every session.**

## Project Type

This is the **SkillForge** framework — a self-evolving skill synthesis system for AI agents. The codebase lives in `src/skillforge/` with Python modules, tests in `tests/`, and a persistent wiki in `wiki/`.

## Key Files

- `AGENTS.md` — Schema, conventions, workflows. The single source of truth.
- `wiki/index.md` — Master catalog of all wiki pages.
- `wiki/log.md` — Chronological operation log.
- `wiki/overview.md` — High-level synthesis of the system.

---

## Mandatory Post-Change Pipeline

**Every time any code or wiki change is made — without exception — execute all 4 steps before declaring the task complete.**

1. **Update the Wiki** — module pages, architecture, decisions, log.md, index.md
2. **Sync Gate** — Code-Wiki Mapping Table + bidirectional verification (Workflow 7)
3. **Run Tests** — `pytest tests/`; fix code on failure before proceeding
4. **Update README.md** — if architecture, API surface, or setup changed

---

## Core Rules

1. **Never modify files in `raw/`.** Sources are immutable.
2. **Always update `wiki/index.md` and `wiki/log.md`** after any wiki operation.
3. **Use YAML frontmatter** on every wiki page (see AGENTS.md for format).
4. **Use `[[wikilinks]]`** for cross-references between wiki pages.
5. **Flag contradictions** with `> [!contradiction]` callouts — never silently overwrite.
6. **Flag breaking changes** with `> [!breaking]` callouts on affected pages.
7. **New modules** → register in `wiki/modules/` and update architecture pages.
8. **Non-trivial design choices** → record in `wiki/decisions/` as an ADR.
9. **Sync Gate is mandatory** after every code change (Workflow 7).
10. **Spec-vs-code divergences** → log in `wiki/deviations.md` and add `> [!note] Deviation:` callouts on affected pages.

---

## Workflow Quick Reference

| Workflow | Trigger | Action |
|----------|---------|--------|
| **Ingest** | File added to `raw/` | Read → discuss → create/update wiki pages |
| **Query** | Question about content | Read `wiki/index.md` → find pages → synthesize answer |
| **Lint** | Health check request | Scan for orphans, broken links, stale claims → report → fix with approval |
| **Analysis** | Comparison or deep-dive | Gather pages → generate `wiki/analyses/` page → update index |
| **Brownfield** | Existing codebase audit | Run lint → back-fill wiki → baseline deviations |
