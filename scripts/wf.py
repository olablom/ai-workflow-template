#!/usr/bin/env python3
"""
Workflow CLI. Subcommand: reviewer — append reviewer evidence to workflow/EVIDENCE.jsonl (B6 staged diff).
Stdlib only.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


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


def main() -> int:
    root = repo_root()
    parser = argparse.ArgumentParser(prog="wf", description="Workflow CLI (reviewer evidence).")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)
    rev = subparsers.add_parser("reviewer", help="Run reviewer commands and append evidence (B6 staged diff).")
    rev.add_argument("--cmd", action="append", metavar="CMD", help="Command to run (repeat for multiple).")
    rev.add_argument("--run-id", metavar="ID", help="Run ID (else read from workflow/SESSION_HEADER.md).")
    rev.add_argument("--repo", metavar="NAME", help="Repo name (default: directory name).")
    rev.set_defaults(func=reviewer)
    args = parser.parse_args()
    return args.func(args, root)


if __name__ == "__main__":
    raise SystemExit(main())
