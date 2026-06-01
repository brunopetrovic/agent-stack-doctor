# Agent Stack Doctor – Integration Examples

This directory contains practical, lightweight examples demonstrating how to integrate `agent-stack-doctor` (packaged as `agent-doctor`) into various LLM Agent frameworks and developer workflows.

## Examples Directory

1. **[Hermes Agent Integration](file:///home/unc/projects/agent-stack-doctor/examples/hermes/README.md)**
   - Demonstrates credential scanning and routing policy enforcement (e.g. avoiding premium model leakage) in Hermes pipelines.
   - Files: `.env`, `routing-config.yaml`, `routing-policy.yaml`.

2. **[Claude & MCP Skill Validation](file:///home/unc/projects/agent-stack-doctor/examples/claude/README.md)**
   - Shows how to recursively validate YAML frontmatter schemas for `SKILL.md` files used by Claude desktop or custom MCP servers.
   - Files: `skills/git_ops/SKILL.md`, `skills/db_query/SKILL.md`.

3. **[Cursor Rules Integration](file:///home/unc/projects/agent-stack-doctor/examples/cursor/README.md)**
   - Illustrates using editor instruction sets via `.cursorrules` to instruct the assistant models to avoid config corruption and auto-verify states.
   - Files: `.cursorrules`.

4. **[LangGraph Memory & State Budgets](file:///home/unc/projects/agent-stack-doctor/examples/langgraph/README.md)**
   - Shows how to verify that character/context windows for memory checkpointers do not exceed maximum context budgets.
   - Files: `memory/memory.md`, `memory/user.md`.

5. **[Codex Job Scheduler Diagnostics](file:///home/unc/projects/agent-stack-doctor/examples/codex/README.md)**
   - Demonstrates checking for stale background runs, missing output files, and invalid job script mappings.
   - Files: `jobs.json`, `job_outputs/`.
