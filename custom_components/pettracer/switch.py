"""Support for petTracer collar switches (LED, buzzer)."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import PetTracerDataUpdateCoordinator
from .const import DOMAIN
from .entity import PetTracerEntity
from .helpers import device_display_name

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
            device_name = device_display_name(device, device_id)
            entities.append(PetTracerLedSwitch(coordinator, device_id, device_name))
            if device.buz is not None:
                entities.append(
                    PetTracerBuzzerSwitch(coordinator, device_id, device_name)
                )

    async_add_entities(entities)


class PetTracerSwitchBase(PetTracerEntity, SwitchEntity):
    """Base class for petTracer collar switches."""

    def __init__(
        self,
        coordinator: PetTracerDataUpdateCoordinator,
        device_id: str,
        device_name: str,
        key: str,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, device_id, device_name, key)


class PetTracerLedSwitch(PetTracerSwitchBase):
    """Switch to control a petTracer collar's LED."""

    _attr_name = "LED"
    _attr_icon = "mdi:led-on"

    def __init__(
        self,
        coordinator: PetTracerDataUpdateCoordinator,
        device_id: str,
        device_name: str,
    ) -> None:
        """Initialize the LED switch."""
        super().__init__(coordinator, device_id, device_name, "led")

    @property
    def is_on(self) -> bool | None:
        """Return true if the LED is on."""
        device = self._device()
        if device is None:
            return None
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
        device_id: str,
        device_name: str,
    ) -> None:
        """Initialize the buzzer switch."""
        super().__init__(coordinator, device_id, device_name, "buzzer")

    @property
    def is_on(self) -> bool | None:
        """Return true if the buzzer is on."""
        device = self._device()
        if device is None:
            return None
        return device.buz

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the buzzer on."""
        await self.coordinator.client.get_device(self._device_id).set_buzzer(True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the buzzer off."""
        await self.coordinator.client.get_device(self._device_id).set_buzzer(False)
        await self.coordinator.async_request_refresh()