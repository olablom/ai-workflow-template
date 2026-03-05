#!/usr/bin/env python3
"""
Read-only UX wrapper: runs wf route and prints a copy/paste-ready WF NEXT instruction block.
Does not run reviewer, modify repo state, commit, or call AI tools. Stdlib only.
"""
import json
import subprocess
import sys
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def main() -> int:
    root = repo_root()
    wf_script = root / "scripts" / "wf.py"
    proc = subprocess.run(
        [sys.executable, str(wf_script), "route"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        print(proc.stderr or "wf route failed", file=sys.stderr)
        return 1

    try:
        obj = json.loads(proc.stdout.strip())
    except (json.JSONDecodeError, TypeError) as e:
        print(f"Invalid JSON from wf route: {e}", file=sys.stderr)
        return 1

    if not isinstance(obj, dict):
        print("wf route output is not a JSON object", file=sys.stderr)
        return 1
    target = obj.get("target")
    mode = obj.get("mode")
    reason = obj.get("reason")
    prompt = obj.get("prompt")
    if target not in ("cursor", "gpt", "new_chat"):
        print("wf route output missing or invalid 'target'", file=sys.stderr)
        return 1
    if not isinstance(mode, str):
        print("wf route output missing or invalid 'mode'", file=sys.stderr)
        return 1
    if not isinstance(reason, list) or not all(isinstance(r, str) for r in reason):
        print("wf route output missing or invalid 'reason' (must be list of str)", file=sys.stderr)
        return 1
    if not isinstance(prompt, str):
        print("wf route output missing or invalid 'prompt'", file=sys.stderr)
        return 1

    if target in ("gpt", "new_chat"):
        print("copy/paste:\n")
        print(prompt)
        return 0

    print("WF NEXT\n")
    print(f"target: {target}")
    print(f"mode:   {mode}\n")
    print("reason:")
    for r in reason:
        print(f"- {r}")
    print("\ncopy/paste:\n")
    print("/plan\n")
    print(prompt)
    return 0


if __name__ == "__main__":
    sys.exit(main())
