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
    CONF_DIENSTEN,
    CONF_REGIOS,
    CONF_PRIO1,
    CONF_LIFE,
    CONF_MELDING,
)

class P2000OptionsFlowHandler(config_entries.OptionsFlow):
    """Opties-flow zodat bestaande P2000 sensoren via de UI te wijzigen zijn."""

    def __init__(self, config_entry: config_entries.ConfigEntry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Toon formulier met huidige configuratie."""
        if user_input is not None:
            for field in [
                CONF_WOONPLAATSEN, CONF_GEMEENTEN, CONF_CAPCODES,
                CONF_REGIOS, CONF_DIENSTEN, CONF_MELDING
            ]:
                value = user_input.get(field)
                if value:
                    user_input[field] = [v.strip() for v in value.split(",") if v.strip()]
            return self.async_create_entry(title="", data=user_input)

        data = self.config_entry.options or self.config_entry.data

        schema = vol.Schema({
            vol.Required(CONF_NAME, default=data.get(CONF_NAME)): str,
            vol.Optional(CONF_ICON, default=data.get(CONF_ICON, "mdi:fire-truck")): str,
            vol.Optional(CONF_WOONPLAATSEN, default=", ".join(data.get(CONF_WOONPLAATSEN, []))): str,
            vol.Optional(CONF_GEMEENTEN, default=", ".join(data.get(CONF_GEMEENTEN, []))): str,
            vol.Optional(CONF_CAPCODES, default=", ".join(data.get(CONF_CAPCODES, []))): str,
            vol.Optional(CONF_DIENSTEN, default=", ".join(data.get(CONF_DIENSTEN, []))): str,
            vol.Optional(CONF_REGIOS, default=", ".join(data.get(CONF_REGIOS, []))): str,
            vol.Optional(CONF_MELDING, default=", ".join(data.get(CONF_MELDING, []))): str,
            vol.Optional(CONF_PRIO1, default=data.get(CONF_PRIO1, False)): bool,
            vol.Optional(CONF_LIFE, default=data.get(CONF_LIFE, False)): bool,
        })
        return self.async_show_form(step_id="init", data_schema=schema)
