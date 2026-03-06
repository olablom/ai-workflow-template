#!/usr/bin/env python3
"""
Read-only UX wrapper: runs wf route and prints a copy/paste-ready WF NEXT instruction block.
Does not run reviewer, modify repo state, commit, or call AI tools. Stdlib only.
Optional: --advice local runs a local LLM sidecar (advice-only) after rendering.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def main() -> int:
    root = repo_root()
    parser = argparse.ArgumentParser()
    parser.add_argument("--advice", choices=["local"], help="Run local LLM sidecar after WF NEXT (advice-only).")
    parser.add_argument("--model", metavar="NAME", help="Ollama model for sidecar (e.g. llama3.1:8b).")
    args = parser.parse_args()

    # UX warning only: hooks not installed (do not fail, do not affect stdout)
    hooks_proc = subprocess.run(
        ["git", "config", "--get", "core.hooksPath"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    hooks_path = (hooks_proc.stdout or "").strip() if hooks_proc.returncode == 0 else ""
    if hooks_path != ".githooks":
        print("Hooks not installed (core.hooksPath != .githooks). Run: python scripts/install-hooks.py", file=sys.stderr)

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
        route_json_raw = proc.stdout.strip()
        obj = json.loads(route_json_raw)
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
    else:
        print("WF NEXT\n")
        print(f"target: {target}")
        print(f"mode:   {mode}\n")
        print("reason:")
        for r in reason:
            print(f"- {r}")
        print("\ncopy/paste:\n")
        print("/plan\n")
        print(prompt)

    if args.advice == "local":
        sidecar_cmd = [sys.executable, str(root / "scripts" / "sidecar_llm.py"), "--route-json", route_json_raw]
        if args.model:
            sidecar_cmd.extend(["--model", args.model])
        sc = subprocess.run(sidecar_cmd, cwd=root, capture_output=True, text=True, encoding="utf-8")
        if sc.returncode != 0:
            print(sc.stderr or "sidecar failed", file=sys.stderr)
            return sc.returncode
        if sc.stdout.strip():
            print("--- ADVICE (local LLM, non-authoritative) ---", file=sys.stderr)
            print(sc.stdout.strip(), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
