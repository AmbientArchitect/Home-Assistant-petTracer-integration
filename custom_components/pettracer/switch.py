"""Support for petTracer collar switches (LED, buzzer)."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import PetTracerDataUpdateCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up petTracer switch entities from config entry."""
    coordinator: PetTracerDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    if coordinator.data:
        for device_id, device in coordinator.data.items():
            device_name = (
                device.details.name if device.details else f"Pet Tracker {device_id}"
            )
            entities.append(PetTracerLedSwitch(coordinator, device_id, device_name))
            if device.buz is not None:
                entities.append(
                    PetTracerBuzzerSwitch(coordinator, device_id, device_name)
                )

    async_add_entities(entities)


class PetTracerSwitchBase(CoordinatorEntity, SwitchEntity):
    """Base class for petTracer collar switches."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: PetTracerDataUpdateCoordinator,
        device_id: int,
        device_name: str,
        key: str,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._device_name = device_name
        self._attr_unique_id = f"{DOMAIN}_{device_id}_{key}"

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information about this switch."""
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device_name,
            "manufacturer": "petTracer",
            "model": "Pet Collar",
        }

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            super().available
            and self.coordinator.data is not None
            and self._device_id in self.coordinator.data
        )


class PetTracerLedSwitch(PetTracerSwitchBase):
    """Switch to control a petTracer collar's LED."""

    _attr_name = "LED"
    _attr_icon = "mdi:led-on"

    def __init__(
        self,
        coordinator: PetTracerDataUpdateCoordinator,
        device_id: int,
        device_name: str,
    ) -> None:
        """Initialize the LED switch."""
        super().__init__(coordinator, device_id, device_name, "led")

    @property
    def is_on(self) -> bool | None:
        """Return true if the LED is on."""
        device = self.coordinator.data[self._device_id]
        return device.led

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the LED on."""
        await self.coordinator.client.get_device(self._device_id).set_led(True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the LED off."""
        await self.coordinator.client.get_device(self._device_id).set_led(False)
        await self.coordinator.async_request_refresh()


class PetTracerBuzzerSwitch(PetTracerSwitchBase):
    """Switch to control a petTracer collar's buzzer."""

    _attr_name = "Buzzer"
    _attr_icon = "mdi:volume-high"

    def __init__(
        self,
        coordinator: PetTracerDataUpdateCoordinator,
        device_id: int,
        device_name: str,
    ) -> None:
        """Initialize the buzzer switch."""
        super().__init__(coordinator, device_id, device_name, "buzzer")

    @property
    def is_on(self) -> bool | None:
        """Return true if the buzzer is on."""
        device = self.coordinator.data[self._device_id]
        return device.buz

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the buzzer on."""
        await self.coordinator.client.get_device(self._device_id).set_buzzer(True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the buzzer off."""
        await self.coordinator.client.get_device(self._device_id).set_buzzer(False)
        await self.coordinator.async_request_refresh()
