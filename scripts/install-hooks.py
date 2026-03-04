#!/usr/bin/env python3
"""Set git core.hooksPath to .githooks so versioned hooks run. Stdlib only."""
import subprocess
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    result = subprocess.run(
        ["git", "config", "core.hooksPath", ".githooks"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(result.stderr or "git config failed", file=sys.stderr)
        return 1
    print("Set core.hooksPath to .githooks. Pre-commit will run scripts/wf.py commit-check.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
