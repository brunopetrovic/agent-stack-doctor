# Hermes Agent Integration Example

This example demonstrates how to integrate `agent-stack-doctor` into a **Hermes** agent pipeline.

Hermes agents often rely on environment variables, background tasks (crons) for monitoring, and specific model routing rules (e.g., ensuring secondary reasoning isn't leaking costly premium calls).

## Files in this Example
- `.env`: A sample environment file containing both valid configurations and common placeholder mistakes.
- `routing-config.yaml`: The current model routing configuration for the Hermes agent.
- `routing-policy.yaml`: The policy rules defining constraints on which models can be used.

## Usage

### 1. Check Credentials
To check for missing or placeholder credentials (such as `<INSERT_KEY>` or empty values):
```bash
agent-doctor credentials --env-file .env
```

### 2. Verify Routing Policies
Ensure your Hermes routing configuration adheres to security or billing policies:
```bash
agent-doctor routing --config routing-config.yaml --policy routing-policy.yaml
```

### 3. Integrated CI/CD Check
Add `agent-doctor` to your pre-commit hooks or GitHub actions to prevent deploying with local placeholders:
```yaml
# .github/workflows/ci.yml
- name: Run Agent Stack Doctor
  run: |
    pip install agent-doctor
    agent-doctor scan --root ./
```
