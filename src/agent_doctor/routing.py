"""
Routing policy checker – parses config/policy YAML or JSON and detects
premium-provider leakage and other routing misconfigurations.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterator


@dataclass
class RoutingFinding:
    rule_id: str
    severity: str  # "error" | "warning" | "info"
    message: str
    evidence: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class RoutingReport:
    file_path: str
    findings: list[RoutingFinding] = field(default_factory=list)


def _iter_lines(path: Path) -> Iterator[tuple[int, str]]:
    with path.open("r", encoding="utf-8", errors="replace") as fh:
        for lineno, line in enumerate(fh, start=1):
            yield lineno, line


def load_config(path: Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8", errors="replace")
    if path.suffix in (".yaml", ".yml"):
        try:
            import yaml  # type: ignore
            return yaml.safe_load(raw) or {}
        except Exception:
            return {"__raw": raw}
    elif path.suffix == ".json":
        return json.loads(raw)
    else:
        # try both
        try:
            import yaml  # type: ignore
            return yaml.safe_load(raw) or {}
        except Exception:
            return json.loads(raw)


def _normalize_provider(provider: str) -> str:
    """Strip version/model suffixes to get provider family.

    Handles provider/model formats like:
      openai/gpt-4o        -> openai
      anthropic/claude-3-5 -> anthropic
      azure-gpt-35          -> azure
    """
    return re.split(r"[-_/]", provider.strip())[0].lower()


_PREMIUM_FAMILIES = {"openai", "anthropic", "cohere", "google", "azure"}


def check_routing(config_path: Path, policy_path: Path) -> RoutingReport:
    """
    Compare a routing config against a policy file.
    Detects:
      - premium providers used in auxiliary/non-primary routes
      - missing expected providers
      - unwanted provider/model substitutions
    """
    config = load_config(config_path)
    policy = load_config(policy_path)

    report = RoutingReport(file_path=str(config_path))

    # Extract routes from config (flexible structure)
    config_routes = _extract_routes(config)
    policy_routes = _extract_routes(policy)

    # Check each policy route
    for p_rule in policy_routes:
        rule_id = p_rule.get("id", "unknown")
        expected_provider = _normalize_provider(p_rule.get("provider", ""))
        route_type = p_rule.get("type", "standard")
        allowed_providers = [_normalize_provider(p) for p in p_rule.get("allowed_providers", [])]
        blocked_providers = [_normalize_provider(p) for p in p_rule.get("blocked_providers", [])]

        # Find matching config routes (by id or type)
        matching = [r for r in config_routes if r.get("id") == rule_id or r.get("type") == route_type]

        if not matching:
            # Expected route not found at all
            report.findings.append(
                RoutingFinding(
                    rule_id=rule_id,
                    severity="error",
                    message=f"Expected route '{rule_id}' (type={route_type}) not found in config",
                    evidence={"expected_provider": expected_provider},
                )
            )
            continue

        for route in matching:
            provider = _normalize_provider(route.get("provider", ""))

            # Check premium provider in auxiliary route
            if route_type == "auxiliary" and provider in _PREMIUM_FAMILIES:
                report.findings.append(
                    RoutingFinding(
                        rule_id=rule_id,
                        severity="error",
                        message=f"Premium provider '{provider}' used in auxiliary route '{rule_id}'",
                        evidence={"provider": provider, "route_type": route_type},
                    )
                )

            # Check blocked providers
            if blocked_providers and provider in blocked_providers:
                report.findings.append(
                    RoutingFinding(
                        rule_id=rule_id,
                        severity="error",
                        message=f"Blocked provider '{provider}' used in route '{rule_id}'",
                        evidence={"provider": provider, "blocked": blocked_providers},
                    )
                )

            # Check allowed providers constraint
            if allowed_providers and provider not in allowed_providers:
                report.findings.append(
                    RoutingFinding(
                        rule_id=rule_id,
                        severity="warning",
                        message=f"Provider '{provider}' not in allowed list for route '{rule_id}'",
                        evidence={"provider": provider, "allowed": allowed_providers},
                    )
                )

    return report


def _extract_routes(cfg: dict[str, Any]) -> list[dict[str, Any]]:
    """Walk a config/policy dict and collect route entries.

    Config route entries have a 'provider' key.
    Policy entries have 'allowed_providers'/'blocked_providers' keys.
    """
    routes: list[dict[str, Any]] = []

    def walk(obj: Any) -> None:
        if isinstance(obj, dict):
            if "provider" in obj or "allowed_providers" in obj or "blocked_providers" in obj:
                routes.append(obj)
            for v in obj.values():
                walk(v)
        elif isinstance(obj, list):
            for item in obj:
                walk(item)

    walk(cfg)
    return routes