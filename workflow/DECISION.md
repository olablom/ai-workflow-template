# Workflow decisions (locked)

Checklist of locked decisions. Change only by explicit decision record.

- [ ] **1) Commit-binding** — Hard block via `wf commit-check` + pre-commit hook calling it. Binding is against latest evidence entry: compare diff_sha256 to sha256(git diff --cached). If staged diff exists: require latest evidence has git.dirty=true AND git.diff_sha256 matches current staged diff sha256 AND all commands exit_code==0. If staged diff is empty: commit-check passes (no evidence required).
- [ ] **2) Latest evidence** — Last valid JSON line in workflow/EVIDENCE.jsonl that is not _schema and not a comment. No branch/head matching in MVP. Route treats empty staged diff as clean.
- [ ] **3) RUN_ID policy** — RUN_ID required for `wf reviewer` and `wf route`. Reviewer fails if RUN_ID missing or equals "<run_id>" placeholder. Route: if RUN_ID missing/placeholder → target=cursor, mode=resume, prompt="set RUN_ID". RUN_ID is session-id (reusable across multiple reviewer runs).
- [ ] **4) Router ABI** — Stable JSON: `{ "target":"cursor|gpt|new_chat", "mode":"plan|debug|review|resume|commit", "reason":["..."], "prompt":"..." }`. prompt is plain text (no YAML/JSON in MVP).
- [ ] **5) Evidence minimum contract** — Per entry: required ts, repo, run_id, step; git.branch, git.head, git.dirty, git.diff_stat; commands[] with cmd+exit_code. git.diff_sha256 required iff git.dirty=true. stdout_tail optional. Commit-check fails if staged diff exists but diff_sha256 missing/mismatch OR any exit_code != 0.
- [ ] **6) Decision-adapter (future)** — Returns JSON `{ "action":"CURSOR_DEBUG", "confidence":0.77, "reason":["..."], "do":["..."] }`.
- [ ] **7) Hooks** — Version under .githooks/ + installer script that runs: `git config core.hooksPath .githooks`.
- [ ] **8) Source of truth** — wf route decides action; GPT/local LLM are advisory only. The local LLM sidecar (scripts/sidecar_llm.py) is advisory-only and outside the truth chain; it does not affect reviewer or commit-check.

## Operational loop

edit → git add → wf reviewer → wf route → Cursor/GPT → commit

(Commit is blocked by pre-commit unless commit-check passes.)

- "`commit-check` uses the last valid evidence entry in `workflow/EVIDENCE.jsonl` (last non-comment, non-_schema JSON line), regardless of RUN_ID/branch."
- "If you change the staged diff after running `wf reviewer`, you must run `wf reviewer` again; otherwise `commit-check` will block the commit."
