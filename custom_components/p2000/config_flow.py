from __future__ import annotations
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME, CONF_ICON
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_WOONPLAATSEN,
    CONF_GEMEENTEN,
    CONF_CAPCODES,
    CONF_REGIOS,
    CONF_DIENSTEN,
    CONF_PRIO1,
    CONF_LIFE,
    CONF_MELDING,
)

FORM_SCHEMA = vol.Schema({
    vol.Required(CONF_NAME): str,
    vol.Optional(CONF_ICON, default="mdi:fire-truck"): str,
    vol.Optional(CONF_WOONPLAATSEN): selector.TextSelector(),
    vol.Optional(CONF_GEMEENTEN): selector.TextSelector(),
    vol.Optional(CONF_CAPCODES): selector.TextSelector(),
    vol.Optional(CONF_DIENSTEN): selector.TextSelector(),
    vol.Optional(CONF_REGIOS): selector.TextSelector(),
    vol.Optional(CONF_MELDING): selector.TextSelector(),
    vol.Optional(CONF_PRIO1, default=False): bool,
    vol.Optional(CONF_LIFE, default=False): bool,
})

@config_entries.HANDLERS.register(DOMAIN)
class P2000ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow voor de P2000 integratie."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            name = user_input.get(CONF_NAME)
            if not name:
                errors["base"] = "no_name"
            else:
                for field in [
                    CONF_WOONPLAATSEN, CONF_GEMEENTEN, CONF_CAPCODES,
                    CONF_REGIOS, CONF_DIENSTEN, CONF_MELDING
                ]:
                    value = user_input.get(field)
                    if value:
                        user_input[field] = [v.strip() for v in value.split(",") if v.strip()]
                return self.async_create_entry(title=name, data=user_input)

        return self.async_show_form(step_id="user", data_schema=FORM_SCHEMA, errors=errors)
from .options_flow import P2000OptionsFlowHandler

@config_entries.HANDLERS.register(DOMAIN)
class P2000ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow voor de P2000 integratie."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            name = user_input.get(CONF_NAME)
            if not name:
                errors["base"] = "no_name"
            else:
                for field in [
                    CONF_WOONPLAATSEN, CONF_GEMEENTEN, CONF_CAPCODES,
                    CONF_REGIOS, CONF_DIENSTEN, CONF_MELDING
                ]:
                    value = user_input.get(field)
                    if value:
                        user_input[field] = [v.strip() for v in value.split(",") if v.strip()]
                return self.async_create_entry(title=name, data=user_input)

        return self.async_show_form(step_id="user", data_schema=FORM_SCHEMA, errors=errors)

    @staticmethod
    def async_get_options_flow(config_entry):
        """Wijs de options flow toe."""
        return P2000OptionsFlowHandler(config_entry)
