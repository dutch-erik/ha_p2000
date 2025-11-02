import logging
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.const import (CONF_NAME, CONF_ICON)
import homeassistant.helpers.config_validation as cv
from .api import P2000Api
from datetime import timedelta

"""Start the logger"""
_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "p2000"

CONF_GEMEENTEN = "gemeenten"
CONF_CAPCODES = "capcodes"
CONF_DIENSTEN = "diensten"
CONF_WOONPLAATSEN = "woonplaatsen"
CONF_REGIOS = "regios"
CONF_PRIO1 = "prio1"
CONF_LIFE = "lifeliners"
CONF_MELDING = "melding"  # Nieuwe configuratieoptie voor melding filter
SCAN_INTERVAL = timedelta(minutes=2)  # Update elke 1 minuten

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
    vol.Optional(CONF_MELDING): vol.All(cv.ensure_list, [cv.string]),  # Validatie van de melding filter
})

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Setup the sensor platform."""

    name = config.get(CONF_NAME)
    icon = config.get(CONF_ICON)

    apiFilter = {}
        
    # Voeg string / string array eigenschappen toe aan de apiFilter
    for prop in [CONF_WOONPLAATSEN, CONF_GEMEENTEN, CONF_CAPCODES, CONF_DIENSTEN, CONF_REGIOS]:
        if prop in config:
            apiFilter[prop] = config[prop]

    # Voeg boolean eigenschappen toe aan de apiFilter
    for prop in [CONF_PRIO1, CONF_LIFE]:
        if prop in config and config[prop] == True:
            apiFilter[prop] = "1"

    # Voeg de melding filter toe aan de apiFilter
    if CONF_MELDING in config:
        apiFilter[CONF_MELDING] = config[CONF_MELDING][0]  # Neem de eerste melding als filter

    api = P2000Api()

    add_entities([P2000Sensor(api, name, icon, apiFilter)])

class P2000Sensor(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, api, name, icon, apiFilter):
        """Initialize the sensor."""
        self.api = api
        self.attributes = {}
        self.apiFilter = apiFilter
        self._name = name
        self.icon = icon
        self._state = None

        # Gebruik een unieke ID gebaseerd op de naam en filteropties
        self._unique_id = f"p3000_{name}_{'_'.join(apiFilter.keys())}"

    @property
    def unique_id(self):
        """Return a unique ID for this sensor."""
        return self._unique_id

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the monitored installation."""
        attributes = self.attributes
        attributes['icon'] = self.icon
        return attributes

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        data = self.api.get_data(self.apiFilter)

        if data is None:
            return

        self.attributes = data
        self._state = data["melding"]
