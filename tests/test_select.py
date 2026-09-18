"""Tests for the tracking-mode select platform."""

from __future__ import annotations

from pettracer.types import TrackingMode

from custom_components.pettracer.select import (
    OPTION_TO_MODE,
    PetTracerTrackingModeSelect,
    async_setup_entry,
)

from tests.conftest import ConfigEntry, make_device


def _select(coordinator, device) -> PetTracerTrackingModeSelect:
    coordinator.data = {device.id: device}
    return PetTracerTrackingModeSelect(coordinator, device.id, "Whiskers")


def test_options_exclude_search_mode() -> None:
    select = PetTracerTrackingModeSelect(None, "dev-1", "Whiskers")  # type: ignore[arg-type]
    assert select._attr_options == ["Fast", "Normal", "Slow", "Super slow"]


def test_option_maps_are_inverse(coordinator) -> None:
    select = _select(coordinator, make_device())
    for option in select._attr_options:
        assert OPTION_TO_MODE[option] is not None


def test_current_option_prefers_mode_set(coordinator) -> None:
    device = make_device(modeSet=TrackingMode.SUPER_SLOW, mode=TrackingMode.FAST)
    assert _select(coordinator, device).current_option == "Super slow"


def test_current_option_falls_back_to_confirmed_mode(coordinator) -> None:
    device = make_device(modeSet=None, mode=TrackingMode.SLOW)
    assert _select(coordinator, device).current_option == "Slow"


def test_current_option_none_when_unknown(coordinator) -> None:
    device = make_device(modeSet=None, mode=None)
    assert _select(coordinator, device).current_option is None


def test_current_option_none_for_search_mode(coordinator) -> None:
    """Search is transient, so it is not a selectable option."""
    device = make_device(mode=TrackingMode.SEARCH, modeSet=None)
    assert _select(coordinator, device).current_option is None


def test_current_option_none_when_device_missing(coordinator) -> None:
    """Regression: used to raise KeyError instead of reporting unknown."""
    select = PetTracerTrackingModeSelect(coordinator, "ghost", "Ghost")
    assert select.current_option is None


async def test_async_select_option_sends_mode(coordinator) -> None:
    device = make_device()
    select = _select(coordinator, device)
    await select.async_select_option("Super slow")
    assert coordinator.client.calls == [
        ("set_tracking_mode", ("dev-1", TrackingMode.SUPER_SLOW))
    ]


async def test_setup_entry_creates_one_select_per_device(coordinator) -> None:
    coordinator.data = {"dev-1": make_device()}
    added: list[object] = []
    entry = ConfigEntry()

    class FakeHass:
        data = {"pettracer": {"entry1": coordinator}}

    await async_setup_entry(FakeHass(), entry, added.extend)
    assert len(added) == 1
    assert isinstance(added[0], PetTracerTrackingModeSelect)