#!/usr/bin/env python3
"""Dump all Modbus registers from a Parmair device to a JSON file.

This tool reads all registers from a real Parmair ventilation unit
and saves them to a JSON file for offline testing.

Usage:
    python dump_registers.py <host> [options]

Examples:
    python dump_registers.py 192.168.1.100
    python dump_registers.py 192.168.1.100 --output dumps/my_device.json
    python dump_registers.py 192.168.1.100 --port 502 --slave-id 1 --version 2.x
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

# Add parent directory to path to import from custom_components
sys.path.insert(0, str(Path(__file__).parent.parent))
import importlib.util

from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

# Import const.py directly to avoid homeassistant dependency in __init__.py
_const_path = Path(__file__).parent.parent / "custom_components" / "parmair" / "const.py"
_spec = importlib.util.spec_from_file_location("parmair_const", _const_path)
_const = importlib.util.module_from_spec(_spec)
sys.modules["parmair_const"] = _const  # Register module to fix dataclass issues
_spec.loader.exec_module(_const)

POLLING_REGISTER_KEYS = _const.POLLING_REGISTER_KEYS
SOFTWARE_VERSION_1 = _const.SOFTWARE_VERSION_1
SOFTWARE_VERSION_2 = _const.SOFTWARE_VERSION_2
RegisterDefinition = _const.RegisterDefinition
get_registers_for_version = _const.get_registers_for_version


@dataclass
class RegisterDump:
    """Container for a single register dump."""

    key: str
    address: int
    label: str
    raw: int | None
    scaled: float | int | None
    scale: float
    optional: bool
    writable: bool


@dataclass
class DeviceDump:
    """Container for complete device dump."""

    metadata: dict[str, Any]
    registers: dict[str, dict[str, Any]]

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(
            {"metadata": self.metadata, "registers": self.registers},
            indent=2,
            ensure_ascii=False,
        )

    @classmethod
    def from_json(cls, json_str: str) -> DeviceDump:
        """Create from JSON string."""
        data = json.loads(json_str)
        return cls(metadata=data["metadata"], registers=data["registers"])


def read_single_register(
    client: ModbusTcpClient,
    definition: RegisterDefinition,
    slave_id: int,
) -> tuple[int | None, float | int | None]:
    """Read a single register and return (raw, scaled) values."""
    # pymodbus 3.11+ uses: address (positional), count= (keyword), device_id= (keyword)
    try:
        result = client.read_holding_registers(definition.address, count=1, device_id=slave_id)
    except TypeError:
        # Fallback for older pymodbus versions
        try:
            result = client.read_holding_registers(definition.address, 1, slave=slave_id)
        except TypeError:
            try:
                result = client.read_holding_registers(definition.address, 1, unit=slave_id)
            except TypeError:
                client.slave = slave_id
                result = client.read_holding_registers(definition.address, 1)

    if not result or (hasattr(result, "isError") and result.isError()):
        return None, None

    if hasattr(result, "registers"):
        raw = result.registers[0]
    elif isinstance(result, list | tuple):
        raw = result[0]
    else:
        raw = result

    # Convert to signed int16 if value is > 32767 (handle negative temperatures)
    if raw > 32767:
        raw = raw - 65536

    # Check if optional sensor is not installed
    if definition.optional and raw < 0:
        return raw, None

    # Apply scaling
    scaled = raw if definition.scale == 1 else raw * definition.scale

    return raw, scaled


def read_register_with_retry(
    client: ModbusTcpClient,
    definition: RegisterDefinition,
    slave_id: int,
    max_attempts: int = 3,
    retry_delay: float = 0.5,
) -> tuple[int | None, float | int | None]:
    """Read a single register with retries on failure (e.g. transaction_id mismatch)."""
    for attempt in range(max_attempts):
        if attempt > 0:
            time.sleep(retry_delay)
        raw, scaled = read_single_register(client, definition, slave_id)
        if raw is not None:
            return raw, scaled
    return None, None


def dump_device(
    host: str,
    port: int = 502,
    slave_id: int = 1,
    software_version: str = SOFTWARE_VERSION_1,
    verbose: bool = False,
) -> DeviceDump:
    """Connect to device and dump all registers."""
    print(f"Connecting to Parmair device at {host}:{port} (slave ID: {slave_id})")
    print(f"Using register map for software version: {software_version}")

    client = ModbusTcpClient(host=host, port=port)

    if not client.connect():
        raise ModbusException(f"Failed to connect to {host}:{port}")

    print("✓ Connected successfully\n")

    # Longer delay after connect to allow device to stabilize and prevent transaction_id mismatch
    time.sleep(0.3)

    # Get version-specific register map
    registers = get_registers_for_version(software_version)

    # First, try to detect actual software version if we're on auto
    detected_version = None
    detected_hw_type = None

    try:
        # Read software version register
        sw_def = registers.get("software_version")
        if sw_def:
            raw, scaled = read_register_with_retry(
                client, sw_def, slave_id, max_attempts=3, retry_delay=0.5
            )
            if scaled is not None:
                detected_version = scaled
                print(f"Detected software version: {detected_version}")

        # Read hardware type register
        hw_def = registers.get("hardware_type")
        if hw_def:
            time.sleep(0.25)  # Delay between reads to prevent transaction ID conflicts
            raw, scaled = read_register_with_retry(
                client, hw_def, slave_id, max_attempts=3, retry_delay=0.5
            )
            if scaled is not None:
                detected_hw_type = int(scaled)
                print(f"Detected hardware type: MAC {detected_hw_type}")

    except Exception as e:
        print(f"Warning: Could not auto-detect device info: {e}")

    print("\nReading registers...")

    register_dumps: dict[str, dict[str, Any]] = {}
    failed_count = 0
    success_count = 0

    for key in POLLING_REGISTER_KEYS:
        if key not in registers:
            if verbose:
                print(f"  [SKIP] {key}: Not in register map for {software_version}")
            continue

        definition = registers[key]
        time.sleep(0.25)  # Delay between reads to prevent transaction_id mismatch

        raw, scaled = read_register_with_retry(
            client, definition, slave_id, max_attempts=3, retry_delay=0.5
        )

        if raw is None:
            failed_count += 1
            if verbose:
                print(f"  [FAIL] {key} (addr {definition.address}): Read failed")
            register_dumps[key] = {
                "address": definition.address,
                "label": definition.label,
                "raw": None,
                "scaled": None,
                "scale": definition.scale,
                "optional": definition.optional,
                "writable": definition.writable,
                "error": "Read failed",
            }
        else:
            success_count += 1
            if verbose:
                scaled_str = f"{scaled}" if scaled is not None else "N/A"
                print(f"  [OK]   {key} (addr {definition.address}): raw={raw}, scaled={scaled_str}")
            register_dumps[key] = {
                "address": definition.address,
                "label": definition.label,
                "raw": raw,
                "scaled": scaled,
                "scale": definition.scale,
                "optional": definition.optional,
                "writable": definition.writable,
            }

    client.close()

    print(f"\n✓ Read {success_count} registers successfully")
    if failed_count > 0:
        print(f"✗ Failed to read {failed_count} registers")

    # Build metadata
    metadata = {
        "timestamp": datetime.now().isoformat(),
        "host": host,
        "port": port,
        "slave_id": slave_id,
        "register_map_version": software_version,
        "detected_software_version": detected_version,
        "detected_hardware_type": detected_hw_type,
        "registers_read": success_count,
        "registers_failed": failed_count,
    }

    return DeviceDump(metadata=metadata, registers=register_dumps)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Dump Modbus registers from a Parmair device to JSON",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s 192.168.1.100
    %(prog)s 192.168.1.100 --output dumps/my_device.json
    %(prog)s 192.168.1.100 --version 2.x --verbose
        """,
    )
    parser.add_argument("host", help="IP address or hostname of the Parmair device")
    parser.add_argument(
        "--port", "-p", type=int, default=502, help="Modbus TCP port (default: 502)"
    )
    parser.add_argument(
        "--slave-id", "-s", type=int, default=1, help="Modbus slave ID (default: 1)"
    )
    parser.add_argument(
        "--version",
        "-V",
        choices=["1.x", "2.x"],
        default="1.x",
        help="Register map version to use (default: 1.x)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output JSON file path (default: dumps/<host>_<timestamp>.json)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed register readings"
    )

    args = parser.parse_args()

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_host = args.host.replace(".", "_")
        output_dir = Path(__file__).parent / "dumps"
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"{safe_host}_{timestamp}.json"

    try:
        dump = dump_device(
            host=args.host,
            port=args.port,
            slave_id=args.slave_id,
            software_version=args.version,
            verbose=args.verbose,
        )

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write JSON file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(dump.to_json())

        print(f"\n✓ Dump saved to: {output_path}")

        # Print summary
        print("\n" + "=" * 50)
        print("DUMP SUMMARY")
        print("=" * 50)
        print(f"Device: {args.host}:{args.port}")
        if dump.metadata.get("detected_software_version"):
            print(f"Software Version: {dump.metadata['detected_software_version']}")
        if dump.metadata.get("detected_hardware_type"):
            print(f"Hardware Type: MAC {dump.metadata['detected_hardware_type']}")
        print(
            f"Registers: {dump.metadata['registers_read']} read, {dump.metadata['registers_failed']} failed"
        )
        print(f"Output: {output_path}")

    except ModbusException as e:
        print(f"\n✗ Modbus error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
