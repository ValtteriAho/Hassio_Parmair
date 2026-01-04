## 0.6.2 - Filter Change Date Sensor (2026-01-04)

### Added
- New sensor: **Filter Last Changed** - displays when air filter was last changed (YYYY-MM-DD format)
- Sensor includes `next_change_date` attribute showing when next filter change is due
- Reads from FILTER_DAY, FILTER_MONTH, FILTER_YEAR registers (86-88/1086-1088)
- Also polls FILTERNEXT_DAY, FILTERNEXT_MONTH, FILTERNEXT_YEAR registers (89-91/1089-1091)

### Technical
- Added filter date registers to const.py (REG_FILTER_DAY, REG_FILTER_MONTH, etc.)
- Created ParmairFilterChangeDateSensor class
- Sensor categorized as EntityCategory.DIAGNOSTIC
- Validates date values before display

## 0.6.1 - Switch Display Fix (2026-01-04)

### Fixed
- Fixed Post Heater, Summer Mode, and Time Program switches displaying with dual icons instead of toggle switches
- Added `SwitchDeviceClass.SWITCH` to all switch entities for proper UI rendering

### Technical
- Set `device_class = SwitchDeviceClass.SWITCH` on all switch entities
- Ensures switches render as proper toggles in Home Assistant UI

## 0.6.0 - Simplified Architecture (2026-01-04)

### Changed
- **BREAKING**: Removed hardware/firmware version detection and constants
- Simplified codebase to use single register map (all MAC models use same registers)
- Removed `CONF_MODEL` and `CONF_FIRMWARE_VERSION` from configuration
- Removed firmware version constants (`FIRMWARE_V1`, `FIRMWARE_V2`, etc.)
- Removed model constants (`MODEL_MAC80`, `MODEL_MAC100`, `MODEL_MAC150`)
- Removed hardware type mapping and model-based register maps
- Simplified `get_register_definition()` to only take key parameter
- Device info now shows generic "MAC" model
- Config flow no longer detects hardware type or firmware version

### Technical
- Renamed `_build_v1_registers()` to `_build_registers()`
- Replaced multiple register maps with single `REGISTERS` map
- Removed firmware version change detection from coordinator
- Reduced code complexity and maintenance burden

### Rationale
- All MAC models use identical Modbus register mappings per CSV specification
- Hardware/firmware detection was unnecessary complexity
- Simpler codebase is more maintainable and reliable

## 0.5.3 - Firmware Version Sensor Fix (2026-01-04)

### Fixed
- Fixed firmware version sensor showing "unavailable"
- Removed code that was overwriting firmware_version data with string constant
- Now properly displays the numeric value from MULTI_FW_VER register
- Added type safety for firmware version display

## 0.5.2 - Device Info Type Fix (2026-01-04)

### Fixed
- Fixed "Unknown format code 'f' for object of type 'str'" error in device_info
- Added type checking for software and firmware version formatting

## 0.5.1 - Transaction ID Fix (2026-01-04)

### Fixed
- Fixed pymodbus transaction ID mismatch errors by adding 10ms delay between register reads
- Prevents "request ask for transaction_id=X but got id=Y" errors in logs

## 0.5.0 - Device Info Enhancement (2026-01-04)

### Changed
- **Firmware Version**: Now reads actual firmware version from MULTI_FW_VER register (17/1017)
- **Device Info**: Software version and firmware version now displayed in device information
  - Software version shown in "Software version" field
  - Firmware version shown in "Hardware version" field
- **Firmware Family Sensor**: Renamed to "Firmware Version" and shows actual value from device (e.g., "1.87")

### Technical
- Added REG_FIRMWARE_VERSION register definition
- Centralized device_info in coordinator for consistency
- All entities now use coordinator.device_info property

## 0.4.1 - Diagnostic Entity Fix (2026-01-04)

### Fixed
- Fixed diagnostic entities (Software Version, Firmware Family) not appearing properly
- Added proper EntityCategory import for diagnostic entities

## 0.4.0 - Boost and Overpressure Controls (2026-01-04)

### Added
- **Boost Mode Switch**: Toggle boost ventilation mode (control state 3)
- **Overpressure Mode Switch**: Toggle overpressure mode (control state 4)
- **Boost Timer**: Number slider to set boost mode timer (0-300 minutes)
- **Overpressure Timer**: Number slider to set overpressure mode timer (0-300 minutes)
- Firmware version now displayed during installation alongside hardware model
- Registers: BOOST_STATE_FI (1201), BOOST_TIMER_FM (1202, writable), OVERP_STATE_FI (1203), OVERP_TIMER_FM (1204, writable)

### Changed
- Config flow now shows detected firmware version during setup
- Timer registers are now writable for direct timer control

## 0.3.4 - Firmware Version Sensor Fix (2026-01-04)

### Fixed
- Fixed firmware version sensor not displaying - now always includes firmware_version in coordinator data

## 0.3.3 - Bugfix Release (2026-01-04)

### Fixed
- Fixed duplicate argument in function definition causing syntax error

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
