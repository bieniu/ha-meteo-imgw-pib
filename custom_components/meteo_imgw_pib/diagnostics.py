"""Diagnostics support for Meteo IMGW-PIB."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from homeassistant.core import HomeAssistant

from .coordinator import MeteoImgwPibConfigEntry


async def async_get_config_entry_diagnostics(
    _hass: HomeAssistant, entry: MeteoImgwPibConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = entry.runtime_data.coordinator

    return {
        "config_entry_data": entry.as_dict(),
        "weather_data": asdict(coordinator.data),
    }
