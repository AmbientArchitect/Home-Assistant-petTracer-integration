"""Diagnostics support for the petTracer integration."""

from __future__ import annotations

import dataclasses
from enum import Enum
from typing import Any

from homeassistant.components.diagnostics import RedactData, async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD
from homeassistant.core import HomeAssistant

from . import PetTracerDataUpdateCoordinator
from .const import DOMAIN

TO_REDACT: RedactData = {
    CONF_PASSWORD: "***",
}


def _dump(value: Any) -> Any:
    """Serialize a Device tree for diagnostics output."""
    if dataclasses.is_dataclass(value):
        return {field: _dump(item) for field, item in vars(value).items()}
    if isinstance(value, dict):
        return {key: _dump(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_dump(item) for item in value]
    if isinstance(value, Enum):
        return value.value
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator: PetTracerDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    return {
        "entry": async_redact_data(entry.data, TO_REDACT),
        "client": {
            "user_id": coordinator.client.user_id,
            "user_name": coordinator.client.user_name,
            "email": coordinator.client.email,
            "is_authenticated": coordinator.client.is_authenticated,
            "token_expires": coordinator.client.token_expires,
            "stream_connected": (
                coordinator.stream.connected if coordinator.stream is not None else None
            ),
        },
        "devices": {
            device_id: _dump(device)
            for device_id, device in (coordinator.data or {}).items()
        },
    }