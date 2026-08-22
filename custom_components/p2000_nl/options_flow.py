"""Options flow for P2000 integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.helpers import selector

from .config_flow import (
    _has_any_filter,
    _normalize_user_input,
    diensten_selector,
    grip_selector,
    regios_selector,
    scan_interval_selector,
)
from .const import (
    CONF_CAPCODES,
    CONF_DIENSTEN,
    CONF_GEMEENTEN,
    CONF_GRIP,
    CONF_LIFE,
    CONF_MELDING,
    CONF_PRIO1,
    CONF_REGIOS,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
)


class P2000OptionsFlowHandler(config_entries.OptionsFlow):
    """Options flow for P2000."""

    def __init__(self, entry: config_entries.ConfigEntry) -> None:
        self.entry = entry
        self._pending_data: dict[str, Any] | None = None

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        return await self.async_step_options()

    async def async_step_options(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        current = {**self.entry.data, **self.entry.options}

        # Convert stored lists back to comma-separated strings for the text fields.
        def _to_str(key: str) -> str:
            v = current.get(key, [])
            if isinstance(v, (list, tuple)):
                return ", ".join(str(x) for x in v)
            return str(v) if v else ""

        # Field selectors (regios_selector, diensten_selector, grip_selector,
        # scan_interval_selector) are imported from config_flow.py so this
        # form can never drift out of sync with the "create" form again.
        schema = vol.Schema({
            vol.Optional(CONF_GEMEENTEN, default=_to_str(CONF_GEMEENTEN)):
                selector.TextSelector(),
            vol.Optional(CONF_CAPCODES, default=_to_str(CONF_CAPCODES)):
                selector.TextSelector(),
            vol.Optional(CONF_REGIOS, default=current.get(CONF_REGIOS, [])):
                regios_selector(),
            vol.Optional(CONF_DIENSTEN, default=current.get(CONF_DIENSTEN, [])):
                diensten_selector(),
            # Comma-separated keywords; ALL must match (AND logic).
            vol.Optional(CONF_MELDING, default=_to_str(CONF_MELDING)):
                selector.TextSelector(),
            vol.Optional(CONF_GRIP, default=current.get(CONF_GRIP, "")):
                grip_selector(),
            vol.Optional(CONF_PRIO1, default=current.get(CONF_PRIO1, False)): bool,
            vol.Optional(CONF_LIFE, default=current.get(CONF_LIFE, False)): bool,
            vol.Optional(
                CONF_SCAN_INTERVAL,
                default=current.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
            ): scan_interval_selector(),
        })

        if user_input is not None:
            normalized = _normalize_user_input(user_input)

            if not _has_any_filter(normalized):
                self._pending_data = normalized
                return await self.async_step_confirm_no_filter()

            # Saving options triggers async_reload_entry via the update listener
            # registered in __init__.py.
            return self.async_create_entry(title="", data=normalized)

        return self.async_show_form(step_id="options", data_schema=schema, errors={})

    async def async_step_confirm_no_filter(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Extra confirmation step shown only when no filter is set."""
        if user_input is not None:
            assert self._pending_data is not None
            return self.async_create_entry(title="", data=self._pending_data)

        return self.async_show_form(
            step_id="confirm_no_filter",
            data_schema=vol.Schema({}),
            description_placeholders={},
        )
