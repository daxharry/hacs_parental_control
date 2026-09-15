"""Config flow for Parental Control."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    BooleanSelector,
    EntitySelector,
    EntitySelectorConfig,
    TextSelector,
    TimeSelector,
)

from .const import (
    CONF_INVERT,
    CONF_NAME,
    CONF_SWITCH_ENTITY,
    DEFAULT_END,
    DEFAULT_START,
    DOMAIN,
    WEEKDAYS,
)


def _base_defaults() -> dict[str, Any]:
    defaults: dict[str, Any] = {
        CONF_NAME: "",
        CONF_INVERT: False,
        CONF_SWITCH_ENTITY: None,
    }
    for day in WEEKDAYS:
        defaults[f"{day}_enabled"] = False
        defaults[f"{day}_start"] = DEFAULT_START
        defaults[f"{day}_end"] = DEFAULT_END
    return defaults


def _user_schema(defaults: dict[str, Any]) -> vol.Schema:
    switch_selector = EntitySelector(EntitySelectorConfig(domain="switch"))
    fields: dict[Any, Any] = {
        vol.Required(CONF_NAME, default=defaults.get(CONF_NAME) or ""): TextSelector(),
    }
    if defaults.get(CONF_SWITCH_ENTITY):
        fields[
            vol.Required(CONF_SWITCH_ENTITY, default=defaults[CONF_SWITCH_ENTITY])
        ] = switch_selector
    else:
        fields[vol.Required(CONF_SWITCH_ENTITY)] = switch_selector
    fields[
        vol.Optional(CONF_INVERT, default=bool(defaults.get(CONF_INVERT, False)))
    ] = BooleanSelector()
    return vol.Schema(fields)


def _schedule_schema(defaults: dict[str, Any]) -> vol.Schema:
    fields: dict[Any, Any] = {}
    for day in WEEKDAYS:
        fields[
            vol.Required(
                f"{day}_enabled",
                default=bool(defaults.get(f"{day}_enabled", False)),
            )
        ] = BooleanSelector()
        fields[
            vol.Required(
                f"{day}_start",
                default=defaults.get(f"{day}_start") or DEFAULT_START,
            )
        ] = TimeSelector()
        fields[
            vol.Required(
                f"{day}_end",
                default=defaults.get(f"{day}_end") or DEFAULT_END,
            )
        ] = TimeSelector()
    return vol.Schema(fields)


def _validate_schedule(user_input: dict[str, Any]) -> dict[str, str]:
    errors: dict[str, str] = {}
    for day in WEEKDAYS:
        if not user_input.get(f"{day}_enabled"):
            continue
        start = user_input.get(f"{day}_start")
        end = user_input.get(f"{day}_end")
        if not start or not end or start == end:
            errors[f"{day}_end"] = "invalid_period"
    return errors


class ParentalControlConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Parental Control."""

    VERSION = 1

    def __init__(self) -> None:
        self._data: dict[str, Any] = _base_defaults()

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return ParentalControlOptionsFlow(config_entry)

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}

        if user_input is not None:
            name = (user_input.get(CONF_NAME) or "").strip()
            entity_id = user_input[CONF_SWITCH_ENTITY]
            if not name:
                state = self.hass.states.get(entity_id)
                name = state.name if state else entity_id
            self._data[CONF_NAME] = name
            self._data[CONF_SWITCH_ENTITY] = entity_id
            self._data[CONF_INVERT] = bool(user_input.get(CONF_INVERT, False))

            await self.async_set_unique_id(entity_id)
            self._abort_if_unique_id_configured()
            return await self.async_step_schedule()

        return self.async_show_form(
            step_id="user",
            data_schema=_user_schema(self._data),
            errors=errors,
        )

    async def async_step_schedule(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}

        if user_input is not None:
            errors = _validate_schedule(user_input)
            if not errors:
                self._data.update(user_input)
                return self.async_create_entry(
                    title=self._data[CONF_NAME],
                    data=self._data,
                )

        return self.async_show_form(
            step_id="schedule",
            data_schema=_schedule_schema(self._data),
            errors=errors,
        )


class ParentalControlOptionsFlow(config_entries.OptionsFlow):
    """Handle options for Parental Control."""

    def __init__(self, config_entry: config_entries.ConfigEntry | None = None) -> None:
        self._config_entry = config_entry
        self._user: dict[str, Any] = {}

    @property
    def _entry(self) -> config_entries.ConfigEntry:
        return getattr(self, "config_entry", None) or self._config_entry

    def _current(self) -> dict[str, Any]:
        current = _base_defaults()
        current.update(dict(self._entry.data))
        current.update(dict(self._entry.options))
        return current

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        return await self.async_step_user()

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        current = self._current()
        errors: dict[str, str] = {}

        if user_input is not None:
            name = (user_input.get(CONF_NAME) or "").strip() or current[CONF_NAME]
            self._user = {
                CONF_NAME: name,
                CONF_SWITCH_ENTITY: user_input[CONF_SWITCH_ENTITY],
                CONF_INVERT: bool(user_input.get(CONF_INVERT, False)),
            }
            return await self.async_step_schedule()

        return self.async_show_form(
            step_id="user",
            data_schema=_user_schema(current),
            errors=errors,
        )

    async def async_step_schedule(self, user_input: dict[str, Any] | None = None):
        current = self._current()
        errors: dict[str, str] = {}

        if user_input is not None:
            errors = _validate_schedule(user_input)
            if not errors:
                self.hass.config_entries.async_update_entry(
                    self._entry,
                    title=self._user[CONF_NAME],
                    data={
                        **dict(self._entry.data),
                        **self._user,
                    },
                )
                return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="schedule",
            data_schema=_schedule_schema(current),
            errors=errors,
        )
