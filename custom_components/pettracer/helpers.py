"""Shared pure helpers for the petTracer integration.

These functions deliberately avoid importing Home Assistant so the unit
test suite can exercise them without a full HA install.
"""

from __future__ import annotations

from pettracer.types import TrackingMode

# Raw tracking-mode values reported by the petTracer API, mapped to the
# portal's labels. ``MODE_SET`` covers every ``TrackingMode`` enum value
# (including ``SUPER_SLOW`` and the transient ``SEARCH`` mode) so all
# entities that display a mode agree with each other.
TRACKING_MODE_LABELS: dict[int, str] = {
    int(TrackingMode.FAST): "Fast",
    int(TrackingMode.NORMAL): "Normal",
    int(TrackingMode.SLOW): "Slow",
    int(TrackingMode.SUPER_SLOW): "Super slow",
    int(TrackingMode.SEARCH): "Search",
}

# Battery voltage range (millivolts) the portal uses to derive a
# percentage: 3300 mV empty -> 4200 mV full.
BATTERY_EMPTY_MV = 3300
BATTERY_FULL_MV = 4200
BATTERY_SPAN_MV = BATTERY_FULL_MV - BATTERY_EMPTY_MV


def battery_percentage(bat: int | None) -> int | None:
    """Convert raw battery voltage (mV) to a 0-100 percentage."""
    if bat is None:
        return None
    percent = (bat - BATTERY_EMPTY_MV) * 100 // BATTERY_SPAN_MV
    return min(100, max(0, percent))


def tracking_mode_label(mode_set: int | None) -> str | None:
    """Return the portal label for a raw tracking-mode value."""
    if mode_set is None:
        return None
    return TRACKING_MODE_LABELS.get(mode_set, "Unknown")


def charging_label(chg: int | None) -> str | None:
    """Return the charging status label for the raw charger flag."""
    if chg is None:
        return None
    return "Charging" if chg == 1 else "Not charging"


def is_searching(mode: TrackingMode | None) -> bool:
    """Return True while the collar is in its transient search mode."""
    return mode is not None and mode == TrackingMode.SEARCH


def device_display_name(device, device_id: str) -> str:
    """Return the device's registered name, falling back to its id."""
    if device is not None and device.details is not None and device.details.name:
        return device.details.name
    return f"Pet Tracker {device_id}"