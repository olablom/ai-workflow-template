# AI WORKFLOW MASTER

This document defines the operational workflow used for complex technical work across many ChatGPT sessions.

It is **not** meant to be pasted into every chat.
It defines the **method**, not the runtime state.

---

## Core Idea

Separate the system into three layers:

Memory layer → documents
Reasoning layer → ChatGPT
Execution layer → Cursor

---

## Core Loop

problem
↓
design (ChatGPT)
↓
implementation (Cursor)
↓
review (ChatGPT)
↓
update state

---

## State Model

STATE = PROJECT_CONTEXT + DECISIONS_LOG

PROJECT_CONTEXT = stable anchor
DECISIONS_LOG = incremental changes

Rebuild the anchor periodically from the log.

---

## Reasoning Preservation

Use CORE summaries:

C — conclusions
O — options
R — reasoning
E — evidence

---

## Development Rules

- smallest possible diff
- architecture must remain consistent
- every bugfix adds regression tests
- ask if context is missing

---

## Session Structure

SESSION RULES
STATE
INVARIANTS
CURRENT TASK
SESSION OBJECTIVE
REMINDER
