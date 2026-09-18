"""Tests for the switch platform (LED, buzzer)."""

from __future__ import annotations

from custom_components.pettracer.switch import (
    PetTracerBuzzerSwitch,
    PetTracerLedSwitch,
    async_setup_entry,
)

from tests.conftest import ConfigEntry, make_device


def _led(coordinator, device) -> PetTracerLedSwitch:
    coordinator.data = {device.id: device}
    return PetTracerLedSwitch(coordinator, device.id, "Whiskers")


def test_led_is_on(coordinator) -> None:
    assert _led(coordinator, make_device(led=True)).is_on is True
    assert _led(coordinator, make_device(led=False)).is_on is False


def test_led_is_on_none_when_device_missing(coordinator) -> None:
    """Regression: used to raise KeyError instead of reporting unknown."""
    switch = PetTracerLedSwitch(coordinator, "ghost", "Ghost")
    assert switch.is_on is None


def test_buzzer_is_on(coordinator) -> None:
    device = make_device(buz=True)
    switch = PetTracerBuzzerSwitch(coordinator, device.id, "Whiskers")
    coordinator.data = {device.id: device}
    assert switch.is_on is True


async def test_led_turn_on_and_off(coordinator) -> None:
    device = make_device(led=False)
    switch = _led(coordinator, device)
    await switch.async_turn_on()
    await switch.async_turn_off()
    assert coordinator.client.calls == [
        ("set_led", ("dev-1", True)),
        ("set_led", ("dev-1", False)),
    ]


async def test_buzzer_turn_on_and_off(coordinator) -> None:
    device = make_device(buz=False)
    switch = PetTracerBuzzerSwitch(coordinator, device.id, "Whiskers")
    coordinator.data = {device.id: device}
    await switch.async_turn_on()
    await switch.async_turn_off()
    assert coordinator.client.calls == [
        ("set_buzzer", ("dev-1", True)),
        ("set_buzzer", ("dev-1", False)),
    ]


async def test_setup_entry_creates_led_and_buzzer(coordinator) -> None:
    coordinator.data = {"dev-1": make_device(buz=True)}
    added: list[object] = []
    entry = ConfigEntry()

    class FakeHass:
        data = {"pettracer": {"entry1": coordinator}}

    await async_setup_entry(FakeHass(), entry, added.extend)

    classes = [type(entity) for entity in added]
    assert PetTracerLedSwitch in classes
    assert PetTracerBuzzerSwitch in classes


async def test_setup_entry_skips_buzzer_without_hardware(coordinator) -> None:
    coordinator.data = {"dev-1": make_device(buz=None)}
    added: list[object] = []
    entry = ConfigEntry()

    class FakeHass:
        data = {"pettracer": {"entry1": coordinator}}

    await async_setup_entry(FakeHass(), entry, added.extend)

    classes = [type(entity) for entity in added]
    assert PetTracerLedSwitch in classes
    assert PetTracerBuzzerSwitch not in classes