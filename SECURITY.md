# Security Policy

## Supported Versions

The following versions of `agent-stack-doctor` (packaged as `agent-doctor`) are currently supported with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1.0 | :x:                |

## Reporting a Vulnerability

We take the security of `agent-stack-doctor` seriously. If you find a vulnerability that could leak secrets, misclassify sensitive credentials, or produce unsafe diagnostic output, please do **not** open a public issue with exploit details.

Use GitHub's private vulnerability reporting flow if enabled, or contact the repository owner privately through the GitHub profile.

In your report, please include:
- A description of the vulnerability.
- A proof of concept (PoC) or steps to reproduce the issue.
- The potential impact of the vulnerability.

We will acknowledge receipt when possible and provide a fix timeline based on severity.

## Secret-Value Handling

`agent-stack-doctor` is designed as a local-only CLI tool that:
1. Reports credential key names, presence, and placeholder status without intentionally printing credential values.
2. Does not make network requests or send telemetry.
3. Operates completely offline.

If you find a path where a credential value is printed, treat it as a security bug.
