"""Tests for the config flow validation logic."""

from __future__ import annotations

import aiohttp
import pytest
from pettracer import PetTracerError

from custom_components.pettracer import config_flow
from custom_components.pettracer.config_flow import (
    CannotConnect,
    InvalidAuth,
    validate_input,
)

from tests.conftest import make_device


class FakeAuthClient:
    """PetTracerClient stand-in that never touches the network."""

    def __init__(self, devices=None, error: Exception | None = None) -> None:
        self.devices = devices
        self.error = error

    async def login(self, username: str, password: str, timeout: int = 30) -> None:
        if self.error is not None:
            raise self.error

    async def get_all_devices(self):
        if self.error is not None:
            raise self.error
        return self.devices


def _patch_client(monkeypatch, devices=None, error: Exception | None = None) -> None:
    monkeypatch.setattr(
        config_flow, "PetTracerClient", lambda session: FakeAuthClient(devices, error)
    )


async def test_validate_input_success(monkeypatch) -> None:
    _patch_client(monkeypatch, devices=[make_device(id="dev-1")])
    info = await validate_input(None, {"username": "pet@example.com", "password": "pw"})
    assert info == {"title": "pet@example.com"}


async def test_validate_input_raises_invalid_auth_on_api_error(monkeypatch) -> None:
    _patch_client(monkeypatch, error=PetTracerError("auth refused"))
    with pytest.raises(InvalidAuth):
        await validate_input(None, {"username": "u", "password": "p"})


async def test_validate_input_raises_cannot_connect_on_http_error(monkeypatch) -> None:
    _patch_client(monkeypatch, error=aiohttp.ClientError("timeout"))
    with pytest.raises(CannotConnect):
        await validate_input(None, {"username": "u", "password": "p"})


async def test_validate_input_raises_cannot_connect_on_unknown_error(
    monkeypatch,
) -> None:
    _patch_client(monkeypatch, error=RuntimeError("boom"))
    with pytest.raises(CannotConnect):
        await validate_input(None, {"username": "u", "password": "p"})


async def test_validate_input_rejects_empty_account(monkeypatch) -> None:
    _patch_client(monkeypatch, devices=[])
    with pytest.raises(CannotConnect):
        await validate_input(None, {"username": "u", "password": "p"})


async def test_validate_input_rejects_devices_without_ids(monkeypatch) -> None:
    _patch_client(monkeypatch, devices=[make_device(id=None)])
    with pytest.raises(CannotConnect):
        await validate_input(None, {"username": "u", "password": "p"})