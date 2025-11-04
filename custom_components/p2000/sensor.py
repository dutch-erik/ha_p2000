"""P2000 Sensor integration for Home Assistant."""

import logging
import json
import hashlib
from datetime import timedelta
import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.const import CONF_NAME, CONF_ICON
import homeassistant.helpers.config_validation as cv

from .api import P2000Api
from .coordinator import P2000DataUpdateCoordinator
from .const import (
    CONF_WOONPLAATSEN,
    CONF_GEMEENTEN,
    CONF_CAPCODES,
    CONF_DIENSTEN,
    CONF_REGIOS,
    CONF_PRIO1,
    CONF_LIFE,
    CONF_MELDING,
)

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "p2000"
SCAN_INTERVAL = timedelta(minutes=1)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_ICON, default="mdi:fire-truck"): cv.icon,
    vol.Optional(CONF_WOONPLAATSEN): vol.All(cv.ensure_list, [cv.string]),
    vol.Optional(CONF_GEMEENTEN): vol.All(cv.ensure_list, [cv.string]),
    vol.Optional(CONF_CAPCODES): vol.All(cv.ensure_list, [cv.string]),
    vol.Optional(CONF_REGIOS): vol.All(cv.ensure_list, [cv.string]),
    vol.Optional(CONF_DIENSTEN): vol.All(cv.ensure_list, [cv.string]),
    vol.Optional(CONF_PRIO1, default=False): cv.boolean,
    vol.Optional(CONF_LIFE, default=False): cv.boolean,
    vol.Optional(CONF_MELDING): vol.All(cv.ensure_list, [cv.string]),
})


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Legacy YAML setup."""
    name = config.get(CONF_NAME)
    icon = config.get(CONF_ICON)
    api_filter = {}

    for prop in [CONF_WOONPLAATSEN, CONF_GEMEENTEN, CONF_CAPCODES, CONF_DIENSTEN, CONF_REGIOS]:
        if prop in config:
            api_filter[prop] = config[prop]

    for prop in [CONF_PRIO1, CONF_LIFE]:
        if config.get(prop, False):
            api_filter[prop] = "1"

    if CONF_MELDING in config:
        value = config[CONF_MELDING]
        if isinstance(value, list):
            api_filter[CONF_MELDING] = value[0]
        else:
            api_filter[CONF_MELDING] = value

    api = P2000Api()
    coordinator = P2000DataUpdateCoordinator(hass, api, api_filter, SCAN_INTERVAL)
    await coordinator.async_refresh()
    async_add_entities([P2000Sensor(coordinator, name, icon, api_filter)], True)


async def async_setup_entry(hass, entry, async_add_entities):
    """Setup P2000 via UI (config entry)."""
    conf = entry.data
    name = conf.get(CONF_NAME)
    icon = conf.get(CONF_ICON)
    api_filter = {}

    for prop in [CONF_WOONPLAATSEN, CONF_GEMEENTEN, CONF_CAPCODES, CONF_DIENSTEN, CONF_REGIOS]:
        value = conf.get(prop)
        if value:
            api_filter[prop] = value

    for prop in [CONF_PRIO1, CONF_LIFE]:
        if conf.get(prop, False):
            api_filter[prop] = "1"

    if CONF_MELDING in conf:
        value = conf[CONF_MELDING]
        if isinstance(value, list):
            api_filter[CONF_MELDING] = value[0]
        else:
            api_filter[CONF_MELDING] = value

    api = P2000Api()
    coordinator = P2000DataUpdateCoordinator(hass, api, api_filter, SCAN_INTERVAL)
    await coordinator.async_refresh()
    async_add_entities([P2000Sensor(coordinator, name, icon, api_filter)], True)


class P2000Sensor(SensorEntity):
    """Representation of a P2000 Sensor."""

    _attr_should_poll = False

    def __init__(self, coordinator, name, icon, api_filter):
        self.coordinator = coordinator
        self._name = name
        self._icon = icon
        self._api_filter = api_filter
        unique_str = name + json.dumps(api_filter, sort_keys=True, ensure_ascii=False)
        unique_hash = hashlib.md5(unique_str.encode()).hexdigest()
        self._attr_unique_id = f"p2000_{unique_hash}"
        self.coordinator.async_add_listener(self.async_write_ha_state)
        _LOGGER.debug("P2000 Sensor aangemaakt met unique_id: %s", self._attr_unique_id)

    @property
    def name(self):
        return self._name

    @property
    def icon(self):
        return self._icon

    @property
    def state(self):
        data = self.coordinator.data
        if data is None:
            return None
        return data.get("melding")

    @property
    def available(self):
        return self.coordinator.last_update_success

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        attributes = {}
        if data:
            attributes = data.copy()
        else:
            attributes["status"] = "Nog geen meldingen"
        attributes["icon"] = self._icon
        return attributes
