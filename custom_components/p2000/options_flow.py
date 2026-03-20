"""Options flow (v2.1.5) for P2000 integration."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import (
    CONF_GEMEENTEN,
    CONF_CAPCODES,
    CONF_REGIOS,
    CONF_DIENSTEN,
    CONF_PRIO1,
    CONF_LIFE,
    CONF_MELDING,
    REGIO_OPTIES,
    DIENST_OPTIES,
)
from .config_flow import _normalize_user_input


class P2000OptionsFlowHandler(config_entries.OptionsFlow):
    """Options flow for P2000 (v2.1.5)."""

    def __init__(self, entry):
        self.entry = entry

    async def async_step_init(self, user_input=None):
        return await self.async_step_options()

    async def async_step_options(self, user_input=None):
        current = {**self.entry.data, **self.entry.options}

        # Convert stored lists back to comma-separated strings for the text fields.
        def _to_str(key: str) -> str:
            v = current.get(key, [])
            if isinstance(v, (list, tuple)):
                return ", ".join(str(x) for x in v)
            return str(v) if v else ""

        schema = vol.Schema({
            vol.Optional(CONF_GEMEENTEN, default=_to_str(CONF_GEMEENTEN)):
                selector.TextSelector(),
            vol.Optional(CONF_CAPCODES, default=_to_str(CONF_CAPCODES)):
                selector.TextSelector(),
            vol.Optional(CONF_REGIOS, default=current.get(CONF_REGIOS, [])):
                selector.SelectSelector(
                    selector.SelectSelectorConfig(options=REGIO_OPTIES, multiple=True)
                ),
            vol.Optional(CONF_DIENSTEN, default=current.get(CONF_DIENSTEN, [])):
                selector.SelectSelector(
                    selector.SelectSelectorConfig(options=DIENST_OPTIES, multiple=True)
                ),
            # Comma-separated keywords; ALL must match (AND logic).
            vol.Optional(CONF_MELDING, default=_to_str(CONF_MELDING)):
                selector.TextSelector(),
            vol.Optional(CONF_PRIO1, default=current.get(CONF_PRIO1, False)): bool,
            vol.Optional(CONF_LIFE, default=current.get(CONF_LIFE, False)): bool,
        })

        if user_input is not None:
            normalized = _normalize_user_input(user_input)
            # Saving options triggers async_reload_entry via the update listener
            # registered in __init__.py.
            return self.async_create_entry(title="", data=normalized)

        return self.async_show_form(step_id="options", data_schema=schema, errors={})
