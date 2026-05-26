"""
Cron/job drift checker – inspects jobs JSON and optional output artifacts to
detect stale outputs, missing no-agent scripts, and delivery anomalies.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class CronFinding:
    job_id: str
    severity: str  # "error" | "warning" | "info"
    message: str
    evidence: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class CronReport:
    file_path: str
    findings: list[CronFinding] = field(default_factory=list)
    jobs_total: int = 0
    jobs_enabled: int = 0


def _parse_timestamp(raw: str) -> datetime | None:
    formats = [
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(raw.strip(), fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    return None


def check_cron(jobs_path: Path, output_dir: Path | None = None) -> CronReport:
    """
    Parse a jobs JSON file and optionally check corresponding output artifacts.
    Flags:
      - enabled jobs whose latest output is stale (>24 h)
      - enabled jobs with no output at all
      - enabled jobs missing no-agent script references
      - jobs with no output file when one is expected
    """
    report = CronReport(file_path=str(jobs_path))

    data = json.loads(jobs_path.read_text(encoding="utf-8", errors="replace"))
    jobs = data if isinstance(data, list) else data.get("jobs", [data])

    report.jobs_total = len(jobs)
    report.jobs_enabled = sum(1 for j in jobs if j.get("enabled", True))

    now = datetime.now(timezone.utc)

    for job in jobs:
        job_id = job.get("id", job.get("name", "unknown"))
        enabled = job.get("enabled", True)
        last_run = job.get("last_run") or job.get("lastScheduledRun")
        script = job.get("script") or job.get("command") or job.get("handler")

        if not enabled:
            continue

        # Missing no-agent script
        if not script:
            report.findings.append(
                CronFinding(
                    job_id=job_id,
                    severity="error",
                    message=f"Job '{job_id}' is enabled but has no script/command/handler field",
                    evidence={},
                )
            )

        # Check output staleness
        if output_dir and last_run:
            ts = _parse_timestamp(str(last_run))
            if ts:
                age_h = (now - ts).total_seconds() / 3600
                if age_h > 24:
                    report.findings.append(
                        CronFinding(
                            job_id=job_id,
                            severity="warning",
                            message=f"Job '{job_id}' output is stale (last run {age_h:.1f} h ago)",
                            evidence={"last_run": str(last_run), "age_hours": round(age_h, 1)},
                        )
                    )

        # Check expected output files
        if output_dir:
            output_files = job.get("outputs") or job.get("output_files") or []
            for out_file in output_files:
                out_path = output_dir / str(out_file).lstrip("/")
                if not out_path.exists():
                    report.findings.append(
                        CronFinding(
                            job_id=job_id,
                            severity="error",
                            message=f"Job '{job_id}' declares output '{out_file}' but it does not exist",
                            evidence={"missing_file": str(out_path)},
                        )
                    )

    return report