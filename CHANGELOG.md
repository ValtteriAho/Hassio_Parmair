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
