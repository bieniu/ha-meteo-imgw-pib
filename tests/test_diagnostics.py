"""Tests for the diagnostics data provided by the Meteo IMGW PIB integration."""

from unittest.mock import AsyncMock

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.components.diagnostics import (
    get_diagnostics_for_config_entry,
)
from pytest_homeassistant_custom_component.typing import ClientSessionGenerator
from syrupy.assertion import SnapshotAssertion

from . import init_integration


async def test_diagnostics(
    hass: HomeAssistant,
    hass_client: ClientSessionGenerator,
    mock_config_entry: MockConfigEntry,
    mock_imgw_pib_client: AsyncMock,
    snapshot: SnapshotAssertion,
) -> None:
    """Test diagnostics."""
    await init_integration(hass, mock_config_entry)
    assert (
        await get_diagnostics_for_config_entry(hass, hass_client, mock_config_entry)
        == snapshot
    )
