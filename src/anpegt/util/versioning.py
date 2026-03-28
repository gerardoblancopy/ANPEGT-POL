"""Content hashing and diff tracking utilities."""

import hashlib
import json
from typing import Any


def content_hash(data: dict[str, Any]) -> str:
    """Compute a stable SHA-256 hash (first 16 hex chars) of a dict."""
    raw = json.dumps(data, sort_keys=True, default=str, ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def compute_diff(old: dict[str, Any], new: dict[str, Any]) -> dict[str, Any]:
    """Compute a simple diff between two dicts, showing added/removed/changed keys."""
    diff: dict[str, Any] = {"added": {}, "removed": {}, "changed": {}}
    all_keys = set(old.keys()) | set(new.keys())
    for key in all_keys:
        if key not in old:
            diff["added"][key] = new[key]
        elif key not in new:
            diff["removed"][key] = old[key]
        elif old[key] != new[key]:
            diff["changed"][key] = {"old": old[key], "new": new[key]}
    return diff
