"""Tests for the coordinator and entry setup."""

from __future__ import annotations

import pytest
from pettracer import PetTracerError

from custom_components.pettracer import PetTracerDataUpdateCoordinator
from custom_components.pettracer.helpers import device_display_name

from tests.conftest import make_device


async def test_first_refresh_builds_device_dict(coordinator) -> None:
    coordinator.client.devices = {
        "dev-1": make_device(id="dev-1", details=None),
        "dev-2": make_device(id="dev-2"),
    }
    await coordinator.async_config_entry_first_refresh()
    assert set(coordinator.data) == {"dev-1", "dev-2"}
    assert coordinator.data["dev-1"].id == "dev-1"


async def test_first_refresh_skips_devices_without_id(coordinator) -> None:
    coordinator.client.devices = {
        "dev-1": make_device(id="dev-1"),
        "ghost": make_device(id=None),
    }
    await coordinator.async_config_entry_first_refresh()
    assert set(coordinator.data) == {"dev-1"}


async def test_update_failure_raises_update_failed(coordinator, monkeypatch) -> None:
    async def boom() -> None:
        raise PetTracerError("api down")

    monkeypatch.setattr(coordinator.client, "get_all_devices", boom)
    with pytest.raises(Exception) as excinfo:
        await coordinator.async_config_entry_first_refresh()
    assert "Error communicating with petTracer API" in str(excinfo.value)
    assert isinstance(excinfo.value.__cause__, PetTracerError)


def test_stream_update_merges_device(coordinator) -> None:
    coordinator.data = {"dev-1": make_device(id="dev-1", bat=3900)}
    pushed = make_device(id="dev-1", bat=4100)
    coordinator._handle_stream_update(pushed)
    assert coordinator.data["dev-1"].bat == 4100


def test_stream_update_adds_new_device(coordinator) -> None:
    coordinator.data = {}
    coordinator._handle_stream_update(make_device(id="dev-2"))
    assert set(coordinator.data) == {"dev-2"}


async def test_start_and_stop_stream(coordinator) -> None:
    await coordinator.async_start_stream()
    assert coordinator.stream is not None
    assert coordinator.stream.started is True
    stream = coordinator.stream
    await coordinator.async_stop_stream()
    assert stream.stopped is True
    assert coordinator.stream is None


async def test_stream_update_refreshes_data(coordinator) -> None:
    """A pushed device update lands in coordinator.data without a poll."""
    coordinator.client.devices = {"dev-1": make_device(id="dev-1", bat=3900)}
    await coordinator.async_config_entry_first_refresh()
    pushed = make_device(id="dev-1", bat=4050)
    coordinator._handle_stream_update(pushed)
    assert coordinator.data["dev-1"].bat == 4050


def test_coordinator_is_data_update_coordinator(coordinator) -> None:
    assert isinstance(coordinator, PetTracerDataUpdateCoordinator)


def test_device_display_name_is_used_for_unknown_devices(coordinator) -> None:
    device = make_device(id="dev-x", details=None)
    assert device_display_name(device, "dev-x") == "Pet Tracker dev-x"