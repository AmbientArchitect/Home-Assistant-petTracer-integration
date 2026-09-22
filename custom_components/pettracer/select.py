"""Support for petTracer collar tracking-mode selection."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from pettracer.types import TrackingMode

from . import PetTracerDataUpdateCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

MODE_TO_OPTION: dict[TrackingMode, str] = {
    TrackingMode.SEARCH: "Search",
    TrackingMode.FAST: "Fast",
    TrackingMode.NORMAL: "Normal",
    TrackingMode.SLOW: "Slow",
    TrackingMode.SUPER_SLOW: "Super slow",
}
OPTION_TO_MODE = {option: mode for mode, option in MODE_TO_OPTION.items()}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up petTracer select entities from config entry."""
    coordinator: PetTracerDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    if coordinator.data:
        for device_id, device in coordinator.data.items():
            device_name = (
                device.details.name if device.details else f"Pet Tracker {device_id}"
            )
            entities.append(
                PetTracerTrackingModeSelect(coordinator, device_id, device_name)
            )

    async_add_entities(entities)


class PetTracerTrackingModeSelect(CoordinatorEntity, SelectEntity):
    """Select entity for a petTracer collar's tracking mode."""

    _attr_has_entity_name = True
    _attr_name = "Tracking mode"
    _attr_icon = "mdi:crosshairs-gps"
    _attr_options = list(OPTION_TO_MODE)

    def __init__(
        self,
        coordinator: PetTracerDataUpdateCoordinator,
        device_id: int,
        device_name: str,
    ) -> None:
        """Initialize the tracking mode select."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._device_name = device_name
        self._attr_unique_id = f"{DOMAIN}_{device_id}_tracking_mode_select"

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information about this select."""
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
    def current_option(self) -> str | None:
        """Return the current tracking mode."""
        device = self.coordinator.data[self._device_id]
        #        mode = device.modeSet if device.modeSet is not None else device.mode
        #        if mode is None:
        mode = device.mode if device.mode is not None else None
        if mode is None:
            return None
        try:
            return MODE_TO_OPTION.get(TrackingMode(mode))
        except ValueError:
            # Firmware/Search mode or another id this selector doesn't expose.
            return None

    async def async_select_option(self, option: str) -> None:
        """Change the collar's tracking mode."""
        mode = OPTION_TO_MODE[option]
        await self.coordinator.client.get_device(self._device_id).set_tracking_mode(
            mode
        )
        await self.coordinator.async_request_refresh()
