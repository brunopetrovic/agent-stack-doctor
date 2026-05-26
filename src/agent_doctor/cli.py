"""
agent-doctor CLI – top-level entry-point.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .credentials import check_file as check_credentials
from .cron import check_cron
from .memory import check_memory
from .report import Finding, Report
from .routing import check_routing
from .skills import check_skills


def _severity_map(severity: str) -> str:
    """Map internal severity to confidence."""
    if severity == "error":
        return "high"
    if severity == "warning":
        return "medium"
    return "low"


def cmd_scan(args: argparse.Namespace) -> int:
    root = Path(args.root)
    if not root.exists():
        print(f"Error: root path does not exist: {root}", file=sys.stderr)
        return 1

    report = Report(scanner="agent-doctor scan")
    exit_code = 0

    # Auto-discover and run each scanner
    env_file = root / ".env"
    if env_file.exists():
        cred_report = check_credentials(env_file)
        for ck in cred_report.placeholders:
            report.add_finding(
                Finding(
                    source="credentials",
                    severity="warning",
                    confidence="high",
                    message=f"Placeholder value detected for key '{ck.key}' in {env_file.name}",
                    evidence={"key": ck.key, "line": ck.line},
                    remediation="Replace with a real credential or env var",
                )
            )
        for ck in cred_report.missing:
            report.add_finding(
                Finding(
                    source="credentials",
                    severity="error",
                    confidence="high",
                    message=f"Required key '{ck.key}' is missing from {env_file.name}",
                    evidence={"key": ck.key},
                    remediation=f"Add {ck.key}=<value> to {env_file.name}",
                )
            )

    # skills dir
    skills_dir = root / "skills"
    if skills_dir.is_dir():
        skill_report = check_skills(skills_dir)
        for sf in skill_report.files:
            report.add_finding(
                Finding(
                    source="skills",
                    severity=sf.severity,
                    confidence="high",
                    message=sf.message,
                    evidence=sf.evidence,
                    remediation="Fix the SKILL.md frontmatter",
                )
            )

    # memory files
    memory_file = root / "memory" / "memory.md"
    user_file = root / "memory" / "user.md"
    if memory_file.exists():
        mem_report, mem_stats = check_memory(memory_file, user_file if user_file.exists() else None, limits=args.memory_limits)
        for mf in mem_report.files:
            report.add_finding(
                Finding(
                    source="memory",
                    severity=mf.severity,
                    confidence="high",
                    message=mf.message,
                    evidence=mf.evidence,
                    remediation="Prune old entries from memory or increase budget",
                )
            )

    if not report.findings:
        print("No issues found.")
        return 0

    if args.format == "json":
        print(report.render_json())
    else:
        print(report.render_text())
    return exit_code


def cmd_credentials(args: argparse.Namespace) -> int:
    cred_report = check_credentials(Path(args.env_file))
    report = Report(scanner="credentials")

    for ck in cred_report.placeholders:
        report.add_finding(
            Finding(
                source="credentials",
                severity="warning",
                confidence="high",
                message=f"Placeholder value for key '{ck.key}' (line {ck.line})",
                evidence={"key": ck.key, "line": ck.line},
                remediation="Replace with a real value",
            )
        )
    for ck in cred_report.missing:
        report.add_finding(
            Finding(
                source="credentials",
                severity="error",
                confidence="high",
                message=f"Required key '{ck.key}' is missing",
                evidence={"key": ck.key},
                remediation=f"Add {ck.key}=<value>",
            )
        )

    if not report.findings:
        print("No credential issues found.")
        return 0

    if args.format == "json":
        print(report.render_json())
    else:
        print(report.render_text())
    return 1 if report.findings else 0


def cmd_routing(args: argparse.Namespace) -> int:
    routing_report = check_routing(Path(args.config), Path(args.policy))
    report = Report(scanner="routing")

    for rf in routing_report.findings:
        report.add_finding(
            Finding(
                source="routing",
                severity=rf.severity,
                confidence="high",
                message=rf.message,
                evidence=rf.evidence,
                remediation="Review routing policy constraints",
            )
        )

    if not report.findings:
        print("No routing issues found.")
        return 0

    if args.format == "json":
        print(report.render_json())
    else:
        print(report.render_text())
    return 1 if report.findings else 0


def cmd_cron(args: argparse.Namespace) -> int:
    output_dir = Path(args.output_dir) if args.output_dir else None
    cron_report = check_cron(Path(args.jobs), output_dir)
    report = Report(scanner="cron")

    for cf in cron_report.findings:
        report.add_finding(
            Finding(
                source="cron",
                severity=cf.severity,
                confidence="high",
                message=cf.message,
                evidence=cf.evidence,
                remediation="Fix the cron job configuration",
            )
        )

    if not report.findings:
        print(f"No cron issues found. ({cron_report.jobs_enabled}/{cron_report.jobs_total} jobs enabled)")
        return 0

    if args.format == "json":
        print(report.render_json())
    else:
        print(report.render_text())
    return 1 if report.findings else 0


def cmd_memory(args: argparse.Namespace) -> int:
    user_file = Path(args.user_file) if args.user_file else None
    limits = None
    if args.limits:
        parts = args.limits.split(",")
        if len(parts) == 2:
            limits = (int(parts[0]), int(parts[1]))

    mem_report, mem_stats = check_memory(Path(args.memory_file), user_file, limits=limits)
    report = Report(scanner="memory")

    for mf in mem_report.files:
        report.add_finding(
            Finding(
                source="memory",
                severity=mf.severity,
                confidence="high",
                message=mf.message,
                evidence=mf.evidence,
                remediation="Prune memory or increase budget",
            )
        )

    # Print stats
    for stat in mem_stats:
        print(f"  {stat.char_count}/{stat.limit} chars ({stat.pct}%)")

    if not report.findings:
        print("Memory budget OK.")
        return 0

    if args.format == "json":
        print(report.render_json())
    else:
        print(report.render_text())
    return 1 if report.findings else 0


def cmd_skills(args: argparse.Namespace) -> int:
    skill_report = check_skills(Path(args.skills_dir))
    report = Report(scanner="skills")

    for sf in skill_report.files:
        report.add_finding(
            Finding(
                source="skills",
                severity=sf.severity,
                confidence="high",
                message=sf.message,
                evidence=sf.evidence,
                remediation="Fix the SKILL.md frontmatter",
            )
        )

    print(f"Skills: {skill_report.skills_valid}/{skill_report.skills_total} valid")

    if not report.findings:
        print("No skill schema issues found.")
        return 0

    if args.format == "json":
        print(report.render_json())
    else:
        print(report.render_text())
    return 1 if report.findings else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agent-doctor", description="AI Agent Stack Doctor – diagnose configuration failures before they bite.")
    parser.add_argument("--format", "-f", choices=["text", "json"], default="text", help="Output format")

    sub = parser.add_subparsers(dest="command", required=True)

    def add_format_option(p: argparse.ArgumentParser) -> None:
        # Accept `--format` after the subcommand too, matching the README and
        # common CLI muscle memory. SUPPRESS preserves the top-level default
        # when the subcommand-local option is omitted.
        p.add_argument("--format", "-f", choices=["text", "json"], default=argparse.SUPPRESS, help="Output format")

    # scan
    p_scan = sub.add_parser("scan", help="Scan entire project root")
    add_format_option(p_scan)
    p_scan.add_argument("--root", required=True, help="Project root directory")
    p_scan.add_argument("--memory-limits", help="Comma-separated memory,user char limits (e.g. 10000,5000)")
    p_scan.set_defaults(func=cmd_scan)

    # credentials
    p_cred = sub.add_parser("credentials", help="Check env file for placeholder/missing keys")
    add_format_option(p_cred)
    p_cred.add_argument("--env-file", required=True, help="Path to .env file")
    p_cred.set_defaults(func=cmd_credentials)

    # routing
    p_route = sub.add_parser("routing", help="Check routing config against policy")
    add_format_option(p_route)
    p_route.add_argument("--config", required=True, help="Routing config file (YAML/JSON)")
    p_route.add_argument("--policy", required=True, help="Routing policy file (YAML/JSON)")
    p_route.set_defaults(func=cmd_routing)

    # cron
    p_cron = sub.add_parser("cron", help="Check cron/jobs configuration")
    add_format_option(p_cron)
    p_cron.add_argument("--jobs", required=True, help="Path to jobs JSON file")
    p_cron.add_argument("--output-dir", help="Directory containing job output artifacts")
    p_cron.set_defaults(func=cmd_cron)

    # memory
    p_mem = sub.add_parser("memory", help="Check memory file char budgets")
    add_format_option(p_mem)
    p_mem.add_argument("--memory-file", required=True, help="Path to memory file")
    p_mem.add_argument("--user-file", help="Path to user file")
    p_mem.add_argument("--limits", help="Comma-separated memory,user char limits")
    p_mem.set_defaults(func=cmd_memory)

    # skills
    p_skills = sub.add_parser("skills", help="Validate SKILL.md files")
    add_format_option(p_skills)
    p_skills.add_argument("--skills-dir", required=True, help="Directory containing SKILL.md files")
    p_skills.set_defaults(func=cmd_skills)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover - exercised by CLI subprocess tests
    raise SystemExit(main())