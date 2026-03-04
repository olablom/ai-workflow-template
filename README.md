# AI Workflow Template

A minimal workflow for running complex AI-assisted development projects across many ChatGPT sessions without losing context.

## Problem

When using LLMs for development, three issues appear quickly:

- context window limits
- summary drift across sessions
- patch-driven development

This workflow provides a lightweight structure to maintain stable reasoning and project continuity.

## Core Loop


problem
↓
design (ChatGPT)
↓
implementation (Cursor)
↓
review (ChatGPT)
↓
refinement (Cursor)
↓
update decisions


Roles:

- **ChatGPT** → reasoning, architecture, debugging
- **Cursor** → code generation and repository edits
- **Documents** → project memory

## Repository Structure


AI_WORKFLOW/
│
├── AI_WORKFLOW_MASTER.md
├── SESSION_HEADER.md
├── PROJECT_CONTEXT.md
├── DECISIONS_LOG.md


### AI_WORKFLOW_MASTER.md

System definition of the workflow.

Used only as documentation and reference.

### SESSION_HEADER.md

Runtime header used to start new ChatGPT sessions.

### PROJECT_CONTEXT.md

Stable project context (anchor).

### DECISIONS_LOG.md

Log of important architectural decisions.

## Typical Usage

1. Fill in `PROJECT_CONTEXT.md` when starting a project.
2. Start ChatGPT sessions using `SESSION_HEADER.md`.
3. Record important decisions in `DECISIONS_LOG.md`.
4. Periodically merge decisions into the project context.

## Design Principles

- explicit project state
- deterministic workflow
- minimal prompt overhead
- human-in-the-loop orchestration

## License

MIT
