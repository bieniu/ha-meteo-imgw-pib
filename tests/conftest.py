"""Global fixtures for Meteo IMGW-PIB integration."""

from collections.abc import Generator
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch
from zoneinfo import ZoneInfo

import pytest
from imgw_pib.model import Alert, SensorData, WeatherData
from pytest_homeassistant_custom_component.common import MockConfigEntry
from syrupy.assertion import SnapshotAssertion
from syrupy.extensions.amber import AmberSnapshotExtension
from syrupy.location import PyTestLocation

from custom_components.meteo_imgw_pib.const import CONF_STATION_ID, DOMAIN

WEATHER_DATA = WeatherData(
    temperature=SensorData(name="temperature", value=12.5),
    humidity=SensorData(name="humidity", value=88),
    pressure=SensorData(name="pressure", value=1002),
    wind_speed=SensorData(name="wind_speed", value=4),
    wind_direction=SensorData(name="wind_direction", value=12),
    precipitation=SensorData(name="precipitation", value=5),
    station="Warszawa",
    station_id="12200",
    measurement_date=None,
    weather_alert=Alert(
        value="strong_wind",
        level="yellow",
        probability=80,
        valid_from=datetime.strptime("2025-07-11 14:00", "%Y-%m-%d %H:%M").replace(
            tzinfo=ZoneInfo("Europe/Warsaw")
        ),
        valid_to=datetime.strptime("2025-07-11 22:00", "%Y-%m-%d %H:%M").replace(
            tzinfo=ZoneInfo("Europe/Warsaw")
        ),
    ),
)


@pytest.fixture
def mock_imgw_pib_client() -> Generator[AsyncMock]:
    """Mock a ImgwPib client."""
    with (
        patch("custom_components.meteo_imgw_pib.ImgwPib", autospec=True) as mock_client,
        patch(
            "custom_components.meteo_imgw_pib.config_flow.ImgwPib",
            new=mock_client,
        ),
    ):
        client = mock_client.create.return_value
        client.get_weather_data.return_value = WEATHER_DATA
        client.weather_stations = {"12200": "Warszawa"}

        yield client


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Mock a config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="Warszawa",
        unique_id="12200",
        data={
            CONF_STATION_ID: "12200",
        },
    )


@pytest.fixture
def mock_setup_entry() -> Generator[AsyncMock]:
    """Override async_setup_entry."""
    with patch(
        "custom_components.meteo_imgw_pib.async_setup_entry", return_value=True
    ) as mock_setup_entry:
        yield mock_setup_entry


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: Mock) -> None:
    """Auto enable custom integrations."""
    return


@pytest.fixture
def snapshot(snapshot: SnapshotAssertion) -> SnapshotAssertion:
    """Return snapshot assertion fixture."""
    return snapshot.use_extension(SnapshotExtension)


class SnapshotExtension(AmberSnapshotExtension):
    """Extension for Syrupy."""

    @classmethod
    def dirname(cls, *, test_location: PyTestLocation) -> str:
        """Return the directory for the snapshot files."""
        test_dir = Path(test_location.filepath).parent
        return str(test_dir.joinpath("snapshots"))
