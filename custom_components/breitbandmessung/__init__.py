"""Support for testing internet speed via breitbandmessung.de."""
from __future__ import annotations

import logging
from datetime import timedelta
from homeassistant.core import HomeAssistant, CoreState
from homeassistant.const import CONF_SCAN_INTERVAL, EVENT_HOMEASSISTANT_STARTED
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.exceptions import ConfigEntryNotReady
from .breitbandmessung import Breitbandmessung, BreitbandException

from .const import (
    DOMAIN,
    BREITBAND_SERVICE,
    PLATFORMS,
    DEFAULT_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up the breitbandmessung.de component."""
    coordinator = BreitbandDataCoordinator(hass, config_entry)
    await coordinator.async_setup()

    async def _enable_scheduled_breitbandmessungen(*_):
        """Activate the data update coordinator."""
        coordinator.update_interval = timedelta(
            minutes=config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        )
        await coordinator.async_refresh()

    if hass.state == CoreState.running:
        await _enable_scheduled_breitbandmessungen()
    else:
        # Running a speed test during startup can prevent
        # integrations from being able to setup because it
        # can saturate the network interface.
        hass.bus.async_listen_once(
            EVENT_HOMEASSISTANT_STARTED, _enable_scheduled_breitbandmessungen
        )

    hass.data[DOMAIN] = coordinator

    hass.config_entries.async_setup_platforms(config_entry, PLATFORMS)

    return True


class BreitbandDataCoordinator(DataUpdateCoordinator):
    """Get the latest data from breitbandmessung.de."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize the data object."""
        self.hass = hass
        self.config_entry: ConfigEntry = config_entry
        self.api: Breitbandmessung | None = None
        super().__init__(
            self.hass,
            _LOGGER,
            name=DOMAIN,
            update_method=self.async_update,
        )

    def initialize(self) -> None:
        """Initialize breitbandmessung api."""
        self.api = Breitbandmessung()

    def update_data(self):
        """Get the latest data from speedtest.net."""
        _LOGGER.debug(
            "Executing breitbandmessung speed test",
        )
        return self.api.run()

    async def async_update(self) -> dict[str, str]:
        """Update Breitband data."""
        try:
            return await self.hass.async_add_executor_job(self.update_data)
        except BreitbandException as err:
            raise UpdateFailed(err) from err

    async def async_setup(self) -> None:
        """Set up Breitband."""
        try:
            await self.hass.async_add_executor_job(self.initialize)
        except BreitbandException as err:
            raise ConfigEntryNotReady from err

        async def request_update(_):
            """Request update."""
            await self.async_request_refresh()

        self.hass.services.async_register(DOMAIN, BREITBAND_SERVICE, request_update)

        self.config_entry.async_on_unload(
            self.config_entry.add_update_listener(options_updated_listener)
        )


async def options_updated_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    hass.data[DOMAIN].update_interval = timedelta(
        minutes=entry.options[CONF_SCAN_INTERVAL]
    )
    await hass.data[DOMAIN].async_request_refresh()
