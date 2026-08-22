"""Diagnostics support for the P2000 integration.

Accessible via Settings -> Devices & Services -> P2000 -> the entry's
three-dot menu -> Download diagnostics. This produces a JSON file the
user can attach to a GitHub issue without exposing personal details.
"""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

# Keys that could reveal where the user lives/works are redacted before
# the diagnostics file is generated, since these files are often shared
# publicly in bug reports.
TO_REDACT = {
    "straat",
    "postcode",
    "plaats",
    "latitude",
    "longitude",
    "lat",
    "lon",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a P2000 config entry."""
    # The coordinator is stashed on entry.runtime_data during
    # sensor.async_setup_entry(); guard with getattr in case diagnostics
    # is requested before setup has finished.
    coordinator = getattr(entry, "runtime_data", None)

    diagnostics: dict[str, Any] = {
        "entry": {
            "title": entry.title,
            "version": entry.version,
            "data": async_redact_data(dict(entry.data), TO_REDACT),
            "options": async_redact_data(dict(entry.options), TO_REDACT),
        },
    }

    if coordinator is not None:
        last_data = getattr(coordinator, "last_valid_data", None)
        diagnostics["coordinator"] = {
            "last_update_success_time": str(
                getattr(coordinator, "last_update_success_time", None)
            ),
            "last_valid_data": async_redact_data(dict(last_data), TO_REDACT)
            if isinstance(last_data, dict)
            else None,
        }
    else:
        diagnostics["coordinator"] = "not available (entry not fully set up)"

    return diagnostics
