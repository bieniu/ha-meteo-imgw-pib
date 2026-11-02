"""Test weather of Meteo IMGW-PIB integration."""

import dataclasses
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.components.weather import DOMAIN as WEATHER_DOMAIN
from homeassistant.components.weather import SERVICE_GET_FORECASTS
from homeassistant.const import STATE_UNAVAILABLE, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.util.dt import utcnow
from pytest_homeassistant.common import (
    MockConfigEntry,
    async_fire_time_changed,
    snapshot_platform,
)
from syrupy.assertion import SnapshotAssertion

from custom_components.meteo_imgw_pib.const import UPDATE_INTERVAL

from . import init_integration
from .conftest import WEATHER_DATA

ENTITY_ID = "weather.warszawa"


async def test_weather(
    hass: HomeAssistant,
    entity_registry: er.EntityRegistry,
    mock_config_entry: MockConfigEntry,
    mock_imgw_pib_client: AsyncMock,
    snapshot: SnapshotAssertion,
) -> None:
    """Test weather entity state when proxy data is available."""
    with patch("custom_components.meteo_imgw_pib.PLATFORMS", [Platform.WEATHER]):
        await init_integration(hass, mock_config_entry)

    await snapshot_platform(hass, entity_registry, snapshot, mock_config_entry.entry_id)


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


@pytest.mark.parametrize("forecast_type", ["twice_daily", "hourly"])
async def test_forecast_without_icon(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_imgw_pib_client: AsyncMock,
    snapshot: SnapshotAssertion,
    forecast_type: str,
) -> None:
    """Test forecast is returned when an item has no icon."""
    field = f"forecast_{forecast_type}"
    item = {k: v for k, v in getattr(WEATHER_DATA, field)[0].items() if k != "icon"}
    mock_imgw_pib_client.get_weather_data.return_value = dataclasses.replace(
        WEATHER_DATA, **{field: [item]}
    )

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
