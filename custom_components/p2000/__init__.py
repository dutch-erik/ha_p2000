"""Init file (v2.1.5) for P2000 integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_MELDING

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Legacy YAML not supported (UI-only)."""
    _LOGGER.debug("P2000 v2.1.5: async_setup called (UI-only integration).")
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Setup P2000 platform via UI-config entry."""
    _LOGGER.debug("P2000 v2.1.5: async_setup_entry for %s", entry.title)
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    # Reload the entry whenever the user saves new options, so the sensor
    # picks up the updated api_filter without requiring a full HA restart.
    entry.async_on_unload(entry.add_update_listener(_async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload sensor when config entry is removed."""
    _LOGGER.debug("P2000 v2.1.5: async_unload_entry for %s", entry.title)
    return await hass.config_entries.async_forward_entry_unload(entry, "sensor")


async def _async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the config entry when options are updated."""
    _LOGGER.debug("P2000 v2.1.5: options changed, reloading entry %s", entry.title)
    await hass.config_entries.async_reload(entry.entry_id)


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate config entries from older versions to the current schema.

    Version history:
      v1 → v2: CONF_MELDING changed from a plain string (or absent) to a list
               of lowercase keyword strings. This allows AND-matching on
               multiple keywords. Existing single-string values are wrapped in
               a one-element list; missing values stay absent.
    """
    _LOGGER.debug(
        "P2000: migrating config entry '%s' from v%s to v%s",
        entry.title,
        entry.version,
        2,
    )

    if entry.version == 1:
        new_data = dict(entry.data)

        melding = new_data.get(CONF_MELDING)
        if isinstance(melding, str) and melding.strip():
            # v1 stored a single comma-separated string; convert to list.
            keywords = [kw.strip().lower() for kw in melding.split(",") if kw.strip()]
            new_data[CONF_MELDING] = keywords
            _LOGGER.debug(
                "P2000: migrated CONF_MELDING '%s' → %s", melding, keywords
            )
        elif melding is None or melding == "":
            # Not set in v1 — remove the key entirely for a clean state.
            new_data.pop(CONF_MELDING, None)

        hass.config_entries.async_update_entry(entry, data=new_data, version=2)
        _LOGGER.info(
            "P2000: successfully migrated config entry '%s' to version 2.",
            entry.title,
        )

    return True
