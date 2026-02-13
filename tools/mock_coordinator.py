"""Mock coordinator for testing Parmair integration without Home Assistant.

This module provides a MockCoordinator that loads register data from JSON dumps
and provides the same interface as the real ParmairCoordinator, allowing
offline testing of entity interpretation logic.

Usage:
    from mock_coordinator import MockCoordinator

    coord = MockCoordinator.from_file("dumps/my_device.json")
    print(coord.data)  # Access parsed register values
"""

from __future__ import annotations

import importlib.util
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Add parent directory to path to import from custom_components
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import const.py directly to avoid homeassistant dependency in __init__.py
_const_path = Path(__file__).parent.parent / "custom_components" / "parmair" / "const.py"
_spec = importlib.util.spec_from_file_location("parmair_const", _const_path)
_const = importlib.util.module_from_spec(_spec)
sys.modules["parmair_const"] = _const  # Register module to fix dataclass issues
_spec.loader.exec_module(_const)

SOFTWARE_VERSION_1 = _const.SOFTWARE_VERSION_1
SOFTWARE_VERSION_2 = _const.SOFTWARE_VERSION_2
HARDWARE_TYPE_MAP_V2 = _const.HARDWARE_TYPE_MAP_V2
REG_POWER = _const.REG_POWER
REG_CONTROL_STATE = _const.REG_CONTROL_STATE
RegisterDefinition = _const.RegisterDefinition
get_register_definition = _const.get_register_definition
get_registers_for_version = _const.get_registers_for_version


@dataclass
class MockDeviceInfo:
    """Mock device info matching HA's device_info structure."""

    identifiers: set
    name: str
    manufacturer: str
    model: str
    sw_version: str | None = None


class MockCoordinator:
    """Mock coordinator that loads data from a JSON dump file.

    This provides the same interface as ParmairCoordinator but without
    any Home Assistant dependencies, making it suitable for offline testing.
    """

    def __init__(
        self,
        data: dict[str, Any],
        metadata: dict[str, Any],
        registers: dict[str, dict[str, Any]],
        software_version: str = SOFTWARE_VERSION_1,
    ) -> None:
        """Initialize the mock coordinator.

        Args:
            data: The processed register data (key -> scaled value)
            metadata: Dump metadata (timestamp, host, etc.)
            registers: Raw register dump data
            software_version: Software version for register map selection
        """
        self._data = data
        self._metadata = metadata
        self._raw_registers = registers
        self._software_version = software_version
        self._registers = get_registers_for_version(software_version)

    @property
    def data(self) -> dict[str, Any]:
        """Return the processed register data."""
        return self._data

    @property
    def metadata(self) -> dict[str, Any]:
        """Return the dump metadata."""
        return self._metadata

    @property
    def raw_registers(self) -> dict[str, dict[str, Any]]:
        """Return the raw register data including addresses and labels."""
        return self._raw_registers

    @property
    def software_version(self) -> str:
        """Return the software version string."""
        return self._software_version

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information (compatible with HA device_info)."""
        sw_version = self._data.get("software_version")
        hw_type = self._data.get("hardware_type")

        model = "MAC"
        if hw_type is not None:
            hw_int = int(hw_type)
            is_v2 = self._software_version == SOFTWARE_VERSION_2 or str(
                self._software_version
            ).startswith("2.")
            model_num = HARDWARE_TYPE_MAP_V2.get(hw_int, hw_int) if is_v2 else hw_int
            model = f"MAC {model_num}"

        device_info = {
            "identifiers": {("parmair", "mock_device")},
            "name": f"Parmair {model} (Mock)",
            "manufacturer": "Parmair",
            "model": model,
        }

        if sw_version is not None:
            if isinstance(sw_version, int | float):
                device_info["sw_version"] = f"{sw_version:.2f}"
            else:
                device_info["sw_version"] = str(sw_version)

        return device_info

    def get_register_definition(self, key: str) -> RegisterDefinition:
        """Get register definition for a key."""
        return get_register_definition(key, self._registers)

    def get_raw_value(self, key: str) -> int | None:
        """Get the raw (unscaled) value for a register key."""
        if key in self._raw_registers:
            return self._raw_registers[key].get("raw")
        return None

    @classmethod
    def from_file(cls, filepath: str | Path) -> MockCoordinator:
        """Create a MockCoordinator from a JSON dump file.

        Args:
            filepath: Path to the JSON dump file

        Returns:
            MockCoordinator instance with loaded data
        """
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"Dump file not found: {filepath}")

        with open(filepath, encoding="utf-8") as f:
            dump = json.load(f)

        metadata = dump.get("metadata", {})
        registers = dump.get("registers", {})

        # Determine software version from metadata or detect from version register
        software_version = metadata.get("register_map_version", SOFTWARE_VERSION_1)

        # Override if we have detected version that suggests different map
        detected_ver = metadata.get("detected_software_version")
        if detected_ver is not None:
            software_version = SOFTWARE_VERSION_2 if detected_ver >= 2.0 else SOFTWARE_VERSION_1

        # Build data dict from scaled values
        data: dict[str, Any] = {}
        for key, reg_data in registers.items():
            if reg_data.get("scaled") is not None:
                data[key] = reg_data["scaled"]
            elif reg_data.get("raw") is not None:
                # For registers without scaling, use raw value
                data[key] = reg_data["raw"]

        # v2.x: derive home_state, boost_state, overpressure_state from control_state
        # (USERSTATECONTROL_FO: 0=Off, 1=Away, 2=Home, 3=Boost, 4=Sauna, 5=Fireplace)
        is_v2 = software_version == SOFTWARE_VERSION_2 or str(software_version).startswith("2.")
        if is_v2:
            user_state = data.get("control_state")
            if user_state is not None:
                data["home_state"] = 1 if user_state == 2 else 0
                data["boost_state"] = 1 if user_state == 3 else 0
                data["overpressure_state"] = 1 if user_state in (4, 5) else 0

        return cls(
            data=data,
            metadata=metadata,
            registers=registers,
            software_version=software_version,
        )

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
        software_version: str = SOFTWARE_VERSION_1,
    ) -> MockCoordinator:
        """Create a MockCoordinator from a data dictionary.

        This is useful for creating test fixtures with specific values.

        Args:
            data: Dictionary of register key -> scaled value
            software_version: Software version for register map

        Returns:
            MockCoordinator instance
        """
        # Build register dict from data
        registers_map = get_registers_for_version(software_version)
        registers: dict[str, dict[str, Any]] = {}

        for key, value in data.items():
            if key in registers_map:
                reg_def = registers_map[key]
                # Calculate raw value from scaled
                if reg_def.scale == 1:
                    raw = int(value) if value is not None else None
                else:
                    raw = int(round(value / reg_def.scale)) if value is not None else None

                registers[key] = {
                    "address": reg_def.address,
                    "label": reg_def.label,
                    "raw": raw,
                    "scaled": value,
                    "scale": reg_def.scale,
                    "optional": reg_def.optional,
                    "writable": reg_def.writable,
                }

        metadata = {
            "source": "from_dict",
            "register_map_version": software_version,
        }

        # v2.x: derive home_state, boost_state, overpressure_state from control_state
        is_v2 = software_version == SOFTWARE_VERSION_2 or str(software_version).startswith("2.")
        if is_v2:
            data = dict(data)  # Copy to avoid mutating user input
            user_state = data.get("control_state")
            if user_state is not None:
                data["home_state"] = 1 if user_state == 2 else 0
                data["boost_state"] = 1 if user_state == 3 else 0
                data["overpressure_state"] = 1 if user_state in (4, 5) else 0

        return cls(
            data=data,
            metadata=metadata,
            registers=registers,
            software_version=software_version,
        )

    def __repr__(self) -> str:
        """Return string representation."""
        source = self._metadata.get("host", self._metadata.get("source", "unknown"))
        return f"MockCoordinator(source={source}, registers={len(self._data)})"


# Convenience function for quick loading
def load_dump(filepath: str | Path) -> MockCoordinator:
    """Load a dump file and return a MockCoordinator.

    Args:
        filepath: Path to the JSON dump file

    Returns:
        MockCoordinator instance
    """
    return MockCoordinator.from_file(filepath)
