# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-06-01

### Added
- Initial release of `agent-stack-doctor` (packaged as `agent-doctor`).
- **Credentials Scanner**: Detect placeholder/fake API keys and missing keys in `.env` files.
- **Routing Scanner**: Match routing policies with configurations to prevent premium-provider leakage.
- **Cron Scanner**: Detect stale outputs, missing no-agent script references, and delivery issues.
- **Memory Scanner**: Verify character budget consumption in markdown-based agent memory systems.
- **Skills Scanner**: Validate `SKILL.md` frontmatter formatting (YAML schema).
- Unified CLI `agent-doctor scan` for auto-discovering and running all checks.
- Support for JSON output (`--format json`) for CI/CD integrations.
