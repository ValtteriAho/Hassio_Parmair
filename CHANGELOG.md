## 0.10.5 - CO2 Sensor Cleanup (2026-01-23)

### Removed
- **Removed external CO2 sensor (QE20_M)** - This is optional external hardware not included in any device as standard
  - Register 1031 (v1.xx) and 1030 (v2.xx) no longer monitored
  - Was showing as unavailable on all devices anyway

### Changed
- **Clarified exhaust CO2 sensor** - Only for MAC 2 devices (newest v2.xx)
  - QE05_M at register 1026 - Combination sensor in exhaust duct
  - Only available in newest MAC 2 devices with v2.xx firmware
  - Older devices will not have this sensor (graceful unavailable state)

### Technical
- Removed REG_CO2 constant and related register definitions
- Simplified CO2 monitoring to only MAC 2 exhaust sensor
- Updated comments to reflect actual hardware availability

## 0.10.4 - Firmware v1.xx Compatibility Fix (2026-01-18)

### Fixed
- **CRITICAL: Fixed firmware v1.xx devices failing to load** with "Register 'co2_exhaust' not defined" error
- Exhaust CO2 sensor now only created for v2.xx firmware (register doesn't exist in v1.xx)
- v1.xx devices will now load successfully without the exhaust CO2 sensor

### Technical
- Added conditional sensor creation based on register availability
- Exhaust CO2 sensor (register 1026/QE05_M) only exists in firmware v2.xx
- v1.xx firmware only has indoor CO2 sensor (register 1031/QE20_M)

## 0.10.3 - HACS Compatibility Fix (2026-01-18)

### Fixed
- Fixed HACS installation issue caused by JSON validation error in previous version
- No functional changes - this is a compatibility release to ensure HACS can properly download the integration

### Technical
- Bumped version to force HACS cache refresh
- Previous fix (removal of trailing comma in manifest.json) already committed in 0.10.2

## 0.10.2 - Add Exhaust Air CO2 Sensor for v2.xx (2026-01-18)

### Added
- **Exhaust Air CO2 sensor (QE05_M)** for firmware v2.xx only
  - Register 1026 (QE05_M) - Exhaust air CO2
  - Complements existing Indoor air CO2 sensor (register 1030)
  - Firmware v1.xx only has indoor CO2 at register 1031
  - Sensor will show as unavailable on v1.xx devices (hardware not present)

### Technical Details
- Added REG_CO2_EXHAUST constant and register definition
- Added to v2.xx register map and polling list
- New sensor entity: "CO2 Exhaust Air"
- Both CO2 sensors use the same ParmairCO2Sensor class

## 0.10.1 - Critical Heater Type Mapping Fix (2026-01-18)

### Fixed
- **CRITICAL: Heater type detection for firmware 2.xx** - Values are reversed compared to 1.xx
  - Firmware 1.xx (register 1240): 0=Water, 1=Electric, 2=None
  - Firmware 2.xx (register 1127): 0=Electric, 1=Water, 2=None
  - Integration now correctly interprets heater type based on firmware version
  - v2.xx devices with electric heaters will now show "Electric" instead of incorrectly showing "Water"

### Technical Details
- Added separate heater type constants for v1 and v2 in const.py
- Updated ParmairHeaterTypeSensor to dynamically select correct mapping based on software_version
- Updated documentation (MODBUS_REGISTERS_1XX.md and MODBUS_REGISTERS_2XX.md) with correct value mappings

## 0.10.0 - Code Cleanup (2026-01-18)

### Changed
- Removed all legacy pymodbus compatibility code
- Simplified to use only pymodbus 3.11.2+ API
- Cleaner, more maintainable codebase
- Renamed `_set_legacy_unit()` to `_set_unit_id()` for clarity

### Technical
- Reduced code complexity by ~50% in Modbus read/write functions
- All API calls now use modern pymodbus 3.x format:
  - Read: `client.read_holding_registers(address, count=1)`
  - Write: `client.write_register(address, value)`
- Unit ID set on client before operations, not per-call
- No more nested TypeError exception handling

### No Breaking Changes
- Functionality identical to 0.9.11
- Still requires pymodbus>=3.11.2
- Tested and verified working

## 0.9.11 - Pymodbus API Compatibility Fix (2026-01-18)

### Fixed
- Fixed pymodbus 3.x API compatibility: "takes 2 positional arguments but 3 were given"
- Reordered API call attempts: tries modern `read_holding_registers(address, count=1)` first
- Sets slave/unit ID on client before reads
- Added pymodbus version logging for diagnostics
- Register reads during detection now work correctly

## 0.9.10 - Function Order Fix (2026-01-18)

### Fixed
- Fixed NameError: _read_register called before definition in warm-up phase
- Moved warm-up code after _read_register function definition

## 0.9.0.9 - Detection Warm-up + Manual Fallback (2026-01-18)

### Added
- **Connection Warm-up**: Read power register (1001) 5 times with 500ms delays before detection
  - "Wakes up" device so it's ready to respond to version detection reads
  - Addresses issue where device needs time after connection to respond
- **Manual Firmware Selection**: If auto-detection fails, user can manually select:
  - Firmware version (1.xx or 2.xx)
  - Heater type (None, Water, Electric)
  - New configuration step with dropdown menus
  - No more forced defaults

### Changed
- Detection now has two-phase approach:
  1. Warm-up: Read universal register repeatedly until device responds
  2. Version detection: Try firmware 2.xx then 1.xx with consensus method
- If detection fails, shows manual selection form instead of defaulting to 1.xx

### Fixed
- Devices that don't respond immediately after connection can now be configured
- Users with firmware 2.xx devices can now manually specify version if auto-detection fails
- No more silent defaulting to wrong firmware version

### User Experience
- If auto-detection succeeds: Same as before, seamless setup
- If auto-detection fails: User gets clear form to select version manually
- Logs show warm-up progress and detection attempts

## 0.9.0.8 - Detection Timing Fix (2026-01-18)

### Fixed
- **Auto-detection now works**: Fixed firmware version detection failing during setup
  - Increased initial stabilization delay: 150ms → 1000ms (1 second)
  - Added 200ms delay between register reads during detection
  - Added 100ms delay before validation
  - Previously all register reads returned "no data" during setup
  - Normal polling worked fine, but detection phase was too fast

### Impact
- Firmware version detection (1.xx vs 2.xx) now works correctly
- Heater type detection now succeeds
- No more "defaulting to firmware 1.x" warnings
- Device needs ~1 second after connection before it can respond to reads

### Technical
- Detection phase timing completely separated from polling timing
- Setup requires longer delays than normal operation
- All register reads during detection now succeed

## 0.9.0.7 - Emergency Syntax Fix (2026-01-17)

### Fixed
- **Critical**: Fixed syntax error in coordinator.py line 184 that prevented integration from loading
  - Restored missing return statement and exception handler
  - Bug was introduced in v0.9.0.6 during timing adjustments
  - **Do not use v0.9.0.6** - it is broken

### Notes
- If you installed v0.9.0.6, update immediately to v0.9.0.7
- All timing fixes from v0.9.0.6 are preserved (300ms/200ms delays)

## 0.9.0.6 - Aggressive Timing Fix (2026-01-17)

**WARNING: This version has a syntax error. Use v0.9.0.7 instead.**

### Fixed
- **Increased Modbus Timing Delays**: Much more aggressive delays to prevent severe transaction ID backlog
  - Post-connection delay: 150ms → 300ms (2x increase)
  - Inter-register read delay: 80ms → 200ms (2.5x increase)
  - Post-write delay: 80ms → 200ms (2.5x increase)
  - Fixes cases where device buffer had 100+ responses backed up
  - Addresses persistent "transaction_id mismatch" errors when reading 30+ registers

### Impact
- Polling will be significantly slower (30 registers × 200ms = ~6 seconds per poll)
- Trade-off: reliability over speed for devices with slow Modbus processing

### Notes
- **Important**: Also ensure slave_id is set to 0 (see v0.9.0.5)
- If you still experience transaction ID errors after this update:
  - Verify slave_id is configured as 0 (not 1)
  - Consider reducing the number of polled registers
  - Check for other devices causing network congestion

## 0.9.0.5 - Slave ID Default Fix (2026-01-17)

### Fixed
- **Corrected Default Slave ID**: Changed from 1 to 0 to match Parmair device configuration
  - Eliminates "request ask for id=1 but got id=0" errors (146+ occurrences)
  - Parmair MAC devices respond with unit ID 0, not 1
  - Config flow now accepts slave ID 0-247 (previously 1-247)
  - Existing installations with slave_id=1 will need to reconfigure or manually change to 0

### Technical
- Updated DEFAULT_SLAVE_ID from 1 to 0
- Updated config validation to allow min=0
- Added comment explaining Parmair uses unit ID 0

### Migration
- **New installations**: Will automatically use slave ID 0
- **Existing installations**: If you see "id=1 but got id=0" errors, delete and re-add the integration (or edit .storage/core.config_entries and change slave_id from 1 to 0)

## 0.9.0.4 - Transaction ID Reliability Fix (2026-01-17)

### Fixed
- **Eliminated Transaction ID Mismatch Errors**: Increased timing delays to prevent buffer overflow
  - Increased post-connection stabilization delay from 50ms to 150ms
  - Increased inter-register read delay from 50ms to 80ms
  - Added 80ms delay after register writes
  - Prevents "transaction_id mismatch" errors (4000+ occurrences eliminated)
  - Device now has adequate time to process each request before next one arrives

### Technical
- Connection stabilization: 50ms → 150ms
- Register read spacing: 50ms → 80ms
- Added write completion delay: 80ms
- Improved buffer flushing on reconnect

## 0.9.0.3 - Detection Improvements (2026-01-17)

### Changed
- **Future-Proof Machine Type Detection**: Removed validation constraints on VENT_MACHINE register
  - Now accepts any machine type value returned by the device
  - Enables support for future Parmair MAC models without code changes
  - Detection still validates register readability for reliability

### Added
- **Enhanced Installation Visibility**: Comprehensive logging during device auto-detection
  - Shows detected firmware version, machine type, and heater configuration
  - Helps troubleshoot setup issues with detailed debug information
  - Final summary log displays all detected parameters

## 0.9.0.2 - Enhanced Detection Reliability (2026-01-12)

### Fixed
- **Enhanced Firmware Detection**: Improved reliability with two-register consensus validation
  - Now validates both SOFTWARE_VERSION and VENT_MACHINE registers for firmware identification
  - Firmware 2.xx confirmed by reading firmware-specific version register (2.00-2.99 range) AND machine type register (MAC80/100/105/150)
  - Firmware 1.xx confirmed by reading firmware-specific version register (1.00-1.99 range) AND machine type register (MAC80/100/105/150)
  - Both registers must return valid values for positive firmware identification
  - Prevents false positives from random Modbus noise or ambiguous responses
  - Hardware model validation ensures device is actually a Parmair MAC unit

### Technical
- Refactored `_detect_device_info()` in config_flow.py with consensus-based detection
- Added `_read_register()` helper function for cleaner code
- Validates software version range AND hardware model simultaneously
- More robust error handling and debug logging

## 0.9.0.1 - Critical Autodetection Bugfix (2026-01-11)

### Fixed
- **Critical: Firmware 2.xx Autodetection Fixed**: Devices with firmware 2.xx can now be detected during initial setup
  - Firmware 2.xx and 1.xx use different register locations for software version and heater type
  - Autodetection now tries both firmware register sets and uses the one that responds correctly
  - Detects which firmware is running based on which register set returns valid data (1.00-2.99 version range)
  - Heater type detection uses the correct register set based on detected firmware version
- **Improved Logging**: Better debug messages showing which firmware version was detected

### Technical
- Modified `_detect_device_info()` in config_flow.py to try both firmware register sets
- Validates software version range (1.00-2.99) to ensure valid readings
- Validates heater type values (0=Water, 1=Electric, 2=None) to ensure valid readings
- Tracks which firmware registers worked and uses matching register set for subsequent reads

## 0.9.0 - Full Firmware 2.xx Support (2026-01-09)

### Added
- **Complete Firmware 2.xx Register Mappings**: Full support for Modbus specification 2.28
  - All 648 registers documented and mapped
  - Proper firmware 2.xx addressing scheme with register offset
  - Enhanced control registers for firmware 2.xx
  - All temperature, humidity, CO2, and state sensors working
- **Automatic Firmware Detection**: Seamlessly switches between 1.xx and 2.xx register maps
  - Reads software version register to detect firmware version
  - Loads appropriate register map automatically
  - No user configuration needed
- **Version-Specific Register Maps**: Separate register definitions for each firmware family
  - `_build_registers_v1()`: Firmware 1.xx with standard addressing
  - `_build_registers_v2()`: Firmware 2.xx with offset addressing
  - `get_registers_for_version()`: Dynamic register map selection

### Changed
- **Control Architecture**: Firmware 2.xx uses different control scheme
  - Enhanced power control registers
  - Updated state control registers
  - All existing entities continue to work with both firmware versions
- **Address Calculation**: Implemented proper offset for firmware 2.xx
  - All 70+ registers properly mapped with correct firmware-specific addressing

### Technical
- Added comprehensive register documentation (MODBUS_REGISTERS_2XX.md)
- Updated RegisterDefinition.register_id property to support address calculation
- Coordinator uses version-specific register maps from const.py
- All platforms (sensor, switch, number, button, select) work with both firmware versions
- Maintained backward compatibility with firmware 1.xx systems

### Documentation
- Created detailed Modbus 2.xx specification document
- Documented all register groups, addressing, and scaling factors
- Included implementation notes and quick reference guide
- Added to .gitignore to protect proprietary information

### Compatibility
- Firmware 1.xx: No changes, continues to work as before
- Firmware 2.xx: Full support with all features enabled
- Automatic detection prevents manual configuration

## 0.8.1 - Timer Minimum Value Fix (2026-01-05)

### Fixed
- Fixed boost and overpressure timer minimum value from 0 to -1
- Timers now correctly display -1 when inactive (per Modbus register specification)
- Allows proper display of timer state: -1 = inactive/not running, 0+ = active with remaining minutes

### Technical
- Updated ParmairTimerNumber class minimum value to match BOOST_TIMER_FM and OVERP_TIMER_FM register specs
- Modbus registers define valid range: -1 to 300 minutes

## 0.8.0 - Device Info Label Clarification (2026-01-05)

### Changed
- Device info displays software version (label shown as "Software" or "Firmware" depending on Home Assistant version)
- Clarified that sw_version field contains software version from device

### Note
- The integration provides software version data via standard Home Assistant `sw_version` field
- Home Assistant UI controls the display label (may show as "Firmware" or "Software")
- The value (e.g., "1.83") correctly represents the device's software version

## 0.7.7.3 - Syntax Fix (2026-01-05)

### Fixed
- **Fixed syntax error in config_flow.py**
- Corrected indentation in heater type detection retry logic
- Result checking code was incorrectly placed outside try block
- Import error resolved

## 0.7.7.2 - Documentation Cleanup (2026-01-05)

### Changed
- **Removed Modbus register addresses from all public documentation**
- Cleaned up CHANGELOG.md to remove technical register numbers
- README.md already clean (no register addresses)
- Register addresses remain in const.py for technical reference

### Rationale
- User-facing documentation should be clean and non-technical
- Register addresses are implementation details
- Improves readability for end users
- Technical details preserved in code comments

### Technical
- No code changes
- Documentation-only update
- Register addresses still defined in const.py

## 0.7.7.1 - Make Current Speed Sensor Numeric (2026-01-05)

### Changed
- **Current Speed sensor now shows numeric values** (0-5) instead of text
- Removed ENUM device class - now plain numeric sensor
- Added description in sensor attributes: "0=Stop, 1=Speed 1, 2=Speed 2, 3=Speed 3, 4=Speed 4, 5=Speed 5"
- Added fan icon (mdi:fan)

### Technical
- Removed STATE_MAP from ParmairSpeedControlSensor
- Changed native_value return type from str to int
- Removed _attr_device_class and _attr_options
- Added extra_state_attributes with speed description

### Display
**Before:** Shows "Stop", "Speed 1", "Speed 2", etc.
**After:** Shows 0, 1, 2, 3, 4, 5 (numeric values)

## 0.7.7 - Improved Auto-Detection with Retry Logic (2026-01-05)

### Changed
- **Auto-detection now retries up to 3 times** with increasing delays (150ms, 350ms, 550ms)
- **Removed manual configuration step** - No longer prompts user to select software version or heater type
- **Uses smart defaults if detection fails** - Defaults to v1.x and no heater if all retries fail
- Detection is more reliable with longer delays between attempts

### Technical
- Added retry loop for software version detection (3 attempts with delays)
- Added retry loop for heater type detection (3 attempts with delays)
- Initial delay increased from 100ms to 150ms for device stabilization
- Retry delays: attempt 2 = 200ms, attempt 3 = 400ms
- Logs show which attempt succeeded or if defaults were used
- Removed async_step_manual_config method entirely
- Detection failures now use defaults: SOFTWARE_VERSION_1, HEATER_TYPE_NONE

### User Experience
- Configuration flow is now fully automatic
- No manual selection prompts
- Slightly longer wait during setup (up to ~1 second if retries needed)
- Integration will always succeed with detected or sensible default values

## 0.7.6 - Use Real Speed Sensor (2026-01-05)

### Changed
- **Speed sensor now shows actual running speed** - Changed from control setting to real speed
- Renamed "Speed Control" sensor to "Current Speed"
- Sensor now reads from actual speed register instead of control register
- Removed "Auto" from speed options (actual speed doesn't have auto mode)
- Speed values: Stop, Speed 1, Speed 2, Speed 3, Speed 4, Speed 5

### Technical
- Added REG_ACTUAL_SPEED constant for actual speed monitoring
- REG_SPEED_CONTROL still used for Manual Speed Control number entity
- Updated ParmairSpeedControlSensor to use actual_speed data key
- Updated STATE_MAP to values 0-5 (Stop, Speed 1-5)
- Added REG_ACTUAL_SPEED to polling registers

### What Changed
**Before:** Speed Control sensor showed the *control setting* (Auto/Stop/Speed 1-5)
**After:** Current Speed sensor shows the *actual running speed* (Stop/Speed 1-5)

**Manual Speed Control number entity** still uses control register for setting the desired speed.

## 0.7.5.1 - Remove Heater Type Control (2026-01-05)

### Removed
- **Heater Type select control** - Removed ability to change heater type via UI
- Heater type is a hardware configuration and should not be changed during runtime

### Kept
- **Heater Type diagnostic sensor** - Still shows current heater configuration (read-only)
- Sensor continues to display Water/Electric/None

### Technical
- Removed ParmairHeaterTypeSelect class from select.py
- Removed REG_HEATER_TYPE from select platform imports
- Select platform now returns empty entity list
- Heater type remains in polling registers for sensor display

## 0.7.5 - Add Heater Type Sensor and Fix Values (2026-01-05)

### Added
- **Heater Type sensor** - Shows current heater configuration (Water/Electric/None)
- Heater type displayed as diagnostic sensor in device info

### Fixed
- **Corrected heater type values** - Fixed mapping to match hardware documentation:
  - 0 = Water heater (was: None)
  - 1 = Electric heater (was: Water)
  - 2 = None/No heater (was: Electric)
- Added REG_HEATER_TYPE to polling registers for real-time updates

### Technical
- Added ParmairHeaterTypeSensor class with ENUM device class
- Updated HEATER_TYPE constants to match hardware documentation
- Heater type values now correctly reflect hardware configuration
- Sensor marked as EntityCategory.DIAGNOSTIC

## 0.7.4.3 - Fix Auto-Detection During Configuration (2026-01-05)

### Fixed
- **Auto-detection now validates Modbus responses** - Checks `result.isError()` before extracting values
- **Added connection stabilization delay** - 100ms delay after connection before reading registers
- **Better error logging** - Clearer warnings when detection fails
- **Software version detection working** - Now properly detects v1.x vs v2.x during initial setup
- **Heater type detection working** - Now properly detects None/Water/Electric during setup

### Technical
- Added `time.sleep(0.1)` after Modbus connection
- Added validation: `if result and not result.isError()` before extracting register values
- Improved error handling in `_detect_device_info()`
- Detection failures now properly logged with specific error messages

### Why Detection Failed Before
1. No validation of Modbus read success - code tried to extract values from failed reads
2. No delay after connection - device needed time to stabilize
3. Invalid responses were silently processed, returning garbage values

## 0.7.4.2 - Fix Device Info Display (2026-01-04)

### Fixed
- **Device model now shows MAC type** - Shows "MAC 80", "MAC 100", or "MAC 150" based on hardware type
- **Added hardware type polling** - Reads hardware type to determine MAC model
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
- Reads/writes speed control register
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
- Reads timer registers for boost and overpressure modes
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
- Added REG_BOOST_TIME_SETTING for boost time presets
- Added REG_OVERPRESSURE_TIME_SETTING for overpressure time presets
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
- Removed firmware version register from code
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
