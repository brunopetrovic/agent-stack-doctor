"""
Credentials checker – parses env-like files and reports key status without exposing values.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator


@dataclass
class CredentialKey:
    key: str
    status: str  # "set" | "placeholder" | "missing"
    line: int = 0


@dataclass
class CredentialReport:
    file_path: str
    keys: list[CredentialKey] = field(default_factory=list)

    @property
    def placeholders(self) -> list[CredentialKey]:
        return [k for k in self.keys if k.status == "placeholder"]

    @property
    def missing(self) -> list[CredentialKey]:
        return [k for k in self.keys if k.status == "missing"]

    @property
    def set_keys(self) -> list[CredentialKey]:
        return [k for k in self.keys if k.status == "set"]


_Placeholder_re = re.compile(
    r"^\s*(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*"
    r"(?P<value>"
    r"['\"][Ff][Aa][Kk][Ee]['\"]"   # "Fake", 'Fake', 'FAKE', etc.
    r"|<[^>]+>"                      # <placeholder>, <INSERT_KEY>, etc.
    r"|\{\{.*\}\}"                   # {{ ... }}
    r"|\$\{.*\}"                     # ${ ... }
    r"|['\"]?(?:NULL|null|None|NONE|CHANGE[_-]ME.*|TODO.*|REPLACE[_-]ME.*|YOUR[_-]KEY[_-]HERE|YOUR[_-]API[_-]KEY|INSERT[_-]KEY[_-]HERE|INSERT[_-]API[_-]KEY|YOUR_.*_HERE|your_.*_here)['\"]?"
    r"|['\"]{2}"                    # empty quotes "" or ''
    r"|['\"]?[xX]{4,}['\"]?"         # xxxx or XXXXXX
    r"|['\"]?123456+['\"]?"          # 123456
    r"|\s*"                          # empty or whitespace
    r")$",
    re.IGNORECASE,
)

_Set_re = re.compile(
    r"^\s*(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>.+)$",
)


def _iter_lines(path: Path) -> Iterator[tuple[int, str]]:
    with path.open("r", encoding="utf-8", errors="replace") as fh:
        for lineno, line in enumerate(fh, start=1):
            yield lineno, line


def check_file(path: Path, required_keys: list[str] | None = None) -> CredentialReport:
    """
    Parse an env / dotenv-style file and return a report.

    required_keys: extra keys (beyond those present in the file) to flag as missing.
    """
    report = CredentialReport(file_path=str(path))

    seen: set[str] = set()

    for lineno, line in _iter_lines(path):
        # strip comments
        stripped = line.split("#")[0]
        if _Placeholder_re.match(stripped):
            m = _Placeholder_re.match(stripped)
            assert m is not None
            key = m.group("key")
            seen.add(key)
            report.keys.append(CredentialKey(key=key, status="placeholder", line=lineno))
        elif _Set_re.match(stripped):
            m = _Set_re.match(stripped)
            assert m is not None
            key = m.group("key")
            value = m.group("value").strip()
            # empty value counts as placeholder
            if not value:
                status = "placeholder"
            else:
                status = "set"
            seen.add(key)
            report.keys.append(CredentialKey(key=key, status=status, line=lineno))

    if required_keys:
        for key in required_keys:
            if key not in seen:
                report.keys.append(CredentialKey(key=key, status="missing", line=0))

    return report