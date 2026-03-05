#!/usr/bin/env python3
"""
Local LLM sidecar (advice-only). Reads workflow state and staged diff, optionally route JSON;
calls Ollama with a prompt, prints or writes advice to workflow/ADVICE.md. Stdlib only.
Does not stage, commit, or modify workflow logic.
"""
import argparse
import subprocess
import sys
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def main() -> int:
    root = repo_root()
    parser = argparse.ArgumentParser(description="Local LLM sidecar for workflow advice.")
    parser.add_argument("--route-json", metavar="JSON", help="wf route JSON string.")
    parser.add_argument("--route-json-file", metavar="PATH", help="Path to file containing wf route JSON.")
    parser.add_argument("--model", default="llama3.1:8b", metavar="MODEL", help="Ollama model (default: llama3.1:8b).")
    parser.add_argument("--write-advice", action="store_true", help="Write advice to workflow/ADVICE.md.")
    args = parser.parse_args()

    state_path = root / "workflow" / "STATE.md"
    task_path = root / "workflow" / "TASK_QUEUE.md"
    state_text = state_path.read_text(encoding="utf-8") if state_path.exists() else "(no STATE.md)"
    task_text = task_path.read_text(encoding="utf-8") if task_path.exists() else "(no TASK_QUEUE.md)"

    proc = subprocess.run(
        ["git", "diff", "--staged"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    staged_diff = (proc.stdout or "").strip() if proc.returncode == 0 else ""

    status_proc = subprocess.run(
        ["git", "status", "-sb"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    git_status_sb = (status_proc.stdout or "").strip() if status_proc.returncode == 0 else ""

    route_json_text = None
    if args.route_json:
        route_json_text = args.route_json.strip()
    elif args.route_json_file:
        p = Path(args.route_json_file)
        if not p.is_absolute():
            p = root / p
        if p.exists():
            route_json_text = p.read_text(encoding="utf-8").strip()

    staged_section = (
        staged_diff
        if staged_diff
        else "(no staged diff)\n\n--- git status -sb ---\n" + (git_status_sb or "(unknown)")
    )
    prompt_parts = [
        "You are an advice-only assistant for a deterministic AI workflow repo. Give brief, actionable advice.",
        "",
        "--- workflow/STATE.md ---",
        state_text,
        "",
        "--- workflow/TASK_QUEUE.md ---",
        task_text,
        "",
        "--- staged diff (git diff --staged) ---",
        staged_section,
    ]
    if route_json_text:
        prompt_parts.extend(["", "--- wf route output (JSON) ---", route_json_text])
    prompt_parts.extend(["", "---", "Provide short advice for the next step (do not modify files)."])

    prompt = "\n".join(prompt_parts)

    ollama = subprocess.run(
        ["ollama", "run", args.model],
        cwd=root,
        input=prompt,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if ollama.returncode != 0:
        print(ollama.stderr or "ollama run failed", file=sys.stderr)
        return 1

    advice = (ollama.stdout or "").strip()

    if args.write_advice:
        advice_path = root / "workflow" / "ADVICE.md"
        advice_path.write_text(advice + "\n", encoding="utf-8")
        return 0

    print(advice)
    return 0


if __name__ == "__main__":
    sys.exit(main())
