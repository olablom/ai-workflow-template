#!/usr/bin/env python3
"""
Bootstrap workflow placeholders for a new project created from the template.
Updates only existing placeholders; does not remove or rewrite structure.
"""
import argparse
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Initialize workflow placeholders for a new project."
    )
    parser.add_argument(
        "--project",
        required=True,
        metavar="NAME",
        help="Project name to set in workflow placeholders.",
    )
    args = parser.parse_args()
    project_name = args.project
    root = repo_root()

    updated: list[str] = []

    # 1) workflow/STATE.md: replace project placeholder variants
    state_path = root / "workflow" / "STATE.md"
    if state_path.exists():
        text = state_path.read_text(encoding="utf-8")
        original = text
        for placeholder in ("<project name>", "<project_name>", "<project>"):
            if placeholder in text:
                text = text.replace(placeholder, project_name)
        if text != original:
            state_path.write_text(text, encoding="utf-8", newline="\n")
            updated.append(str(state_path))

    # 2) workflow/SESSION_HEADER.md: replace exactly "P: <project>"
    session_path = root / "workflow" / "SESSION_HEADER.md"
    if session_path.exists():
        text = session_path.read_text(encoding="utf-8")
        if "P: <project>" in text:
            text = text.replace("P: <project>", f"P: {project_name}")
            session_path.write_text(text, encoding="utf-8", newline="\n")
            updated.append(str(session_path))

    # 3) workflow/TASK_QUEUE.md: only replace "- <active task>"
    task_path = root / "workflow" / "TASK_QUEUE.md"
    if task_path.exists():
        text = task_path.read_text(encoding="utf-8")
        if "- <active task>" in text:
            text = text.replace("- <active task>", "- Initialize project")
            task_path.write_text(text, encoding="utf-8", newline="\n")
            updated.append(str(task_path))

    # Summary
    print("Bootstrap complete")
    print(f"Project: {project_name}")
    if updated:
        print("Files updated:")
        for p in updated:
            print(f"  - {p}")
    else:
        print("No changes made (placeholders not found or already set).")


if __name__ == "__main__":
    main()
