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
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, DEFAULT_NAME
from .coordinator import ParmairCoordinator

_LOGGER = logging.getLogger(__name__)


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
        
        # Temperature sensors
        ParmairTemperatureSensor(coordinator, entry, "fresh_air_temp", "Fresh Air Temperature"),
        ParmairTemperatureSensor(coordinator, entry, "supply_after_recovery_temp", "Supply Air Temperature (After Recovery)"),
        ParmairTemperatureSensor(coordinator, entry, "supply_temp", "Supply Air Temperature"),
        ParmairTemperatureSensor(coordinator, entry, "exhaust_temp", "Exhaust Air Temperature"),
        ParmairTemperatureSensor(coordinator, entry, "waste_temp", "Waste Air Temperature"),
        ParmairTemperatureSensor(coordinator, entry, "exhaust_temp_setpoint", "Exhaust Temperature Setpoint"),
        ParmairTemperatureSensor(coordinator, entry, "supply_temp_setpoint", "Supply Temperature Setpoint"),
        
        # Other sensors
        ParmairStateSensor(coordinator, entry, "control_state", "Control State"),
        ParmairStateSensor(coordinator, entry, "power", "Power State"),
        ParmairStateSensor(coordinator, entry, "home_state", "Home/Away State"),
        ParmairStateSensor(coordinator, entry, "boost_state", "Boost State"),
        ParmairTimerSensor(coordinator, entry, "boost_timer", "Boost Timer"),
        ParmairTimerSensor(coordinator, entry, "overpressure_timer", "Overpressure Timer"),
        ParmairAlarmSensor(coordinator, entry, "alarm_count", "Alarm Count"),
        ParmairAlarmSensor(coordinator, entry, "sum_alarm", "Summary Alarm"),
        
        # State sensors
        ParmairStateSensor(coordinator, entry, "defrost_state", "Defrost State"),
        ParmairStateSensor(coordinator, entry, "filter_state", "Filter Status"),
        
        # Performance sensors
        ParmairPercentageSensor(coordinator, entry, "heat_recovery_efficiency", "Heat Recovery Efficiency"),
        ParmairPercentageSensor(coordinator, entry, "supply_fan_speed", "Supply Fan Speed"),
        ParmairPercentageSensor(coordinator, entry, "exhaust_fan_speed", "Exhaust Fan Speed"),
        
        # Optional sensors (will show unavailable if hardware not present)
        ParmairHumiditySensor(coordinator, entry, "humidity", "Humidity"),
        ParmairCO2Sensor(coordinator, entry, "co2", "CO2"),
    ]
    
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
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.data.get("name", DEFAULT_NAME),
            "manufacturer": "Parmair",
            "model": coordinator.model,
        }

    @property
    def extra_state_attributes(self) -> dict[str, object]:
        """Expose register metadata for diagnostics."""

        return {
            "parmair_model": self.coordinator.model,
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
        value = self.coordinator.data.get(self._data_key)
        # 0 or 65535 (0xFFFF) indicates sensor not installed
        if value == 0 or value == 65535:
            return None
        return value


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
        value = self.coordinator.data.get(self._data_key)
        # 0 or 65535 (0xFFFF) indicates sensor not installed
        if value == 0 or value == 65535:
            return None
        return value


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


class ParmairTimerSensor(ParmairRegisterEntity, SensorEntity):
    """Representation of a Parmair timer sensor."""

    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES

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
    _attr_entity_category = "diagnostic"

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
