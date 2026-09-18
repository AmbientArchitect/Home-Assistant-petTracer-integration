"""Tests for the find button platform."""

from __future__ import annotations

from custom_components.pettracer.button import PetTracerFindButton, async_setup_entry

from tests.conftest import ConfigEntry, make_device


def _button(coordinator, device) -> PetTracerFindButton:
    coordinator.data = {device.id: device}
    return PetTracerFindButton(coordinator, device.id, "Whiskers")


async def test_async_press_starts_search_mode(coordinator) -> None:
    button = _button(coordinator, make_device())
    await button.async_press()
    assert coordinator.client.calls == [("start_search_mode", ("dev-1",))]


async def test_async_press_noop_when_device_missing(coordinator) -> None:
    """Regression: used to raise KeyError when the collar disappeared."""
    button = PetTracerFindButton(coordinator, "ghost", "Ghost")
    await button.async_press()
    assert coordinator.client.calls == []


async def test_setup_entry_creates_one_button_per_device(coordinator) -> None:
    coordinator.data = {"dev-1": make_device()}
    added: list[object] = []
    entry = ConfigEntry()

    class FakeHass:
        data = {"pettracer": {"entry1": coordinator}}

    await async_setup_entry(FakeHass(), entry, added.extend)
    assert len(added) == 1
    assert isinstance(added[0], PetTracerFindButton)