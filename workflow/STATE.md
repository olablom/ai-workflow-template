# STATE (single source of truth)

One file for current project state. Keep this updated; other workflow files reference it.

---

PROJECT
<project name>

MILESTONE
<current milestone>

ARCHITECTURE
planner → implementer → reviewer → memory

TOOLS
ChatGPT = reasoning / design / review
Cursor = coding / repo changes

ANCHOR
PROJECT_CONTEXT.md = stable
SESSION_HEADER.md = per-session
DECISIONS_LOG.md = decisions

RISKS
context window limits
iteration drift
architecture drift

CURRENT TASK
<active task>

STABLE_REF
dd28deb10232964992172a5e5749c69098bada49
Last known-good baseline commit. For rollback: git checkout <STABLE_REF> (or create a branch from it).

SESSION OBJECTIVE
<desired outcome>

---

Update this file when task or objective changes. Sync with TASK_QUEUE and SESSION_HEADER as needed.
