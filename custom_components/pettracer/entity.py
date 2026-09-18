"""Shared base entity for the petTracer integration."""

from __future__ import annotations

from typing import Any

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import PetTracerDataUpdateCoordinator
from .const import DOMAIN


class PetTracerEntity(CoordinatorEntity):
    """Base entity for a single petTracer collar.

    Holds the coordinator plus the collar's id and display name, and
    provides the device-registry info, availability check, and safe
    device access shared by every entity in this integration.
    """

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: PetTracerDataUpdateCoordinator,
        device_id: str,
        device_name: str,
        key: str | None = None,
    ) -> None:
        """Initialize the entity for one collar."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._device_name = device_name
        unique_id = f"{DOMAIN}_{device_id}"
        if key:
            unique_id = f"{unique_id}_{key}"
        self._attr_unique_id = unique_id

    def _device(self) -> Any | None:
        """Return the collar's latest data, or None when it is missing."""
        data = self.coordinator.data
        if not data or self._device_id not in data:
            return None
        return data[self._device_id]

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information for the HA device registry."""
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device_name,
            "manufacturer": "petTracer",
            "model": "Pet Collar",
        }

    @property
    def available(self) -> bool:
        """Return True while the collar's latest data is available."""
        return super().available and self._device() is not None