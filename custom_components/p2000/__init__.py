"""Init file (v2.1.5) for P2000 integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict):
    """Legacy YAML not supported (UI-only)."""
    _LOGGER.debug("P2000 v2.1.5: async_setup called (UI-only integration).")
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Setup P2000 platform via UI-config entry."""
    _LOGGER.debug("P2000 v2.1.5: async_setup_entry for %s", entry.title)
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    # FIX (#5): Reload the entry whenever the user saves new options, so the
    # sensor picks up the updated api_filter without requiring a full HA restart.
    entry.async_on_unload(entry.add_update_listener(_async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload sensor when config entry is removed."""
    _LOGGER.debug("P2000 v2.1.5: async_unload_entry for %s", entry.title)
    return await hass.config_entries.async_forward_entry_unload(entry, "sensor")


async def _async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the config entry when options are updated."""
    _LOGGER.debug("P2000 v2.1.5: options changed, reloading entry %s", entry.title)
    await hass.config_entries.async_reload(entry.entry_id)
