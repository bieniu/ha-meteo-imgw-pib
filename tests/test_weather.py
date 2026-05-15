"""Test weather of Meteo IMGW-PIB integration."""

import dataclasses
from unittest.mock import AsyncMock

from pytest_homeassistant_custom_component.common import (
    HomeAssistant,
    MockConfigEntry,
    er,
)
from syrupy import SnapshotAssertion

from . import init_integration
from .conftest import WEATHER_DATA


async def test_weather_not_created_without_proxy(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_imgw_pib_client: AsyncMock,
) -> None:
    """Test that no weather entity is created when proxy is not used."""
    entity_registry = er.async_get(hass)

    await init_integration(hass, mock_config_entry)

    entity_entries = er.async_entries_for_config_entry(
        entity_registry, mock_config_entry.entry_id
    )

    weather_entries = [e for e in entity_entries if e.domain == "weather"]
    assert weather_entries == []


async def test_weather(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_imgw_pib_client: AsyncMock,
    snapshot: SnapshotAssertion,
) -> None:
    """Test weather entity state when proxy data is available."""
    mock_imgw_pib_client.get_weather_data.return_value = dataclasses.replace(
        WEATHER_DATA, proxy_used=True, condition="sunny"
    )

    entity_registry = er.async_get(hass)

    await init_integration(hass, mock_config_entry)

    entity_entries = er.async_entries_for_config_entry(
        entity_registry, mock_config_entry.entry_id
    )

    weather_entries = [e for e in entity_entries if e.domain == "weather"]
    assert len(weather_entries) == 1

    for entity_entry in weather_entries:
        entity_entry_dict = entity_entry.as_partial_dict
        for item in (
            "area_id",
            "categories",
            "config_entry_id",
            "created_at",
            "device_id",
            "hidden_by",
            "id",
            "labels",
            "modified_at",
        ):
            entity_entry_dict.pop(item)
        assert entity_entry_dict == snapshot(name=f"{entity_entry.entity_id}-entry")

        state_obj = hass.states.get(entity_entry.entity_id)
        assert state_obj is not None
        state = state_obj._as_dict
        for item in ("context", "last_changed", "last_reported", "last_updated"):
            state.pop(item)
        assert state == snapshot(name=f"{entity_entry.entity_id}-state")
