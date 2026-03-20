"""Config flow (v2.1.5) for P2000 integration (UI-only)."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CONF_CAPCODES,
    CONF_DIENSTEN,
    CONF_GEMEENTEN,
    CONF_LIFE,
    CONF_MELDING,
    CONF_NAME,
    CONF_PRIO1,
    CONF_REGIOS,
    DIENST_OPTIES,
    DOMAIN,
    REGIO_OPTIES,
)
from .util import normalize_filter, stable_hash

_LOGGER = logging.getLogger(__name__)

FORM_SCHEMA = vol.Schema({
    vol.Required(CONF_NAME): str,
    vol.Optional(CONF_GEMEENTEN): selector.TextSelector(),
    vol.Optional(CONF_CAPCODES): selector.TextSelector(),
    vol.Optional(CONF_REGIOS): selector.SelectSelector(
        selector.SelectSelectorConfig(
            options=REGIO_OPTIES,
            multiple=True,
        )
    ),
    vol.Optional(CONF_DIENSTEN): selector.SelectSelector(
        selector.SelectSelectorConfig(
            options=DIENST_OPTIES,
            multiple=True,
        )
    ),
    # Comma-separated keywords; ALL must match (AND logic).
    vol.Optional(CONF_MELDING): selector.TextSelector(),
    vol.Optional(CONF_PRIO1, default=False): bool,
    vol.Optional(CONF_LIFE, default=False): bool,
})


@config_entries.HANDLERS.register(DOMAIN)
class P2000ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for P2000 (UI-only)."""

    VERSION = 2

    def _compute_unique_id(self, data: dict[str, Any]) -> str:
        normalized = normalize_filter(data)
        return stable_hash(normalized)

    async def async_step_intro(self, user_input=None):
        if user_input is not None:
            return await self.async_step_user()
        return self.async_show_form(step_id="intro", description_placeholders={})

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            user_input = _normalize_user_input(user_input)

            unique_id = self._compute_unique_id(user_input)
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()

            entry_data = {**user_input, "unique_id": unique_id}
            return self.async_create_entry(title=user_input[CONF_NAME], data=entry_data)

        return self.async_show_form(step_id="user", data_schema=FORM_SCHEMA, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(entry):
        from .options_flow import P2000OptionsFlowHandler  # noqa: PLC0415
        return P2000OptionsFlowHandler(entry)


def _normalize_user_input(user_input: dict) -> dict:
    """
    Normalize text fields from the UI form into canonical list types.

    - CONF_GEMEENTEN  → list of lowercase strings
    - CONF_CAPCODES   → list of strings (case preserved)
    - CONF_MELDING    → list of lowercase keyword strings (ALL must match)
    """
    result = dict(user_input)
    for key in (CONF_GEMEENTEN, CONF_CAPCODES, CONF_MELDING):
        v = result.get(key)
        if not isinstance(v, str):
            continue
        parts = [i.strip() for i in v.split(",") if i.strip()]
        # Both gemeenten and melding are lowercased.
        if key in (CONF_GEMEENTEN, CONF_MELDING):
            parts = [p.lower() for p in parts]
        result[key] = parts
    return result
