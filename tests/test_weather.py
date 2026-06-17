"""Test weather of Meteo IMGW-PIB integration."""

import dataclasses
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.components.weather import DOMAIN as WEATHER_DOMAIN
from homeassistant.components.weather import SERVICE_GET_FORECASTS
from homeassistant.const import STATE_UNAVAILABLE, Platform
from homeassistant.util.dt import utcnow
from pytest_homeassistant_custom_component.common import (
    HomeAssistant,
    MockConfigEntry,
    async_fire_time_changed,
    er,
)
from syrupy import SnapshotAssertion

from custom_components.meteo_imgw_pib.const import UPDATE_INTERVAL

from . import init_integration
from .conftest import WEATHER_DATA

ENTITY_ID = "weather.warszawa"


async def test_weather(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_imgw_pib_client: AsyncMock,
    snapshot: SnapshotAssertion,
) -> None:
    """Test weather entity state when proxy data is available."""
    entity_registry = er.async_get(hass)

    with patch("custom_components.meteo_imgw_pib.PLATFORMS", [Platform.WEATHER]):
        await init_integration(hass, mock_config_entry)

    entity_entries = er.async_entries_for_config_entry(
        entity_registry, mock_config_entry.entry_id
    )

    weather_entries = [
        entry for entry in entity_entries if entry.domain == WEATHER_DOMAIN
    ]
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

        state = hass.states.get(entity_entry.entity_id)
        assert state is not None

        state_dict = state._as_dict
        for item in ("context", "last_changed", "last_reported", "last_updated"):
            state_dict.pop(item)

        assert state_dict == snapshot(name=f"{entity_entry.entity_id}-state")


async def test_weather_not_created_without_proxy(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_imgw_pib_client: AsyncMock,
) -> None:
    """Test that no weather entity is created when proxy is not used."""
    mock_imgw_pib_client.get_weather_data = AsyncMock(proxy_used=False)

    await init_integration(hass, mock_config_entry)

    state = hass.states.get(ENTITY_ID)
    assert state is not None


async def test_weather_unavailable_after_proxy_change(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_imgw_pib_client: AsyncMock,
) -> None:
    """Test that weather entity becomes unavailable when proxy_used changes to False."""
    with patch("custom_components.meteo_imgw_pib.PLATFORMS", [Platform.WEATHER]):
        await init_integration(hass, mock_config_entry)

    state = hass.states.get(ENTITY_ID)
    assert state is not None
    assert state.state != STATE_UNAVAILABLE

    mock_imgw_pib_client.get_weather_data.return_value = dataclasses.replace(
        WEATHER_DATA, proxy_used=False
    )

    async_fire_time_changed(hass, utcnow() + UPDATE_INTERVAL)
    await hass.async_block_till_done()

    state = hass.states.get(ENTITY_ID)
    assert state is not None
    assert state.state == STATE_UNAVAILABLE


@pytest.mark.parametrize(
    ("forecast_type"),
    ["twice_daily", "hourly"],
)
async def test_forecast_service(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_imgw_pib_client: AsyncMock,
    snapshot: SnapshotAssertion,
    forecast_type: str,
) -> None:
    """Test multiple forecast."""
    with patch("custom_components.meteo_imgw_pib.PLATFORMS", [Platform.WEATHER]):
        await init_integration(hass, mock_config_entry)

    response = await hass.services.async_call(
        WEATHER_DOMAIN,
        SERVICE_GET_FORECASTS,
        {
            "entity_id": ENTITY_ID,
            "type": forecast_type,
        },
        blocking=True,
        return_response=True,
    )
    assert response == snapshot
