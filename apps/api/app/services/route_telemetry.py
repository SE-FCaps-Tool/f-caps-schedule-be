"""Small in-process route usage counter for the legacy deprecation window."""

from __future__ import annotations

from collections import Counter
from threading import Lock

_counts: Counter[tuple[str, str]] = Counter()
_lock = Lock()


def record_route_usage(method: str, path: str) -> None:
    with _lock:
        _counts[(method.upper(), path)] += 1


def route_usage_snapshot() -> dict[str, int]:
    with _lock:
        return {f"{method} {path}": count for (method, path), count in _counts.items()}
