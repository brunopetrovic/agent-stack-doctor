# Agent Stack Doctor 🩺

[![CI](https://github.com/brunopetrovic/agent-stack-doctor/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/brunopetrovic/agent-stack-doctor/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**AI agents fail in silent, boring, and costly ways:** expired/placeholder API keys, zombie cron tasks, memory/context window bloat, and malformed prompt/skill files.

`agent-stack-doctor` (packaged as `agent-doctor`) is a lightweight, low-dependency, local-first **Agent Ops diagnostic wedge** that detects configuration drift and runtime anomalies before your agents silently rot.

```bash
pip install agent-doctor

# Run a complete diagnostic check of your agent project
agent-doctor scan --root ./my-agent-project
```

---

## 🔍 Features

*   **🔑 Credentials** – Scans environment files (e.g., `.env`), flags placeholder/mock keys (`TODO`, `CHANGE_ME`, `<INSERT_KEY>`), detects missing keys, and *never* logs or prints actual secret values.
*   **🚦 Routing** – Validates routing configs against policies. Prevents expensive premium-provider leakage (like GPT-4/Claude Sonnet) into secondary or auxiliary routes.
*   **⏰ Cron & Background Jobs** – Audits job runner configurations, detects stale/zombie background tasks, alerts if expected output artifacts are missing, and flags jobs missing scripting entry points.
*   **🧠 Memory Budgets** – Audits character/token budget consumption for text-based memory systems (like markdown checkpoints), warning you before your agent hits context window limits.
*   **🛠️ Skills** – Recursively validates the YAML frontmatter schema for skill definitions (`SKILL.md`), ensuring that agents have a valid name and description.

---

## 🛠️ CLI Usage

Scan a project root or run targeted checks on individual files:

```bash
# Run all diagnostics across a project root
agent-doctor scan --root PATH [--format json]

# Validate environment credentials
agent-doctor credentials --env-file PATH [--format json]

# Check routing configuration alignment
agent-doctor routing --config PATH --policy PATH [--format json]

# Audit background cron tasks
agent-doctor cron --jobs PATH [--output-dir PATH] [--format json]

# Analyze memory context budgets
agent-doctor memory --memory-file PATH [--user-file PATH] [--limits 10000,5000] [--format json]

# Validate skill description frontmatter
agent-doctor skills --skills-dir PATH [--format json]
```

### Fail-Loud Philosophy
To integrate smoothly into CI/CD pipelines, `agent-doctor` adheres to a **fail-loud** approach: it prints structured error messages and exits with code `1` if issues are found, making it easy to block bad builds.

---

## 💡 Integration Examples

We have created lightweight, practical examples demonstrating how to hook `agent-stack-doctor` into common agent stacks and developer tools:

*   **[Hermes Agent Configuration](examples/hermes/)**: Validate API keys and prevent premium model leakage in Hermes pipelines.
*   **[Claude & MCP Skills](examples/claude/)**: Ensure skill descriptions used by Claude or MCP servers comply with schema rules.
*   **[Cursor rules](examples/cursor/)**: Add rules to Cursor to prevent code generators from outputting dummy API placeholders.
*   **[LangGraph Memory Control](examples/langgraph/)**: Warn when LangGraph state checkpoints approach context limits.
*   **[Codex Task Runner](examples/codex/)**: Monitor scheduled batch runs and output logs.

For detailed walk-throughs, see the **[Examples Directory](examples/)**.

---

## 🚀 Quick Start

### Installation

```bash
# Local development install
pip install -e .

# Or from source/PyPI
pip install agent-doctor
```

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run test suite
pytest
```

---

## 🛡️ Design Principles

1.  **No Secret-Value Output By Design** – Secret values are redacted. The scanner reports key names, presence, and placeholder status instead of printing credential values.
2.  **No Network Overhead** – Operates 100% offline. Zero external API calls, tracking, or remote telemetry.
3.  **Standalone CLI** – Minimal runtime dependencies beyond standard YAML parsing (`PyYAML`). Fast, clean, and easy to audit.

---

## 📄 License & Security

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
For security-related issues, please refer to our [Security Policy](SECURITY.md).