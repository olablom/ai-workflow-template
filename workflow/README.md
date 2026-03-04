This directory contains the persistent AI workflow state.

Files:

PROJECT_CONTEXT.md
Defines the stable project definition.

SESSION_HEADER.md
Defines the current session state.

DECISIONS_LOG.md
Chronological record of decisions.

TASK_QUEUE.md
Tracks active, next and completed tasks.

Update rules:

- PROJECT_CONTEXT changes rarely
- SESSION_HEADER every session
- DECISIONS_LOG when decisions occur
- TASK_QUEUE when tasks move
