"""Tests for the sensor platform."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pettracer.types import TrackingMode

from custom_components.pettracer.sensor import SENSOR_TYPES, PetTracerSensor

from tests.conftest import make_device, make_last_pos


def _sensor(coordinator, device, key: str) -> PetTracerSensor:
    coordinator.data = {device.id: device}
    desc = next(d for d in SENSOR_TYPES if d.key == key)
    return PetTracerSensor(coordinator, device.id, "Whiskers", desc)


def test_sensor_types_cover_eight_entities() -> None:
    assert len(SENSOR_TYPES) == 8


@pytest.mark.parametrize("key", [d.key for d in SENSOR_TYPES])
def test_native_value_none_when_device_missing(coordinator, key: str) -> None:
    desc = next(d for d in SENSOR_TYPES if d.key == key)
    sensor = PetTracerSensor(coordinator, "ghost", "Ghost", desc)
    assert sensor.native_value is None


def test_battery_level(coordinator) -> None:
    sensor = _sensor(coordinator, make_device(bat=3900), "battery_level")
    assert sensor.native_value == 66


def test_battery_level_none_when_absent(coordinator) -> None:
    sensor = _sensor(coordinator, make_device(bat=None), "battery_level")
    assert sensor.native_value is None


def test_battery_voltage(coordinator) -> None:
    sensor = _sensor(coordinator, make_device(bat=3900), "battery_voltage")
    assert sensor.native_value == 3900


def test_signal_strength(coordinator) -> None:
    device = make_device(lastPos=make_last_pos(rssi=-65))
    sensor = _sensor(coordinator, device, "signal_strength")
    assert sensor.native_value == -65


def test_signal_strength_none_without_last_pos(coordinator) -> None:
    sensor = _sensor(coordinator, make_device(lastPos=None), "signal_strength")
    assert sensor.native_value is None


def test_last_contact_parses_iso_string(coordinator) -> None:
    device = make_device(lastContact="2026-09-18T11:00:00Z")
    sensor = _sensor(coordinator, device, "last_contact")
    assert sensor.native_value == datetime(2026, 9, 18, 11, 0, tzinfo=timezone.utc)


def test_last_contact_passes_datetime_through(coordinator) -> None:
    value = datetime(2026, 9, 18, 11, 0, tzinfo=timezone.utc)
    sensor = _sensor(coordinator, make_device(lastContact=value), "last_contact")
    assert sensor.native_value == value


def test_last_contact_none_for_garbage_and_missing(coordinator) -> None:
    sensor = _sensor(coordinator, make_device(lastContact="not-a-date"), "last_contact")
    assert sensor.native_value is None
    sensor = _sensor(coordinator, make_device(lastContact=None), "last_contact")
    assert sensor.native_value is None


def test_satellites(coordinator) -> None:
    device = make_device(lastPos=make_last_pos(sat=11))
    sensor = _sensor(coordinator, device, "satellites")
    assert sensor.native_value == 11


def test_satellites_none_without_last_pos(coordinator) -> None:
    sensor = _sensor(coordinator, make_device(lastPos=None), "satellites")
    assert sensor.native_value is None


@pytest.mark.parametrize(
    ("chg", "expected"),
    [(1, "Charging"), (0, "Not charging"), (None, None)],
)
def test_charging_status(coordinator, chg: int | None, expected: str | None) -> None:
    sensor = _sensor(coordinator, make_device(chg=chg), "charging_status")
    assert sensor.native_value == expected


@pytest.mark.parametrize(
    ("mode_set", "expected"),
    [
        (TrackingMode.FAST, "Fast"),
        (TrackingMode.NORMAL, "Normal"),
        (TrackingMode.SLOW, "Slow"),
        (TrackingMode.SUPER_SLOW, "Super slow"),
        (TrackingMode.SEARCH, "Search"),
        (999, "Unknown"),
        (None, None),
    ],
)
def test_tracking_mode_sensor(coordinator, mode_set, expected: str | None) -> None:
    sensor = _sensor(coordinator, make_device(modeSet=mode_set), "tracking_mode")
    assert sensor.native_value == expected


@pytest.mark.parametrize(
    ("mode", "expected"),
    [
        (TrackingMode.SEARCH, "On"),
        (TrackingMode.NORMAL, "Off"),
        (None, None),
    ],
)
def test_search_status_sensor(coordinator, mode, expected: str | None) -> None:
    sensor = _sensor(coordinator, make_device(mode=mode), "search_status")
    assert sensor.native_value == expected


def test_voltage_sensor_disabled_by_default() -> None:
    desc = next(d for d in SENSOR_TYPES if d.key == "battery_voltage")
    assert desc.entity_registry_enabled_default is False


def test_unique_ids_are_stable(coordinator) -> None:
    device = make_device()
    sensor = _sensor(coordinator, device, "battery_level")
    assert sensor.unique_id == "pettracer_dev-1_battery_level"