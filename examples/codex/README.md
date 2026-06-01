# Codex Environment Integration Example

Codex environments (for large-scale code generation and execution) rely heavily on background workers and cron jobs to schedule batch evaluations, clean up resources, and compile code.

Using `agent-stack-doctor`, you can run periodic validation on these scheduler queues to catch jobs that are silent/failing or running outdated scripts.

## Files in this Example
- `jobs.json`: A task schedule for batch execution, with some cron outputs defined.
- `job_outputs/`: Directory representing where job logs/reports are outputted.

## Usage

### Run Cron / Scheduler Diagnostic
```bash
agent-doctor cron --jobs jobs.json --output-dir ./job_outputs
```

This checks:
1. If every enabled job points to an actual script / handler.
2. If any output file declared in `jobs.json` is missing from `output-dir`.
3. If the `last_run` timestamp for any job is more than 24 hours old.
