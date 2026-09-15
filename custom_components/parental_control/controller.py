"""Runtime controller for Parental Control."""

from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import datetime, timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.util import dt as dt_util

from .const import (
    CONF_INVERT,
    CONF_NAME,
    DOMAIN,
    STATUS_ALLOWED,
    STATUS_DISABLED,
    STATUS_RESTRICTED,
    STATUS_UNAVAILABLE,
    normalize_switch_entities,
)
from .schedule import (
    format_time,
    is_in_allowed_period,
    merged_config,
    next_change,
    schedule_markdown,
    schedule_summary,
    today_window,
    week_config,
)

_LOGGER = logging.getLogger(__name__)


class ParentalControlController:
    """Evaluate the weekly schedule and drive the target switch."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self.enabled: bool | None = None
        self._unsub: Callable[[], None] | None = None
        self._listeners: list[Callable[[], None]] = []

    @property
    def config(self) -> dict:
        return merged_config(dict(self.entry.data), dict(self.entry.options))

    @property
    def name(self) -> str:
        return self.config.get(CONF_NAME) or "Parental Control"

    @property
    def switch_entity_ids(self) -> list[str]:
        return normalize_switch_entities(self.config)

    @property
    def switch_entity_id(self) -> str | None:
        ids = self.switch_entity_ids
        return ids[0] if ids else None

    @property
    def invert(self) -> bool:
        return bool(self.config.get(CONF_INVERT, False))

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.entry.entry_id)},
            name=self.name,
            manufacturer="Parental Control",
            model="Weekly schedule",
            sw_version="1.2.0",
            entry_type=DeviceEntryType.SERVICE,
            configuration_url="https://github.com/daxharry/hacs_parental_control",
        )

    def now(self) -> datetime:
        return dt_util.now()

    def in_allowed_period(self, now: datetime | None = None) -> bool:
        return is_in_allowed_period(now or self.now(), self.config)

    def desired_switch_on(self, now: datetime | None = None) -> bool:
        """Desired state of the target switch.

        By default the switch is turned off during the allowed window
        (parental control deactivated) and turned on outside of it.
        """
        allowed = self.in_allowed_period(now)
        return allowed if self.invert else not allowed

    def next_change_at(self, now: datetime | None = None) -> datetime | None:
        return next_change(now or self.now(), self.config)

    def status(self) -> str:
        if self.enabled is False:
            return STATUS_DISABLED
        ids = self.switch_entity_ids
        available = False
        for entity_id in ids:
            state = self.hass.states.get(entity_id)
            if state is not None and state.state not in ("unavailable", "unknown"):
                available = True
                break
        if not ids or not available:
            return STATUS_UNAVAILABLE
        if self.in_allowed_period():
            return STATUS_ALLOWED
        return STATUS_RESTRICTED

    def extra_attributes(self) -> dict:
        now = self.now()
        today = today_window(now, self.config)
        next_at = self.next_change_at(now)
        desired_on = self.desired_switch_on(now)
        switch_states = {}
        for entity_id in self.switch_entity_ids:
            state = self.hass.states.get(entity_id)
            switch_states[entity_id] = state.state if state else "unavailable"
        return {
            "name": self.name,
            "switch_entity_ids": self.switch_entity_ids,
            "switch_states": switch_states,
            "in_allowed_period": self.in_allowed_period(now),
            "desired_switch_state": "on" if desired_on else "off",
            "today": "enabled" if today.enabled else "disabled",
            "today_start": format_time(today.start) if today.enabled else None,
            "today_end": format_time(today.end) if today.enabled else None,
            "next_change": next_at.isoformat() if next_at else None,
            "invert": self.invert,
            "schedule": week_config(self.config),
            "schedule_summary": schedule_summary(self.config),
            "schedule_markdown": schedule_markdown(self.config),
        }

    def schedule_summary(self) -> str:
        return schedule_summary(self.config)

    def async_add_listener(self, update_callback: Callable[[], None]) -> Callable[[], None]:
        self._listeners.append(update_callback)

        def _remove() -> None:
            if update_callback in self._listeners:
                self._listeners.remove(update_callback)

        return _remove

    @callback
    def async_notify(self) -> None:
        for listener in list(self._listeners):
            listener()

    async def async_start(self) -> None:
        self._unsub = async_track_time_interval(
            self.hass, self.async_tick, timedelta(minutes=1)
        )

    async def async_stop(self) -> None:
        if self._unsub:
            self._unsub()
            self._unsub = None

    async def async_tick(self, now=None) -> None:
        await self.async_apply()
        self.async_notify()

    async def async_apply(self, now: datetime | None = None) -> None:
        """Set each target switch to the scheduled state when the scheduler is on."""
        if self.enabled is not True:
            return

        want_on = self.desired_switch_on(now)
        service = "turn_on" if want_on else "turn_off"
        entity_ids: list[str] = []

        for entity_id in self.switch_entity_ids:
            state = self.hass.states.get(entity_id)
            if state is None or state.state in ("unavailable", "unknown"):
                _LOGGER.debug("Target switch %s is not available", entity_id)
                continue
            if (state.state == "on") == want_on:
                continue
            entity_ids.append(entity_id)

        if not entity_ids:
            return

        _LOGGER.debug("Parental Control: calling switch.%s on %s", service, entity_ids)
        await self.hass.services.async_call(
            "switch",
            service,
            {"entity_id": entity_ids},
            blocking=False,
        )
