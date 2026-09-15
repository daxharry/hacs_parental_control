"""Binary sensors for Parental Control."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .controller import ParentalControlController


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    controller: ParentalControlController = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([ParentalControlAllowedSensor(controller)])


class ParentalControlAllowedSensor(BinarySensorEntity):
    """On when the current time is inside today's allowed window."""

    _attr_has_entity_name = True
    _attr_translation_key = "allowed_period"
    _attr_icon = "mdi:clock-check-outline"

    def __init__(self, controller: ParentalControlController) -> None:
        self.controller = controller
        self._attr_unique_id = f"{controller.entry.entry_id}_allowed_period"
        self._attr_device_info = controller.device_info

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(self.controller.async_add_listener(self.async_write_ha_state))

    @property
    def is_on(self) -> bool:
        return self.controller.in_allowed_period()

    @property
    def extra_state_attributes(self) -> dict:
        return self.controller.extra_attributes()
