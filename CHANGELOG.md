## 0.3.2 - Bugfix Release (2026-01-04)

### Fixed
- Fixed trailing comma in manifest.json causing HACS installation failure

## 0.3.1 - 24-Hour Humidity Average Sensor (2026-01-04)

### Added
- **24-Hour Humidity Average Sensor**: New sensor for monitoring 24-hour averaged humidity
  - Uses ME05_AVG_FM register (192/1192)
  - Displays percentage humidity averaged over 24 hours
  - Shows "Not Available" when measurement is not present
  - Optional sensor - marked unavailable if hardware doesn't support it

## 0.3.0 - Multi-Firmware Support (2026-01-04)

### Added
- **Multi-Firmware Architecture**: Support for different firmware versions (1.x and 2.x)
  - Automatic firmware version detection from MULTI_SW_VER register
  - Firmware-specific register mapping selection
  - Firmware version displayed in Home Assistant as diagnostic sensor
- **Firmware 2.x Placeholder**: Infrastructure for future firmware 2.x support
  - Register map placeholder (currently mirrors 1.x)
  - Will be updated when firmware 2.x Modbus specification becomes available
- **Enhanced Detection**: During setup, integration now detects both:
  - Hardware model (MAC80/100/150) from VENT_MACHINE register
  - Firmware version (1.x/2.x) from MULTI_SW_VER register

### Changed
- **Register Map Structure**: Refactored to support multiple firmware versions
  - Firmware-based register selection (primary)
  - Model-based register selection (legacy support)
- **Coordinator**: Now uses firmware version for register mapping
- **Config Flow**: Detects and stores firmware version during initial setup
- **Software Version Sensor**: Now actively used for firmware version detection

### Technical
- Added `CONF_FIRMWARE_VERSION` configuration key
- Added `detect_firmware_version()` helper function
- Added `get_registers_for_firmware()` function
- Register definitions now organized by firmware version
- Coordinator logs firmware version changes and suggests reconfiguration

### Notes
- **Firmware 1.x users**: No changes needed, continues to work as before
- **Firmware 2.x users**: Currently uses 1.x register map as fallback
- **Future**: Firmware 2.x register map will be updated when specification is available

## 0.2.5 - Critical Fixes & UX Improvements (2026-01-03)

### Fixed
- **CRITICAL: Negative Temperature Handling**: Fixed signed int16 conversion for temperature sensors
  - Temperatures below 0°C were displaying as huge values (e.g., -8.6°C showed as 6545°C)
  - All temperature sensors now properly handle negative values
- **Software Version Sensor**: Corrected register address to 1018 (register 18 + 1000 offset)

### Added
- **Human-Readable State Sensors**: State sensors now display meaningful text instead of numbers
  - **Control State**: Stop, Away, Home, Boost, Overpressure, Timer modes, Manual
  - **Power State**: Off, Shutting Down, Starting, Running
  - **Home/Away State**: Now shows "Home" or "Away" instead of 1/0
  - **Boost State**: Shows "On" or "Off" instead of 1/0
  - **Defrost State**: Shows "Active" or "Off" instead of 1/0
  - **Filter Status**: Shows "Replace" or "OK" instead of 0/1
- **Missing Hardware Indication**: CO2 and Humidity sensors now display "Not Installed" when hardware is absent

### Changed
- All state sensors use ENUM device class with proper options for better Home Assistant integration
- Improved sensor display consistency across the board

## 0.2.4 - Software Version Monitoring (2026-01-03)

### Added
- **Software Version Sensor**: Monitor Multi24 firmware application version (MULTI_SW_VER, Register 18)
  - Diagnostic sensor showing firmware version (e.g., 2.00)
  - Automatically polled with other system data
  - Helps identify firmware-related issues and compatibility

### Changed
- Software version now included in polling cycle for system monitoring

## 0.2.3 - Enhanced Control & Monitoring (2025-12-28)

### Added
- **Button Platform** with 2 actions:
  - Acknowledge Alarms button - Clear active alarms (register 3)
  - Filter Replaced button - Acknowledge filter change (register 205)
- **Select Platform** with configuration:
  - Heater Type selector - Choose between Water/Electric heater (register 240)
- **Number Entities** (2 additional):
  - Summer Mode Temperature Limit (15-30°C, register 78) - Outdoor temp to disable heat recovery
  - Filter Change Interval (3/4/6 months, register 85) - Set maintenance schedule
- **Sensor Entities** (7 additional):
  - Heat Recovery Efficiency - Real-time efficiency % (register 190)
  - Overpressure Timer - Fireplace mode time remaining (register 204)
  - Defrost State - Heat recovery defrost active (register 183)
  - Supply Fan Speed - Current fan output % (register 40)
  - Exhaust Fan Speed - Current fan output % (register 42)
  - Filter Status - Replace/OK status (register 205)

### Changed
- Updated HACS domains to include "button" and "select"
- Extended polling to include performance and state monitoring registers

## 0.2.2 - Temperature Sensor Fix (2025-12-28)

### Fixed
- Added missing TE05_M temperature sensor (Register 22, Address 1022)

### Added
- **Number Platform**: Control fan speed presets and temperature setpoints
  - Home speed preset (0-4, register 128)
  - Away speed preset (0-4, register 129)
  - Boost setting preset (2-4, register 130)
  - Exhaust temperature setpoint (18-26°C, register 10)
  - Supply temperature setpoint (15-25°C, register 12)
- **Switch Platform**: Control system features
  - Summer mode toggle (register 79)
  - Time program enable toggle (register 108)
  - Heater enable toggle (register 109)
- **Finnish Translation**: Complete fi.json translation for broader user base
- Updated HACS configuration with number and switch domains

### Changed
- Expanded integration from read-only monitoring to full control capabilities
- Users can now adjust fan speeds, temperature targets, and system modes directly from Home Assistant

## 0.2.2 - Temperature Sensor Fix (2025-12-28)

### Fixed
- Added missing TE05_M temperature sensor (Register 22, Address 1022)
- Supply Air Temperature (After Recovery) sensor now properly monitored
- All 5 temperature measurement sensors now present (registers 20, 22, 23, 24, 25)

## 0.2.1 - Model Detection & Configuration Improvements (2025-12-28)

### Added
- Configurable polling interval in config flow (5-300 seconds, default 30)
- MAC100 model support to register map
- Translations for polling interval field (English/Finnish)

### Changed
- Improved model auto-detection: VENT_MACHINE register value directly maps to model (80→MAC80, 100→MAC100, 150→MAC150)
- Updated coordinator to use configured scan_interval from config entry

### Fixed
- Default integration name changed from "Parmair Ventilation" to "Parmair MAC"
- Register ID calculation corrected: Address - 1000 = Register ID (was incorrectly Address + 1)
- Model detection now returns formatted model names (MAC80/MAC100/MAC150) instead of raw numbers

## 0.2.0 - Control Features & Localization (2025-12-27)

### Added
- **Number Platform** with 5 controllable entities:
  - Home Speed Preset (0-4)
  - Away Speed Preset (0-4)
  - Boost Setting (2-4)
  - Exhaust Temperature Setpoint (18-26°C)
  - Supply Temperature Setpoint (15-25°C)
- **Switch Platform** with 3 toggle entities:
  - Summer Mode Enable/Disable
  - Time Program Enable/Disable
  - Heater Enable/Disable
- **Finnish Translation** (fi.json) for complete localization support
- Write capability via coordinator.async_write_register() method
- New register definitions: REG_SUMMER_MODE (1079), REG_TIME_PROGRAM_ENABLE (1108), REG_HEATER_ENABLE (1109)

### Changed
- Updated HACS metadata with "number" and "switch" domains
- Updated platform list in __init__.py to include Platform.NUMBER and Platform.SWITCH

## 0.1.13 - Branding Update (2025-12-27)

### Changed
- Updated integration name from "Parmair Ventilation" to "Parmair MAC" to align with official product naming
- Updated all references in documentation and user-facing strings
- Added disclaimer about project independence from Parmair

## 0.1.12 - Address Calculation Fix (2025-12-27)

### Fixed
- **CRITICAL**: Fixed off-by-one error in all register addresses
- Register ID + 1000 = Address (e.g., Register 20 = Address 1020, not 1019)
- All addresses were off by 1, preventing proper communication

## 0.1.11 - Register Documentation & Sensor Fixes (2025-12-27)

### Fixed
- Handle 65535 (0xFFFF) value for CO2 and humidity sensors (indicates sensor not installed)
- Corrected VENT_MACHINE register address from 1124 to 1243

### Changed
- Updated register documentation with official Parmair register IDs (TE01_M, TE10_M, etc.)
- All register definitions now use official IDs from Parmair documentation

## 0.1.10 - Register Address Fix (2025-12-27)

### Fixed
- **CRITICAL**: Fixed all Modbus register addresses by adding +1000 offset to match actual device addressing
- Register 20 is now correctly addressed as 1019 (not 19), register 124 as 1124, etc.
- This was the root cause preventing all sensor data from being read correctly
- Slave ID 0 should be used instead of default slave ID 1 for most devices

## 0.1.9 - Thread Safety & Auto-Detection (2025-12-27)

### Fixed
- **CRITICAL**: Add threading lock to fix transaction ID mismatch errors causing sensor data loss.
- ModbusTcpClient is not thread-safe; now all Modbus operations are serialized with threading.Lock().
- Always create all sensor entities (show unavailable if data missing) instead of conditional creation.
- Improve diagnostic logging with failed register tracking and data key reporting.

### Added
- Automatic hardware model detection via VENT_MACHINE register (eliminates manual model selection).
- Enhanced logging showing which registers fail to read with addresses.

## 0.1.8 - Extended Legacy Compatibility (2025-12-27)

### Fixed
- Add `device_id` keyword argument as additional fallback layer in Modbus read/write methods, supporting extremely old pymodbus builds (pre-2.0 era).
- Improve compatibility chain: `unit` → `slave` → `device_id` → attribute assignment → positional arguments.
- Reference jormai/parmair implementation patterns for legacy client handling.

## 0.1.7 - Countless Legacy Clients (2025-12-27)

### Fixed
- Retry Modbus reads without a count parameter after assigning legacy attributes to support the oldest pymodbus variants.
- Accept primitive read responses when legacy clients do not expose a `registers` buffer.

## 0.1.6 - Legacy Attribute Fallback (2025-12-27)

### Fixed
- Assign the slave/unit id through client attributes before retrying Modbus calls so extremely old pymodbus clients work during setup and polling.
- Avoid calling `isError()` on result objects that do not expose the method, preventing AttributeError on legacy responses.

## 0.1.5 - Legacy Modbus Support (2025-12-27)

### Fixed
- Add positional Modbus read/write fallback so very old pymodbus clients lacking both `unit` and `slave` keywords still work during setup and runtime.

## 0.1.4 - Modbus Compatibility (2025-12-27)

### Fixed
- Restore compatibility with deployments running older pymodbus builds by falling back to the legacy `slave` keyword when `unit` is rejected during reads or writes.
- Prevent config flow connection tests from crashing with a `TypeError` when the Modbus client lacks `unit` support.

## 0.1.3 - Model-Aware Registers (2025-12-27)

### Added
- Register metadata definitions per hardware model with placeholder support for MAC150
- Config flow model selector to ensure correct register mapping on setup
- Extra diagnostics attributes exposing register ids, addresses, and model info on fan and sensors

### Changed
- Coordinator read/write logic now scales values using register definitions instead of hard-coded addresses

## 0.1.2 - Handler Compatibility (2025-12-27)

### Fixed
- Resolve "Invalid handler specified" by registering the config flow domain explicitly
- Refresh README and register map to drop classified documentation references

## 0.1.1 - Config Flow Fixes (2025-12-27)

### Fixed
- Allow Home Assistant OS 2025.12+ to reuse bundled `pymodbus>=3.11.2`
- Provide translations bundle required by 2025.12 config flow loader
- Register config flow handler correctly for Home Assistant 2025.12

## 0.1.0 - Initial Release (2025-12-27)

### Added
- Initial release of Parmair Ventilation integration
- Fan entity with Away/Home/Boost presets
- Temperature sensors (fresh air, supply, exhaust, waste)
- Temperature setpoint sensors
- State sensors (control, power, home/away, boost)
- Timer sensors (boost timer)
- Alarm sensors (count, summary)
- Optional humidity sensor (if hardware present)
- Optional CO2 sensor (if hardware present)
- Config flow for easy setup via UI
- Modbus TCP communication support
- Based on Parmair My Air Control V1.87 specification

### Features
- Read-only monitoring of ventilation system
- Control ventilation modes (Away, Home, Boost)
- Real-time temperature monitoring
- Alarm status monitoring
- 30-second polling interval
- Automatic retry on connection failures
