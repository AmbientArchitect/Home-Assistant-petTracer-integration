"""Tests for the diagnostics module."""

from __future__ import annotations

import asyncio
import json

from pettracer.types import TrackingMode

from custom_components.pettracer.diagnostics import (
    _dump,
    async_get_config_entry_diagnostics,
)

from tests.conftest import make_device, make_last_pos


def test_dump_flattens_dataclasses_and_enums() -> None:
    device = make_device(
        mode=TrackingMode.SEARCH,
        lastPos=make_last_pos(posLat=54.352),
        details=None,
    )
    payload = _dump(device)
    assert payload["mode"] == 11
    assert payload["id"] == "dev-1"
    assert payload["lastPos"]["posLat"] == 54.352
    assert payload["lastPos"]["acc"] == 12
    assert payload["details"] is None


def test_dump_json_serializable() -> None:
    payload = _dump(make_device(bat=3900))
    assert json.dumps(payload)


def test_diagnostics_redacts_password(coordinator) -> None:
    entry = coordinator.entry
    entry.data = {"username": "pet@example.com", "password": "super-secret"}

    class FakeHass:
        data = {"pettracer": {"entry1": coordinator}}

    coordinator.data = {"dev-1": make_device(bat=3900)}

    result = asyncio.run(async_get_config_entry_diagnostics(FakeHass(), entry))

    assert result["entry"] == {
        "username": "pet@example.com",
        "password": "***",
    }
    assert result["devices"]["dev-1"]["bat"] == 3900
    assert result["client"]["is_authenticated"] is True
    assert json.dumps(result)