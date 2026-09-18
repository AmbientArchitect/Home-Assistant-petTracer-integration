"""Tests for the shared base entity."""

from __future__ import annotations

from custom_components.pettracer.entity import PetTracerEntity

from tests.conftest import make_device


def _entity(coordinator, key: str | None = None) -> PetTracerEntity:
    return PetTracerEntity(coordinator, "dev-1", "Whiskers", key)


def test_unique_id_without_key(coordinator) -> None:
    assert _entity(coordinator).unique_id == "pettracer_dev-1"


def test_unique_id_with_key(coordinator) -> None:
    assert _entity(coordinator, "led").unique_id == "pettracer_dev-1_led"


def test_has_entity_name_enabled(coordinator) -> None:
    assert _entity(coordinator)._attr_has_entity_name is True


def test_device_info(coordinator) -> None:
    info = _entity(coordinator).device_info
    assert info["identifiers"] == {("pettracer", "dev-1")}
    assert info["name"] == "Whiskers"
    assert info["manufacturer"] == "petTracer"
    assert info["model"] == "Pet Collar"


def test_available_false_without_data(coordinator) -> None:
    entity = _entity(coordinator)
    coordinator.data = None
    assert entity.available is False


def test_available_false_when_device_missing(coordinator) -> None:
    entity = _entity(coordinator)
    coordinator.data = {"other-dev": make_device(id="other-dev")}
    assert entity.available is False


def test_available_true_when_device_present(coordinator) -> None:
    entity = _entity(coordinator)
    coordinator.data = {"dev-1": make_device()}
    assert entity.available is True


def test_available_false_when_coordinator_unsuccessful(coordinator) -> None:
    entity = _entity(coordinator)
    coordinator.data = {"dev-1": make_device()}
    coordinator.last_update_success = False
    assert entity.available is False


def test_device_returns_none_when_missing(coordinator) -> None:
    assert _entity(coordinator)._device() is None


def test_device_returns_latest_data(coordinator) -> None:
    device = make_device()
    coordinator.data = {"dev-1": device}
    assert _entity(coordinator)._device() is device