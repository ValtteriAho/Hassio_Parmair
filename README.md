# Parmair MAC - Home Assistant Integration

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
  - Register metadata exposed via entity attributes for diagnostics
  
- **Local Polling**: Direct communication with your device via Modbus TCP
- **Automatic Model Detection**: Reads hardware type register to identify MAC80/MAC150 automatically

## System Information

This integration targets Parmair "My Air Control" firmware V1.87 behaviour observed on production units.

## Installation

### Manual Installation

1. Copy the `custom_components/parmair` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Go to Settings → Devices & Services → Add Integration
4. Search for "Parmair MAC"
5. Enter your device's connection details:
   - IP Address
   - Port (default: 502)
   - Modbus Slave ID (default: 1)
   - Name (optional)
   
   Hardware model will be auto-detected from the device.

## Configuration

The integration is configured through the Home Assistant UI. You'll need:

- **IP Address**: The IP address of your Parmair device
- **Port**: The Modbus TCP port (typically 502)
- **Slave ID**: The Modbus slave ID of your device (typically 1)

The hardware model (MAC80/MAC150) is automatically detected by reading the VENT_MACHINE register.

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
- **Control State**: Current operating mode
- **Power State**: Power status (0=Off, 3=Running)
- **Home/Away State**: Whether system is in home or away mode
- **Boost State**: Whether boost mode is active
- **Boost Timer**: Remaining boost time in minutes
- **Alarm Count**: Number of active alarms
- **Summary Alarm**: Overall alarm status

Optional sensors (if hardware is present):
- **Humidity**: Indoor humidity level
- **CO2**: Indoor CO2 concentration
- Entity attributes include the selected model plus register id, address, and scaling to aid troubleshooting

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

## Documentation

- [Modbus Register Documentation](MODBUS_REGISTERS.md)

## Release Notes

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
