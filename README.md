# AI Workflow Template

## Overview

This repository is a **template for deterministic AI-assisted development**. It gives you a fixed workflow so that:

- **Context is anchored** in the repo (state, tasks, decisions, evidence), not only in chat.
- **Commits are gated** on reviewer evidence: staged changes must match a recorded run of verification commands before commit.
- **Routing is deterministic**: `wf route` decides the next step (Cursor vs GPT, and mode) from workflow state and staged diff alone—no LLM call.

Use it when you want to combine ChatGPT (reasoning, design, review) and Cursor (code, repo edits) across many sessions without drift: the repo is the source of truth; AI is advisory; you run the loop and approve commits.

## Architecture

**Workflow state** (human- and AI-editable; defines “where we are”):

- **workflow/STATE.md** — Single source of truth: project, milestone, current task, risks. **STABLE_REF** (optional) records a known-good commit SHA for rollback; to roll back, run `git checkout <STABLE_REF>` or create a branch from it (no automation in this template).
- **workflow/TASK_QUEUE.md** — ACTIVE / NEXT / DONE task list.
- **workflow/SESSION_HEADER.md** — Session rules, RUN_ID, current task, invariants.
- **workflow/DECISIONS_LOG.md** — Chronological architectural decisions.

**Evidence logging** (append-only; binds commits to verification):

- **workflow/EVIDENCE.jsonl** — One JSON object per reviewer run: git snapshot (branch, head, dirty, diff_stat, diff_sha256 when dirty) and commands (cmd, exit_code, optional stdout_tail). Commit-check compares the **last valid entry** to the current staged diff.

**CLI tooling** (stdlib-only; no extra deps):

- **scripts/wf.py reviewer** — Run verification commands (e.g. tests, lint), record their exit codes, and append one evidence entry for the **staged** diff (B6). **Requires at least one `--cmd`** (no empty-commands evidence). Requires RUN_ID (in SESSION_HEADER or `--run-id`).
- **scripts/wf.py route** — Print one JSON: `target`, `mode` (plan | review | resume | commit), `reason`, `prompt`. ABI is stable. Uses only workflow files and `git diff --cached`; deterministic.
- **scripts/wf.py commit-check** — If there is staged diff, require the latest evidence entry to have `git.dirty=true`, matching `diff_sha256`, **non-empty `commands`**, and all `commands[].exit_code == 0`. **Rejects evidence with zero verification commands.** If no staged diff, pass. Used by the pre-commit hook.

**Commit gate:**

- **.githooks/pre-commit** — Runs `python scripts/wf.py commit-check`. Commit is blocked unless evidence matches staged diff (or staged is empty).

**Install script:**

- **scripts/install-hooks.py** — Sets `git config core.hooksPath .githooks` so the versioned hook runs on commit.

## Operational Loop

The loop is:

**edit → git add → wf reviewer → wf route → Cursor/GPT → commit**

1. **Edit** — Change code or workflow files.
2. **git add** — Stage what you want to commit.
3. **wf reviewer** — Run your checks with **at least one `--cmd`** (e.g. `wf reviewer --cmd "pytest" --cmd "ruff check"`). Appends evidence for the current staged diff. If any command fails, fix and re-run reviewer before committing. Empty commands are not allowed; commit-check will reject evidence with no verification commands.
4. **wf route** — Get the next step: JSON with `target`, `mode`, `reason`, `prompt`. Use it in Cursor or paste into ChatGPT.
5. **Cursor/GPT** — Execute the suggested step (implement, review, or plan).
6. **commit** — Pre-commit runs `wf commit-check`. If staged diff exists, it must match the latest evidence (same diff_sha256, all exit_code 0). If you changed staged diff after reviewer, run reviewer again.

Commit is **blocked** until commit-check passes (or you have no staged diff).

## Quickstart

1. **Clone (or create from template)**  
   ```bash
   git clone <this-repo> my-project && cd my-project
   ```

2. **Install hooks**  
   ```bash
   python scripts/install-hooks.py
   ```  
   Confirms: `core.hooksPath` is set to `.githooks`.

3. **Bootstrap project name** (optional; for new repos from template)  
   ```bash
   python scripts/bootstrap.py --project "My Project"
   ```  
   Fills placeholders in `workflow/STATE.md`, `workflow/SESSION_HEADER.md`, `workflow/TASK_QUEUE.md`.

4. **Set RUN_ID**  
   Edit `workflow/SESSION_HEADER.md`: set `RUN_ID: <your-session-id>` (e.g. a date or short label). Required for `wf reviewer` and used by `wf route`.

5. **Make a change, stage it, run reviewer, then commit**  
   ```bash
   # edit files, then:
   git add .
   python scripts/wf.py reviewer --cmd "python -m py_compile scripts/wf.py"
   git commit -m "Your message"
   ```  
   Pre-commit runs `commit-check`; if the staged diff matches the evidence just appended and all commands passed, commit succeeds.

## Demo

Short example of one full cycle:

```bash
# 1. Hooks installed, RUN_ID set in workflow/SESSION_HEADER.md
python scripts/install-hooks.py
# 2. Small change
echo "# demo" >> workflow/STATE.md
git add workflow/STATE.md
# 3. Reviewer records evidence for this staged diff
python scripts/wf.py reviewer --run-id demo --cmd "true"
# 4. Route suggests next step (e.g. plan or commit)
python scripts/wf.py route
# 5. Commit (pre-commit runs commit-check; passes because evidence matches)
git commit -m "docs: demo workflow"
```

If you had run `git add` again after step 3 (changing staged diff), commit would be blocked until you run `wf reviewer` again for the new staged diff.

## Design Principles

- **Repo = source of truth** — State, tasks, decisions, and evidence live in the repo. Sessions and tools read from it; no hidden context.
- **Determinism** — `wf route` and `wf commit-check` are pure functions of workflow files and staged diff. No LLM inside the gate or the router.
- **Evidence + commit gating** — Staged diff is bound to a reviewer run (diff_sha256 + non-empty command list + all exit_code 0). Commit-check rejects empty-commands evidence. Commits only succeed when that binding holds or there is no staged diff.
- **AI = advisory** — ChatGPT and Cursor suggest and implement; you run reviewer, route, and commit. Human executes and approves.
- **Human-in-the-loop** — You choose when to run reviewer, what commands to run, and when to commit. The hook only enforces that evidence matches staged diff when there is one.

## Repository Structure

.
├── workflow/          # State, evidence, session helpers
├── scripts/           # wf.py, bootstrap.py, install-hooks.py
├── .githooks/         # pre-commit (calls wf commit-check)
├── artifacts/
├── src/
├── README.md
└── LICENSE

See **workflow/README.md** for roles of each workflow file. See **workflow/DECISION.md** for locked decisions (commit-binding, evidence contract, RUN_ID, router ABI, hooks).

## License

MIT
