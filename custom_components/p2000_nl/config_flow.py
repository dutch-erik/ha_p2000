"""Config flow for P2000 integration (UI-only)."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.core import callback
from homeassistant.helpers import selector
from homeassistant.helpers.selector import (
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectOptionDict,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import (
    CONF_CAPCODES,
    CONF_DIENSTEN,
    CONF_GEMEENTEN,
    CONF_GRIP,
    CONF_LIFE,
    CONF_MELDING,
    CONF_NAME,
    CONF_PRIO1,
    CONF_REGIOS,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DIENST_OPTIES,
    DOMAIN,
    GRIP_OPTIES,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
    REGIO_OPTIES,
)
from .util import normalize_filter, stable_hash

# Config keys that count as a "filter". At least one should be set,
# otherwise the sensor pulls alerts from the entire Netherlands.
_FILTER_KEYS = (
    CONF_GEMEENTEN,
    CONF_CAPCODES,
    CONF_REGIOS,
    CONF_DIENSTEN,
    CONF_MELDING,
    CONF_GRIP,
)

# Convert raw dicts to typed SelectOptionDict objects once at module level.
REGIO_OPTIONS: list[SelectOptionDict] = [
    SelectOptionDict(value=o["value"], label=o["label"]) for o in REGIO_OPTIES
]
DIENST_OPTIONS: list[SelectOptionDict] = [
    SelectOptionDict(value=o["value"], label=o["label"]) for o in DIENST_OPTIES
]
GRIP_OPTIONS: list[SelectOptionDict] = [
    SelectOptionDict(value=o["value"], label=o["label"]) for o in GRIP_OPTIES
]


# ----------------------------------------------------------------------
# Shared field selectors, used by both config_flow.py (create) and
# options_flow.py (edit) so the two forms always stay in sync: a field
# added here automatically shows up in both places.
# ----------------------------------------------------------------------


def regios_selector() -> selector.SelectSelector:
    return selector.SelectSelector(SelectSelectorConfig(options=REGIO_OPTIONS, multiple=True))


def diensten_selector() -> selector.SelectSelector:
    return selector.SelectSelector(SelectSelectorConfig(options=DIENST_OPTIONS, multiple=True))


def grip_selector() -> selector.SelectSelector:
    """Minimum GRIP level; only alerts at or above this level are shown."""
    return selector.SelectSelector(
        SelectSelectorConfig(options=GRIP_OPTIONS, mode=SelectSelectorMode.DROPDOWN)
    )


def scan_interval_selector() -> selector.NumberSelector:
    """How often to poll AlarmeringDroid, in seconds.

    Bounded so the free API isn't hammered by an accidentally tiny interval.
    """
    return selector.NumberSelector(
        NumberSelectorConfig(
            min=MIN_SCAN_INTERVAL,
            max=MAX_SCAN_INTERVAL,
            step=5,
            unit_of_measurement="s",
            mode=NumberSelectorMode.BOX,
        )
    )


FORM_SCHEMA = vol.Schema({
    vol.Required(CONF_NAME): str,
    vol.Optional(CONF_GEMEENTEN): selector.TextSelector(),
    vol.Optional(CONF_CAPCODES): selector.TextSelector(),
    vol.Optional(CONF_REGIOS): regios_selector(),
    vol.Optional(CONF_DIENSTEN): diensten_selector(),
    # Comma-separated keywords; ALL must match (AND logic).
    vol.Optional(CONF_MELDING): selector.TextSelector(),
    vol.Optional(CONF_GRIP): grip_selector(),
    vol.Optional(CONF_PRIO1, default=False): bool,
    vol.Optional(CONF_LIFE, default=False): bool,
    vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): scan_interval_selector(),
})


def _has_any_filter(data: dict[str, Any]) -> bool:
    """Return True if at least one real filter field is set."""
    return any(data.get(key) for key in _FILTER_KEYS)


@config_entries.HANDLERS.register(DOMAIN)
class P2000ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for P2000 (UI-only)."""

    VERSION = 2

    def __init__(self) -> None:
        # Holds the normalized data while we wait for the user to confirm
        # the "no filter set" warning (see async_step_confirm_no_filter).
        self._pending_data: dict[str, Any] | None = None

    def _compute_unique_id(self, data: dict[str, Any]) -> str:
        normalized = normalize_filter(data)
        return stable_hash(normalized)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            user_input = _normalize_user_input(user_input)

            # Validation: warn (not block) if no filter field is set at all,
            # since that means the sensor would pull every P2000 alert in NL.
            if not _has_any_filter(user_input):
                self._pending_data = user_input
                return await self.async_step_confirm_no_filter()

            return await self._create_entry(user_input)

        return self.async_show_form(step_id="user", data_schema=FORM_SCHEMA, errors={})

    async def async_step_confirm_no_filter(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Extra confirmation step shown only when no filter was set.

        Presented as a separate page with a warning and a plain Submit
        button (empty schema). Submitting confirms the choice; the user
        can also go back and add a filter instead.
        """
        if user_input is not None:
            assert self._pending_data is not None
            return await self._create_entry(self._pending_data)

        return self.async_show_form(
            step_id="confirm_no_filter",
            data_schema=vol.Schema({}),
            description_placeholders={},
        )

    async def _create_entry(self, data: dict[str, Any]) -> ConfigFlowResult:
        unique_id = self._compute_unique_id(data)
        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(title=data[CONF_NAME], data=data)

    @staticmethod
    @callback
    def async_get_options_flow(
        entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        from .options_flow import P2000OptionsFlowHandler  # noqa: PLC0415

        return P2000OptionsFlowHandler(entry)


def _normalize_user_input(user_input: dict[str, Any]) -> dict[str, Any]:
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
