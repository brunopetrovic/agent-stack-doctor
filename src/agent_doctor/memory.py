"""
Memory budget checker – reports character budget usage and warns when > 95 % consumed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class MemoryFinding:
    file_path: str
    severity: str  # "error" | "warning" | "info"
    message: str
    evidence: dict = None

    def __post_init__(self):
        if self.evidence is None:
            self.evidence = {}


@dataclass
class MemoryReport:
    files: list[MemoryFinding] = None

    def __post_init__(self):
        if self.files is None:
            self.files = []


@dataclass
class MemoryStats:
    char_count: int
    limit: int
    pct: float


def check_memory(
    memory_file: Path,
    user_file: Path | None = None,
    limits: tuple[int, int] | None = None,
) -> tuple[MemoryReport, list[MemoryStats]]:
    """
    Parse memory (and optional user) files and compute character budget vs limits.

    limits: (memory_limit, user_limit) as char counts.
    Returns (report, stats).
    """
    report = MemoryReport()
    stats: list[MemoryStats] = []

    memory_chars = _count_chars(memory_file)
    memory_limit = (limits[0] if limits else 10000) if limits else 10000
    mem_pct = (memory_chars / memory_limit * 100) if memory_limit else 0
    stats.append(MemoryStats(char_count=memory_chars, limit=memory_limit, pct=round(mem_pct, 1)))

    if mem_pct >= 95:
        report.files.append(
            MemoryFinding(
                file_path=str(memory_file),
                severity="error",
                message=f"Memory file is at {mem_pct:.1f}% of budget ({memory_chars}/{memory_limit} chars)",
                evidence={"char_count": memory_chars, "limit": memory_limit, "pct": mem_pct},
            )
        )
    elif mem_pct >= 80:
        report.files.append(
            MemoryFinding(
                file_path=str(memory_file),
                severity="warning",
                message=f"Memory file is at {mem_pct:.1f}% of budget ({memory_chars}/{memory_limit} chars)",
                evidence={"char_count": memory_chars, "limit": memory_limit, "pct": mem_pct},
            )
        )

    if user_file:
        user_chars = _count_chars(user_file)
        user_limit = (limits[1] if limits else 5000) if limits else 5000
        user_pct = (user_chars / user_limit * 100) if user_limit else 0
        stats.append(MemoryStats(char_count=user_chars, limit=user_limit, pct=round(user_pct, 1)))

        if user_pct >= 95:
            report.files.append(
                MemoryFinding(
                    file_path=str(user_file),
                    severity="error",
                    message=f"User file is at {user_pct:.1f}% of budget ({user_chars}/{user_limit} chars)",
                    evidence={"char_count": user_chars, "limit": user_limit, "pct": user_pct},
                )
            )

    return report, stats


def _count_chars(path: Path) -> int:
    try:
        return len(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return 0