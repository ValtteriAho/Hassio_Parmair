# Parmair Test Tools

This directory contains standalone tools for testing the Parmair integration
without requiring Home Assistant.

## Overview

```
tools/
├── dump_registers.py      # Dump device registers to JSON
├── mock_coordinator.py    # Mock coordinator for testing
├── test_interpretation.py # Test data interpretation
├── dumps/                 # Your device dumps (gitignored)
└── test_fixtures/         # Sample test data
```

## Quick Start

### 1. Dump Your Device Data

Connect to your Parmair ventilation unit and dump all register values:

```bash
# Basic usage
python dump_registers.py 192.168.1.100

# With options
python dump_registers.py 192.168.1.100 --port 502 --slave-id 1 --version 1.x

# Save to specific file
python dump_registers.py 192.168.1.100 --output my_device.json

# Verbose output
python dump_registers.py 192.168.1.100 --verbose
```

The output is a JSON file containing:
- Device metadata (timestamp, detected version, hardware type)
- All register values (raw and scaled)

### 2. Test Interpretation

Verify the integration correctly interprets your device data:

```bash
# Test a specific dump file
python test_interpretation.py dumps/my_device.json

# Show raw values
python test_interpretation.py dumps/my_device.json --verbose

# Test all fixtures
python test_interpretation.py --all
```

### 3. Share Test Data

If you want to contribute test data:

1. Dump your device: `python dump_registers.py <ip> --output test_fixtures/macXXX_vX.json`
2. Optionally anonymize the host IP in the JSON
3. Run tests: `python test_interpretation.py test_fixtures/macXXX_vX.json`
4. Submit a PR with your fixture

## Requirements

- Python 3.9+
- pymodbus (same as the integration)

Install dependencies:
```bash
pip install pymodbus
```

## Tools Reference

### dump_registers.py

Reads all Modbus registers from a Parmair device and saves them to JSON.

```
Usage: dump_registers.py <host> [options]

Arguments:
  host                 IP address of the Parmair device

Options:
  --port, -p          Modbus TCP port (default: 502)
  --slave-id, -s      Modbus slave ID (default: 1)
  --version, -V       Register map version: 1.x or 2.x (default: 1.x)
  --output, -o        Output file path
  --verbose, -v       Show detailed output
```

### test_interpretation.py

Tests that register values are correctly interpreted.

```
Usage: test_interpretation.py [file] [options]

Arguments:
  file                JSON dump file to test

Options:
  --all, -a           Test all files in test_fixtures/ and dumps/
  --verbose, -v       Show raw register values
```

### mock_coordinator.py

A standalone mock of `ParmairCoordinator` for use in custom tests.

```python
from mock_coordinator import MockCoordinator, load_dump

# Load from file
coord = load_dump("dumps/my_device.json")

# Access data
print(coord.data)  # Scaled values
print(coord.get_raw_value("fresh_air_temp"))  # Raw value
print(coord.device_info)  # Device info dict

# Or create from dict for unit tests
coord = MockCoordinator.from_dict({
    "power": 3,
    "control_state": 2,
    "fresh_air_temp": -5.0,
})
```

## Firmware Versions

The integration supports two firmware versions with different register maps:

- **1.x** - Original firmware, uses registers like `POWER_BTN_FI`, `IV01_CONTROLSTATE_FO`
- **2.x** - Newer firmware, uses `UNIT_CONTROL_FO`, `USERSTATECONTROL_FO`

The dump tool will detect the firmware version automatically from the
`software_version` register and record it in the metadata.
