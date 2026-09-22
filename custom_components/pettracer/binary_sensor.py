"""Support for petTracer binary sensors."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from pettracer.types import TrackingMode

from . import PetTracerDataUpdateCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up petTracer binary sensor entities from config entry."""
    coordinator: PetTracerDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    if coordinator.data:
        for device_id, device in coordinator.data.items():
            device_name = (
                device.details.name if device.details else f"Pet Tracker {device_id}"
            )
            entities.append(
                PetTracerLiveTrackingBinarySensor(coordinator, device_id, device_name)
            )

    async_add_entities(entities)


class PetTracerLiveTrackingBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of a petTracer collar's live tracking status."""

    _attr_has_entity_name = True
    _attr_name = "Live tracking"
    _attr_device_class = BinarySensorDeviceClass.RUNNING

    def __init__(
        self,
        coordinator: PetTracerDataUpdateCoordinator,
        device_id: str,
        device_name: str,
    ) -> None:
        """Initialize the live tracking binary sensor."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._device_name = device_name
        self._attr_unique_id = f"{DOMAIN}_{device_id}_live_tracking"

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information about this binary sensor."""
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

    @property
    def is_on(self) -> bool | None:
        """Return true if the collar is in live (search) tracking mode."""
        device = self.coordinator.data[self._device_id]
        if device.mode is None:
            return None
        return device.mode == TrackingMode.SEARCH
