"""P2000 Sensor integration for Home Assistant."""

import logging
from datetime import timedelta
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.const import CONF_NAME, CONF_ICON
import homeassistant.helpers.config_validation as cv
from .api import p2000Api

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "p2000"

CONF_GEMEENTEN = "gemeenten"
CONF_CAPCODES = "capcodes"
CONF_DIENSTEN = "diensten"
CONF_WOONPLAATSEN = "woonplaatsen"
CONF_REGIOS = "regios"
CONF_PRIO1 = "prio1"
CONF_LIFE = "lifeliners"
CONF_MELDING = "melding"

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
    """Set up the P2000 sensor platform."""
    name = config.get(CONF_NAME)
    icon = config.get(CONF_ICON)

    api_filter = {}

    # Voeg string / string array eigenschappen toe
    for prop in [CONF_WOONPLAATSEN, CONF_GEMEENTEN, CONF_CAPCODES, CONF_DIENSTEN, CONF_REGIOS]:
        if prop in config:
            api_filter[prop] = config[prop]

    # Voeg booleans toe
    for prop in [CONF_PRIO1, CONF_LIFE]:
        if config.get(prop, False):
            api_filter[prop] = "1"

    # Voeg meldingfilter toe
    if CONF_MELDING in config:
        api_filter[CONF_MELDING] = config[CONF_MELDING]

    api = p2000Api()
    async_add_entities([P2000Sensor(api, name, icon, api_filter)], True)


class P2000Sensor(SensorEntity):
    """Representation of a P2000 Sensor."""

    _attr_should_poll = True  # Zorgt dat SCAN_INTERVAL wordt gebruikt

    def __init__(self, api, name, icon, api_filter):
        """Initialize the sensor."""
        self.api = api
        self._api_filter = api_filter
        self._name = name
        self._icon = icon
        self._state = None
        self._attributes = {}

        # Unieke ID op basis van naam + filters
        self._attr_unique_id = f"p2000_{name}_{'_'.join(sorted(api_filter.keys()))}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def icon(self):
        """Return the icon for the sensor."""
        return self._icon

    @property
    def state(self):
        """Return the current state."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        attributes = self._attributes.copy()
        attributes["icon"] = self._icon
        return attributes

    async def async_update(self):
        """Fetch new data from the API."""
        data = await self.hass.async_add_executor_job(self.api.get_data, self._api_filter)

        if not data:
            _LOGGER.warning("Geen data ontvangen van p2000 API")
            return

        self._attributes = data
        self._state = data.get("melding")
