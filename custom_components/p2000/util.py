"""Utility helpers for P2000 integration (v2.1.5)."""

import hashlib
import json
from typing import Any


def _normalize_value(v: Any) -> Any:
    """Normalize a single config value to a stable, comparable form."""
    if v is None:
        return None
    if isinstance(v, str):
        return v.strip()
    if isinstance(v, (list, tuple)):
        norm = []
        for item in v:
            if isinstance(item, str):
                norm.append(item.strip().lower())
            else:
                norm.append(item)
        uniq = sorted({i for i in norm if i not in (None, "", [])})
        return uniq
    return v


def normalize_filter(data: dict[str, Any]) -> dict[str, Any]:
    """
    Return a normalized copy of the api_filter/config dict.
    - strings trimmed
    - lists converted to sorted unique lists
    - gemeenten lowercased
    """
    out: dict[str, Any] = {}
    for k, v in (data or {}).items():
        if v is None or v == "":
            continue
        if k == "gemeenten":
            if isinstance(v, str):
                arr: list[str] = [x.strip().lower() for x in v.split(",") if x.strip()]
            elif isinstance(v, (list, tuple)):
                arr = [str(x).strip().lower() for x in v if x not in (None, "")]
            else:
                arr = [str(v).strip().lower()]
            out[k] = sorted(set(arr))
            continue
        if isinstance(v, str):
            out[k] = v.strip()
            continue
        if isinstance(v, (list, tuple)):
            cleaned: list[Any] = []
            for item in v:
                if isinstance(item, str):
                    cleaned.append(item.strip())
                else:
                    cleaned.append(item)
            out[k] = sorted({i for i in cleaned if i not in (None, "")})
            continue
        out[k] = v
    return out


def stable_hash(data: Any) -> str:
    """Return a stable md5 hash of a dictionary or any JSON-serializable data."""
    try:
        s = json.dumps(data, sort_keys=True, ensure_ascii=False)
    except (TypeError, ValueError):
        s = str(data)
    return hashlib.md5(s.encode()).hexdigest()
