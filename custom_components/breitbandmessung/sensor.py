"""Support for breitbandmessung.de internet speed testing sensor."""
from __future__ import annotations

from typing import Any, cast

from homeassistant.components.sensor import SensorEntity
from . import BreitbandDataCoordinator
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTRIBUTION,
    DEFAULT_NAME,
    DOMAIN,
    ICON,
    SENSOR_TYPES,
    BreitbandSensorEntityDescription,
    ATTR_SERVER,
    ATTR_TEST_ID
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Breitband sensors."""
    breitband_coordinator = hass.data[DOMAIN]
    async_add_entities(
        BreitbandSensor(breitband_coordinator, description)
        for description in SENSOR_TYPES
    )


class BreitbandSensor(CoordinatorEntity, RestoreEntity, SensorEntity):
    """Implementation of a breitbandmessung.de sensor."""

    coordinator: BreitbandDataCoordinator
    entity_description: BreitbandSensorEntityDescription
    _attr_icon = ICON

    def __init__(
        self,
        coordinator: BreitbandDataCoordinator,
        description: BreitbandSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_name = f"{DEFAULT_NAME} {description.name}"
        self._attr_unique_id = description.key
        self._state: StateType = None
        self._attrs = {ATTR_ATTRIBUTION: ATTRIBUTION}
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.config_entry.entry_id)},
            name=DEFAULT_NAME,
            entry_type="service",
            configuration_url="https://breitbandmessung.de/",
        )

    @property
    def native_value(self) -> StateType:
        """Return native value for entity."""
        if self.coordinator.data:
            state = self.coordinator.data[self.entity_description.key]
            self._state = cast(StateType, self.entity_description.value(state))
        return self._state

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        if self.coordinator.data:
            self._attrs.update(
                {
                    ATTR_SERVER: self.coordinator.data["server"],
                    ATTR_TEST_ID: self.coordinator.data["test_id"],
                }
            )

        return self._attrs

    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        await super().async_added_to_hass()
        if state := await self.async_get_last_state():
            self._state = state.state
