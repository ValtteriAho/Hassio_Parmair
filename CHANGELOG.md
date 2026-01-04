## 0.7.4.2 - Fix Device Info Display (2026-01-04)

### Fixed
- **Device model now shows MAC type** - Shows "MAC 80", "MAC 100", or "MAC 150" based on hardware type
- **Added hardware type polling** - Reads VENT_MACHINE register (1244) to determine MAC model
- Device info now displays correct model information in Home Assistant

### Technical
- Added REG_HARDWARE_TYPE to polling registers
- Updated device_info property to read hardware_type and format model string
- Software version continues to display correctly as sw_version

## 0.7.4.1 - Fix Pymodbus Compatibility and Auto-Detection (2026-01-04)

### Fixed
- **Pymodbus compatibility** - Now tries keyword arguments first (address=, count=, slave=)
- **Auto-detection working** - Fixed "ModbusClientMixin.read_holding_registers() takes 2 positional arguments but 3 were given" error
- **Software version detection** - Now correctly detects software version during setup
- **Heater type detection** - Now correctly detects heater type during setup
- **Transaction ID conflicts** - Increased inter-register read delay from 20ms to 50ms to reduce transaction ID mismatch errors

### Technical
- Updated config_flow.py to try keyword arguments before positional
- Updated coordinator.py read method with better pymodbus version compatibility
- Improved timing to prevent buffer conflicts

## 0.7.4 - Add Speed Control Sensor and Manual Speed Control (2026-01-04)

### Added
- **Speed Control sensor** - Displays current speed setting (Auto, Stop, Speed 1-5)
- **Manual Speed Control number entity** - Allows direct speed control (0-6)
  - 0 = Auto mode
  - 1 = Stop
  - 2-6 = Speed 1-5
- Speed map information shown in Manual Speed Control attributes

### Technical
- Added ParmairSpeedControlSensor class (enum sensor with 7 states)
- Added ParmairManualSpeedNumber class (number entity 0-6)
- Reads/writes REG_SPEED_CONTROL (register 1187, IV01_SPEED_FOC)
- Speed control updates in real-time with 30-second polling

## 0.7.3 - Remove Redundant Timer Sensors (2026-01-04)

### Removed
- Removed separate Boost Timer sensor entity
- Removed separate Overpressure Timer sensor entity
- Removed ParmairTimerSensor class (no longer needed)

### Changed
- Timer information now only shown as attributes on Boost/Overpressure switches
- Boost Mode switch shows: preset_duration, preset_speed, remaining_time
- Overpressure Mode switch shows: preset_duration, remaining_time

### Technical
- Reduced entity count by removing duplicate timer displays
- Timer data still available via switch extra_state_attributes
- Cleaner entity list with less redundancy

## 0.7.2.1 - Fix Optional Sensor ValueError (2026-01-04)

### Fixed
- Fixed ValueError when optional sensors (CO2, humidity) are not installed
- Changed return value from "Not Installed"/"Not Available" strings to `None`
- Added dynamic state_class property that returns `None` when sensor not present
- Resolves: "could not convert string to float: 'Not Installed'" error

### Technical
- Optional sensors now properly return `None` instead of error strings
- state_class dynamically set to `None` when hardware not detected
- Prevents numeric sensor errors when optional hardware missing

## 0.7.2 - Display Timer Remaining Time (2026-01-04)

### Added
- Boost Mode switch now displays `remaining_time` attribute showing minutes left when active
- Overpressure Mode switch now displays `remaining_time` attribute showing minutes left when active

### Changed
- Enhanced extra_state_attributes on boost and overpressure switches
- Timer values update in real-time during mode operation

### Technical
- Added REG_BOOST_TIMER and REG_OVERPRESSURE_TIMER to switch.py imports
- Reads BOOST_TIMER_FM (register 1202) and OVERP_TIMER_FM (register 1204)
- Displays remaining time only when timer > 0 (mode is active)

## 0.7.1 - Fix Config Flow Import Error (2026-01-04)

### Fixed
- Fixed syntax error in config_flow.py (escaped quotes in string literals)
- Resolves "Error importing platform config_flow" during setup

## 0.7.0 - Software Version Detection & Register Versioning (2026-01-04)

### Added
- **Auto-detection during setup:**
  - Software version detection (1.xx or 2.xx)
  - Heater type detection (None/Water/Electric)
- **Manual configuration fallback:**
  - If auto-detection fails, user can manually select software version and heater type
  - User-friendly selection interface
- **Version-specific register maps:**
  - Infrastructure for v1.xx and v2.xx register addresses
  - Current implementation uses v1 addresses (CSV documentation)
  - v2 addresses prepared as placeholder for future update

### Changed
- Coordinator now uses version-specific register map based on detected software version
- Register map selection: `get_registers_for_version(software_version)`
- Renamed `_build_registers()` to `_build_registers_v1()` (documented as version 1.xx from CSV)
- Added `_build_registers_v2()` placeholder (TODO: update when v2 addresses available)

### Technical
- Added CONF_SOFTWARE_VERSION and CONF_HEATER_TYPE to config entry
- Added SOFTWARE_VERSION_1, SOFTWARE_VERSION_2, SOFTWARE_VERSION_UNKNOWN constants
- Added HEATER_TYPE_NONE, HEATER_TYPE_WATER, HEATER_TYPE_ELECTRIC constants
- Coordinator stores software_version and heater_type attributes
- Enhanced config_flow with _detect_device_info() function
- Added async_step_manual_config() for manual selection
- get_register_definition() now accepts optional registers parameter

### Notes
- Current CSV documentation = v1.xx register addresses
- v2.xx register addresses will be added in future update
- Default fallback to v1 registers if version unknown

## 0.6.9 - Switch Predefined Values Display (2026-01-04)

### Added
- Display predefined settings as attributes on switches
- Boost Mode switch now shows preset_duration (30-180 minutes) and preset_speed (Speed 3-5)
- Overpressure Mode switch now shows preset_duration (15-120 minutes)
- Summer Mode switch now shows temperature_limit

### Technical
- Added REG_BOOST_TIME_SETTING register (1106, BOOST_TIME_S)
- Added REG_OVERPRESSURE_TIME_SETTING register (1107, OVERP_TIME_S)
- Added REG_SUMMER_MODE_TEMP_LIMIT to predefined settings section
- Added extra_state_attributes methods to switch entities
- Added new registers to polling list for real-time display
- Boost time maps: 0=30min, 1=60min, 2=90min, 3=120min, 4=180min
- Overpressure time maps: 0=15min, 1=30min, 2=45min, 3=60min, 4=120min
- Boost speed maps: 2=Speed 3, 3=Speed 4, 4=Speed 5

## 0.6.8 - Remove Firmware Version (2026-01-04)

### Removed
- Removed firmware version sensor completely
- Removed firmware version from device info section
- Removed REG_FIRMWARE_VERSION register definition
- Removed firmware version from polling list

### Changed
- Device info now displays only software version
- Simplified device_info property in coordinator

### Technical
- Removed MULTI_FW_VER register (1017) from code
- Removed ParmairFirmwareFamilySensor class
- Removed fw_version references from coordinator.device_info
- Reduced number of registers polled per cycle

## 0.6.7 - Coordinator Attribute Fix (2026-01-04)

### Fixed
- Fixed AttributeError in sensor and fan entities trying to access removed coordinator.model
- Removed leftover references to coordinator.model from v0.6.0 refactoring
- Entities now use coordinator.device_info consistently

### Technical
- Removed parmair_model from sensor extra_state_attributes
- Removed parmair_model from fan extra_state_attributes
- Fan entity now uses coordinator.device_info instead of building device_info manually

## 0.6.6 - Manifest JSON Fix (2026-01-04)

### Fixed
- Fixed JSON syntax error in manifest.json (trailing comma after version)
- Resolves "Failed to perform the action update/install. trailing comma is not allowed" error

### Technical
- Removed invalid trailing comma after version field in manifest.json
- No functional changes - only manifest syntax correction

## 0.6.5 - Transaction ID Fix (2026-01-04)

### Fixed
- Fixed pymodbus transaction ID mismatch errors (93+ occurrences)
- Increased delay between register reads from 10ms to 20ms
- Added 50ms stabilization delay after Modbus connection
- Prevents "request ask for transaction_id=X but got id=Y" errors

### Technical
- Changed inter-register delay from `time.sleep(0.01)` to `time.sleep(0.02)`
- Added `time.sleep(0.05)` after connection establishment
- Allows device to stabilize before polling registers
- Reduces transaction ID conflicts when polling 30+ registers

## 0.6.4 - Number Entity Bugfix (2026-01-04)

### Fixed
- Fixed TypeError: 'NoneType' object does not support item assignment in number.py
- Moved interval_description attribute from ParmairTimerNumber to ParmairFilterIntervalNumber
- Fixed extra_state_attributes to handle None return from parent class
- Resolved 621+ error occurrences in Home Assistant logs

### Technical
- Changed `attrs = super().extra_state_attributes if hasattr(super(), 'extra_state_attributes') else {}` to `attrs = super().extra_state_attributes or {}`
- Moved filter interval description logic to correct class (ParmairFilterIntervalNumber)
- Removed incorrect extra_state_attributes from ParmairTimerNumber

## 0.6.3 - Documentation Security Update (2026-01-04)

### Changed
- Removed all Modbus register address numbers from public documentation
- Removed register/address mapping tables from SETUP_COMPLETE.md
- Keep only register names (e.g., FILTER_DAY, MULTI_FW_VER) in documentation
- Per Parmair manufacturer request: restrict normal user access to registry numbers

### Technical
- Register addresses remain in source code (const.py) for functionality
- Only public-facing documentation files modified
- No changes to integration functionality

## 0.6.2 - Filter Change Date Sensor (2026-01-04)

### Added
- New sensor: **Filter Last Changed** - displays when air filter was last changed (YYYY-MM-DD format)
- Sensor includes `next_change_date` attribute showing when next filter change is due
- Reads from FILTER_DAY, FILTER_MONTH, FILTER_YEAR registers
- Also polls FILTERNEXT_DAY, FILTERNEXT_MONTH, FILTERNEXT_YEAR registers

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
- **Firmware Version**: Now reads actual firmware version from MULTI_FW_VER register
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
- Registers: BOOST_STATE_FI, BOOST_TIMER_FM (writable), OVERP_STATE_FI, OVERP_TIMER_FM (writable)

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
  - Uses ME05_AVG_FM register
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
- **Software Version Sensor**: Corrected register address

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
- **Software Version Sensor**: Monitor Multi24 firmware application version (MULTI_SW_VER)
  - Diagnostic sensor showing firmware version (e.g., 2.00)
  - Automatically polled with other system data
  - Helps identify firmware-related issues and compatibility

### Changed
- Software version now included in polling cycle for system monitoring

## 0.2.3 - Enhanced Control & Monitoring (2025-12-28)

### Added
- **Button Platform** with 2 actions:
  - Acknowledge Alarms button - Clear active alarms
  - Filter Replaced button - Acknowledge filter change
- **Select Platform** with configuration:
  - Heater Type selector - Choose between Water/Electric heater
- **Number Entities** (2 additional):
  - Summer Mode Temperature Limit (15-30°C) - Outdoor temp to disable heat recovery
  - Filter Change Interval (3/4/6 months) - Set maintenance schedule
- **Sensor Entities** (7 additional):
  - Heat Recovery Efficiency - Real-time efficiency %
  - Overpressure Timer - Fireplace mode time remaining
  - Defrost State - Heat recovery defrost active
  - Supply Fan Speed - Current fan output %
  - Exhaust Fan Speed - Current fan output %
  - Filter Status - Replace/OK status

### Changed
- Updated HACS domains to include "button" and "select"
- Extended polling to include performance and state monitoring registers

## 0.2.2 - Temperature Sensor Fix (2025-12-28)

### Fixed
- Added missing TE05_M temperature sensor

### Added
- **Number Platform**: Control fan speed presets and temperature setpoints
  - Home speed preset (0-4)
  - Away speed preset (0-4)
  - Boost setting preset (2-4)
  - Exhaust temperature setpoint (18-26°C)
  - Supply temperature setpoint (15-25°C)
- **Switch Platform**: Control system features
  - Summer mode toggle
  - Time program enable toggle
  - Heater enable toggle
- **Finnish Translation**: Complete fi.json translation for broader user base
- Updated HACS configuration with number and switch domains

### Changed
- Expanded integration from read-only monitoring to full control capabilities
- Users can now adjust fan speeds, temperature targets, and system modes directly from Home Assistant

## 0.2.2 - Temperature Sensor Fix (2025-12-28)

### Fixed
- Added missing TE05_M temperature sensor
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
- Register ID calculation corrected to use proper addressing formula
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
- New register definitions: REG_SUMMER_MODE, REG_TIME_PROGRAM_ENABLE, REG_HEATER_ENABLE

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
- Register ID + 1000 = Address calculation corrected
- All addresses were off by 1, preventing proper communication

## 0.1.11 - Register Documentation & Sensor Fixes (2025-12-27)

### Fixed
- Handle 65535 (0xFFFF) value for CO2 and humidity sensors (indicates sensor not installed)
- Corrected VENT_MACHINE register address

### Changed
- Updated register documentation with official Parmair register IDs (TE01_M, TE10_M, etc.)
- All register definitions now use official IDs from Parmair documentation

## 0.1.10 - Register Address Fix (2025-12-27)

### Fixed
- **CRITICAL**: Fixed all Modbus register addresses to match actual device addressing
- Register addressing corrected to use proper +1000 offset formula
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
