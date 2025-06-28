"""Test sensor of Meteo IMGW-PIB integration."""

from unittest.mock import AsyncMock

import pytest
from pytest_homeassistant_custom_component.common import (
    HomeAssistant,
    MockConfigEntry,
    er,
)
from syrupy import SnapshotAssertion

from custom_components.meteo_imgw_pib.sensor import _get_wind_direction

from . import init_integration


async def test_sensor(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_imgw_pib_client: AsyncMock,
    snapshot: SnapshotAssertion,
) -> None:
    """Test sensor."""
    entity_registry = er.async_get(hass)

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

        state = hass.states.get(entity_entry.entity_id)._as_dict
        for item in ("context", "last_changed", "last_reported", "last_updated"):
            state.pop(item)
        assert state == snapshot(name=f"{entity_entry.entity_id}-state")


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
