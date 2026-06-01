# LangGraph Memory & State Budget Check

LangGraph applications maintain active agent states and checkpoint histories. To prevent exceeding context limits (which degrades performance or increases costs), you can monitor character counts in your text-based memory or log dumps.

This example illustrates checking:
1. `memory/memory.md`: The agent's persistent memory file.
2. `memory/user.md`: The cached user profile state.

## Files in this Example
- `memory/memory.md`: A small memory file within budget.
- `memory/user.md`: An oversized user state file exceeding budget limits.

## Usage

### Run Memory Diagnostic
To check if memory files are approaching limits:
```bash
agent-doctor memory --memory-file memory/memory.md --user-file memory/user.md --limits 5000,1000
```
This sets a memory limit of 5,000 characters and a user profile limit of 1,000 characters.

If the file exceeds 80% of the limit, a warning is raised. If it exceeds 95%, an error is raised.
