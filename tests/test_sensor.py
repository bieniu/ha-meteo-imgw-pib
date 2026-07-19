"""Test sensor of Meteo IMGW-PIB integration."""

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.const import Platform
from pytest_homeassistant_custom_component.common import (
    HomeAssistant,
    MockConfigEntry,
    er,
)
from syrupy import SnapshotAssertion

from custom_components.meteo_imgw_pib.sensor import _get_wind_direction

from . import init_integration
from .conftest import WEATHER_DATA_NO_DATA


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_sensor(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_imgw_pib_client: AsyncMock,
    snapshot: SnapshotAssertion,
) -> None:
    """Test sensor."""
    entity_registry = er.async_get(hass)

    with patch("custom_components.meteo_imgw_pib.PLATFORMS", [Platform.SENSOR]):
        await init_integration(hass, mock_config_entry)

    entity_entries = er.async_entries_for_config_entry(
        entity_registry, mock_config_entry.entry_id
    )

    for entity_entry in entity_entries:
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


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_sensor_no_data(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_imgw_pib_client: AsyncMock,
) -> None:
    """Test sensor with no data (all SensorData values None)."""
    mock_imgw_pib_client.get_weather_data.return_value = WEATHER_DATA_NO_DATA
    entity_registry = er.async_get(hass)

    with patch("custom_components.meteo_imgw_pib.PLATFORMS", [Platform.SENSOR]):
        await init_integration(hass, mock_config_entry)

    entity_entries = er.async_entries_for_config_entry(
        entity_registry, mock_config_entry.entry_id
    )

    expected_entities = {
        "sensor.warszawa_weather_alert",
        "sensor.warszawa_temperature",
        "sensor.warszawa_humidity",
        "sensor.warszawa_pressure",
        "sensor.warszawa_wind_speed",
        "sensor.warszawa_wind_direction",
        "sensor.warszawa_precipitation_intensity",
        "sensor.warszawa_apparent_temperature",
        "sensor.warszawa_rainfall_intensity",
        "sensor.warszawa_snowfall_intensity",
    }
    registered_entities = {e.entity_id for e in entity_entries}
    assert registered_entities == expected_entities

    for entity_entry in entity_entries:
        state = hass.states.get(entity_entry.entity_id)
        assert state is not None
        if entity_entry.entity_id == "sensor.warszawa_weather_alert":
            assert state.state == "no_alert"
        else:
            assert state.state == "unknown"


@pytest.mark.parametrize(
    ("degree", "result"),
    [
        (0, "n"),
        (30, "nne"),
        (45, "ne"),
        (70, "ene"),
        (90, "e"),
        (110, "ese"),
        (135, "se"),
        (160, "sse"),
        (180, "s"),
        (210, "ssw"),
        (225, "sw"),
        (250, "wsw"),
        (270, "w"),
        (300, "wnw"),
        (315, "nw"),
        (330, "nnw"),
        (360, "n"),
    ],
)
def test_get_wind_direction(degree: float, result: str) -> None:
    """Test _get_wind_direction function."""
    assert _get_wind_direction(degree) == result
