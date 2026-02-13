"""Sensor platform for Parmair integration."""

from __future__ import annotations

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONCENTRATION_PARTS_PER_MILLION,
    PERCENTAGE,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONTROL_STATE_MAP_V1,
    CONTROL_STATE_MAP_V2,
    DOMAIN,
    FILTER_STATE_MAP_V1,
    FILTER_STATE_MAP_V2,
    HEATER_TYPE_ELECTRIC_V1,
    HEATER_TYPE_ELECTRIC_V2,
    HEATER_TYPE_NONE_V1,
    HEATER_TYPE_NONE_V2,
    HEATER_TYPE_WATER_V1,
    HEATER_TYPE_WATER_V2,
    POWER_STATE_MAP_V1,
    POWER_STATE_MAP_V2,
    SOFTWARE_VERSION_2,
)
from .coordinator import ParmairCoordinator

_LOGGER = logging.getLogger(__name__)


def _filter_state_map(coordinator: ParmairCoordinator) -> dict[int, str]:
    """Return filter state mapping based on device firmware version.
    Prefers device-reported software_version over config entry."""
    sw = coordinator.data.get("software_version")
    if sw is not None:
        if sw >= 2.0 if isinstance(sw, int | float) else str(sw).startswith("2."):
            return FILTER_STATE_MAP_V2
        return FILTER_STATE_MAP_V1
    # Fallback to config entry when device data not yet available
    cfg = coordinator.software_version
    if cfg == SOFTWARE_VERSION_2 or str(cfg).startswith("2."):
        return FILTER_STATE_MAP_V2
    return FILTER_STATE_MAP_V1


def _power_state_map(coordinator: ParmairCoordinator) -> dict[int, str]:
    """Return power state mapping based on device firmware version.
    V1: Off, Shutting Down, Starting, Running. V2: Off, On."""
    sw = coordinator.data.get("software_version")
    if sw is not None:
        if sw >= 2.0 if isinstance(sw, int | float) else str(sw).startswith("2."):
            return POWER_STATE_MAP_V2
        return POWER_STATE_MAP_V1
    cfg = coordinator.software_version
    if cfg == SOFTWARE_VERSION_2 or str(cfg).startswith("2."):
        return POWER_STATE_MAP_V2
    return POWER_STATE_MAP_V1


def _control_state_map(coordinator: ParmairCoordinator) -> dict[int, str]:
    """Return control state mapping based on device firmware version.
    V1: Stop, Away, Home, Boost, Overpressure, timers, Manual. V2: Off, Away, Home, Boost, Sauna, Fireplace."""
    sw = coordinator.data.get("software_version")
    if sw is not None:
        if sw >= 2.0 if isinstance(sw, int | float) else str(sw).startswith("2."):
            return CONTROL_STATE_MAP_V2
        return CONTROL_STATE_MAP_V1
    cfg = coordinator.software_version
    if cfg == SOFTWARE_VERSION_2 or str(cfg).startswith("2."):
        return CONTROL_STATE_MAP_V2
    return CONTROL_STATE_MAP_V1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Parmair sensor platform."""
    coordinator: ParmairCoordinator = hass.data[DOMAIN][entry.entry_id]

    _LOGGER.debug(
        "Setting up Parmair sensors. Available data keys: %s",
        list(coordinator.data.keys()) if coordinator.data else "None",
    )

    entities = [
        # System information
        ParmairSoftwareVersionSensor(coordinator, entry, "software_version", "Software Version"),
        ParmairHeaterTypeSensor(coordinator, entry, "heater_type", "Heater Type"),
        # Temperature sensors
        ParmairTemperatureSensor(coordinator, entry, "fresh_air_temp", "Fresh Air Temperature"),
        ParmairTemperatureSensor(
            coordinator,
            entry,
            "supply_after_recovery_temp",
            "Supply Air Temperature (After Recovery)",
        ),
        ParmairTemperatureSensor(coordinator, entry, "supply_temp", "Supply Air Temperature"),
        ParmairTemperatureSensor(coordinator, entry, "exhaust_temp", "Exhaust Air Temperature"),
        ParmairTemperatureSensor(coordinator, entry, "waste_temp", "Waste Air Temperature"),
        ParmairTemperatureSensor(
            coordinator, entry, "exhaust_temp_setpoint", "Exhaust Temperature Setpoint"
        ),
        ParmairTemperatureSensor(
            coordinator, entry, "supply_temp_setpoint", "Supply Temperature Setpoint"
        ),
        # Other sensors
        ParmairControlStateSensor(coordinator, entry, "control_state", "Control State"),
        ParmairSpeedControlSensor(coordinator, entry, "actual_speed", "Current Speed"),
        ParmairPowerStateSensor(coordinator, entry, "power", "Power State"),
        ParmairBinarySensor(
            coordinator, entry, "home_state", "Home/Away State", {0: "Away", 1: "Home"}
        ),
        ParmairBinarySensor(coordinator, entry, "boost_state", "Boost State", {0: "Off", 1: "On"}),
        ParmairAlarmSensor(coordinator, entry, "alarm_count", "Alarm Count"),
        ParmairAlarmSensor(coordinator, entry, "sum_alarm", "Summary Alarm"),
        # State sensors
        ParmairBinarySensor(
            coordinator, entry, "defrost_state", "Defrost State", {0: "Off", 1: "Active"}
        ),
        ParmairBinarySensor(
            coordinator,
            entry,
            "filter_state",
            "Filter Status",
            _filter_state_map(coordinator),
        ),
        # Performance sensors
        ParmairPercentageSensor(
            coordinator, entry, "heat_recovery_efficiency", "Heat Recovery Efficiency"
        ),
        ParmairPercentageSensor(
            coordinator, entry, "lto_heat_recovery_control", "LTO Heat Recovery Control"
        ),
        ParmairPercentageSensor(coordinator, entry, "supply_fan_speed", "Supply Fan Speed"),
        ParmairPercentageSensor(coordinator, entry, "exhaust_fan_speed", "Exhaust Fan Speed"),
        ParmairPercentageSensor(coordinator, entry, "pre_heater_output", "Pre-heater Output"),
        ParmairPercentageSensor(coordinator, entry, "post_heater_output", "Post-heater Output"),
        # Optional sensors (will show unavailable if hardware not present)
        ParmairHumiditySensor(coordinator, entry, "humidity", "Humidity"),
        ParmairHumidity24hAvgSensor(coordinator, entry, "humidity_24h_avg", "Humidity 24h Average"),
        # Filter change date sensor
        ParmairFilterChangeDateSensor(coordinator, entry),
    ]

    # Add exhaust CO2 sensor only for MAC 2 devices (v2.xx firmware)
    # QE05_M = Combination sensor in exhaust duct (CO2 + humidity)
    # Only in newest MAC 2 devices
    try:
        coordinator.get_register_definition("co2_exhaust")
        entities.append(ParmairCO2Sensor(coordinator, entry, "co2_exhaust", "CO2 Exhaust Air"))
    except (KeyError, ValueError):
        # Register doesn't exist in v1.xx firmware - skip this sensor
        pass

    async_add_entities(entities)


class ParmairRegisterEntity(CoordinatorEntity[ParmairCoordinator]):
    """Base entity that exposes register metadata."""

    def __init__(
        self,
        coordinator: ParmairCoordinator,
        entry: ConfigEntry,
        data_key: str,
        name: str,
    ) -> None:
        super().__init__(coordinator)
        self._data_key = data_key
        self._register = coordinator.get_register_definition(data_key)
        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_{data_key}"
        self._attr_has_entity_name = True
        self._attr_device_info = coordinator.device_info

    @property
    def extra_state_attributes(self) -> dict[str, object]:
        """Expose register metadata for diagnostics."""

        return {
            "parmair_register": self._register.label,
            "parmair_register_id": self._register.register_id,
            "parmair_register_address": self._register.address,
            "parmair_register_scale": self._register.scale,
            "parmair_register_writable": self._register.writable,
        }


class ParmairTemperatureSensor(ParmairRegisterEntity, SensorEntity):
    """Representation of a Parmair temperature sensor."""

    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(
        self,
        coordinator: ParmairCoordinator,
        entry: ConfigEntry,
        data_key: str,
        name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, data_key, name)

    @property
    def native_value(self) -> float | None:
        """Return the sensor value."""
        return self.coordinator.data.get(self._data_key)


class ParmairHumiditySensor(ParmairRegisterEntity, SensorEntity):
    """Representation of a Parmair humidity sensor."""

    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.HUMIDITY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(
        self,
        coordinator: ParmairCoordinator,
        entry: ConfigEntry,
        data_key: str,
        name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, data_key, name)

    @property
    def native_value(self) -> int | None:
        """Return the sensor value."""
        return self.coordinator.data.get(self._data_key)


class ParmairHumidity24hAvgSensor(ParmairRegisterEntity, SensorEntity):
    """Representation of a Parmair 24-hour humidity average sensor."""

    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.HUMIDITY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(
        self,
        coordinator: ParmairCoordinator,
        entry: ConfigEntry,
        data_key: str,
        name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, data_key, name)

    @property
    def native_value(self) -> float | None:
        """Return the sensor value."""
        return self.coordinator.data.get(self._data_key)


class ParmairCO2Sensor(ParmairRegisterEntity, SensorEntity):
    """Representation of a Parmair CO2 sensor."""

    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.CO2
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = CONCENTRATION_PARTS_PER_MILLION

    def __init__(
        self,
        coordinator: ParmairCoordinator,
        entry: ConfigEntry,
        data_key: str,
        name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, data_key, name)

    @property
    def native_value(self) -> int | None:
        """Return the sensor value."""
        return self.coordinator.data.get(self._data_key)


class ParmairStateSensor(ParmairRegisterEntity, SensorEntity):
    """Representation of a Parmair state sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ParmairCoordinator,
        entry: ConfigEntry,
        data_key: str,
        name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, data_key, name)

    @property
    def native_value(self) -> int | None:
        """Return the sensor value."""
        return self.coordinator.data.get(self._data_key)


class ParmairAlarmSensor(ParmairRegisterEntity, SensorEntity):
    """Representation of a Parmair alarm sensor."""

    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.ENUM

    def __init__(
        self,
        coordinator: ParmairCoordinator,
        entry: ConfigEntry,
        data_key: str,
        name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, data_key, name)

    @property
    def native_value(self) -> int | None:
        """Return the sensor value."""
        return self.coordinator.data.get(self._data_key)


class ParmairPercentageSensor(ParmairRegisterEntity, SensorEntity):
    """Representation of a Parmair percentage sensor."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_icon = "mdi:gauge"

    def __init__(
        self,
        coordinator: ParmairCoordinator,
        entry: ConfigEntry,
        data_key: str,
        name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, data_key, name)

    @property
    def native_value(self) -> float | None:
        """Return the sensor value."""
        return self.coordinator.data.get(self._data_key)


class ParmairSoftwareVersionSensor(ParmairRegisterEntity, SensorEntity):
    """Representation of a Parmair software version sensor."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:information-outline"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self,
        coordinator: ParmairCoordinator,
        entry: ConfigEntry,
        data_key: str,
        name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, data_key, name)

    @property
    def native_value(self) -> float | None:
        """Return the sensor value."""
        return self.coordinator.data.get(self._data_key)


class ParmairControlStateSensor(ParmairRegisterEntity, SensorEntity):
    """Representation of control state with mapped values.

    V1.x (IV01_CONTROLSTATE_FO): Stop, Away, Home, Boost, Overpressure, timers, Manual.
    V2.x (USERSTATECONTROL_FO): Off, Away, Home, Boost, Sauna, Fireplace.
    """

    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.ENUM

    def __init__(
        self,
        coordinator: ParmairCoordinator,
        entry: ConfigEntry,
        data_key: str,
        name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, data_key, name)
        state_map = _control_state_map(coordinator)
        self._attr_options = list(state_map.values())

    @property
    def native_value(self) -> str | None:
        """Return the sensor value using correct mapping for firmware version."""
        raw_value = self.coordinator.data.get(self._data_key)
        if raw_value is None:
            return None
        state_map = _control_state_map(self.coordinator)
        return state_map.get(int(raw_value), f"Unknown ({raw_value})")


class ParmairSpeedControlSensor(ParmairRegisterEntity, SensorEntity):
    """Representation of actual running speed as numeric value."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:fan"

    def __init__(
        self,
        coordinator: ParmairCoordinator,
        entry: ConfigEntry,
        data_key: str,
        name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, data_key, name)

    @property
    def native_value(self) -> int | None:
        """Return the numeric speed value (0-5)."""
        raw_value = self.coordinator.data.get(self._data_key)
        if raw_value is None:
            return None
        return int(raw_value)

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """Return additional attributes."""
        return {"description": "0=Stop, 1=Speed 1, 2=Speed 2, 3=Speed 3, 4=Speed 4, 5=Speed 5"}


class ParmairPowerStateSensor(ParmairRegisterEntity, SensorEntity):
    """Representation of power state with mapped values.

    V1.x (POWER_BTN_FI): 0=Off, 1=Shutting Down, 2=Starting, 3=Running.
    V2.x (UNIT_CONTROL_FO): 0=Off, 1=On.
    """

    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.ENUM

    def __init__(
        self,
        coordinator: ParmairCoordinator,
        entry: ConfigEntry,
        data_key: str,
        name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, data_key, name)
        state_map = _power_state_map(coordinator)
        self._attr_options = list(state_map.values())

    @property
    def native_value(self) -> str | None:
        """Return the sensor value using correct mapping for firmware version."""
        raw_value = self.coordinator.data.get(self._data_key)
        if raw_value is None:
            return None
        state_map = _power_state_map(self.coordinator)
        return state_map.get(int(raw_value), f"Unknown ({raw_value})")


class ParmairHeaterTypeSensor(ParmairRegisterEntity, SensorEntity):
    """Representation of heater type with mapped values.

    NOTE: Heater type values are REVERSED between firmware versions!
    v1.xx: 0=Water, 1=Electric, 2=None
    v2.xx: 0=Electric, 1=Water, 2=None
    """

    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = ["Water", "Electric", "None"]
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    # v1.xx mapping (register 1240)
    STATE_MAP_V1 = {
        HEATER_TYPE_WATER_V1: "Water",
        HEATER_TYPE_ELECTRIC_V1: "Electric",
        HEATER_TYPE_NONE_V1: "None",
    }

    # v2.xx mapping (register 1127)
    STATE_MAP_V2 = {
        HEATER_TYPE_ELECTRIC_V2: "Electric",
        HEATER_TYPE_WATER_V2: "Water",
        HEATER_TYPE_NONE_V2: "None",
    }

    def __init__(
        self,
        coordinator: ParmairCoordinator,
        entry: ConfigEntry,
        data_key: str,
        name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, data_key, name)

    @property
    def native_value(self) -> str | None:
        """Return the sensor value using correct mapping for firmware version."""
        raw_value = self.coordinator.data.get(self._data_key)
        if raw_value is None:
            return None

        # Determine firmware version from software_version sensor
        software_version = self.coordinator.data.get("software_version")
        if software_version and software_version >= 2.0:
            # v2.xx firmware uses reversed mapping
            return self.STATE_MAP_V2.get(raw_value, f"Unknown ({raw_value})")
        else:
            # v1.xx firmware uses original mapping
            return self.STATE_MAP_V1.get(raw_value, f"Unknown ({raw_value})")


class ParmairBinarySensor(ParmairRegisterEntity, SensorEntity):
    """Representation of a binary state sensor with custom mapping."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ParmairCoordinator,
        entry: ConfigEntry,
        data_key: str,
        name: str,
        state_map: dict[int, str],
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, data_key, name)
        self._state_map = state_map
        self._attr_device_class = SensorDeviceClass.ENUM
        # Include "Unknown" so Home Assistant accepts unmapped values (e.g. v2 USERSTATECONTROL 2-5)
        self._attr_options = list(state_map.values()) + ["Unknown"]

    @property
    def native_value(self) -> str | None:
        """Return the sensor value."""
        raw_value = self.coordinator.data.get(self._data_key)
        if raw_value is None:
            return None
        mapped = self._state_map.get(raw_value)
        return mapped if mapped is not None else "Unknown"

    @property
    def extra_state_attributes(self) -> dict[str, object]:
        """Expose register metadata and raw value for diagnostics."""
        attrs = super().extra_state_attributes
        raw_value = self.coordinator.data.get(self._data_key)
        if raw_value is not None and raw_value not in self._state_map:
            attrs["raw_value"] = raw_value
        return attrs


class ParmairFilterChangeDateSensor(CoordinatorEntity[ParmairCoordinator], SensorEntity):
    """Sensor showing when air filter was last changed."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:air-filter"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self,
        coordinator: ParmairCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Filter Last Changed"
        self._attr_unique_id = f"{entry.entry_id}_filter_last_changed"
        self._attr_device_info = coordinator.device_info

    @property
    def native_value(self) -> str | None:
        """Return the filter last change date as YYYY-MM-DD."""
        day = self.coordinator.data.get("filter_day")
        month = self.coordinator.data.get("filter_month")
        year = self.coordinator.data.get("filter_year")

        if day is None or month is None or year is None:
            return None

        # Validate date values
        try:
            if not (1 <= day <= 31 and 1 <= month <= 12 and 2000 <= year <= 3000):
                return None
            return f"{year:04d}-{month:02d}-{day:02d}"
        except (ValueError, TypeError):
            return None

    @property
    def extra_state_attributes(self) -> dict[str, any]:
        """Return additional attributes."""
        next_day = self.coordinator.data.get("filter_next_day")
        next_month = self.coordinator.data.get("filter_next_month")
        next_year = self.coordinator.data.get("filter_next_year")

        attrs = {}

        if next_day is not None and next_month is not None and next_year is not None:
            try:
                if 1 <= next_day <= 31 and 1 <= next_month <= 12 and 2000 <= next_year <= 3000:
                    attrs["next_change_date"] = f"{next_year:04d}-{next_month:02d}-{next_day:02d}"
            except (ValueError, TypeError):
                pass

        return attrs
