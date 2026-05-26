"""
Shared Finding dataclass and report rendering (text + JSON).
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class Finding:
    source: str  # "credentials" | "routing" | "cron" | "memory" | "skills"
    severity: str  # "error" | "warning" | "info"
    confidence: str  # "high" | "medium" | "low"
    message: str
    evidence: dict[str, Any] = field(default_factory=dict)
    remediation: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def render_text(self) -> str:
        evidence_str = ""
        if self.evidence:
            ev = ", ".join(f"{k}={v!r}" for k, v in self.evidence.items())
            evidence_str = f"  Evidence: {ev}\n"
        return (
            f"[{self.severity.upper():^8}] ({self.confidence}) {self.message}\n"
            f"{evidence_str}"
            f"  Remediation: {self.remediation}\n"
        )


@dataclass
class Report:
    scanner: str
    findings: list[Finding] = field(default_factory=list)
    summary: dict[str, int] = field(default_factory=dict)  # severity counts

    def add_finding(self, finding: Finding) -> None:
        self.findings.append(finding)
        key = finding.severity
        self.summary[key] = self.summary.get(key, 0) + 1

    def render_text(self) -> str:
        lines = [f"=== {self.scanner} Report ==="]
        if not self.findings:
            lines.append("  No issues found.")
            return "\n".join(lines)
        for f in self.findings:
            lines.append(f.render_text())
        lines.append(f"\nSummary: {self.summary}")
        return "\n".join(lines)

    def render_json(self) -> str:
        return json.dumps(
            {"scanner": self.scanner, "findings": [f.to_dict() for f in self.findings], "summary": self.summary},
            indent=2,
        )