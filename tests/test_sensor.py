"""Test sensor of Meteo IMGW-PIB integration."""

from unittest.mock import AsyncMock, Mock

from pytest_homeassistant_custom_component.common import (
    HomeAssistant,
    er,
)
from syrupy import SnapshotAssertion


async def test_sensor(
    hass: HomeAssistant,
    mock_config_entry: Mock,
    mock_imgw_pib_client: AsyncMock,
    snapshot: SnapshotAssertion,
) -> None:
    """Test sensor."""
    entity_registry = er.async_get(hass)

    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

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
