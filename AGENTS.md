# SkillForge — AI Development Framework Schema

This file defines conventions, structure, and workflows for the AI development agent.
Read this file at the start of every session.

---

## Purpose

This framework provides **persistent context** for AI-assisted development of SkillForge. It combines:
- **Knowledge management** — ingest documents, research, and references into a structured wiki.
- **Codebase awareness** — track architecture decisions, module contracts, conventions, and change history so the AI never loses context as the project grows.

**Before** any code or document operation, the AI reads the wiki to stay consistent.
**After** any operation, the AI updates the wiki to preserve context for future sessions.

---

## Terminology

- **Workflows** (1–9) — operational procedures for managing knowledge and code. Defined in this file.
- **Post-Change Pipeline** — the mandatory 4-step sequence (wiki → sync gate → tests → README) that runs after every code change.
- **Sync Gate** — Workflow 7: bidirectional code↔wiki verification with a Code-Wiki Mapping Table.
- **Brownfield** — adoption of the framework on an already-running codebase (Workflow 9).

---

## Directory Structure

```
raw/                  # Immutable source documents (articles, papers, specs, data)
wiki/                 # AI-maintained pages — never edit manually
  sources/            # One summary page per ingested document
  entities/           # People, orgs, products, tools, services
  concepts/           # Ideas, frameworks, patterns, theories
  analyses/           # Comparisons, syntheses, research outputs
  architecture/       # System design, component maps, data flows
  decisions/          # Architecture Decision Records (ADRs)
  conventions/        # Coding standards, naming rules, project patterns
  modules/            # One page per module/component/service
  deviations.md       # Audit trail of spec-vs-code divergences
  index.md            # Master catalog of all wiki pages
  log.md              # Chronological record of all operations
  overview.md         # High-level synthesis (knowledge + system state)
src/                  # Source code
  skillforge/         # Main package
    core/             # Core domain: forge, evolution, generator, skill bank, verifier
    memory/           # Tiered memory system
    evaluation/       # Benchmarking, simulation, metrics
    agentic/          # Agent provider, tools, events
    integrations/     # API server, LLM middleware, agent adapter
tests/                # Test suite
AGENTS.md             # This file — schema and conventions
```

---

## Page Conventions

### Frontmatter

Every wiki page must start with YAML frontmatter:

```yaml
---
title: "Page Title"
type: source | entity | concept | analysis | architecture | decision | convention | module | overview
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [tag1, tag2]
sources: []           # raw documents this page draws from
related: []           # related wiki pages (wikilink targets)
source_paths: []      # optional — repo-relative code paths this page documents
status: active | draft | deprecated | superseded | spec | verified
---
```

> `source_paths` is optional but strongly recommended on `module`, `architecture`, and `convention`
> pages. It lets the validator flag wiki pages whose underlying code has been removed, so
> documentation does not silently drift out of sync with the codebase.

### Content Format

- Use standard markdown with `[[wikilinks]]` for cross-references between wiki pages.
- Use `> [!note]` callouts for editorial commentary or open questions.
- Use `> [!contradiction]` callouts when new data conflicts with existing claims.
- Use `> [!breaking]` callouts when a change breaks existing contracts or conventions.
- Headings: `##` for major sections, `###` for subsections. Reserve `#` for the page title only.
- Keep paragraphs concise — prefer bullet points for factual claims.
- Cite sources inline: `(Source: [[source-page-name]])`.

### Naming

- Filenames: lowercase, hyphenated. E.g. `machine-learning.md`, `user-auth-service.md`.
- Source pages: named after the source document.
- Entity pages: named after the entity.
- Module pages: named after the module/component.
- Decision pages: numbered. E.g. `adr-001-use-dataclasses.md`.
- Convention pages: named by topic. E.g. `error-handling.md`, `naming-conventions.md`.

---

## Workflows

### Knowledge Workflows

#### 1. Ingest a Source

When the user adds a new file to `raw/` and asks to ingest it:

1. **Read** the source document in full.
2. **Discuss** key takeaways with the user (3–5 bullet points). Wait for confirmation before proceeding.
3. **Create** a source summary page in `wiki/sources/`.
   - Include: title, author, date, key claims, notable quotes, relevance to existing wiki.
4. **Update** existing pages:
   - Add/revise relevant entity pages in `wiki/entities/`.
   - Add/revise relevant concept pages in `wiki/concepts/`.
   - Flag contradictions with `> [!contradiction]` callouts on affected pages.
   - Add `[[wikilinks]]` cross-references on all touched pages.
5. **Update** `wiki/index.md` — add entries for any new pages, update summaries for modified pages.
6. **Update** `wiki/overview.md` if the source materially changes the high-level synthesis.
7. **Append** to `wiki/log.md`.

#### 2. Query the Wiki

When the user asks a question:

1. **Read** `wiki/index.md` to identify relevant pages.
2. **Read** the relevant pages.
3. **Synthesize** an answer with inline citations: `(Source: [[page-name]])`.
4. **Offer** to file the answer as a new analysis page in `wiki/analyses/` if it's substantive.

#### 3. Create Analysis

When the user asks for a comparison, synthesis, or deep-dive:

1. **Gather** relevant wiki pages.
2. **Generate** the analysis as a new page in `wiki/analyses/`.
3. **Cross-reference** the analysis from relevant entity/concept pages.
4. **Update** `wiki/index.md`.
5. **Append** to `wiki/log.md`.

### Code Workflows

#### 4. Before Any Code Change

Before writing, modifying, or deleting code:

1. **Read** `wiki/index.md` to locate relevant module, architecture, decision, and convention pages.
2. **Read** the relevant pages to understand:
   - Existing patterns and conventions (`wiki/conventions/`).
   - Module contracts and dependencies (`wiki/modules/`).
   - Architecture constraints and data flows (`wiki/architecture/`).
   - Past decisions and their rationale (`wiki/decisions/`).
3. **Follow** established patterns. If the change conflicts with existing conventions, flag it to the user before proceeding.
4. **Apply Coding Discipline P1 — Think Before Coding** (see Guiding Principles). Name the interpretation you're acting on, state assumptions explicitly, and ask for clarification rather than guessing.

#### 5. After Any Code Change

After completing a code create/update/delete operation:

1. **Update module pages** (`wiki/modules/`) — reflect new exports, changed interfaces, added/removed dependencies.
2. **Update architecture pages** (`wiki/architecture/`) — if the change affects system design, data flows, or component relationships.
3. **Update convention pages** (`wiki/conventions/`) — if a new pattern was introduced or an existing one was modified.
4. **Create a decision record** (`wiki/decisions/`) — if the change involved a non-trivial architectural or design choice.
5. **Flag contradictions** — if the change conflicts with documented patterns, add `> [!breaking]` callouts on affected pages.
6. **Update** `wiki/index.md` for any new or modified pages.
7. **Append** to `wiki/log.md`.
8. **Run the Sync Gate** (Workflow 7) before marking the change complete.

#### 6. Register a Module

When a new module, component, or service is created:

1. **Create** a module page in `wiki/modules/` with:
   - Purpose and responsibility.
   - Public interface (exports, APIs, events).
   - Dependencies (what it imports/consumes).
   - Dependents (what depends on it) — update those module pages too.
   - Key design decisions and constraints.
2. **Update** `wiki/architecture/` pages to show the new component in the system.
3. **Cross-reference** from relevant concept and entity pages.
4. **Update** `wiki/index.md`.
5. **Append** to `wiki/log.md`.

### Development Discipline Protocols

#### Post-Change Pipeline (mandatory after every code change)

After completing any code create/update/delete, execute all 4 steps in order.
No step may be skipped, even for "small" changes.

> Apply the **Coding Discipline** principles throughout (see Guiding Principles).

**Step 1 — Update the Wiki**
- Update every affected module page in `wiki/modules/`.
- Update `wiki/architecture/` if system design or data flows changed.
- Create an ADR in `wiki/decisions/` for any non-trivial design choice.
- Add `> [!breaking]` callouts on pages affected by breaking changes.
- Always append to `wiki/log.md`. Always update `wiki/index.md`.

**Step 2 — Sync Gate**
Run Workflow 7. Both passes must succeed before proceeding.

**Step 3 — Run Tests**
- Run the project's full test suite (`pytest tests/`).
- Report pass/fail. On failure, fix code (not tests) and re-run before continuing.

**Step 4 — Update README.md**
- If the change affects the architecture diagram, Quick Start steps, API surface,
  environment variables, or configuration — update `README.md` accordingly.

#### Dependency Impact Protocol

When modifying any module:
1. Search for all importers of that module.
2. Check if the public interface changed (signatures, return shapes, exports).
3. If yes — update every caller and their wiki module pages.
4. If a breaking change — add `> [!breaking]` callouts on all affected wiki pages.

#### Configuration Change Protocol

When project configuration files change (model config, environment variables, API keys):
1. Update every wiki page that names or describes the changed values.
2. Propagate to architecture pages, module pages, and README where applicable.
3. Register any spec-vs-code gap in `wiki/deviations.md`.

### Maintenance Workflows

#### 7. Sync Gate (Bidirectional Verification)

Required after every code change, before marking the change complete. This ensures code and wiki stay in sync in **both directions**.

##### Step 1 — Code-Wiki Mapping Table

Output a visible table listing every file touched:

```markdown
| Change | Type | Wiki Page Updated | Verified |
|--------|------|-------------------|----------|
| (every file created/modified/deleted) | create/modify/delete | (wiki page) | ✅/❌ |
```

Rules:
- Every row must map to a wiki page. If none exists, create one or update an existing one.
- The table must be shown to the user. Do not skip it.

##### Step 2 — Pass 1: Code → Wiki (every code artifact has documentation)

- List every file created, modified, or deleted in the change.
- For each, confirm it appears in the relevant wiki module page's directory listing.
- For each new route/endpoint, confirm it appears in the architecture routes page.

##### Step 3 — Pass 2: Wiki → Code (every wiki claim is true)

- Read the directory listings in affected wiki module pages.
- Verify every listed file actually exists. If not: remove it or mark `(planned — not yet implemented)`.
- Verify route tables match registered routes.

##### Output

A pass/fail summary for each direction. Both must pass before the change is considered complete.

##### Deviation Protocol

When implementation differs from spec:

1. Add `> [!note] Deviation from spec: {description}` on the affected wiki page.
2. Update the directory listing to reflect reality, not aspiration.
3. Append an entry to `wiki/deviations.md`:

```markdown
| Date | Wiki Page | Spec Claim | Actual Implementation | Reason |
|------|-----------|------------|----------------------|--------|
```

#### 8. Lint / Health Check

When the user asks to lint or review the wiki:

1. **Scan** all wiki pages for:
   - Orphan pages (no inbound `[[wikilinks]]`).
   - Broken `[[wikilinks]]` (target page doesn't exist).
   - Stale claims superseded by newer sources or code changes.
   - Unresolved `> [!contradiction]` or `> [!breaking]` callouts.
   - Modules in code that lack wiki pages.
   - Convention pages that don't match actual code patterns.
   - Missing or incomplete frontmatter fields.
   - Deprecated decisions still referenced as active.
2. **Report** findings as a checklist.
3. **Fix** issues with user approval.
4. **Append** to `wiki/log.md`.

#### 9. Brownfield Onboarding

When adopting the framework on an already-running codebase:

1. **Run lint** (Workflow 8) to discover what wiki coverage is missing.
2. **Back-fill module pages** (`wiki/modules/`) — one page per existing module/service/component, written from the live code.
3. **Back-fill architecture pages** (`wiki/architecture/`) — describe the actual running system, not an aspirational design.
4. **Write ADRs** for the top 3–5 most consequential past decisions that shaped the codebase.
5. **Populate conventions** (`wiki/conventions/`) — document the coding patterns already in use.
6. **Baseline `wiki/deviations.md`** — document any known gaps between the wiki and reality.

> [!note] For brownfield projects, `wiki/overview.md` should be written from the actual system state, not the aspirational one. Mark any unverified claims as `(unverified — pending audit)`.

---

## Log Format

Each entry in `wiki/log.md` follows this format:

```markdown
## [YYYY-MM-DD] operation | Title
- **Operation**: ingest | query | lint | analysis | update | code-change
- **Pages touched**: [[page1]], [[page2]], ...
- **Summary**: One-line description of what changed.
```

---

## Index Format

Each entry in `wiki/index.md` follows this format:

```markdown
### Category Name

| Page | Summary | Sources | Updated |
|------|---------|---------|---------|
| [[page-name]] | One-line summary | 2 | 2026-04-27 |
```

---

## Guiding Principles

These are the non-negotiable defaults for every session. **Wiki Discipline** governs how knowledge is filed and maintained. **Coding Discipline** governs how the agent reasons about and writes code. Both apply together on every change.

### Wiki Discipline

1. **The wiki is the product.** Chat is ephemeral; the wiki is permanent. Anything valuable should be filed.
2. **Compound, don't repeat.** When new data arrives, update existing pages — don't create duplicates.
3. **Flag conflicts explicitly.** Contradictions are valuable information. Never silently overwrite.
4. **Cross-reference aggressively.** The value of the wiki grows with its connections.
5. **Human curates, LLM maintains.** The user decides what to ingest and what questions to ask. The LLM does all the filing, linking, and bookkeeping.

### Coding Discipline

These four principles apply to every code operation — Workflow 4 (before the change), Workflow 5 (after the change), and every step of the Post-Change Pipeline.

#### P1. Think Before Coding

> Don't assume. Don't hide confusion. Surface tradeoffs.

- **State assumptions explicitly** — If uncertain, ask rather than guess.
- **Present multiple interpretations** — Don't pick silently when ambiguity exists.
- **Push back when warranted** — If a simpler approach exists, say so.
- **Stop when confused** — Name what's unclear and ask for clarification.

#### P2. Simplicity First

> Minimum code that solves the problem. Nothing speculative.

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If 200 lines could be 50, rewrite it.

#### P3. Surgical Changes

> Touch only what you must. Clean up only your own mess.

- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it — don't delete it.
- Remove imports/variables/functions that **your** changes made unused.

#### P4. Goal-Driven Execution

> Define success criteria. Loop until verified.

For multi-step tasks, state a brief plan:

```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

---

## SkillForge Agent Interfaces

SkillForge exposes its capabilities as **discoverable agents** that any orchestration framework can invoke.

### Available Agents

| Agent ID | Purpose | Stateful |
|---|---|---|
| `skillforge.evolver` | Evolve a skill through co-evolutionary verification | Yes |
| `skillforge.retriever` | Find relevant skills from the Skill Bank | No |
| `skillforge.executor` | Execute a task using a specific skill | Yes |
| `skillforge.evaluator` | Benchmark skill quality with synthetic tests | No |
| `skillforge.memory` | Query tiered memory for experience and patterns | No |

### Integration Protocols

- **Tool Registration** — Register as callable tools in LangChain/AutoGen/Semantic Kernel
- **Sub-Agent Delegation** — Invoke via `SkillForgeAgentProvider.get_agent()`
- **Event-Driven** — Subscribe to lifecycle events via `SkillForgeEventBus`
- **MCP Server** — Expose as Model Context Protocol server for VS Code agents

See `wiki/architecture/agent-interfaces.md` for full schemas and examples.

---

## Platform Integration

SkillForge provides native integration files for three AI coding platforms. Each platform reads specific files to discover agents, skills, and project context.

### VS Code Copilot Chat

| File | Purpose |
|------|---------|
| `.github/copilot-instructions.md` | Project-wide instructions loaded into every Copilot session |
| `.github/agents/skillforge-evolver.agent.md` | Custom agent: evolve skills via co-evolutionary loops |
| `.github/agents/skillforge-retriever.agent.md` | Custom agent: find and apply existing skills |
| `.github/agents/skillforge-evaluator.agent.md` | Custom agent: benchmark and compare skill quality |
| `.github/skills/skillforge-evolve/SKILL.md` | Skill: step-by-step skill evolution procedure |
| `.github/skills/skillforge-retrieve/SKILL.md` | Skill: find and apply existing skills |
| `.github/skills/skillforge-evaluate/SKILL.md` | Skill: benchmark and compare skill quality |

**Setup**: Open the repo in VS Code with the GitHub Copilot extension installed. Agents appear in the agent picker (`@`), skills appear as slash commands (`/`).

### Claude Code / Claude Workspace

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Project context loaded at the start of every Claude session |
| `.claude/skills/skillforge-evolve/SKILL.md` | Skill: step-by-step skill evolution procedure |
| `.claude/skills/skillforge-retrieve/SKILL.md` | Skill: find and apply existing skills |
| `.claude/skills/skillforge-evaluate/SKILL.md` | Skill: benchmark and compare skill quality |

**Setup**: Open the repo in Claude Code or attach it as a Claude workspace. `CLAUDE.md` is read automatically. Skills are discovered from the `.claude/skills/` directory.

### OpenAI Codex

| File | Purpose |
|------|---------|
| `AGENTS.md` (this file) | Project context loaded at the start of every Codex session |

**Setup**: This file (`AGENTS.md`) is automatically read by Codex at the root of the repository. It provides the full project schema, conventions, workflows, and agent interfaces. The `skills/` directory contains the same skill definitions in a framework-agnostic YAML+markdown format that Codex can reference.

### Skill Files (Cross-Platform)

The `skills/` directory at the repo root contains framework-agnostic skill definitions usable by any platform:

| File | Purpose |
|------|---------|
| `skills/evolve-skill.md` | How to evolve a new skill (YAML frontmatter + procedure) |
| `skills/retrieve-and-apply.md` | How to find and use existing skills |
| `skills/evaluate-skills.md` | How to benchmark skill quality |
