#!/usr/bin/env python3
"""Test Parmair integration data interpretation using dump files.

This tool validates that the integration correctly interprets register values
from Parmair devices. It loads JSON dump files and tests all sensor/entity
interpretation logic without requiring Home Assistant.

Usage:
    python test_interpretation.py <dump_file>
    python test_interpretation.py --all
    python test_interpretation.py dumps/my_device.json --verbose

Examples:
    python test_interpretation.py dumps/192_168_1_100_20260110.json
    python test_interpretation.py test_fixtures/mac100_v1.json
    python test_interpretation.py --all  # Test all fixture files
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
import importlib.util

from tools.mock_coordinator import MockCoordinator, load_dump

# Import const.py directly to avoid homeassistant dependency in __init__.py
_const_path = Path(__file__).parent.parent / "custom_components" / "parmair" / "const.py"
_spec = importlib.util.spec_from_file_location("parmair_const", _const_path)
_const = importlib.util.module_from_spec(_spec)
sys.modules["parmair_const"] = _const  # Register module to fix dataclass issues
_spec.loader.exec_module(_const)

HARDWARE_TYPE_MAP_V2 = _const.HARDWARE_TYPE_MAP_V2
HEATER_TYPE_ELECTRIC = _const.HEATER_TYPE_ELECTRIC
HEATER_TYPE_NONE = _const.HEATER_TYPE_NONE
HEATER_TYPE_WATER = _const.HEATER_TYPE_WATER
MODE_AWAY = _const.MODE_AWAY
MODE_BOOST = _const.MODE_BOOST
MODE_HOME = _const.MODE_HOME
MODE_MANUAL = _const.MODE_MANUAL
MODE_OVERPRESSURE = _const.MODE_OVERPRESSURE
MODE_STOP = _const.MODE_STOP
POWER_OFF = _const.POWER_OFF
POWER_RUNNING = _const.POWER_RUNNING
POWER_SHUTTING_DOWN = _const.POWER_SHUTTING_DOWN
POWER_STARTING = _const.POWER_STARTING
SOFTWARE_VERSION_2 = _const.SOFTWARE_VERSION_2


# ============================================================================
# State Mappings (extracted from sensor.py)
# ============================================================================

# V1.x Power state (POWER_BTN_FI): 0=Off, 1=Shutting Down, 2=Starting, 3=Running
POWER_STATE_MAP_V1 = {
    POWER_OFF: "Off",
    POWER_SHUTTING_DOWN: "Shutting Down",
    POWER_STARTING: "Starting",
    POWER_RUNNING: "Running",
}

# V2.x Power state (UNIT_CONTROL_FO): 0=Off, 1=On
POWER_STATE_MAP_V2 = {
    0: "Off",
    1: "On",
}

# V1.x Control state (IV01_CONTROLSTATE_FO)
CONTROL_STATE_MAP_V1 = {
    MODE_STOP: "Stop",
    MODE_AWAY: "Away",
    MODE_HOME: "Home",
    MODE_BOOST: "Boost",
    MODE_OVERPRESSURE: "Overpressure",
    5: "Away Timer",
    6: "Home Timer",
    7: "Boost Timer",
    8: "Overpressure Timer",
    MODE_MANUAL: "Manual",
}

# V2.x Control state (USERSTATECONTROL_FO): 0=Off, 1=Away, 2=Home, 3=Boost, 4=Sauna, 5=Fireplace
CONTROL_STATE_MAP_V2 = {
    0: "Off",
    1: "Away",
    2: "Home",
    3: "Boost",
    4: "Sauna",
    5: "Fireplace",
}

# V1.x Heater type (HEAT_RADIATOR_TYPE): 0=Water, 1=Electric, 2=None
HEATER_TYPE_MAP_V1 = {
    HEATER_TYPE_WATER: "Water",
    HEATER_TYPE_ELECTRIC: "Electric",
    HEATER_TYPE_NONE: "None",
}

# V2.x Heater type (HEATPUMP_RADIATOR_ENABLE): 0=Electric (default), 1=Water (heat pump)
HEATER_TYPE_MAP_V2 = {
    0: "Electric",
    1: "Water",
}

HOME_STATE_MAP = {0: "Away", 1: "Home"}
BINARY_STATE_MAP = {0: "Off", 1: "On"}

# V1.x Filter state
FILTER_STATE_MAP_V1 = {0: "Replace", 1: "OK"}

# V2.x Filter state (FILTER_STATE_FI): 0=Idle/OK, 1=Ack change, 2=Reminder alarm
FILTER_STATE_MAP_V2 = {0: "OK", 1: "Acknowledge Change", 2: "Replace Reminder"}

# V2.x Summer mode (SUMMER_MODE_I): 0=Winter, 1=Transition, 2=Summer
SUMMER_MODE_MAP_V2 = {0: "Winter", 1: "Transition", 2: "Summer"}


# ============================================================================
# Interpretation Functions
# ============================================================================


def interpret_power_state(value: int | None, is_v2: bool = False) -> str:
    """Interpret power state register value."""
    if value is None:
        return "Unknown"
    state_map = POWER_STATE_MAP_V2 if is_v2 else POWER_STATE_MAP_V1
    return state_map.get(value, f"Unknown ({value})")


def interpret_control_state(value: int | None, is_v2: bool = False) -> str:
    """Interpret control state register value."""
    if value is None:
        return "Unknown"
    state_map = CONTROL_STATE_MAP_V2 if is_v2 else CONTROL_STATE_MAP_V1
    return state_map.get(value, f"Unknown ({value})")


def interpret_heater_type(value: int | None, is_v2: bool = False) -> str:
    """Interpret heater type register value."""
    if value is None:
        return "Unknown"
    heater_map = HEATER_TYPE_MAP_V2 if is_v2 else HEATER_TYPE_MAP_V1
    return heater_map.get(value, f"Unknown ({value})")


def interpret_binary_state(value: int | None, state_map: dict[int, str]) -> str:
    """Interpret a binary state register."""
    if value is None:
        return "Unknown"
    return state_map.get(value, f"Unknown ({value})")


def is_optional_sensor_installed(value: int | None) -> bool:
    """Check if an optional sensor (humidity, CO2) is installed."""
    if value is None:
        return False
    # 0, -1, or 65535 (0xFFFF) indicate sensor not installed
    return value not in (0, -1, 65535)


def format_temperature(value: float | None) -> str:
    """Format a temperature value."""
    if value is None:
        return "N/A"
    return f"{value:.1f}°C"


def format_percentage(value: float | None) -> str:
    """Format a percentage value."""
    if value is None:
        return "N/A"
    return f"{value:.1f}%"


def format_filter_date(day: int | None, month: int | None, year: int | None) -> str:
    """Format filter change date."""
    if day is None or month is None or year is None:
        return "N/A"
    try:
        if not (1 <= day <= 31 and 1 <= month <= 12 and 2000 <= year <= 3000):
            return "Invalid"
        return f"{year:04d}-{month:02d}-{day:02d}"
    except (ValueError, TypeError):
        return "Invalid"


# ============================================================================
# Test Result Types
# ============================================================================


@dataclass
class TestResult:
    """Result of a single interpretation test."""

    category: str
    name: str
    raw_value: Any
    interpreted: str
    status: str  # "ok", "warning", "error"
    note: str = ""


class InterpretationTester:
    """Test runner for data interpretation."""

    def __init__(self, coordinator: MockCoordinator, verbose: bool = False):
        """Initialize the tester."""
        self.coord = coordinator
        self.verbose = verbose
        self.results: list[TestResult] = []

        # Detect if this is a V2.x device
        sw_ver = coordinator.data.get("software_version", 0)
        self.is_v2 = sw_ver >= 2.0 if isinstance(sw_ver, int | float) else False

    def test_all(self) -> list[TestResult]:
        """Run all interpretation tests."""
        self.results = []

        self._test_system_info()
        self._test_temperatures()
        self._test_states()
        self._test_speeds()
        self._test_optional_sensors()
        self._test_filter_info()
        self._test_switch_states()
        self._test_timers()

        return self.results

    def _add_result(
        self,
        category: str,
        name: str,
        raw_value: Any,
        interpreted: str,
        status: str = "ok",
        note: str = "",
    ):
        """Add a test result."""
        self.results.append(
            TestResult(
                category=category,
                name=name,
                raw_value=raw_value,
                interpreted=interpreted,
                status=status,
                note=note,
            )
        )

    def _test_system_info(self):
        """Test system information interpretation."""
        # Software version
        sw_ver = self.coord.data.get("software_version")
        raw = self.coord.get_raw_value("software_version")
        if sw_ver is not None:
            self._add_result("System", "Software Version", raw, f"{sw_ver:.2f}")
        else:
            self._add_result("System", "Software Version", raw, "N/A", "warning")

        # Hardware type
        hw_type = self.coord.data.get("hardware_type")
        raw = self.coord.get_raw_value("hardware_type")
        if hw_type is not None:
            hw_type_int = int(hw_type)
            # For V2, use mapping if available, otherwise use raw value
            if self.coord.software_version == SOFTWARE_VERSION_2:
                model_num = HARDWARE_TYPE_MAP_V2.get(hw_type_int, hw_type_int)
                if model_num != hw_type_int:
                    self._add_result(
                        "System", "Hardware Type", raw, f"MAC {model_num} (type code {hw_type_int})"
                    )
                else:
                    self._add_result("System", "Hardware Type", raw, f"MAC {hw_type_int}")
            else:
                self._add_result("System", "Hardware Type", raw, f"MAC {hw_type_int}")
        else:
            self._add_result("System", "Hardware Type", raw, "N/A", "warning")

        # Heater type
        heater = self.coord.data.get("heater_type")
        raw = self.coord.get_raw_value("heater_type")
        self._add_result(
            "System",
            "Heater Type",
            raw,
            interpret_heater_type(int(heater) if heater is not None else None, self.is_v2),
        )

    def _test_temperatures(self):
        """Test temperature interpretation."""
        temp_keys = [
            ("fresh_air_temp", "Fresh Air"),
            ("supply_after_recovery_temp", "Supply (After Recovery)"),
            ("supply_temp", "Supply"),
            ("exhaust_temp", "Exhaust"),
            ("waste_temp", "Waste"),
            ("exhaust_temp_setpoint", "Exhaust Setpoint"),
            ("supply_temp_setpoint", "Supply Setpoint"),
        ]

        for key, name in temp_keys:
            value = self.coord.data.get(key)
            raw = self.coord.get_raw_value(key)

            # Check for reasonable temperature range
            status = "ok"
            note = ""
            if value is not None and (value < -50 or value > 80):
                status = "warning"
                note = "Unusual temperature"

            self._add_result(
                "Temperature",
                name,
                raw,
                format_temperature(value),
                status,
                note,
            )

    def _test_states(self):
        """Test state interpretation."""
        # Power state
        power = self.coord.data.get("power")
        raw = self.coord.get_raw_value("power")
        self._add_result(
            "State",
            "Power",
            raw,
            interpret_power_state(int(power) if power is not None else None, self.is_v2),
        )

        # Control state
        control = self.coord.data.get("control_state")
        raw = self.coord.get_raw_value("control_state")
        self._add_result(
            "State",
            "Control",
            raw,
            interpret_control_state(int(control) if control is not None else None, self.is_v2),
        )

        # Home/Away state - V2 derives from control_state
        if self.is_v2:
            # V2: derive from USERSTATECONTROL_FO (2=Home, 1=Away)
            home_val = "Home" if control == 2 else ("Away" if control == 1 else f"Mode {control}")
            self._add_result("State", "Home/Away", raw, home_val)
        else:
            home = self.coord.data.get("home_state")
            raw = self.coord.get_raw_value("home_state")
            self._add_result(
                "State",
                "Home/Away",
                raw,
                interpret_binary_state(int(home) if home is not None else None, HOME_STATE_MAP),
            )

        # Boost state - V2 derives from control_state
        if self.is_v2:
            boost_val = "On" if control == 3 else "Off"
            self._add_result("State", "Boost", control, boost_val)
        else:
            boost = self.coord.data.get("boost_state")
            raw = self.coord.get_raw_value("boost_state")
            self._add_result(
                "State",
                "Boost",
                raw,
                interpret_binary_state(int(boost) if boost is not None else None, BINARY_STATE_MAP),
            )

        # Overpressure/Sauna/Fireplace state - V2 has different modes
        if self.is_v2:
            if control == 4:
                mode_val = "Sauna Active"
            elif control == 5:
                mode_val = "Fireplace Active"
            else:
                mode_val = "Off"
            self._add_result("State", "Special Mode", control, mode_val)
        else:
            overp = self.coord.data.get("overpressure_state")
            raw = self.coord.get_raw_value("overpressure_state")
            self._add_result(
                "State",
                "Overpressure",
                raw,
                interpret_binary_state(int(overp) if overp is not None else None, BINARY_STATE_MAP),
            )

        # Defrost state
        defrost = self.coord.data.get("defrost_state")
        raw = self.coord.get_raw_value("defrost_state")
        self._add_result(
            "State",
            "Defrost",
            raw,
            interpret_binary_state(int(defrost) if defrost is not None else None, BINARY_STATE_MAP),
        )

    def _test_speeds(self):
        """Test speed-related values."""
        # Current speed
        speed = self.coord.data.get("actual_speed")
        raw = self.coord.get_raw_value("actual_speed")
        if speed is not None:
            self._add_result("Speed", "Current Speed", raw, f"Speed {int(speed)}")
        else:
            self._add_result("Speed", "Current Speed", raw, "N/A", "warning")

        # Speed control
        speed_ctrl = self.coord.data.get("speed_control")
        raw = self.coord.get_raw_value("speed_control")
        if speed_ctrl is not None:
            speed_names = {0: "Auto", 1: "Stop", 2: "1", 3: "2", 4: "3", 5: "4", 6: "5"}
            name = speed_names.get(int(speed_ctrl), f"Unknown ({speed_ctrl})")
            self._add_result("Speed", "Speed Control", raw, name)
        else:
            self._add_result("Speed", "Speed Control", raw, "N/A")

        # Preset speeds
        for key, name in [
            ("home_speed", "Home Preset"),
            ("away_speed", "Away Preset"),
            ("boost_setting", "Boost Preset"),
        ]:
            value = self.coord.data.get(key)
            raw = self.coord.get_raw_value(key)
            if value is not None:
                self._add_result("Speed", name, raw, f"Speed {int(value)}")
            else:
                self._add_result("Speed", name, raw, "N/A")

        # Fan speeds (percentage)
        for key, name in [
            ("supply_fan_speed", "Supply Fan"),
            ("exhaust_fan_speed", "Exhaust Fan"),
        ]:
            value = self.coord.data.get(key)
            raw = self.coord.get_raw_value(key)
            self._add_result("Speed", name, raw, format_percentage(value))

        # Pre-/post-heaters (percentage)
        for key, name in [
            ("pre_heater_output", "Pre-heater Output"),
            ("post_heater_output", "Post-heater Output"),
        ]:
            value = self.coord.data.get(key)
            raw = self.coord.get_raw_value(key)
            self._add_result("Performance", name, raw, format_percentage(value))

        # Heat recovery efficiency
        efficiency = self.coord.data.get("heat_recovery_efficiency")
        raw = self.coord.get_raw_value("heat_recovery_efficiency")
        self._add_result("Performance", "Heat Recovery", raw, format_percentage(efficiency))

    def _test_optional_sensors(self):
        """Test optional sensor interpretation."""
        # Humidity
        humidity = self.coord.data.get("humidity")
        raw = self.coord.get_raw_value("humidity")
        if is_optional_sensor_installed(raw):
            self._add_result("Optional", "Humidity", raw, f"{humidity}%")
        else:
            self._add_result("Optional", "Humidity", raw, "Not installed", "ok", "Sensor absent")

        # Humidity 24h average
        humidity_avg = self.coord.data.get("humidity_24h_avg")
        raw = self.coord.get_raw_value("humidity_24h_avg")
        if humidity_avg is not None and humidity_avg >= 0:
            self._add_result("Optional", "Humidity 24h Avg", raw, f"{humidity_avg:.1f}%")
        else:
            self._add_result("Optional", "Humidity 24h Avg", raw, "Not available", "ok")

        # CO2
        co2 = self.coord.data.get("co2")
        raw = self.coord.get_raw_value("co2")
        if is_optional_sensor_installed(raw):
            self._add_result("Optional", "CO2", raw, f"{co2} ppm")
        else:
            self._add_result("Optional", "CO2", raw, "Not installed", "ok", "Sensor absent")

    def _test_filter_info(self):
        """Test filter information."""
        # Filter state - V2 uses different values
        filter_state = self.coord.data.get("filter_state")
        raw = self.coord.get_raw_value("filter_state")
        filter_map = FILTER_STATE_MAP_V2 if self.is_v2 else FILTER_STATE_MAP_V1
        self._add_result(
            "Filter",
            "Status",
            raw,
            interpret_binary_state(
                int(filter_state) if filter_state is not None else None,
                filter_map,
            ),
        )

        # Filter change date
        day = self.coord.data.get("filter_day")
        month = self.coord.data.get("filter_month")
        year = self.coord.data.get("filter_year")
        self._add_result(
            "Filter",
            "Last Changed",
            f"{day}/{month}/{year}",
            format_filter_date(day, month, year),
        )

        # Next filter change
        next_day = self.coord.data.get("filter_next_day")
        next_month = self.coord.data.get("filter_next_month")
        next_year = self.coord.data.get("filter_next_year")
        self._add_result(
            "Filter",
            "Next Change",
            f"{next_day}/{next_month}/{next_year}",
            format_filter_date(next_day, next_month, next_year),
        )

        # Filter interval
        # V2: 0=3 months, 1=4 months, 2=6 months
        interval = self.coord.data.get("filter_interval")
        raw = self.coord.get_raw_value("filter_interval")
        if interval is not None:
            interval_map = {0: "3 months", 1: "4 months", 2: "6 months"}
            interval_str = interval_map.get(int(interval), f"{int(interval)} (unknown)")
            self._add_result("Filter", "Interval", raw, interval_str)
        else:
            self._add_result("Filter", "Interval", raw, "N/A")

    def _test_switch_states(self):
        """Test switch state interpretation."""
        # V2: Season is a separate read-only indicator (season_state)
        # V2: Summer mode setting (summer_mode) is auto summer cooling enable
        if self.is_v2:
            # Actual season indicator
            season = self.coord.data.get("season_state")
            raw = self.coord.get_raw_value("season_state")
            if season is not None:
                season_val = SUMMER_MODE_MAP_V2.get(int(season), f"Unknown ({season})")
                self._add_result("State", "Season", raw, season_val)
            else:
                self._add_result("State", "Season", raw, "N/A (register not read)")

            # Summer cooling setting (0=Off, 1=On, 2=Auto?)
            summer = self.coord.data.get("summer_mode")
            raw = self.coord.get_raw_value("summer_mode")
            summer_cooling_map = {0: "Off", 1: "On", 2: "Auto"}
            summer_val = summer_cooling_map.get(
                int(summer) if summer is not None else None, f"Unknown ({summer})"
            )
            self._add_result("Switch", "Summer Cooling", raw, summer_val)
        else:
            # V1: summer_mode is just on/off
            summer = self.coord.data.get("summer_mode")
            raw = self.coord.get_raw_value("summer_mode")
            self._add_result(
                "Switch",
                "Summer Mode",
                raw,
                interpret_binary_state(
                    int(summer) if summer is not None else None, BINARY_STATE_MAP
                ),
            )

        # Other switches
        switches = [
            ("time_program_enable", "Time Program"),
            ("heater_enable", "Heater Enable"),
        ]

        for key, name in switches:
            value = self.coord.data.get(key)
            raw = self.coord.get_raw_value(key)
            self._add_result(
                "Switch",
                name,
                raw,
                interpret_binary_state(int(value) if value is not None else None, BINARY_STATE_MAP),
            )

    def _test_timers(self):
        """Test timer values."""
        timers = [
            ("boost_timer", "Boost Timer"),
            ("overpressure_timer", "Overpressure Timer"),
        ]

        for key, name in timers:
            value = self.coord.data.get(key)
            raw = self.coord.get_raw_value(key)
            if value is not None and value > 0:
                self._add_result("Timer", name, raw, f"{int(value)} min")
            else:
                self._add_result("Timer", name, raw, "Inactive")

        # Preset durations
        boost_time = self.coord.data.get("boost_time_setting")
        raw = self.coord.get_raw_value("boost_time_setting")
        boost_time_map = {0: "30 min", 1: "60 min", 2: "90 min", 3: "120 min", 4: "180 min"}
        if boost_time is not None:
            self._add_result(
                "Timer",
                "Boost Preset",
                raw,
                boost_time_map.get(int(boost_time), f"Unknown ({boost_time})"),
            )
        else:
            self._add_result("Timer", "Boost Preset", raw, "N/A")

        overp_time = self.coord.data.get("overpressure_time_setting")
        raw = self.coord.get_raw_value("overpressure_time_setting")
        overp_time_map = {0: "15 min", 1: "30 min", 2: "45 min", 3: "60 min", 4: "120 min"}
        if overp_time is not None:
            self._add_result(
                "Timer",
                "Overpressure Preset",
                raw,
                overp_time_map.get(int(overp_time), f"Unknown ({overp_time})"),
            )
        else:
            self._add_result("Timer", "Overpressure Preset", raw, "N/A")


def print_results(results: list[TestResult], verbose: bool = False):
    """Print test results in a readable format."""
    # Group by category
    categories: dict[str, list[TestResult]] = {}
    for r in results:
        if r.category not in categories:
            categories[r.category] = []
        categories[r.category].append(r)

    warnings = 0
    errors = 0

    for category, items in categories.items():
        print(f"\n{category.upper()}")
        print("-" * 40)

        for item in items:
            # Status indicator
            if item.status == "warning":
                indicator = "⚠"
                warnings += 1
            elif item.status == "error":
                indicator = "✗"
                errors += 1
            else:
                indicator = "✓"

            # Format output
            raw_str = f"(raw: {item.raw_value})" if verbose else ""
            note_str = f" [{item.note}]" if item.note else ""

            print(f"  {indicator} {item.name:25} {item.interpreted:20} {raw_str}{note_str}")

    # Summary
    print("\n" + "=" * 50)
    total = len(results)
    ok = total - warnings - errors
    print(f"SUMMARY: {ok}/{total} OK", end="")
    if warnings:
        print(f", {warnings} warnings", end="")
    if errors:
        print(f", {errors} errors", end="")
    print()

    return errors == 0


def test_file(filepath: Path, verbose: bool = False) -> bool:
    """Test a single dump file."""
    print("=" * 60)
    print(f"Testing: {filepath}")
    print("=" * 60)

    try:
        coord = load_dump(filepath)
    except FileNotFoundError:
        print(f"✗ File not found: {filepath}")
        return False
    except Exception as e:
        print(f"✗ Error loading file: {e}")
        return False

    # Print metadata
    print(f"\nSource: {coord.metadata.get('host', 'unknown')}")
    if coord.metadata.get("detected_software_version"):
        print(f"Software: {coord.metadata['detected_software_version']}")
    if coord.metadata.get("detected_hardware_type"):
        hw_type = coord.metadata["detected_hardware_type"]
        # For V2, use mapping if available, otherwise use raw value
        if coord.software_version == SOFTWARE_VERSION_2:
            model_num = HARDWARE_TYPE_MAP_V2.get(hw_type, hw_type)
            if model_num != hw_type:
                print(f"Detected hardware type: MAC {model_num} (type code {hw_type})")
            else:
                print(f"Detected hardware type: MAC {hw_type}")
        else:
            print(f"Detected hardware type: MAC {hw_type}")
    print(f"Register map: {coord.software_version}")
    print(f"Timestamp: {coord.metadata.get('timestamp', 'unknown')}")

    # Run tests
    tester = InterpretationTester(coord, verbose=verbose)
    results = tester.test_all()

    return print_results(results, verbose=verbose)


def test_all_fixtures(verbose: bool = False) -> bool:
    """Test all fixture files."""
    fixtures_dir = Path(__file__).parent / "test_fixtures"
    dumps_dir = Path(__file__).parent / "dumps"

    all_passed = True
    files_tested = 0

    # Test fixtures
    if fixtures_dir.exists():
        for filepath in sorted(fixtures_dir.glob("*.json")):
            if not test_file(filepath, verbose):
                all_passed = False
            files_tested += 1
            print()

    # Also test any dumps
    if dumps_dir.exists():
        for filepath in sorted(dumps_dir.glob("*.json")):
            if not test_file(filepath, verbose):
                all_passed = False
            files_tested += 1
            print()

    if files_tested == 0:
        print("No test files found in test_fixtures/ or dumps/")
        print("Create a dump first with: python dump_registers.py <host>")
        return False

    print("=" * 60)
    print(f"OVERALL: {'ALL PASSED' if all_passed else 'SOME FAILED'} ({files_tested} files tested)")
    print("=" * 60)

    return all_passed


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Test Parmair data interpretation using dump files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s dumps/my_device.json
    %(prog)s test_fixtures/mac100_v1.json --verbose
    %(prog)s --all
        """,
    )
    parser.add_argument(
        "file",
        nargs="?",
        type=Path,
        help="JSON dump file to test",
    )
    parser.add_argument(
        "--all",
        "-a",
        action="store_true",
        help="Test all fixture files in test_fixtures/ and dumps/",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show raw register values",
    )

    args = parser.parse_args()

    if args.all:
        success = test_all_fixtures(args.verbose)
    elif args.file:
        success = test_file(args.file, args.verbose)
    else:
        parser.print_help()
        sys.exit(1)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
