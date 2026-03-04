# RULES

## Role split

**ChatGPT**
- Reasoning, architecture, design
- Review and debugging
- Do not edit the repository

**Cursor**
- Code generation
- Repository edits and file changes
- Follow design and decisions from ChatGPT/docs

## Before commit

- Review all changes (diffs)
- Confirm no unintended edits
- Ensure STATE / DECISIONS_LOG / TASK_QUEUE are updated if the work touched them

## Invariants

- Minimal diff: change only what is needed
- Architecture stable: decisions go through DECISIONS_LOG
- Ask if context is missing; do not assume

## Session discipline

- Read full context at session start
- No assumptions about prior sessions
- Respect invariants and RULES
