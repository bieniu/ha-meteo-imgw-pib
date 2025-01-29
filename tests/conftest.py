"""Global fixtures for Meteo IMGW-PIB integration."""

import json
from collections.abc import Generator
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from pytest_homeassistant_custom_component.common import load_fixture
from syrupy.assertion import SnapshotAssertion
from syrupy.extensions.amber import AmberSnapshotExtension
from syrupy.location import PyTestLocation

from custom_components.meteo_imgw_pib import ApiError


@pytest.fixture(name="bypass_get_data")
def bypass_get_data_fixture() -> Generator[None]:
    """Skip calls to get data from API."""
    synop = json.loads(load_fixture("synop.json"))
    station = json.loads(load_fixture("station.json"))
    with patch(
        "custom_components.meteo_imgw_pib.ImgwPib._http_request",
        side_effect=[synop, station],
    ):
        yield


@pytest.fixture(name="error_on_get_data")
def error_get_data_fixture() -> Generator[None]:
    """Simulate error when retrieving data from API."""
    with patch(
        "custom_components.meteo_imgw_pib.ImgwPib._http_request",
        side_effect=ApiError("exception"),
    ):
        yield


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
