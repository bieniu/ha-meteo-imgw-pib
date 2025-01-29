"""Global fixtures for Meteo IMGW-PIB integration."""

from collections.abc import Generator
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest
from imgw_pib.model import SensorData, WeatherData
from syrupy.assertion import SnapshotAssertion
from syrupy.extensions.amber import AmberSnapshotExtension
from syrupy.location import PyTestLocation

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
