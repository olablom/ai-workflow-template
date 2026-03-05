# AI Workflow Template

![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.x-blue)
![Workflow](https://img.shields.io/badge/workflow-deterministic-green)

Deterministic control layer for AI-assisted development.

## Overview

This repository is a **template for deterministic AI-assisted development**.

It provides a simple control layer so that:

- **Context lives in the repo**, not only in chat
- **Commits require verified evidence**
- **Routing is deterministic**
- **AI is advisory, not authoritative**

The goal is to make AI-assisted development **stable across many sessions**.

Instead of relying on ephemeral chat context, the repository stores:

```
state
tasks
decisions
verification evidence
```

The result is a workflow where:

```
repo = source of truth
AI = advisory
human = execution
```

---

# Core Idea

AI-assisted development often fails because:

- context disappears between sessions
- commits happen without verification
- AI reasoning and repo state drift apart

This template solves that by enforcing a simple invariant:

```
reviewed patch == committed patch
```

A commit is only allowed if the **exact staged diff** has been verified by the reviewer.

---

# Architecture

The system has four layers.

## 1. Workflow State

The directory:

```
workflow/
```

contains the **persistent project memory**.

Files:

```
workflow/
STATE.md
TASK_QUEUE.md
SESSION_HEADER.md
DECISIONS_LOG.md
DECISION.md
EVIDENCE.jsonl
```

### STATE.md

High-level project state:

```
project
milestone
current task
risks
STABLE_REF
```

### TASK_QUEUE.md

Task management:

```
ACTIVE
NEXT
DONE
```

### SESSION_HEADER.md

Session metadata:

```
RUN_ID
session rules
current task
invariants
```

### DECISIONS_LOG.md

Chronological architecture decisions.

### DECISION.md

Locked system contracts.

Example:

```
commit-binding
reviewer contract
router ABI
```

### EVIDENCE.jsonl

Append-only verification log.

Each entry records:

```
git.branch
git.head
git.dirty
git.diff_stat
git.diff_sha256
commands[]
exit_code
```

---

# CLI Tools

Located in:

```
scripts/
```

## wf reviewer

Runs verification commands and records evidence.

Example:

```bash
python scripts/wf.py reviewer --cmd "pytest" --cmd "ruff check"
```

Actions:

1. Reads staged diff

```
git diff --cached
```

2. Executes commands

3. Writes verification record to:

```
workflow/EVIDENCE.jsonl
```

---

## wf route

Determines the next step **without using an LLM**.

```bash
python scripts/wf.py route
```

Output:

```json
{
  "target": "cursor | gpt | new_chat",
  "mode": "plan | debug | review | resume | commit",
  "reason": [...],
  "prompt": "..."
}
```

Router only reads:

```
workflow files
staged diff
git state
```

This keeps routing **deterministic**.

---

## wf commit-check

Verifies commit conditions.

```bash
python scripts/wf.py commit-check
```

Rules:

Commit is allowed only if:

```
latest evidence exists
git.dirty == true
diff_sha256 matches staged diff
all commands exit_code == 0
```

---

# Commit Gate

The repository includes a pre-commit hook:

```
.githooks/pre-commit
```

It runs:

```
wf commit-check
```

This blocks commits unless evidence matches the staged diff.

---

# Operational Loop

The development loop is:

```
edit
 ↓
git add
 ↓
wf reviewer
 ↓
wf route
 ↓
Cursor / GPT
 ↓
commit-check
 ↓
git commit
```

This ensures that verification always precedes commits.

---

# Quickstart

Clone the template:

```bash
git clone <repo> my-project
cd my-project
```

Install hooks:

```bash
python scripts/install-hooks.py
```

Set a session ID in:

```
workflow/SESSION_HEADER.md
```

Example:

```
RUN_ID: dev-session-1
```

Make a change and stage it:

```bash
git add .
```

Run reviewer:

```bash
python scripts/wf.py reviewer --cmd "python -m py_compile scripts/wf.py"
```

Commit:

```bash
git commit -m "example change"
```

---

# 30-Second Demo

This demonstrates the core invariant:

```
reviewed patch == committed patch
```

If the staged diff changes after reviewer, the commit is blocked.

```bash
# install hooks
python scripts/install-hooks.py

# make a change
echo "# demo" >> workflow/STATE.md
git add workflow/STATE.md

# record evidence
python scripts/wf.py reviewer --run-id demo --cmd "true"

# change file again AFTER reviewer
echo "# change again" >> workflow/STATE.md
git add workflow/STATE.md

# attempt commit
git commit -m "demo"

# commit will be blocked because staged diff changed

# run reviewer again
python scripts/wf.py reviewer --run-id demo --cmd "true"

# commit now succeeds
git commit -m "demo"
```

This demonstrates how the system prevents commits of unverified changes.

---

# Design Principles

### Repo = source of truth

All context lives in the repository:

```
state
tasks
decisions
evidence
```

No hidden chat context.

---

### Deterministic control layer

Router and commit gate are pure functions of:

```
workflow files
staged diff
git state
```

No LLM calls occur inside enforcement logic.

---

### Evidence-bound commits

Verification evidence includes:

```
git snapshot
diff hash
command results
```

This ensures:

```
reviewed patch == committed patch
```

---

### AI is advisory

AI can:

```
suggest
analyze
review
```

But cannot bypass verification.

---

### Human in the loop

The developer:

```
runs reviewer
runs router
approves commit
```

The system enforces correctness.

---

# Repository Structure

```
.
├── workflow/
│   ├── STATE.md
│   ├── TASK_QUEUE.md
│   ├── SESSION_HEADER.md
│   ├── DECISIONS_LOG.md
│   ├── DECISION.md
│   └── EVIDENCE.jsonl
│
├── scripts/
│   ├── wf.py
│   ├── bootstrap.py
│   └── install-hooks.py
│
├── .githooks/
│   └── pre-commit
│
├── artifacts/
├── src/
├── README.md
└── LICENSE
```

---

# Purpose

This project is not primarily an AI system.

It is **developer tooling** for safe AI-assisted development.

Specifically:

```
deterministic control layer
for AI coding workflows
```

---

# License

MIT
