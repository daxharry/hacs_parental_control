"""Scheduler enable switch for Parental Control."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DOMAIN
from .controller import ParentalControlController


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    controller: ParentalControlController = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([ParentalControlSchedulerSwitch(controller)])


class ParentalControlSchedulerSwitch(RestoreEntity, SwitchEntity):
    """Turn automatic enforcement of the weekly schedule on or off."""

    _attr_has_entity_name = True
    _attr_translation_key = "scheduler"
    _attr_icon = "mdi:calendar-clock"

    def __init__(self, controller: ParentalControlController) -> None:
        self.controller = controller
        self._attr_unique_id = f"{controller.entry.entry_id}_scheduler"
        self._attr_device_info = controller.device_info

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last = await self.async_get_last_state()
        if last is not None:
            self.controller.enabled = last.state == "on"
        else:
            self.controller.enabled = True
        self.async_on_remove(self.controller.async_add_listener(self.async_write_ha_state))
        await self.controller.async_apply()
        self.async_write_ha_state()

    @property
    def is_on(self) -> bool:
        return self.controller.enabled is not False

    async def async_turn_on(self, **kwargs) -> None:
        self.controller.enabled = True
        await self.controller.async_apply()
        self.controller.async_notify()
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        self.controller.enabled = False
        self.controller.async_notify()
        self.async_write_ha_state()
