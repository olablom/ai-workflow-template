# AI Workflow Template

A minimal workflow for running complex AI-assisted development projects across many ChatGPT sessions without losing context.

## Problem

When using LLMs for development, three issues appear quickly:

- context window limits
- summary drift across sessions
- patch-driven development

This workflow provides a lightweight structure to maintain stable reasoning and project continuity.

## Quick Start

To start a new ChatGPT session with full context, follow **workflow/NEW_CHAT_PROMPT.md** (paste the listed files in order, then your message).

## Quick start for new projects

After creating a new repository from this template:

```bash
python scripts/bootstrap.py --project "Your Project Name"
```

This initializes placeholders in:
- workflow/STATE.md
- workflow/SESSION_HEADER.md
- workflow/TASK_QUEUE.md

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

.
├── AI_WORKFLOW_MASTER.md
├── workflow/
├── artifacts/
├── src/
├── README.md
└── LICENSE

### workflow/

Persistent AI workflow state. See `workflow/README.md` for file roles and update rules.

Core runtime:
- STATE.md
- RULES.md
- SESSION_HEADER.md
- PROJECT_CONTEXT.md
- TASK_QUEUE.md
- DECISIONS_LOG.md

Review helper:
- VERIFY.md

Session helpers:
- NEW_CHAT_PROMPT.md
- BOOTSTRAP_PROMPT.md
- CONDUCTOR_PROMPT.md
- RESUME_PACKET.md

### artifacts/

Output and generated artifacts.

### src/

Source code and project assets.

### AI_WORKFLOW_MASTER.md

System definition of the workflow.

Used only as documentation and reference.

## Typical Usage

1. Fill in `workflow/PROJECT_CONTEXT.md` when starting a project.
2. Start ChatGPT sessions using `workflow/SESSION_HEADER.md`.
3. Record important decisions in `workflow/DECISIONS_LOG.md`.
4. Track tasks in `workflow/TASK_QUEUE.md`.
5. Periodically merge decisions into the project context.

## Design Principles

- explicit project state
- deterministic workflow
- minimal prompt overhead
- human-in-the-loop orchestration

## License

MIT
