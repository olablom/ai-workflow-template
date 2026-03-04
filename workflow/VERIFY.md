# VERIFY

Checklist before committing changes:

## State verification
- STATE.md reflects the current milestone and task
- TASK_QUEUE.md reflects what is actually being worked on
- DECISIONS_LOG.md updated if architectural decisions were made

1. Run:
   git status

2. Review changes:
   git diff --stat

3. Run or test any changed code.

4. Update STATE.md if the milestone or current task changed.

5. Update DECISIONS_LOG.md if a decision was made.

6. Update TASK_QUEUE.md if tasks moved (ACTIVE → DONE etc).

7. Commit and push.
