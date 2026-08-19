"""Stable PostgreSQL advisory-lock keys for shared scheduling resources."""

from __future__ import annotations

import hashlib
from collections.abc import Iterable

from sqlalchemy import text


def resource_lock_key(namespace: str, resource_id: int) -> int:
    """Return a deterministic signed PostgreSQL int8 key.

    The namespace is part of the key so a reviewer and room with the same id
    never accidentally share a lock.  Truncation may collide (and therefore
    only over-serialize), but can never produce an out-of-range int8 value.
    """
    digest = hashlib.sha256(f"scheduler:{namespace}:{int(resource_id)}".encode()).digest()
    value = int.from_bytes(digest[:8], "big", signed=False) & ((1 << 63) - 1)
    return value - (1 << 63) if value >= (1 << 62) else value


advisory_lock_key = resource_lock_key
signed_int8_key = resource_lock_key
lock_key = resource_lock_key


def acquire_resource_locks(db, namespace: str, resource_ids: Iterable[int]) -> None:
    """Acquire deterministic transaction-scoped locks in id order."""
    keys = sorted({resource_lock_key(namespace, resource_id) for resource_id in resource_ids})
    for key in keys:
        db.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": key})
