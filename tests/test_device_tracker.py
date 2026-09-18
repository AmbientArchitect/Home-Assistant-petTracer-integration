"""Tests for the device tracker platform."""

from __future__ import annotations

from pettracer.types import Device, TrackingMode

from custom_components.pettracer.device_tracker import PetTracerDeviceTracker

from tests.conftest import make_device, make_last_pos


def _tracker(coordinator, device: Device) -> PetTracerDeviceTracker:
    coordinator.data = {device.id: device}
    return PetTracerDeviceTracker(coordinator, device.id, "Whiskers")


def test_latitude_and_longitude(coordinator) -> None:
    device = make_device(lastPos=make_last_pos(posLat=54.352, posLong=18.6466))
    tracker = _tracker(coordinator, device)
    assert tracker.latitude == 54.352
    assert tracker.longitude == 18.6466


def test_coordinates_none_without_last_pos(coordinator) -> None:
    tracker = _tracker(coordinator, make_device(lastPos=None))
    assert tracker.latitude is None
    assert tracker.longitude is None


def test_coordinates_none_when_device_missing(coordinator) -> None:
    tracker = PetTracerDeviceTracker(coordinator, "ghost", "Ghost")
    assert tracker.latitude is None
    assert tracker.longitude is None
    assert tracker.location_accuracy == 0


def test_location_accuracy(coordinator) -> None:
    tracker = _tracker(coordinator, make_device(lastPos=make_last_pos(acc=12)))
    assert tracker.location_accuracy == 12


def test_location_accuracy_zero_when_unset(coordinator) -> None:
    tracker = _tracker(coordinator, make_device(lastPos=make_last_pos(acc=0)))
    assert tracker.location_accuracy == 0


def test_battery_level_percentage(coordinator) -> None:
    tracker = _tracker(coordinator, make_device(bat=3900))
    assert tracker.battery_level == 66


def test_battery_level_none_when_absent(coordinator) -> None:
    tracker = _tracker(coordinator, make_device(bat=None))
    assert tracker.battery_level is None


def test_extra_state_attributes_empty_when_device_missing(coordinator) -> None:
    tracker = PetTracerDeviceTracker(coordinator, "ghost", "Ghost")
    assert tracker.extra_state_attributes == {}


def test_extra_state_attributes_full(coordinator) -> None:
    device = make_device(
        bat=3900,
        chg=1,
        lastContact="2026-09-18T11:00:00Z",
        lastPos=make_last_pos(sat=9, rssi=-70, timeMeasure="2026-09-18T10:00:00Z"),
        status=5,
        mode=TrackingMode.NORMAL,
    )
    attrs = _tracker(coordinator, device).extra_state_attributes
    assert attrs["battery_voltage"] == 3900
    assert attrs["last_update"] == "2026-09-18T10:00:00Z"
    assert attrs["last_contact"] == "2026-09-18T11:00:00Z"
    assert attrs["satellites"] == 9
    assert attrs["signal_strength"] == -70
    assert attrs["status"] == 5
    assert attrs["charging"] == "Charging"
    assert attrs["tracking_mode"] == "Normal"
    assert attrs["live_tracking"] == "Off"


def test_extra_state_attributes_not_charging(coordinator) -> None:
    attrs = _tracker(coordinator, make_device(chg=0)).extra_state_attributes
    assert attrs["charging"] == "Not charging"


def test_tracking_mode_label_for_super_slow(coordinator) -> None:
    """Regression: modeSet 4 used to report "Unknown" here."""
    device = make_device(modeSet=TrackingMode.SUPER_SLOW)
    attrs = _tracker(coordinator, device).extra_state_attributes
    assert attrs["tracking_mode"] == "Super slow"


def test_tracking_mode_label_for_search(coordinator) -> None:
    """Regression: modeSet 11 used to report "Unknown" here."""
    device = make_device(modeSet=TrackingMode.SEARCH)
    attrs = _tracker(coordinator, device).extra_state_attributes
    assert attrs["tracking_mode"] == "Search"


def test_live_tracking_on_during_search(coordinator) -> None:
    device = make_device(mode=TrackingMode.SEARCH)
    attrs = _tracker(coordinator, device).extra_state_attributes
    assert attrs["live_tracking"] == "On"


def test_tracker_is_gps_source() -> None:
    assert PetTracerDeviceTracker._attr_source_type.value == "gps"