#!/usr/bin/env python3
"""
Workflow CLI. Subcommands: reviewer (append evidence), route (deterministic target + prompt).
Stdlib only.
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROUTE_TARGETS = frozenset({"cursor", "gpt", "new_chat"})
ROUTE_MODES = frozenset({"plan", "review", "resume", "commit"})


def validate_route_output(obj: dict) -> bool:
    """Validate route output schema: target, mode, reason (list of str), prompt (str)."""
    if not isinstance(obj, dict):
        return False
    if obj.get("target") not in ROUTE_TARGETS:
        return False
    if obj.get("mode") not in ROUTE_MODES:
        return False
    reason = obj.get("reason")
    if not isinstance(reason, list) or not all(isinstance(r, str) for r in reason):
        return False
    if not isinstance(obj.get("prompt"), str):
        return False
    return True


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def run_git(args: list[str], cwd: Path, capture: bool = True, text: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git"] + args,
        cwd=cwd,
        capture_output=capture,
        text=text,
    )


def get_run_id(root: Path, from_cli: str | None) -> str:
    if from_cli:
        return from_cli.strip()
    header = root / "workflow" / "SESSION_HEADER.md"
    if not header.exists():
        print("RUN_ID required. Set RUN_ID in workflow/SESSION_HEADER.md or pass --run-id.", file=sys.stderr)
        raise SystemExit(1)
    for line in header.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("RUN_ID:"):
            val = line.split("RUN_ID:", 1)[1].strip()
            if val and val != "<run_id>":
                return val
    print("RUN_ID required. Set RUN_ID in workflow/SESSION_HEADER.md or pass --run-id.", file=sys.stderr)
    raise SystemExit(1)


def reviewer(args: argparse.Namespace, root: Path) -> int:
    if not args.cmd:
        print("reviewer requires at least one --cmd. Run: python scripts/wf.py reviewer --cmd \"<your check>\"", file=sys.stderr)
        return 1
    run_id = get_run_id(root, args.run_id)

    # Git snapshot (staged only)
    branch = run_git(["rev-parse", "--abbrev-ref", "HEAD"], root).stdout.strip() or ""
    head = run_git(["rev-parse", "HEAD"], root).stdout.strip() or ""
    diff_cached = run_git(["diff", "--cached"], root, text=False)
    diff_bytes = diff_cached.stdout or b""
    dirty = len(diff_bytes.strip()) > 0
    diff_stat_proc = run_git(["diff", "--cached", "--stat"], root)
    diff_stat = (diff_stat_proc.stdout or "").strip()
    diff_sha256 = hashlib.sha256(diff_bytes).hexdigest() if dirty else None

    if dirty and diff_sha256 is None:
        print("dirty=true requires diff_sha256.", file=sys.stderr)
        return 1

    # Repo name and remote
    repo_name = (args.repo or root.name).strip()
    remote_proc = run_git(["config", "--get", "remote.origin.url"], root)
    remote = remote_proc.stdout.strip() if remote_proc.returncode == 0 and remote_proc.stdout else None
    repo_obj = {"name": repo_name}
    if remote:
        repo_obj["remote"] = remote

    # Run commands
    commands_out: list[dict] = []
    any_failed = False
    for cmd in args.cmd or []:
        proc = subprocess.run(
            cmd,
            shell=True,
            cwd=root,
            capture_output=True,
            text=True,
        )
        combined = (proc.stdout or "") + (proc.stderr or "")
        lines = combined.strip().splitlines()
        stdout_tail = "\n".join(lines[-20:]) if lines else None
        commands_out.append({
            "cmd": cmd,
            "exit_code": proc.returncode,
            **({"stdout_tail": stdout_tail} if stdout_tail else {}),
        })
        if proc.returncode != 0:
            any_failed = True

    git_obj = {
        "branch": branch,
        "head": head,
        "dirty": dirty,
        "diff_stat": diff_stat,
    }
    if dirty and diff_sha256:
        git_obj["diff_sha256"] = diff_sha256

    ts = datetime.now().isoformat()
    evidence = {
        "ts": ts,
        "repo": repo_obj,
        "run_id": run_id,
        "step": "reviewer",
        "git": git_obj,
        "commands": commands_out,
    }

    evidence_path = root / "workflow" / "EVIDENCE.jsonl"
    try:
        with open(evidence_path, "a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(evidence, ensure_ascii=False) + "\n")
    except OSError as e:
        print(f"Failed to append evidence: {e}", file=sys.stderr)
        return 1

    if any_failed:
        return 1
    return 0


def _read_run_id_optional(root: Path) -> str | None:
    """Return RUN_ID from SESSION_HEADER or None if missing/placeholder."""
    header = root / "workflow" / "SESSION_HEADER.md"
    if not header.exists():
        return None
    for line in header.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("RUN_ID:"):
            val = line.split("RUN_ID:", 1)[1].strip()
            if val and val != "<run_id>":
                return val
    return None


def _read_latest_evidence_entry(path: Path) -> dict | None:
    """Return last valid evidence entry (skip # lines and _schema objects), or None."""
    if not path.exists():
        return None
    latest = None
    for line in path.read_text(encoding="utf-8").strip().splitlines():
        if line.strip().startswith("#"):
            continue
        try:
            obj = json.loads(line)
            if isinstance(obj, dict) and not obj.get("_schema"):
                latest = obj
        except (json.JSONDecodeError, TypeError):
            continue
    return latest


def _last_evidence_run_id(root: Path) -> str | None:
    """Return run_id from last non-schema line in EVIDENCE.jsonl, or None."""
    entry = _read_latest_evidence_entry(root / "workflow" / "EVIDENCE.jsonl")
    return entry.get("run_id") if entry else None


def _has_placeholders(content: str) -> bool:
    """True if content contains placeholder-like <...> (angle brackets with non-empty inside)."""
    return bool(re.search(r"<\s*[^>\s]+\s*>", content))


def _task_queue_active_contains(root: Path, *words: str) -> bool:
    """True if ACTIVE section in TASK_QUEUE contains any of the given words (case-insensitive)."""
    path = root / "workflow" / "TASK_QUEUE.md"
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    in_active = False
    for line in text.splitlines():
        if line.strip() == "ACTIVE":
            in_active = True
            continue
        if in_active:
            if line.strip() in ("NEXT", "DONE") or (line.strip().startswith("#")):
                break
            lower = line.lower()
            if any(w in lower for w in words):
                return True
    return False


def route(_args: argparse.Namespace, root: Path) -> int:
    """Determine target, mode, reason, prompt. ABI: {target, mode, reason, prompt}. Modes: resume, review, commit, plan."""
    run_id = _read_run_id_optional(root)
    diff_cached = run_git(["diff", "--cached"], root, text=False)
    has_staged = len((diff_cached.stdout or b"").strip()) > 0
    last_evidence_run_id = _last_evidence_run_id(root)

    state_path = root / "workflow" / "STATE.md"
    state_text = state_path.read_text(encoding="utf-8") if state_path.exists() else ""
    task_queue_path = root / "workflow" / "TASK_QUEUE.md"
    task_queue_text = task_queue_path.read_text(encoding="utf-8") if task_queue_path.exists() else ""

    target: str
    mode: str
    reason: list[str]
    prompt: str

    if _has_placeholders(state_text) or _has_placeholders(task_queue_text):
        target = "cursor"
        mode = "resume"
        reason = ["STATE or TASK_QUEUE contains placeholders.", "Run bootstrap or fill placeholders before continuing."]
        prompt = "Run bootstrap or fill placeholders: ensure workflow/STATE.md, workflow/SESSION_HEADER.md, and workflow/TASK_QUEUE.md have no <...> placeholders. Use scripts/bootstrap.py --project \"Your Project Name\" if this is a new repo from template."
    elif has_staged and (run_id is None or last_evidence_run_id != run_id):
        target = "gpt"
        mode = "review"
        reason = ["Staged diff exists but no evidence entry for current RUN_ID.", "Reviewer step and evidence append required before commit."]
        prompt = "Perform the reviewer steps: (1) Review the staged diff (git diff --cached). (2) Run verification commands (e.g. tests/lint). (3) Append one evidence entry using: python scripts/wf.py reviewer --cmd \"<your check>\" (or set RUN_ID in workflow/SESSION_HEADER.md first). Do not commit until evidence is appended and all commands exit 0."
    elif has_staged and run_id is not None and last_evidence_run_id == run_id:
        target = "cursor"
        mode = "commit"
        reason = ["Staged diff has matching evidence for current RUN_ID.", "Next step is to commit."]
        prompt = "Commit the staged changes. Pre-commit will run commit-check; ensure you have run reviewer with at least one --cmd and all commands passed."
    elif _task_queue_active_contains(root, "implement", "refactor", "fix"):
        target = "cursor"
        mode = "plan"
        reason = ["ACTIVE task implies implementation work.", "Cursor should apply code/repo changes."]
        prompt = "Implement the current ACTIVE task from workflow/TASK_QUEUE.md. Apply minimal diffs; only touch files needed for the task. Then update TASK_QUEUE (move to DONE if done) and STATE if milestone/task changed."
    else:
        target = "gpt"
        mode = "plan"
        reason = ["No staged-diff gap or implementation task detected.", "Propose next step and update workflow state as needed."]
        prompt = "Propose the next step for this project. Read workflow/STATE.md and workflow/TASK_QUEUE.md. Suggest one concrete action (design, task, or implementation). If the next step is implementation, add it to ACTIVE in TASK_QUEUE and summarize for Cursor."

    out = {"target": target, "mode": mode, "reason": reason, "prompt": prompt}
    if not validate_route_output(out):
        print("route output schema validation failed", file=sys.stderr)
        return 1
    print(json.dumps(out, ensure_ascii=False))
    return 0


def commit_check(_args: argparse.Namespace, root: Path) -> int:
    """Require latest evidence to match staged diff when staged diff exists. Staged only (git diff --cached)."""
    diff_cached = run_git(["diff", "--cached"], root, text=False)
    diff_bytes = diff_cached.stdout or b""
    if len(diff_bytes.strip()) == 0:
        print("OK commit-check (no staged diff)")
        return 0

    evidence_path = root / "workflow" / "EVIDENCE.jsonl"
    if not evidence_path.exists():
        print("commit-check failed: no evidence entry found. Run: python scripts/wf.py reviewer --cmd \"<your check>\"", file=sys.stderr)
        return 1
    latest_entry = _read_latest_evidence_entry(evidence_path)
    if not latest_entry:
        print("commit-check failed: no evidence entry found. Run: python scripts/wf.py reviewer --cmd \"<your check>\"", file=sys.stderr)
        return 1

    git = latest_entry.get("git") or {}
    if git.get("dirty") is not True:
        print("commit-check failed: latest evidence git.dirty not true. Re-run reviewer for current staged diff.", file=sys.stderr)
        return 1
    if not git.get("diff_sha256"):
        print("commit-check failed: latest evidence missing diff_sha256. Re-run reviewer for current staged diff.", file=sys.stderr)
        return 1
    current_sha = hashlib.sha256(diff_bytes).hexdigest()
    if git.get("diff_sha256") != current_sha:
        print("commit-check failed: diff_sha256 mismatch. Re-run reviewer for current staged diff.", file=sys.stderr)
        return 1

    commands = latest_entry.get("commands")
    if not commands:
        print("commit-check failed: latest evidence has no verification commands. Run reviewer with at least one --cmd.", file=sys.stderr)
        return 1
    for c in commands:
        if c.get("exit_code") != 0:
            print("commit-check failed: latest evidence has non-zero exit_code. Fix and re-run reviewer.", file=sys.stderr)
            return 1

    print("OK commit-check")
    return 0


def main() -> int:
    root = repo_root()
    parser = argparse.ArgumentParser(prog="wf", description="Workflow CLI (reviewer evidence).")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)
    rev = subparsers.add_parser("reviewer", help="Run reviewer commands and append evidence (B6 staged diff).")
    rev.add_argument("--cmd", action="append", metavar="CMD", help="Command to run (repeat for multiple).")
    rev.add_argument("--run-id", metavar="ID", help="Run ID (else read from workflow/SESSION_HEADER.md).")
    rev.add_argument("--repo", metavar="NAME", help="Repo name (default: directory name).")
    rev.set_defaults(func=reviewer)
    route_p = subparsers.add_parser("route", help="Print target (cursor/gpt/new_chat), reason, and prompt as JSON.")
    route_p.set_defaults(func=route)
    cc = subparsers.add_parser("commit-check", help="Verify latest evidence matches staged diff; required before commit.")
    cc.set_defaults(func=commit_check)
    args = parser.parse_args()
    return args.func(args, root)


if __name__ == "__main__":
    raise SystemExit(main())
