"""Sensor platform for Parmair integration."""

from __future__ import annotations

import logging
from typing import Any

import homeassistant.util.dt as dt_util
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONCENTRATION_PARTS_PER_MILLION,
    PERCENTAGE,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_CUSTOM_FAN_RATING,
    CONF_CUSTOM_HEATER_RATING,
    CONTROL_STATE_MAP_V1,
    CONTROL_STATE_MAP_V2,
    DEFAULT_MODEL_SPECS,
    DOMAIN,
    FAN_POWER_AFFINITY_EXPONENT,
    FILTER_STATE_MAP_V1,
    FILTER_STATE_MAP_V2,
    HEATER_TYPE_MAP_V1,
    HEATER_TYPE_MAP_V2,
    HEATER_TYPE_UNKNOWN,
    PARMAIR_MODEL_SPECS,
    POWER_STATE_MAP_V1,
    POWER_STATE_MAP_V2,
    REG_EXHAUST_FAN_SPEED,
    REG_FRESH_AIR_TEMP,
    REG_HARDWARE_TYPE,
    REG_POST_HEATER_OUTPUT,
    REG_SUPPLY_AFTER_RECOVERY_TEMP,
    REG_SUPPLY_FAN_SPEED,
    SOFTWARE_VERSION_2,
    derive_operational_mode,
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
        ParmairModelSensor(coordinator, entry),
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
            coordinator,
            entry,
            "exhaust_temp_setpoint",
            "Exhaust Temperature Setpoint",
            EntityCategory.DIAGNOSTIC,
        ),
        ParmairTemperatureSensor(
            coordinator,
            entry,
            "supply_temp_setpoint",
            "Supply Temperature Setpoint",
            EntityCategory.DIAGNOSTIC,
        ),
        # Other sensors
        ParmairControlStateSensor(coordinator, entry, "control_state", "Control State"),
        ParmairSpeedControlSensor(coordinator, entry, "actual_speed", "Current Speed"),
        ParmairPowerStateSensor(coordinator, entry, "power", "Power State"),
        ParmairAlarmSensor(coordinator, entry, "alarm_count", "Alarm Count"),
        ParmairAlarmSensor(coordinator, entry, "sum_alarm", "Summary Alarm"),
        # State sensors
        ParmairBinarySensor(
            coordinator,
            entry,
            "defrost_state",
            "Defrost State",
            {0: "Off", 1: "Active"},
            EntityCategory.DIAGNOSTIC,
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
            coordinator,
            entry,
            "heat_recovery_efficiency",
            "Heat Recovery Efficiency",
            entity_category=None,
        ),
        ParmairPercentageSensor(
            coordinator, entry, "lto_heat_recovery_control", "LTO Heat Recovery Control"
        ),
        ParmairPercentageSensor(
            coordinator, entry, "supply_fan_speed", "Supply Fan Speed", entity_category=None
        ),
        ParmairPercentageSensor(
            coordinator, entry, "exhaust_fan_speed", "Exhaust Fan Speed", entity_category=None
        ),
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

    # Operational Mode sensor: v2.xx only (requires auto-feature & CO2 threshold registers)
    is_v2 = coordinator.software_version == SOFTWARE_VERSION_2 or str(
        coordinator.software_version
    ).startswith("2.")
    if is_v2:
        entities.append(ParmairOperationalStatusSensor(coordinator, entry))
    else:
        # v1-only: dedicated binary state registers (HOME_STATE_FI, BOOST_STATE_FI)
        # In v2 these don't exist — USERSTATECONTROL_FO already covers all states via control_state
        entities.extend(
            [
                ParmairBinarySensor(
                    coordinator,
                    entry,
                    "home_state",
                    "Home/Away State",
                    {0: "Away", 1: "Home"},
                    EntityCategory.DIAGNOSTIC,
                ),
                ParmairBinarySensor(
                    coordinator,
                    entry,
                    "boost_state",
                    "Boost State",
                    {0: "Off", 1: "On"},
                    EntityCategory.DIAGNOSTIC,
                ),
            ]
        )

    # Heat pump module: only add entities when module is installed (hp_rad_enable == 1)
    if coordinator.data.get("hp_rad_enable") == 1:
        entities.append(
            ParmairBinarySensor(
                coordinator,
                entry,
                "hp_rad_output",
                "Heat Pump Output",
                {0: "Inactive", 1: "Active"},
                EntityCategory.DIAGNOSTIC,
            )
        )

    # Power & Energy Estimation sensors
    entities.extend(
        [
            ParmairFanPowerSensor(coordinator, entry),
            ParmairHeaterPowerSensor(coordinator, entry),
            ParmairTotalPowerSensor(coordinator, entry),
            ParmairTotalEnergySensor(coordinator, entry),
            ParmairHeatRecoveryPowerSensor(coordinator, entry),
        ]
    )

    async_add_entities(entities)


class ParmairRegisterEntity(CoordinatorEntity[ParmairCoordinator]):
    """Base entity that exposes register metadata."""

    def __init__(
        self,
        coordinator: ParmairCoordinator,
        entry: ConfigEntry,
        data_key: str,
        name: str | None = None,
    ) -> None:
        super().__init__(coordinator)
        self._data_key = data_key
        self._register = coordinator.get_register_definition(data_key)
        self._attr_translation_key = data_key
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
        entity_category: EntityCategory | None = None,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, data_key, name)
        if entity_category is not None:
            self._attr_entity_category = entity_category

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
        entity_category: EntityCategory | None = EntityCategory.DIAGNOSTIC,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, data_key, name)
        if entity_category is not None:
            self._attr_entity_category = entity_category

    @property
    def native_value(self) -> float | None:
        """Return the sensor value."""
        return self.coordinator.data.get(self._data_key)


class ParmairModelSensor(CoordinatorEntity[ParmairCoordinator], SensorEntity):
    """Representation of a Parmair hardware model sensor."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:information-outline"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_translation_key = "model"

    def __init__(self, coordinator: ParmairCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_model"
        self._attr_device_info = coordinator.device_info

    @property
    def native_value(self) -> str | None:
        """Return the device model."""
        return self.coordinator.device_info.get("model")


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
        return state_map.get(int(raw_value))


class ParmairSpeedControlSensor(ParmairRegisterEntity, SensorEntity):
    """Representation of actual running speed as numeric value."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:fan"
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
        state_map = _power_state_map(coordinator)
        self._attr_options = list(state_map.values())

    @property
    def native_value(self) -> str | None:
        """Return the sensor value using correct mapping for firmware version."""
        raw_value = self.coordinator.data.get(self._data_key)
        if raw_value is None:
            return None
        state_map = _power_state_map(self.coordinator)
        return state_map.get(int(raw_value))


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
    STATE_MAP_V1 = HEATER_TYPE_MAP_V1

    # v2.xx mapping (register 1127)
    STATE_MAP_V2 = HEATER_TYPE_MAP_V2

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
            raw_value = self.coordinator.heater_type
        if raw_value is None or raw_value == HEATER_TYPE_UNKNOWN:
            return None

        # Determine firmware version from software_version sensor
        software_version = self.coordinator.data.get("software_version")
        if software_version and software_version >= 2.0:
            # v2.xx firmware uses reversed mapping
            return self.STATE_MAP_V2.get(raw_value)
        else:
            # v1.xx firmware uses original mapping
            return self.STATE_MAP_V1.get(raw_value)


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
        entity_category: EntityCategory | None = None,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, data_key, name)
        self._state_map = state_map
        self._attr_device_class = SensorDeviceClass.ENUM
        # Include "Unknown" so Home Assistant accepts unmapped values (e.g. v2 USERSTATECONTROL 2-5)
        self._attr_options = list(state_map.values()) + ["Unknown"]
        if entity_category is not None:
            self._attr_entity_category = entity_category

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
        self._attr_translation_key = "filter_last_changed"
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
    def extra_state_attributes(self) -> dict[str, Any]:
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


class ParmairOperationalStatusSensor(CoordinatorEntity[ParmairCoordinator], SensorEntity):
    """Derived operational state combining control state and active automations.

    Hierarchical derivation:
    1. Off state (power == 0 or control_state == 0)
    2. Away state (control_state == 1)
    3. Home state (control_state == 2):
       - Automated CO2 boost (auto_co2_boost enabled + CO2 ≥ threshold)
       - Automated humidity boost (auto_humidity_boost enabled + elevated RH)
       - Summer cooling (summer_mode enabled + summer season active)
       - Normal Home operation
    4. Boost state (control_state == 3):
       - Distinguishes manual boost vs CO2 boost vs humidity boost
    5. Sauna state (control_state == 4)
    6. Fireplace state (control_state == 5)

    v2.x only — not added to the entity registry for v1.x devices.
    """

    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_icon = "mdi:fan-auto"
    _attr_translation_key = "operational_mode"
    _attr_options = [
        "off",
        "away",
        "home",
        "summer",
        "boost",
        "co2_boost",
        "humidity_boost",
        "sauna",
        "fireplace",
    ]

    def __init__(
        self,
        coordinator: ParmairCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_operational_mode"
        self._attr_device_info = coordinator.device_info

    @property
    def native_value(self) -> str | None:
        """Derive the effective operational mode from available register data."""
        return derive_operational_mode(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, object]:
        """Expose active automation states and live sensor values for context."""
        data = self.coordinator.data
        if not data:
            return {}

        attrs: dict[str, object] = {}

        # Automation enable states
        for key, label in (
            ("auto_co2_boost", "auto_co2_boost_enabled"),
            ("auto_humidity_boost", "auto_humidity_boost_enabled"),
            ("auto_co2_home_away", "auto_co2_home_away_enabled"),
            ("auto_cold_lowspeed", "auto_cold_lowspeed_enabled"),
        ):
            val = data.get(key)
            if val is not None:
                attrs[label] = bool(val)

        # Summer cooling state (0=Winter, 1=Mid-season, 2=Summer)
        summer_state = data.get("summer_mode_state")
        if summer_state is not None:
            attrs["summer_mode_state"] = {0: "winter", 1: "mid_season", 2: "summer"}.get(
                summer_state, summer_state
            )

        # CO2 readings and thresholds
        co2 = data.get("co2_exhaust")
        if co2 is not None:
            attrs["co2_ppm"] = co2
        co2_home_thr = data.get("co2_home_threshold")
        if co2_home_thr is not None:
            attrs["co2_home_threshold_ppm"] = co2_home_thr
        co2_boost_thr = data.get("co2_boost_threshold")
        if co2_boost_thr is not None:
            attrs["co2_boost_threshold_ppm"] = co2_boost_thr

        # Humidity readings
        humidity = data.get("humidity")
        if humidity is not None:
            attrs["humidity_pct"] = humidity
        humidity_avg = data.get("humidity_24h_avg")
        if humidity_avg is not None:
            attrs["humidity_24h_avg_pct"] = humidity_avg

        return attrs


class _ParmairPowerSensorBase(CoordinatorEntity[ParmairCoordinator], SensorEntity):
    """Base class for power sensors calculating model-based consumption."""

    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.WATT

    def __init__(self, coordinator: ParmairCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_device_info = coordinator.device_info

    def _get_model_specs(self):
        """Retrieve model power specs, considering options overrides if configured."""
        hw_type = self.coordinator.data.get(REG_HARDWARE_TYPE)
        specs = (
            PARMAIR_MODEL_SPECS.get(int(hw_type), DEFAULT_MODEL_SPECS)
            if hw_type is not None
            else DEFAULT_MODEL_SPECS
        )

        options = self._entry.options or {}
        custom_heater = options.get(CONF_CUSTOM_HEATER_RATING)
        custom_fan = options.get(CONF_CUSTOM_FAN_RATING)

        fan_rating = float(custom_fan) if custom_fan is not None else specs.fan_power_max_w
        heater_rating = (
            float(custom_heater) if custom_heater is not None else specs.heater_power_max_w
        )

        return specs, fan_rating, heater_rating


class ParmairFanPowerSensor(_ParmairPowerSensorBase):
    """Estimates active electrical power consumed by supply and exhaust EC fans."""

    def __init__(self, coordinator: ParmairCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_translation_key = "fan_power"
        self._attr_unique_id = f"{entry.entry_id}_fan_power"

    @property
    def native_value(self) -> float | None:
        """Calculate total fan power in Watts based on fan speeds (0-100%)."""
        supply_speed = self.coordinator.data.get(REG_SUPPLY_FAN_SPEED)
        exhaust_speed = self.coordinator.data.get(REG_EXHAUST_FAN_SPEED)

        if supply_speed is None and exhaust_speed is None:
            return None

        specs, fan_rating, _ = self._get_model_specs()

        # Affinity law model: P ~ (speed_pct / 100) ^ exponent for EC motors
        power = 0.0
        if supply_speed is not None and supply_speed > 0:
            power += fan_rating * ((supply_speed / 100.0) ** FAN_POWER_AFFINITY_EXPONENT)
        if exhaust_speed is not None and exhaust_speed > 0:
            power += fan_rating * ((exhaust_speed / 100.0) ** FAN_POWER_AFFINITY_EXPONENT)

        # Scale if machine has 4 fans (e.g., MAC 220 has 2 supply + 2 exhaust)
        if specs.fan_count == 4:
            power *= 2.0

        return round(power, 1)


class ParmairHeaterPowerSensor(_ParmairPowerSensorBase):
    """Estimates active electrical power consumed by post-heater."""

    def __init__(self, coordinator: ParmairCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_translation_key = "heater_power"
        self._attr_unique_id = f"{entry.entry_id}_post_heater_power"

    @property
    def native_value(self) -> float | None:
        """Calculate electric heater power in Watts based on heating output percentage."""
        # Check heater type: only electric post-heaters draw electrical power
        if not self.coordinator.is_electric_heater:
            # Water or None draws 0 W of electrical power
            return 0.0

        heater_output = self.coordinator.data.get(REG_POST_HEATER_OUTPUT)
        if heater_output is None:
            return None

        _, _, heater_rating = self._get_model_specs()
        power = heater_rating * (heater_output / 100.0)
        return round(power, 1)


class ParmairTotalPowerSensor(_ParmairPowerSensorBase):
    """Estimates total electrical power consumed by the entire ventilation unit."""

    def __init__(self, coordinator: ParmairCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_translation_key = "total_power"
        self._attr_unique_id = f"{entry.entry_id}_total_power"

    @property
    def native_value(self) -> float | None:
        """Sum of fans, electric heater, and standby electronics."""
        # Standby electronics / control panel baseline: ~5 W
        total = 5.0

        # Fan power
        supply_speed = self.coordinator.data.get(REG_SUPPLY_FAN_SPEED)
        exhaust_speed = self.coordinator.data.get(REG_EXHAUST_FAN_SPEED)
        specs, fan_rating, heater_rating = self._get_model_specs()

        fan_power = 0.0
        if supply_speed is not None and supply_speed > 0:
            fan_power += fan_rating * ((supply_speed / 100.0) ** FAN_POWER_AFFINITY_EXPONENT)
        if exhaust_speed is not None and exhaust_speed > 0:
            fan_power += fan_rating * ((exhaust_speed / 100.0) ** FAN_POWER_AFFINITY_EXPONENT)
        if specs.fan_count == 4:
            fan_power *= 2.0

        total += fan_power

        # Electric heater power (if applicable)
        if self.coordinator.is_electric_heater:
            heater_output = self.coordinator.data.get(REG_POST_HEATER_OUTPUT)
            if heater_output is not None and heater_output > 0:
                total += heater_rating * (heater_output / 100.0)

        return round(total, 1)


class ParmairHeatRecoveryPowerSensor(_ParmairPowerSensorBase):
    """Estimates thermal heat recovery power recovered from exhaust air into supply air."""

    def __init__(self, coordinator: ParmairCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_translation_key = "heat_recovery_power"
        self._attr_unique_id = f"{entry.entry_id}_heat_recovery_power"

    @property
    def native_value(self) -> float | None:
        """Calculate thermal power recovered: P = m_dot * c_p * delta_T (Watts)."""
        supply_after_lto = self.coordinator.data.get(REG_SUPPLY_AFTER_RECOVERY_TEMP)
        fresh_air = self.coordinator.data.get(REG_FRESH_AIR_TEMP)
        supply_speed = self.coordinator.data.get(REG_SUPPLY_FAN_SPEED)

        if supply_after_lto is None or fresh_air is None:
            return None

        # Temperature delta across the heat exchanger
        delta_t = supply_after_lto - fresh_air
        if delta_t <= 0:
            return 0.0

        specs, _, _ = self._get_model_specs()

        # Airflow estimation (m³/s): (supply_speed% / 100) * max_airflow_ls / 1000
        # If supply_speed is unavailable, assume ~50% nominal speed
        speed_factor = (supply_speed / 100.0) if supply_speed is not None else 0.5
        v_dot = (speed_factor * specs.max_airflow_ls) / 1000.0  # m³/s

        # Air density rho ~ 1.204 kg/m³, specific heat capacity c_p ~ 1005 J/(kg*K)
        # P = rho * v_dot * c_p * delta_t
        rho_cp = 1.204 * 1005.0  # ~1210 J/(m³*K)
        heat_power = v_dot * rho_cp * delta_t

        return round(heat_power, 1)


class ParmairTotalEnergySensor(CoordinatorEntity[ParmairCoordinator], RestoreEntity, SensorEntity):
    """Accumulates total active energy consumption in kWh for Home Assistant Energy dashboard."""

    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR

    def __init__(self, coordinator: ParmairCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_translation_key = "total_energy"
        self._attr_unique_id = f"{entry.entry_id}_total_energy"
        self._attr_device_info = coordinator.device_info
        self._state: float = 0.0
        self._last_update_time: float | None = None

    async def async_added_to_hass(self) -> None:
        """Restore previous accumulated energy state on restart."""
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state and last_state.state not in (None, "unknown", "unavailable"):
            try:
                self._state = float(last_state.state)
            except (ValueError, TypeError):
                self._state = 0.0

    @property
    def native_value(self) -> float:
        """Return cumulative energy in kWh."""
        return round(self._state, 3)

    def _handle_coordinator_update(self) -> None:
        """Calculate and accumulate energy on each coordinator polling cycle."""
        now = dt_util.utcnow().timestamp()

        # Calculate current total power
        specs_hw = self.coordinator.data.get(REG_HARDWARE_TYPE)
        specs = (
            PARMAIR_MODEL_SPECS.get(int(specs_hw), DEFAULT_MODEL_SPECS)
            if specs_hw is not None
            else DEFAULT_MODEL_SPECS
        )

        options = self._entry.options or {}
        custom_heater = options.get(CONF_CUSTOM_HEATER_RATING)
        custom_fan = options.get(CONF_CUSTOM_FAN_RATING)

        fan_rating = float(custom_fan) if custom_fan is not None else specs.fan_power_max_w
        heater_rating = (
            float(custom_heater) if custom_heater is not None else specs.heater_power_max_w
        )

        supply_speed = self.coordinator.data.get(REG_SUPPLY_FAN_SPEED)
        exhaust_speed = self.coordinator.data.get(REG_EXHAUST_FAN_SPEED)

        power = 5.0  # Standby electronics
        if supply_speed is not None and supply_speed > 0:
            power += fan_rating * ((supply_speed / 100.0) ** FAN_POWER_AFFINITY_EXPONENT)
        if exhaust_speed is not None and exhaust_speed > 0:
            power += fan_rating * ((exhaust_speed / 100.0) ** FAN_POWER_AFFINITY_EXPONENT)
        if specs.fan_count == 4:
            power *= 2.0

        if self.coordinator.is_electric_heater:
            heater_output = self.coordinator.data.get(REG_POST_HEATER_OUTPUT)
            if heater_output is not None and heater_output > 0:
                power += heater_rating * (heater_output / 100.0)

        # Trapezoidal or left-Riemann integration: E (kWh) += P (W) * dt (s) / (3600 * 1000)
        if self._last_update_time is not None:
            time_delta = now - self._last_update_time
            # Discard unreasonable gaps (e.g., system was offline for days or clock jumped)
            if 0 < time_delta < 3600:
                energy_kwh = (power * time_delta) / 3600000.0
                self._state += energy_kwh

        self._last_update_time = now
        super()._handle_coordinator_update()
