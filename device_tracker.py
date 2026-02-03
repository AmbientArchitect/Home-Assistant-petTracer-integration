"""Support for petTracer device tracking."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.device_tracker import SourceType, TrackerEntity
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
    """Set up petTracer device tracker entities from config entry."""
    coordinator: PetTracerDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    if coordinator.data:
        for device_id, device in coordinator.data.items():
            # device is a Device dataclass object
            device_name = (
                device.details.name if device.details else f"Pet Tracker {device_id}"
            )
            entities.append(PetTracerDeviceTracker(coordinator, device_id, device_name))

    async_add_entities(entities)


class PetTracerDeviceTracker(CoordinatorEntity, TrackerEntity):
    """Representation of a petTracer device tracker."""

    _attr_has_entity_name = True
    _attr_name = None

    def __init__(
        self,
        coordinator: PetTracerDataUpdateCoordinator,
        device_id: str,
        device_name: str,
    ) -> None:
        """Initialize the petTracer device tracker."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._device_name = device_name
        self._attr_unique_id = f"{DOMAIN}_{device_id}"
        self._attr_source_type = SourceType.GPS

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information about this tracker."""
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device_name,
            "manufacturer": "petTracer",
            "model": "Pet Collar",
        }

    @property
    def latitude(self) -> float | None:
        """Return latitude value of the device."""
        if not self.coordinator.data or self._device_id not in self.coordinator.data:
            return None

        device = self.coordinator.data[self._device_id]
        return device.lastPos.posLat if device.lastPos else None

    @property
    def longitude(self) -> float | None:
        """Return longitude value of the device."""
        if not self.coordinator.data or self._device_id not in self.coordinator.data:
            return None

        device = self.coordinator.data[self._device_id]
        return device.lastPos.posLong if device.lastPos else None

    @property
    def location_accuracy(self) -> int:
        """Return the location accuracy of the device."""
        if not self.coordinator.data or self._device_id not in self.coordinator.data:
            return 0

        device = self.coordinator.data[self._device_id]
        return device.lastPos.acc if device.lastPos and device.lastPos.acc else 0

    @property
    def battery_level(self) -> int | None:
        """Return the battery level of the device."""
        if not self.coordinator.data or self._device_id not in self.coordinator.data:
            return None

        device = self.coordinator.data[self._device_id]
        # Convert battery voltage (mV) to approximate percentage
        # Typical range: 3300mV (empty) to 4200mV (full)
        if device.bat:
            return min(100, max(0, int((device.bat - 3300) / 9)))
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        attrs = {}

        if not self.coordinator.data or self._device_id not in self.coordinator.data:
            return attrs

        device = self.coordinator.data[self._device_id]

        # Add battery voltage (mV)
        if device.bat:
            attrs["battery_voltage"] = device.bat

        # Add last position timestamp
        if device.lastPos and device.lastPos.timeMeasure:
            attrs["last_update"] = device.lastPos.timeMeasure

        # Add last contact with device
        if device.lastContact:
            attrs["last_contact"] = device.lastContact

        # Add GPS quality info
        if device.lastPos:
            if device.lastPos.sat is not None:
                attrs["satellites"] = device.lastPos.sat
            if device.lastPos.rssi is not None:
                attrs["signal_strength"] = device.lastPos.rssi

        # Add device status
        if device.status is not None:
            attrs["status"] = device.status
        if device.mode is not None:
            attrs["mode"] = device.mode

        # Add charging status
        if device.chg is not None:
            attrs["charging"] = "Charging" if device.chg == 1 else "Not charging"

        # Add tracking mode
        if device.modeSet is not None:
            modes = {1: "Fast", 2: "Normal", 3: "Slow"}
            attrs["tracking_mode"] = modes.get(device.modeSet, "Unknown")

        # Add live tracking status
        if device.search is not None:
            attrs["live_tracking"] = "On" if device.search else "Off"

        return attrs
