"""
Skills schema validator – checks SKILL.md frontmatter shape and required fields.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class SkillFinding:
    file_path: str
    severity: str  # "error" | "warning" | "info"
    message: str
    evidence: dict = field(default_factory=dict)


@dataclass
class SkillReport:
    files: list[SkillFinding] = field(default_factory=list)
    skills_valid: int = 0
    skills_total: int = 0


REQUIRED_FRONT_MATTER_KEYS = {"name", "description"}
OPTIONAL_FRONT_MATTER_KEYS = {"version", "author", "tags", "examples", "inputs", "outputs"}


def check_skills(skills_dir: Path) -> SkillReport:
    """
    Recursively find SKILL.md files and validate their YAML frontmatter.
    """
    report = SkillReport()

    for md_file in skills_dir.rglob("SKILL.md"):
        report.skills_total += 1
        findings = _check_skill_file(md_file)
        if findings:
            report.files.extend(findings)
        else:
            report.skills_valid += 1

    return report


def _check_skill_file(path: Path) -> list[SkillFinding]:
    findings: list[SkillFinding] = []
    raw = path.read_text(encoding="utf-8", errors="replace")

    # Strip code fences
    raw = re.sub(r"^```[\w]*\n", "", raw, flags=re.MULTILINE)
    raw = raw.lstrip()

    if not raw.startswith("---"):
        findings.append(
            SkillFinding(
                file_path=str(path),
                severity="error",
                message="SKILL.md is missing YAML frontmatter (no '---' delimiter)",
                evidence={},
            )
        )
        return findings

    end = raw.find("\n---", 3)
    if end == -1:
        findings.append(
            SkillFinding(
                file_path=str(path),
                severity="error",
                message="SKILL.md frontmatter is not closed with '---'",
                evidence={},
            )
        )
        return findings

    fm_raw = raw[3:end].strip()
    try:
        fm = yaml.safe_load(fm_raw) or {}
    except yaml.YAMLError as exc:
        findings.append(
            SkillFinding(
                file_path=str(path),
                severity="error",
                message=f"Invalid YAML frontmatter: {exc}",
                evidence={"raw": fm_raw[:200]},
            )
        )
        return findings

    if not isinstance(fm, dict):
        findings.append(
            SkillFinding(
                file_path=str(path),
                severity="error",
                message="Frontmatter is not a YAML dict",
                evidence={"type": type(fm).__name__},
            )
        )
        return findings

    # Check required keys
    missing = REQUIRED_FRONT_MATTER_KEYS - fm.keys()
    if missing:
        findings.append(
            SkillFinding(
                file_path=str(path),
                severity="error",
                message=f"Missing required frontmatter keys: {sorted(missing)}",
                evidence={"missing": sorted(missing)},
            )
        )

    # Check name is non-empty
    if "name" in fm:
        name_val = fm["name"]
        if not isinstance(name_val, str) or not name_val.strip():
            findings.append(
                SkillFinding(
                    file_path=str(path),
                    severity="error",
                    message="The 'name' field must be a non-empty string",
                    evidence={"name": name_val},
                )
            )

    # Warn about unknown top-level keys (not an error, just informational)
    unknown = set(fm.keys()) - (REQUIRED_FRONT_MATTER_KEYS | OPTIONAL_FRONT_MATTER_KEYS)
    if unknown:
        findings.append(
            SkillFinding(
                file_path=str(path),
                severity="info",
                message=f"Unknown frontmatter keys (ignored): {sorted(unknown)}",
                evidence={"unknown": sorted(unknown)},
            )
        )

    return findings