"""Tests for the shared pure helpers."""

from __future__ import annotations

import pytest
from pettracer.types import TrackingMode

from custom_components.pettracer.helpers import (
    BATTERY_EMPTY_MV,
    BATTERY_FULL_MV,
    TRACKING_MODE_LABELS,
    battery_percentage,
    charging_label,
    device_display_name,
    is_searching,
    tracking_mode_label,
)

from tests.conftest import make_details, make_device


@pytest.mark.parametrize(
    ("bat", "expected"),
    [
        (None, None),
        (BATTERY_EMPTY_MV, 0),
        (BATTERY_FULL_MV, 100),
        (3900, 66),
        (3750, 50),
        (3600, 33),
        (3301, 0),
        (4199, 99),
        # Clamping beyond the nominal range.
        (3000, 0),
        (4500, 100),
    ],
)
def test_battery_percentage(bat: int | None, expected: int | None) -> None:
    assert battery_percentage(bat) == expected


@pytest.mark.parametrize(
    ("mode", "expected"),
    [
        (int(TrackingMode.FAST), "Fast"),
        (int(TrackingMode.NORMAL), "Normal"),
        (int(TrackingMode.SLOW), "Slow"),
        (int(TrackingMode.SUPER_SLOW), "Super slow"),
        (int(TrackingMode.SEARCH), "Search"),
    ],
)
def test_tracking_mode_label(mode: int, expected: str) -> None:
    assert tracking_mode_label(mode) == expected


def test_tracking_mode_label_unknown_returns_unknown() -> None:
    assert tracking_mode_label(999) == "Unknown"


def test_tracking_mode_label_none_returns_none() -> None:
    assert tracking_mode_label(None) is None


def test_every_enum_member_has_a_label() -> None:
    """Regression: SUPER_SLOW and SEARCH used to show as "Unknown"."""
    assert {int(member) for member in TrackingMode} == set(TRACKING_MODE_LABELS)


@pytest.mark.parametrize(
    ("chg", "expected"),
    [
        (None, None),
        (1, "Charging"),
        (0, "Not charging"),
        (2, "Not charging"),
    ],
)
def test_charging_label(chg: int | None, expected: str | None) -> None:
    assert charging_label(chg) == expected


@pytest.mark.parametrize(
    ("mode", "expected"),
    [
        (TrackingMode.SEARCH, True),
        (TrackingMode.NORMAL, False),
        (TrackingMode.SUPER_SLOW, False),
        (None, False),
    ],
)
def test_is_searching(mode: TrackingMode | None, expected: bool) -> None:
    assert is_searching(mode) is expected


def test_device_display_name_uses_registered_name() -> None:
    device = make_device(details=make_details("Milo"))
    assert device_display_name(device, "dev-1") == "Milo"


def test_device_display_name_falls_back_to_id() -> None:
    device = make_device(details=None)
    assert device_display_name(device, "dev-1") == "Pet Tracker dev-1"


def test_device_display_name_falls_back_for_blank_name() -> None:
    device = make_device(details=make_details(""))
    assert device_display_name(device, "dev-1") == "Pet Tracker dev-1"


def test_device_display_name_handles_missing_device() -> None:
    assert device_display_name(None, "dev-1") == "Pet Tracker dev-1"