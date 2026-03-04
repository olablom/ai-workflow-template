This directory contains the persistent AI workflow state.

## Resuming in a new chat (10 seconds)

Two ways to resume without reading the whole repo:

**A) Full context** — Paste files in the order given in **workflow/NEW_CHAT_PROMPT.md** (BOOTSTRAP_PROMPT → STATE → RULES → SESSION_HEADER → PROJECT_CONTEXT → TASK_QUEUE → DECISIONS_LOG if any → VERIFY optional). End with: *Resume the project. Propose the next step. Respect invariants. No assumptions.*

**B) One-page resume** — Paste **workflow/RESUME_PACKET.md** only. Update RECENT COMMITS and FILES THAT MATTER NOW before pasting. Then ask the model to propose the next step.

---

Files:

PROJECT_CONTEXT.md
Defines the stable project definition.

SESSION_HEADER.md
Defines the current session state.

DECISIONS_LOG.md
Chronological record of decisions.

TASK_QUEUE.md
Tracks active, next and completed tasks.

Update rules:

- PROJECT_CONTEXT changes rarely
- SESSION_HEADER every session
- DECISIONS_LOG when decisions occur
- TASK_QUEUE when tasks move
