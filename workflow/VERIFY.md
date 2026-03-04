# VERIFY

Checklist before committing changes:

## State verification
- STATE.md reflects the current milestone and task
- TASK_QUEUE.md reflects what is actually being worked on
- DECISIONS_LOG.md updated if architectural decisions were made

## Evidence logging (required)
* Reviewer evidence uses **staged** diff only (git diff --cached). git.diff_stat must come from "git diff --cached --stat". When git.dirty=true, require git.diff_sha256 (sha256 of "git diff --cached").
* Append one evidence entry to workflow/EVIDENCE.jsonl per reviewer run.
* Do not commit if the latest evidence entry has any non-zero exit_code or if evidence was not appended.

Evidence example (include diff_sha256 when dirty): "diff_sha256":"<sha256>"

How to compute diff_sha256 (Git Bash):
  git diff --cached --stat
  git diff --cached | sha256sum
  git diff --cached | shasum -a 256
 (shasum if sha256sum not available)

1. Run:
   git status

2. Review changes:
   git diff --stat

3. Run or test any changed code.

4. Update STATE.md if the milestone or current task changed.

5. Update DECISIONS_LOG.md if a decision was made.

6. Update TASK_QUEUE.md if tasks moved (ACTIVE → DONE etc).

7. Commit and push.
