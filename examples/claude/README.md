# Claude Agent & MCP Skill Validation Example

Claude agents, especially those using Model Context Protocol (MCP) or tool-calling frameworks, require structured documentation of their tools and skills.

Using `agent-stack-doctor`, you can validate `SKILL.md` files (which describe capabilities to the LLM agent) to ensure they have correct YAML frontmatter, valid names, and description fields before starting the agent session.

## Files in this Example
- `skills/git_ops/SKILL.md`: A well-formed skill definition.
- `skills/db_query/SKILL.md`: A malformed skill definition missing the required description key.

## Usage

### Validate Skills Directory
Run the skills scanner on the local skills directory:
```bash
agent-doctor skills --skills-dir ./skills
```

### Typical Frontmatter Format
Each `SKILL.md` file must start with a YAML frontmatter block:
```markdown
---
name: my-skill-name
description: Clear, action-oriented description of when to use this skill.
version: 1.0.0
author: Developer
---
# Instructions
Detailed system instructions for the model...
```
