# Agent Stack Doctor

**AI agents fail in boring ways:** expired keys, wrong fallback routes, zombie crons, memory bloat, and broken prompt-skill files. Agent Stack Doctor catches that locally before your agent silently rots.

```
pip install agent-doctor
agent-doctor scan --root ./my-agent-project
```

## Features

- **Credentials** – parse `.env` files, flag placeholder/fake values, detect missing required keys
- **Routing** – compare routing config against policy, catch premium-provider leakage into auxiliary routes
- **Cron** – detect stale job outputs, missing no-agent scripts, delivery anomalies
- **Memory** – track character budget consumption, warn at >80%, error at >95%
- **Skills** – validate `SKILL.md` frontmatter shape and required fields

## CLI

```
agent-doctor scan --root PATH [--format text|json]
agent-doctor credentials --env-file PATH [--format text|json]
agent-doctor routing --config PATH --policy PATH [--format text|json]
agent-doctor cron --jobs PATH [--output-dir PATH] [--format text|json]
agent-doctor memory --memory-file PATH [--user-file PATH] [--limits 10000,5000] [--format text|json]
agent-doctor skills --skills-dir PATH [--format text|json]
```

## Install

```bash
pip install -e .
# or
pip install agent-doctor
```

## Develop

```bash
pip install -e ".[dev]"
pytest
```

## Design Principles

- **No secrets ever printed or copied** – all credential values are redacted; only key names are reported
- **Standalone** – zero external runtime dependencies beyond PyYAML; no network calls, no auth files imported
- **Fail loud** – exits 1 when issues are found so it works in CI/CD pipelines