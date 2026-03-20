"""P2000 sensor (v2.1.5) — all bug fixes applied."""

import hashlib
import json
import logging
from datetime import UTC, datetime, timedelta

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.restore_state import RestoreEntity

from .api import P2000Api
from .coordinator import P2000DataUpdateCoordinator
from .const import (
    CONF_CAPCODES,
    CONF_DIENSTEN,
    CONF_GEMEENTEN,
    CONF_LIFE,
    CONF_MELDING,
    CONF_NAME,
    CONF_PRIO1,
    CONF_REGIOS,
)

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(minutes=1)

DIENST_ICON = {
    "1": "mdi:police-badge",
    "2": "mdi:fire-truck",
    "3": "mdi:ambulance",
    "4": "mdi:ship",
    "5": "mdi:helicopter",
    "7": "mdi:radio-tower",
}

DEFAULT_ICON = "mdi:alert"


def detect_service_from_text(text: str | None) -> str | None:
    """Detect a dienst ID from free-form alert text."""
    if not text:
        return None
    t = text.lower()
    if "ambulance" in t or "ambu" in t:
        return "3"
    if "brw" in t or "brand" in t or "brandweer" in t:
        return "2"
    if "politie" in t or "prio 2 politie" in t:
        return "1"
    if "lifeliner" in t or "heli" in t or "traumahelikopter" in t or "mmt" in t:
        return "5"
    if "knrm" in t or "redding" in t:
        return "4"
    return None


async def async_setup_entry(hass, entry, async_add_entities):
    conf = entry.data
    name = conf.get(CONF_NAME)

    api_filter = {}
    for f in (CONF_GEMEENTEN, CONF_CAPCODES, CONF_DIENSTEN, CONF_REGIOS):
        if conf.get(f):
            api_filter[f] = conf[f]

    if conf.get(CONF_PRIO1):
        api_filter[CONF_PRIO1] = "1"
    if conf.get(CONF_LIFE):
        api_filter[CONF_LIFE] = "1"

    # FIX (#4): CONF_MELDING is now always stored as a list of keywords.
    # Pass the full list to the API so all keywords are filtered (AND logic).
    if conf.get(CONF_MELDING):
        v = conf[CONF_MELDING]
        api_filter[CONF_MELDING] = v if isinstance(v, list) else [v]

    api = P2000Api()
    coordinator = P2000DataUpdateCoordinator(hass, api, api_filter, SCAN_INTERVAL)
    await coordinator.async_refresh()

    async_add_entities(
        [P2000Sensor(hass, coordinator, name, api_filter, entry.entry_id)],
        True,
    )


class P2000Sensor(SensorEntity, RestoreEntity):
    _attr_should_poll = False

    def __init__(self, hass, coordinator, name, api_filter, entry_id):
        self.hass = hass
        self.coordinator = coordinator
        self._name = name
        self._api_filter = api_filter

        # Cached values — only written from _handle_coordinator_update, never
        # from property accessors (FIX #6: no side effects in properties).
        self._cached_state: str | None = None
        self._last_updated: str | None = None
        self._attributes: dict = {}
        self._dienstid_fallback: str | None = None

        # Forced icon when exactly one dienst is configured.
        forced_icon = None
        diensten = api_filter.get(CONF_DIENSTEN)
        if diensten:
            if not isinstance(diensten, (list, tuple)):
                diensten = [diensten]
            if len(diensten) == 1:
                d = str(diensten[0]).strip()
                forced_icon = DIENST_ICON.get(d)
        self._forced_icon = forced_icon

        unique_str = name + json.dumps(api_filter, sort_keys=True, ensure_ascii=False) + entry_id
        self._attr_unique_id = f"p2000_{hashlib.md5(unique_str.encode()).hexdigest()}"

        # FIX (#13): Use suggested_object_id instead of forcing _attr_entity_id
        # directly, so HA's entity registry stays in control.
        slug = name.lower().replace(" ", "_")
        self._attr_suggested_object_id = f"p2000_{slug}"
        self._attr_name = f"P2000 {name}"

    @property
    def device_info(self):
        return {
            "identifiers": {("p2000", "p2000_device")},
            "name": "P2000 Meldingen",
            "manufacturer": "P2000 Nederland",
            "model": "P2000 Live Alerts",
        }

    async def async_added_to_hass(self):
        await super().async_added_to_hass()

        # Restore previous state so the sensor isn't blank on HA restart.
        if (last_state := await self.async_get_last_state()) is not None:
            self._cached_state = last_state.state
            self._attributes = dict(last_state.attributes or {})
            helpers = self._attributes.get("helpers", {})
            if helpers:
                prev = helpers.get("dienst_id_normalized")
                if prev:
                    self._dienstid_fallback = str(prev)

        # Register the coordinator update callback.
        self.async_on_remove(
            self.coordinator.async_add_listener(self._handle_coordinator_update)
        )

    def _handle_coordinator_update(self) -> None:
        """Called by the coordinator whenever new data arrives.

        All mutable state is updated here — never inside property accessors
        (FIX #6).
        """
        data = self.coordinator.data
        if isinstance(data, dict):
            self._cached_state = data.get("melding")
            self._last_updated = datetime.now(UTC).isoformat()
            self._attributes = dict(data)
            dienstid = data.get("dienstid")
            if dienstid is not None:
                self._dienstid_fallback = str(dienstid)
        self.async_write_ha_state()

    # ------------------------------------------------------------------
    # Icon resolution (FIX #3): consistent isinstance guard throughout.
    # ------------------------------------------------------------------

    def _resolve_icon(self) -> str:
        """Determine the most appropriate icon for the current alert."""
        data = self.coordinator.data

        # 1) Forced icon from config (single dienst filter).
        if self._forced_icon:
            return self._forced_icon

        if not isinstance(data, dict):
            return DEFAULT_ICON

        # 2) Direct dienstid from API response.
        if data.get("dienstid"):
            return DIENST_ICON.get(str(data["dienstid"]), DEFAULT_ICON)

        # 3) dienstid inside subitems.
        subitems = data.get("subitems") or []
        if isinstance(subitems, list):
            for si in subitems:
                if not isinstance(si, dict):
                    continue
                sid = si.get("dienstid")
                if sid:
                    icon = DIENST_ICON.get(str(sid))
                    if icon:
                        return icon

        # 4) Detect service from tekstmelding.
        detected = detect_service_from_text(data.get("tekstmelding"))
        if detected:
            return DIENST_ICON.get(detected, DEFAULT_ICON)

        # 5) Detect service from melding text.
        detected = detect_service_from_text(data.get("melding"))
        if detected:
            return DIENST_ICON.get(detected, DEFAULT_ICON)

        # 6) Fall back to last known dienstid (restored from state).
        if self._dienstid_fallback:
            return DIENST_ICON.get(self._dienstid_fallback, DEFAULT_ICON)

        return DEFAULT_ICON

    @property
    def icon(self) -> str:
        return self._resolve_icon()

    # ------------------------------------------------------------------
    # State and attributes — pure reads, no side effects (FIX #6).
    # ------------------------------------------------------------------

    @property
    def state(self) -> str | None:
        return self._cached_state

    @property
    def extra_state_attributes(self) -> dict:
        data = self.coordinator.data
        out: dict = {}

        if isinstance(data, dict):
            out.update(data)
        else:
            out.update(self._attributes)
            out.setdefault("status", "Nog geen meldingen")

        # Helpers block: consistent dienstid source.
        dienstid_val = None
        if isinstance(data, dict):
            dienstid_val = data.get("dienstid")
        if dienstid_val is None:
            dienstid_val = self._dienstid_fallback

        out["helpers"] = {
            "dienst_id_normalized": dienstid_val,
            "icon_used": self._resolve_icon(),
        }

        out["filter"] = self._api_filter
        out["icon"] = self._resolve_icon()
        out["last_updated"] = self._last_updated

        return out
