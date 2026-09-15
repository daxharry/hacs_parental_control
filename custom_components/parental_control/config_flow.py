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
    CONF_SWITCH_ENTITIES,
    CONF_SWITCH_ENTITY,
    DEFAULT_END,
    DEFAULT_START,
    DOMAIN,
    WEEKDAYS,
    normalize_switch_entities,
)
from .schedule import schedule_summary

_IDENTITY_KEYS = {CONF_NAME, CONF_SWITCH_ENTITIES, CONF_INVERT}


def _base_defaults() -> dict[str, Any]:
    defaults: dict[str, Any] = {
        CONF_NAME: "",
        CONF_INVERT: False,
        CONF_SWITCH_ENTITIES: [],
    }
    for day in WEEKDAYS:
        defaults[f"{day}_enabled"] = False
        defaults[f"{day}_start"] = DEFAULT_START
        defaults[f"{day}_end"] = DEFAULT_END
    return defaults


def _title_from_switches(hass, entity_ids: list[str]) -> str:
    names: list[str] = []
    for entity_id in entity_ids[:3]:
        state = hass.states.get(entity_id)
        names.append(state.name if state else entity_id)
    title = ", ".join(names) if names else "Parental Control"
    if len(entity_ids) > 3:
        title += f" +{len(entity_ids) - 3}"
    return title


def _user_schema(defaults: dict[str, Any]) -> vol.Schema:
    switch_selector = EntitySelector(
        EntitySelectorConfig(domain="switch", multiple=True)
    )
    entity_ids = normalize_switch_entities(defaults)
    fields: dict[Any, Any] = {
        vol.Required(CONF_NAME, default=defaults.get(CONF_NAME) or ""): TextSelector(),
    }
    if entity_ids:
        fields[
            vol.Required(CONF_SWITCH_ENTITIES, default=entity_ids)
        ] = switch_selector
    else:
        fields[vol.Required(CONF_SWITCH_ENTITIES)] = switch_selector
    fields[
        vol.Optional(CONF_INVERT, default=bool(defaults.get(CONF_INVERT, False)))
    ] = BooleanSelector()
    return vol.Schema(fields)


def _schedule_fields(defaults: dict[str, Any]) -> dict[Any, Any]:
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
    return fields


def _schedule_schema(defaults: dict[str, Any]) -> vol.Schema:
    return vol.Schema(_schedule_fields(defaults))


def _options_schema(defaults: dict[str, Any]) -> vol.Schema:
    """Single form with current switches, logic, and the weekly schedule."""
    fields: dict[Any, Any] = dict(_user_schema(defaults).schema)
    fields.update(_schedule_fields(defaults))
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

    VERSION = 2

    def __init__(self) -> None:
        self._data: dict[str, Any] = _base_defaults()

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return ParentalControlOptionsFlow(config_entry)

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}

        if user_input is not None:
            entity_ids = normalize_switch_entities(user_input)
            if not entity_ids:
                errors[CONF_SWITCH_ENTITIES] = "no_switches"
            else:
                name = (user_input.get(CONF_NAME) or "").strip()
                if not name:
                    name = _title_from_switches(self.hass, entity_ids)
                self._data[CONF_NAME] = name
                self._data[CONF_SWITCH_ENTITIES] = entity_ids
                self._data[CONF_INVERT] = bool(user_input.get(CONF_INVERT, False))

                await self.async_set_unique_id(",".join(sorted(entity_ids)))
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

    @property
    def _entry(self) -> config_entries.ConfigEntry:
        return getattr(self, "config_entry", None) or self._config_entry

    def _current(self) -> dict[str, Any]:
        current = _base_defaults()
        current.update(dict(self._entry.data))
        current.update(dict(self._entry.options))
        current[CONF_SWITCH_ENTITIES] = normalize_switch_entities(current)
        return current

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        current = self._current()
        errors: dict[str, str] = {}

        if user_input is not None:
            entity_ids = normalize_switch_entities(user_input)
            if not entity_ids:
                errors[CONF_SWITCH_ENTITIES] = "no_switches"
            errors.update(_validate_schedule(user_input))
            if not errors:
                name = (user_input.get(CONF_NAME) or "").strip() or current[CONF_NAME]
                data = {
                    **dict(self._entry.data),
                    CONF_NAME: name,
                    CONF_SWITCH_ENTITIES: entity_ids,
                    CONF_INVERT: bool(user_input.get(CONF_INVERT, False)),
                }
                data.pop(CONF_SWITCH_ENTITY, None)
                self.hass.config_entries.async_update_entry(
                    self._entry,
                    title=name,
                    data=data,
                )
                schedule = {
                    key: value
                    for key, value in user_input.items()
                    if key not in _IDENTITY_KEYS
                }
                return self.async_create_entry(title="", data=schedule)
            current = {**current, **user_input}
            current[CONF_SWITCH_ENTITIES] = entity_ids

        return self.async_show_form(
            step_id="init",
            data_schema=_options_schema(current),
            errors=errors,
            description_placeholders={"summary": schedule_summary(current)},
        )
