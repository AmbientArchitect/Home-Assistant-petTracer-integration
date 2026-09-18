"""Shared pytest fixtures and Home Assistant stand-ins.

The petTracer component only uses a thin slice of the Home Assistant API
(some entity base classes, a few enums, one datetime helper). This module
registers lightweight stand-ins for exactly that slice in ``sys.modules``
so the whole test suite runs without installing Home Assistant itself;
the stand-ins mirror the real API surface the component touches.
"""

from __future__ import annotations

import sys
import types
from datetime import datetime, timezone
from enum import Enum
from typing import Any

import pytest
from pettracer.types import Device, Details, LastPos, TrackingMode


def _register_module(name: str, **attrs: Any) -> types.ModuleType:
    """Register a stand-in module in sys.modules."""
    module = types.ModuleType(name)
    for attr, value in attrs.items():
        setattr(module, attr, value)
    sys.modules[name] = module
    return module


class HomeAssistantError(Exception):
    """Stand-in for homeassistant.exceptions.HomeAssistantError."""


class ConfigEntryAuthFailed(HomeAssistantError):
    """Stand-in for homeassistant.exceptions.ConfigEntryAuthFailed."""


class ConfigEntryNotReady(HomeAssistantError):
    """Stand-in for homeassistant.exceptions.ConfigEntryNotReady."""


class UpdateFailed(Exception):
    """Stand-in for homeassistant.helpers.update_coordinator.UpdateFailed."""


class Platform(Enum):
    """Stand-in for homeassistant.const.Platform."""

    DEVICE_TRACKER = "device_tracker"
    SENSOR = "sensor"
    SWITCH = "switch"
    SELECT = "select"
    BUTTON = "button"


class UnitOfElectricPotential(Enum):
    """Stand-in for homeassistant.const.UnitOfElectricPotential."""

    MILLIVOLT = "mV"
    VOLT = "V"


class SensorDeviceClass(Enum):
    """Stand-in for homeassistant.components.sensor.SensorDeviceClass."""

    BATTERY = "battery"
    VOLTAGE = "voltage"
    SIGNAL_STRENGTH = "signal_strength"
    TIMESTAMP = "timestamp"


class SensorStateClass(Enum):
    """Stand-in for homeassistant.components.sensor.SensorStateClass."""

    MEASUREMENT = "measurement"


class SourceType(Enum):
    """Stand-in for homeassistant.components.device_tracker.SourceType."""

    GPS = "gps"


class SensorEntityDescription:
    """Stand-in for homeassistant.components.sensor.SensorEntityDescription."""

    def __init__(
        self,
        key: str = "",
        name: str = "",
        device_class: SensorDeviceClass | None = None,
        native_unit_of_measurement: str | None = None,
        state_class: SensorStateClass | None = None,
        entity_registry_enabled_default: bool = True,
        icon: str | None = None,
    ) -> None:
        self.key = key
        self.name = name
        self.device_class = device_class
        self.native_unit_of_measurement = native_unit_of_measurement
        self.state_class = state_class
        self.entity_registry_enabled_default = entity_registry_enabled_default
        self.icon = icon


class CoordinatorEntity:
    """Stand-in for CoordinatorEntity: tracks coordinator + availability."""

    def __init__(self, coordinator: Any) -> None:
        self.coordinator = coordinator

    @property
    def available(self) -> bool:
        return bool(getattr(self.coordinator, "last_update_success", True))

    @property
    def unique_id(self) -> str | None:
        return getattr(self, "_attr_unique_id", None)


class DataUpdateCoordinator:
    """Stand-in for DataUpdateCoordinator, minimal async behavior."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.data: Any = None
        self.last_update_success = True

    def async_set_updated_data(self, data: Any) -> None:
        self.data = data

    async def async_config_entry_first_refresh(self) -> None:
        method = getattr(self, "_async_update_data", None)
        if method is not None:
            self.data = await method()
        self.last_update_success = True

    async def async_request_refresh(self) -> None:
        method = getattr(self, "_async_update_data", None)
        if method is not None:
            self.data = await method()


class TrackerEntity:
    """Stand-in for homeassistant.components.device_tracker.TrackerEntity."""


class SensorEntity:
    """Stand-in for homeassistant.components.sensor.SensorEntity."""


class SwitchEntity:
    """Stand-in for homeassistant.components.switch.SwitchEntity."""


class SelectEntity:
    """Stand-in for homeassistant.components.select.SelectEntity."""


class ButtonEntity:
    """Stand-in for homeassistant.components.button.ButtonEntity."""


class ConfigEntry:
    """Stand-in for homeassistant.config_entries.ConfigEntry."""

    def __init__(self, entry_id: str = "entry1", data: dict[str, Any] | None = None):
        self.entry_id = entry_id
        self.data = data or {}


class HomeAssistant:
    """Stand-in for homeassistant.core.HomeAssistant."""


class ConfigFlow:
    """Stand-in for homeassistant.config_entries.ConfigFlow."""

    def __init_subclass__(cls, domain: str | None = None, **kwargs: Any) -> None:
        cls.domain = domain
        super().__init_subclass__(**kwargs)

    def __init__(self) -> None:
        self.domain = getattr(self, "domain", None)


def _register_all() -> None:
    """Register every Home Assistant stand-in used by the component."""
    _register_module("homeassistant")
    _register_module(
        "homeassistant.const",
        CONF_USERNAME="username",
        CONF_PASSWORD="password",
        PERCENTAGE="%",
        SIGNAL_STRENGTH_DECIBELS_MILLIWATT="dBm",
        Platform=Platform,
        UnitOfElectricPotential=UnitOfElectricPotential,
    )
    _register_module("homeassistant.core", HomeAssistant=HomeAssistant)
    _register_module(
        "homeassistant.config_entries",
        ConfigEntry=ConfigEntry,
        ConfigFlow=ConfigFlow,
        ConfigFlowResult=dict,
    )
    _register_module(
        "homeassistant.exceptions",
        HomeAssistantError=HomeAssistantError,
        ConfigEntryAuthFailed=ConfigEntryAuthFailed,
        ConfigEntryNotReady=ConfigEntryNotReady,
    )
    _register_module("homeassistant.helpers.typing", ConfigType=None)
    _register_module(
        "homeassistant.helpers.update_coordinator",
        CoordinatorEntity=CoordinatorEntity,
        DataUpdateCoordinator=DataUpdateCoordinator,
        UpdateFailed=UpdateFailed,
    )
    _register_module(
        "homeassistant.helpers.entity_platform",
        AddEntitiesCallback=None,
        AddConfigEntryEntitiesCallback=None,
    )
    _register_module("homeassistant.helpers.aiohttp_client", async_get_clientsession=None)

    _register_module(
        "homeassistant.components.device_tracker",
        SourceType=SourceType,
        TrackerEntity=TrackerEntity,
    )
    _register_module(
        "homeassistant.components.sensor",
        SensorEntity=SensorEntity,
        SensorEntityDescription=SensorEntityDescription,
        SensorDeviceClass=SensorDeviceClass,
        SensorStateClass=SensorStateClass,
    )
    _register_module("homeassistant.components.switch", SwitchEntity=SwitchEntity)
    _register_module("homeassistant.components.select", SelectEntity=SelectEntity)
    _register_module("homeassistant.components.button", ButtonEntity=ButtonEntity)
    _register_module(
        "homeassistant.components.diagnostics",
        RedactData=None,
        async_redact_data=lambda data, to_redact: {
            key: to_redact.get(key, value) for key, value in data.items()
        },
    )

    def _dt_parse(value: str) -> datetime | None:
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None

    _register_module(
        "homeassistant.util",
    )
    _register_module(
        "homeassistant.util.dt",
        parse_datetime=_dt_parse,
        utcnow=lambda: datetime.now(timezone.utc),
    )


_register_all()


@pytest.fixture
def coordinator() -> Any:
    """A coordinator with no data yet, plus a working fake client."""

    class FakeClient:
        def __init__(self) -> None:
            self.devices: dict[str, Device] = {}
            self.calls: list[tuple[str, Any]] = []
            self.stream = FakeStream()
            self.user_id = 7
            self.user_name = "pet@example.com"
            self.email = "pet@example.com"
            self.is_authenticated = True
            self.token_expires = "2026-10-01T00:00:00Z"

        def get_stream(self) -> FakeStream:
            return self.stream

        def get_device(self, device_id: str) -> "FakeDevice":
            return FakeDevice(self, device_id)

        async def get_all_devices(self) -> list[Device]:
            return list(self.devices.values())

        async def login(self, username: str, password: str, timeout: int = 30) -> None:
            self.calls.append(("login", (username, password, timeout)))

    class FakeDevice:
        def __init__(self, client: FakeClient, device_id: str) -> None:
            self.client = client
            self.device_id = device_id

        async def set_led(self, value: bool) -> None:
            self.client.calls.append(("set_led", (self.device_id, value)))

        async def set_buzzer(self, value: bool) -> None:
            self.client.calls.append(("set_buzzer", (self.device_id, value)))

        async def set_tracking_mode(self, mode: TrackingMode) -> None:
            self.client.calls.append(("set_tracking_mode", (self.device_id, mode)))

        async def start_search_mode(self) -> None:
            self.client.calls.append(("start_search_mode", (self.device_id,)))

    client = FakeClient()
    coord = DataUpdateCoordinator()
    coord.client = client
    coord.data = None
    coord.last_update_success = True

    # Import the real coordinator class once stubs are registered.
    from custom_components.pettracer import PetTracerDataUpdateCoordinator

    class MiniCoordinator(PetTracerDataUpdateCoordinator):
        """Binds the real coordinator logic to the fake client."""

        def __init__(self) -> None:
            super().__init__(None, client, ConfigEntry(), None)

    return MiniCoordinator()


def make_device(**overrides: Any) -> Device:
    """Build a Device with all required dataclass fields filled in."""
    defaults: dict[str, Any] = {
        "id": "dev-1",
        "accuWarn": 0,
        "safetyZone": None,
        "hw": "1.0",
        "sw": "1.0",
        "bl": 0,
        "bat": 3900,
        "chg": 0,
        "userId": 7,
        "masterHs": None,
        "mode": TrackingMode.NORMAL,
        "modeSet": TrackingMode.NORMAL,
        "status": 5,
        "search": False,
        "lastTlgNr": 0,
        "lastContact": None,
        "lastPos": None,
        "devMode": 0,
        "details": None,
        "led": False,
        "ble": False,
        "buz": False,
        "lastRssi": -70,
        "flags": 0,
        "searchModeDuration": None,
        "masterStatus": None,
        "home": None,
        "homeSince": None,
        "owner": None,
        "fiFo": None,
    }
    defaults.update(overrides)
    return Device(**defaults)


def make_last_pos(**overrides: Any) -> LastPos:
    """Build a LastPos with all required dataclass fields filled in."""
    defaults: dict[str, Any] = {
        "id": 1,
        "posLat": 54.352,
        "posLong": 18.6466,
        "fixS": 0,
        "fixP": 0,
        "horiPrec": 0,
        "sat": 9,
        "rssi": -70,
        "acc": 12,
        "flags": 0,
        "timeMeasure": "2026-09-18T10:00:00Z",
        "timeDb": "2026-09-18T10:00:00Z",
    }
    defaults.update(overrides)
    return LastPos(**defaults)


def make_details(name: str = "Whiskers") -> Details:
    """Build a Details with all required dataclass fields filled in."""
    return Details(
        id=1,
        image=None,
        img=None,
        color=None,
        birth=None,
        name=name,
    )


class FakeStream:
    """Stand-in for pettracer.stream.PetTracerStream."""

    def __init__(self) -> None:
        self.started = False
        self.stopped = False
        self.connected = False
        self.handlers: list[Any] = []

    def on_update(self, handler: Any) -> None:
        self.handlers.append(handler)

    def on_connect(self, handler: Any) -> None:
        pass

    def on_disconnect(self, handler: Any) -> None:
        pass

    async def start(self) -> None:
        self.started = True
        self.connected = True

    async def stop(self) -> None:
        self.stopped = True
        self.connected = False