# Parmair MAC - Home Assistant Integration v0.7.4.3

![Parmair MAC Logo](parmair_logo.jpg)

A custom Home Assistant integration for Parmair MAC ventilation systems via Modbus TCP communication.

## Features

- **Fan Control**: Control your Parmair ventilation unit including:
  - Power on/off
  - Mode selection (Away, Home, Boost)
  - Speed control via presets

- **Number Controls**: Adjust ventilation settings:
  - Home Speed Preset (0-4)
  - Away Speed Preset (0-4)
  - Boost Setting (2-4)
  - Exhaust Temperature Setpoint (18-26°C)
  - Supply Temperature Setpoint (15-25°C)

- **Switch Controls**: Toggle system features:
  - Summer Mode Enable/Disable
  - Time Program Enable/Disable
  - Heater Enable/Disable
  
- **Temperature Monitoring**: Real-time monitoring of:
  - Fresh air temperature
  - Supply air temperature  
  - Exhaust air temperature
  - Waste air temperature
  - Temperature setpoints
  
- **Additional Sensors** (if available):
  - Humidity
  - CO2 levels
  - Alarm status
  - Boost timer
  - Software version (Multi24 firmware)
  - Register metadata exposed via entity attributes for diagnostics
  
- **Local Polling**: Direct communication with your device via Modbus TCP
- **Automatic Model Detection**: Reads hardware type register to identify MAC80/MAC100/MAC150 automatically
- **Firmware Version Detection**: Automatically detects firmware version (1.x or 2.x) for optimal register mapping

## System Information

This integration supports Parmair "My Air Control" systems:
- **Firmware 1.x**: Fully supported (Modbus spec 1.87)
- **Firmware 2.x**: Infrastructure ready (register mappings will be added when specification available)

## Installation

### HACS Installation (Recommended)

1. Open HACS in Home Assistant
2. Click the 3 dots in the top right corner
3. Select "Custom repositories"
4. Add this repository URL: `https://github.com/ValtteriAho/Hassio_Parmair`
5. Select category: "Integration"
6. Click "Add"
7. Find "Parmair MAC" in HACS and click "Download"
8. Restart Home Assistant
9. Go to Settings → Devices & Services → Add Integration
10. Search for "Parmair MAC"
11. Enter your device's connection details:
    - IP Address
    - Port (default: 502)
    - Modbus Slave ID (default: 1)
    - Polling Interval (default: 30 seconds)
    - Name (optional)

Hardware model will be auto-detected from the device.

## Configuration

The integration is configured through the Home Assistant UI. You'll need:

- **IP Address**: The IP address of your Parmair device
- **Port**: The Modbus TCP port (typically 502)
- **Slave ID**: The Modbus slave ID of your device (typically 1)

The hardware model (MAC80/MAC100/MAC150) and firmware version (1.x/2.x) are automatically detected by reading the VENT_MACHINE and MULTI_SW_VER registers.

## Entities Created

### Fan Entity
- **parmair_mac**: Main control for the ventilation system
  - Presets: Away, Home, Boost
  - Speed control (percentage based on preset)

### Number Entities
- **Home Speed Preset**: Adjust fan speed for Home mode (0-4)
- **Away Speed Preset**: Adjust fan speed for Away mode (0-4)
- **Boost Setting**: Set boost fan speed level (2-4)
- **Exhaust Temperature Setpoint**: Target exhaust air temperature (18-26°C)
- **Supply Temperature Setpoint**: Target supply air temperature (15-25°C)

### Switch Entities
- **Summer Mode**: Enable/disable summer mode operation
- **Time Program Enable**: Enable/disable scheduled time programs
- **Heater Enable**: Enable/disable heating element

### Sensor Entities
- **Fresh Air Temperature**: Outdoor air temperature
- **Supply Air Temperature**: Air temperature being supplied to rooms
- **Exhaust Air Temperature**: Air temperature being extracted
- **Waste Air Temperature**: Air temperature being exhausted outside
- **Exhaust/Supply Temperature Setpoints**: Target temperatures
- **Control State**: Current operating mode (Stop, Away, Home, Boost, etc.)
- **Power State**: Power status (Off, Shutting Down, Starting, Running)
- **Home/Away State**: Whether system is in home or away mode (Home/Away)
- **Boost State**: Whether boost mode is active (On/Off)
- **Boost Timer**: Remaining boost time in minutes
- **Alarm Count**: Number of active alarms
- **Summary Alarm**: Overall alarm status

Optional sensors (if hardware is present):
- **Humidity**: Indoor humidity level
- **CO2**: Indoor CO2 concentration
- Entity attributes include the selected model plus register id, address, and scaling to aid troubleshooting

Diagnostic sensors:
- **Software Version**: Multi24 firmware application version (used for firmware family detection)
- **Firmware Family**: Automatically detected as 1.x or 2.x based on software version

## Modbus Registers

All register mappings are documented in `MODBUS_REGISTERS.md`. The integration uses:
- Holding registers (Function codes 03, 06, 16)
- int16 data type
- Temperature scaling factor of 10 (210 = 21.0°C)
- Register addresses offset by -1 from documentation IDs

## Development

This integration follows Home Assistant's development guidelines and uses:
- `pymodbus` (tested with 3.11.x bundled in Home Assistant 2025.12) for Modbus communication
- `DataUpdateCoordinator` for efficient data fetching (30-second polling)
- Config flow for user-friendly setup
- Proper error handling and retry logic

## Troubleshooting

### Connection Issues
- Verify the IP address is correct and the device is on the same network
- Check that port 502 is not blocked by firewalls
- Confirm the Modbus slave ID matches your device configuration

### Missing Sensors
- Some sensors (humidity, CO2) only appear if the hardware is installed
- Check the device's Modbus configuration to ensure sensors are enabled

## Support

For issues, feature requests, or questions, please open an issue on GitHub.

## Release Notes

### 0.2.5
- **CRITICAL FIX**: Negative temperature handling - temperatures below 0°C now display correctly
- **Human-Readable States**: All state sensors now show meaningful text (Home/Away, On/Off, etc.)
- **Missing Hardware**: CO2/Humidity sensors display "Not Installed" when hardware is absent
- **Software Version**: Corrected register address for proper firmware version display

### 0.2.4
- **Software Version Sensor**: Monitor Multi24 firmware application version
- **Diagnostic Entity**: Automatically polled firmware version display (e.g., 2.00)
- **System Monitoring**: Helps identify firmware-related issues and compatibility

### 0.2.3
- **Button Platform**: Acknowledge Alarms, Filter Replaced buttons
- **Select Platform**: Heater Type selector (Water/Electric)
- **Number Controls**: Summer Mode Temperature Limit, Filter Change Interval
- **Sensor Monitoring**: Heat Recovery Efficiency, Overpressure Timer, Defrost State, Supply/Exhaust Fan Speeds, Filter Status
- **Extended Polling**: 6 additional registers for enhanced monitoring

### 0.2.2
- **Fixed Missing Sensor**: Added TE05_M temperature sensor.
- **Supply Air Temperature (After Recovery)**: Now properly monitored alongside other temperature sensors.
- **Complete Temperature Monitoring**: All 5 measurement sensors now present (registers 20, 22, 23, 24, 25).

### 0.2.1
- **Configurable Polling Interval**: Added polling interval configuration (5-300 seconds, default 30).
- **Improved Model Detection**: VENT_MACHINE register value directly maps to model (80→MAC80, 100→MAC100, 150→MAC150).
- **MAC100 Support**: Added MAC100 model to register map.
- **Fixed Default Name**: Changed from "Parmair Ventilation" to "Parmair MAC".
- **Fixed Register ID Calculation**: Corrected formula to properly calculate register addresses.
- **Translations**: Added Finnish/English translations for polling interval field.

### 0.2.0
- **Number Platform**: Added 5 controllable entities for fan speed presets and temperature setpoints.
- **Switch Platform**: Added 3 toggle entities for Summer Mode, Time Program Enable, and Heater Enable.
- **Finnish Translation**: Complete localization support (fi.json).
- **Write Capability**: Full read/write control via coordinator.async_write_register().
- **HACS Metadata**: Updated with number and switch domains.

### 0.1.9
- **CRITICAL**: Fix transaction ID mismatch errors with threading lock (resolves sensor data loss).
- Automatic hardware model detection via VENT_MACHINE register.
- Always create all sensors (show unavailable if hardware missing).
- Enhanced diagnostic logging for troubleshooting.

### 0.1.8
- Add `device_id` keyword argument as additional Modbus fallback for pre-2.0 era pymodbus builds.
- Enhanced compatibility chain: `unit` → `slave` → `device_id` → attribute assignment → positional.

### 0.1.7
- Retry Modbus reads without a count parameter to cover extremely old pymodbus clients.
- Handle legacy read responses that do not include a `registers` attribute.

### 0.1.6
- Assign slave/unit ids via client attributes before retrying Modbus operations to support very old pymodbus clients without keyword arguments.
- Handle legacy responses lacking `isError()` gracefully during polling.

### 0.1.5
- Add a final positional Modbus fallback to keep legacy pymodbus deployments working during setup and polling.

### 0.1.4
- Fix config flow connection tests against pymodbus builds that still require the `slave` keyword.
- Apply the same compatibility fallback to runtime reads and writes so older libraries keep working.

### 0.1.3
- Model selector in the config flow with placeholder support for MAC150.
- Register metadata exposed via entity attributes for easier troubleshooting.
- Coordinator read/write logic now uses register definitions for scaling.

### 0.1.2
- Fixed handler registration for Home Assistant 2025.12 config flow loader.
- Dropped classified documentation references from README and register map.

### 0.1.1
- Bundled translations and dependency adjustments for Home Assistant 2025.12.
- Resolved config flow errors related to pymodbus 3.11 compatibility.

### 0.1.0
- Initial public release with fan control, temperature monitoring, and optional humidity/CO2 sensors.

## License

MIT License

---

## Disclaimer

This is an independent, personal project developed by a community member and is **not affiliated with, endorsed by, or supported by Parmair or its parent companies**. This integration is provided as-is, without any warranty or guarantee. The Parmair name and product references are used solely for identification purposes.

For official support, product information, or warranty claims, please contact Parmair directly through their official channels.

Use of this integration is at your own risk. The author assumes no liability for any damage, malfunction, or warranty voidance that may result from using this software with your Parmair ventilation system.
