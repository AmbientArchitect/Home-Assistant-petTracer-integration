"""Support for petTracer device tracking."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.device_tracker import SourceType, TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import PetTracerDataUpdateCoordinator
from .const import DOMAIN
from .entity import PetTracerEntity
from .helpers import battery_percentage, charging_label, device_display_name, is_searching, tracking_mode_label

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
            entities.append(
                PetTracerDeviceTracker(
                    coordinator, device_id, device_display_name(device, device_id)
                )
            )

    async_add_entities(entities)


class PetTracerDeviceTracker(PetTracerEntity, TrackerEntity):
    """Representation of a petTracer device tracker."""

    _attr_name = None
    _attr_source_type = SourceType.GPS

    def __init__(
        self,
        coordinator: PetTracerDataUpdateCoordinator,
        device_id: str,
        device_name: str,
    ) -> None:
        """Initialize the petTracer device tracker."""
        super().__init__(coordinator, device_id, device_name)

    @property
    def latitude(self) -> float | None:
        """Return latitude value of the device."""
        device = self._device()
        if device is None or device.lastPos is None:
            return None
        return device.lastPos.posLat

    @property
    def longitude(self) -> float | None:
        """Return longitude value of the device."""
        device = self._device()
        if device is None or device.lastPos is None:
            return None
        return device.lastPos.posLong

    @property
    def location_accuracy(self) -> int:
        """Return the location accuracy of the device."""
        device = self._device()
        if device is None or device.lastPos is None:
            return 0
        return device.lastPos.acc or 0

    @property
    def battery_level(self) -> int | None:
        """Return the battery level of the device."""
        device = self._device()
        if device is None or not device.bat:
            return None
        return battery_percentage(device.bat)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        attrs = {}
        device = self._device()
        if device is None:
            return attrs

        if device.bat:
            attrs["battery_voltage"] = device.bat

        if device.lastPos is not None and device.lastPos.timeMeasure:
            attrs["last_update"] = device.lastPos.timeMeasure

        if device.lastContact:
            attrs["last_contact"] = device.lastContact

        if device.lastPos is not None:
            if device.lastPos.sat is not None:
                attrs["satellites"] = device.lastPos.sat
            if device.lastPos.rssi is not None:
                attrs["signal_strength"] = device.lastPos.rssi

        if device.status is not None:
            attrs["status"] = device.status
        if device.mode is not None:
            attrs["mode"] = device.mode

        if device.chg is not None:
            attrs["charging"] = charging_label(device.chg)

        if device.modeSet is not None:
            attrs["tracking_mode"] = tracking_mode_label(device.modeSet)

        if device.mode is not None:
            attrs["live_tracking"] = "On" if is_searching(device.mode) else "Off"

        return attrs