"""Sensors for Parental Control."""

from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .controller import ParentalControlController


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    controller: ParentalControlController = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            ParentalControlNextChangeSensor(controller),
            ParentalControlStatusSensor(controller),
        ]
    )


class _ParentalControlSensorBase(SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, controller: ParentalControlController, key: str) -> None:
        self.controller = controller
        self._attr_unique_id = f"{controller.entry.entry_id}_{key}"
        self._attr_device_info = controller.device_info

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(self.controller.async_add_listener(self.async_write_ha_state))


class ParentalControlNextChangeSensor(_ParentalControlSensorBase):
    """Timestamp of the next scheduled switch change."""

    _attr_translation_key = "next_change"
    _attr_icon = "mdi:clock-end"
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, controller: ParentalControlController) -> None:
        super().__init__(controller, "next_change")

    @property
    def native_value(self):
        return self.controller.next_change_at()


class ParentalControlStatusSensor(_ParentalControlSensorBase):
    """Human-readable scheduler status."""

    _attr_translation_key = "status"
    _attr_icon = "mdi:information-outline"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, controller: ParentalControlController) -> None:
        super().__init__(controller, "status")

    @property
    def native_value(self) -> str:
        return self.controller.status()

    @property
    def extra_state_attributes(self) -> dict:
        return self.controller.extra_attributes()
