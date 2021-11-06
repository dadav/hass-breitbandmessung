"""Constants used by Breitbandmessung."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Callable
from homeassistant.components.sensor import (
    STATE_CLASS_MEASUREMENT,
    SensorEntityDescription,
)
from homeassistant.const import DATA_RATE_MEGABITS_PER_SECOND, TIME_MILLISECONDS

DEFAULT_NAME: Final = 'Breitbandmessung'
DOMAIN: Final = 'breitbandmessung'
BREITBAND_SERVICE: Final = 'breitbandmessung'
DEFAULT_SCAN_INTERVAL: Final = 60

ICON: Final = "mdi:speedometer"

PLATFORMS: Final = ["sensor"]

ATTRIBUTION: Final = "Data retrieved from breitbandmessung.de"

ATTR_SERVER: Final = "server"
ATTR_TEST_ID: Final = "test_id"


@dataclass
class BreitbandSensorEntityDescription(SensorEntityDescription):
    """Class describing Speedtest sensor entities."""

    value: Callable = round


SENSOR_TYPES: Final[tuple[BreitbandSensorEntityDescription, ...]] = (
    BreitbandSensorEntityDescription(
        key="ping",
        name="Ping",
        native_unit_of_measurement=TIME_MILLISECONDS,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    BreitbandSensorEntityDescription(
        key="download",
        name="Download",
        native_unit_of_measurement=DATA_RATE_MEGABITS_PER_SECOND,
        state_class=STATE_CLASS_MEASUREMENT,
        value=lambda value: round(value / 10 ** 6, 2),
    ),
    BreitbandSensorEntityDescription(
        key="upload",
        name="Upload",
        native_unit_of_measurement=DATA_RATE_MEGABITS_PER_SECOND,
        state_class=STATE_CLASS_MEASUREMENT,
        value=lambda value: round(value / 10 ** 6, 2),
    ),
)
