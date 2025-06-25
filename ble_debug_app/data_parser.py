import struct
from typing import Optional, Union, Dict, Any
from .ble_config import BLEConfig

class DataType:
    """Data type constants"""
    IMU_RAW = "imu_raw"
    IMU_EULER = "imu_euler" 
    CONFIG = "config"
    FLEX_SENSOR = "flex_sensor"
    JOYSTICK = "joystick"
    BATTERY = "battery"
    CHARGING = "charging"
    DEVICE_INFO = "device_info"
    OVERALL_STATUS = "overall_status"
    BUTTONS = "buttons"
    FORCE_SENSOR = "force_sensor"
    UNKNOWN = "unknown"

class DataParser:
    """Parser for BLE characteristic data with validation"""
    
    def __init__(self, config: BLEConfig):
        self.config = config
        
        # Component status strings
        self._status_map = {
            0: "Not Detected",
            1: "Failed", 
            2: "Idle",
            3: "Running"
        }
        
        # Command strings
        self._cmd_map = {
            0: "IDLE",
            1: "RUN",
            2: "Start calibration IMU 1", 
            3: "Start calibration IMU 2"
        }
        
        # Battery charging states
        self._charging_map = {
            0: "🔌 Not Charging",
            1: "⚡ Charging",
            2: "✅ Fully Charged"
        }

        # IMU configuration limits
        self.imu_limits = {
            "accel_gyro_freq": {
                "min": 10,    # Hz
                "max": 1000   # Hz
            },
            "mag_freq": {
                "min": 10,    # Hz
                "max": 100    # Hz
            },
            "accel_range": {
                "min": 2,     # g
                "max": 16     # g
            },
            "gyro_range": {
                "min": 125,   # dps
                "max": 2000   # dps
            },
            "mag_range": {
                "min": 4,     # gauss
                "max": 16     # gauss
            }
        }
        
    def identify_data_type(self, data: bytes, uuid: str = "") -> str:
        """Identify data type based on length and content"""
        if not data:
            return DataType.UNKNOWN
            
        length = len(data)
        
        # Check data type based on length
        if length == 18:
            return DataType.IMU_RAW
        elif length == 13:
            return DataType.IMU_EULER
        elif length == 15:
            return DataType.CONFIG
        elif length == 20:
            return DataType.FLEX_SENSOR
        elif length == 5:
            return DataType.JOYSTICK
        elif length == 4:
            if all(x <= 3 for x in data):
                return DataType.OVERALL_STATUS if max(data) > 1 else DataType.BUTTONS
            return DataType.FORCE_SENSOR
        elif length == 1:
            return DataType.BATTERY if data[0] <= 100 else DataType.CHARGING
        elif 1 <= length <= 12:
            return DataType.DEVICE_INFO
            
        return DataType.UNKNOWN

    def parse_data(self, data: bytes, uuid: str = "") -> str:
        """Parse BLE data based on data type"""
        data_type = self.identify_data_type(data, uuid)
        
        try:
            if data_type == DataType.IMU_RAW:
                return self._parse_imu_raw(data)
            elif data_type == DataType.IMU_EULER:
                return self._parse_imu_euler(data)
            elif data_type == DataType.CONFIG:
                return self._parse_config(data)
            elif data_type == DataType.FLEX_SENSOR:
                return self._parse_flex_sensor(data)
            elif data_type == DataType.JOYSTICK:
                return self._parse_joystick(data)
            elif data_type == DataType.OVERALL_STATUS:
                return self._parse_overall_status(data)
            elif data_type == DataType.BUTTONS:
                return self._parse_buttons(data)
            elif data_type == DataType.FORCE_SENSOR:
                return self._parse_force_sensor(data)
            elif data_type == DataType.BATTERY:
                return self._parse_battery(data)
            elif data_type == DataType.CHARGING:
                return self._parse_charging(data)
            elif data_type == DataType.DEVICE_INFO:
                return self._parse_device_info(data, uuid)
            else:
                return self._format_raw_data(data)
                
        except Exception as e:
            return f"Parse error: {e}"

    def _parse_imu_raw(self, data: bytes) -> str:
        """Parse raw IMU data with validation"""
        values = struct.unpack('<9h', data)
        result = (
            f"IMU Raw Data:\n"
            f"  Accel (mg): X={values[0]}, Y={values[1]}, Z={values[2]}\n"
            f"  Gyro (0.01 rad/s): X={values[3]}, Y={values[4]}, Z={values[5]}\n"
            f"  Mag (uT): X={values[6]}, Y={values[7]}, Z={values[8]}"
        )
        
        # Validate against typical ranges
        accel_range = max(abs(x) for x in values[0:3])
        gyro_range = max(abs(x) for x in values[3:6])
        mag_range = max(abs(x) for x in values[6:9])
        
        if accel_range > 16000:  # 16g in mg
            result += "\nWARNING: Accelerometer values exceed typical range"
        if gyro_range > 2000:    # 2000 dps
            result += "\nWARNING: Gyroscope values exceed typical range"
        if mag_range > 4800:     # 4.8 gauss in uT
            result += "\nWARNING: Magnetometer values exceed typical range"
            
        return result

    def _parse_imu_euler(self, data: bytes) -> str:
        """Parse IMU Euler angles with validation"""
        euler = struct.unpack('<3f', data[0:12])
        calib = data[12]
        result = (
            f"IMU Euler Data:\n"
            f"  Yaw (deg): {euler[0]:.2f}\n"
            f"  Pitch (deg): {euler[1]:.2f}\n"
            f"  Roll (deg): {euler[2]:.2f}\n"
            f"  Calibration Status: {calib}"
        )
        
        # Validate angle ranges
        if not all(-180 <= angle <= 180 for angle in euler):
            result += "\nWARNING: Euler angles outside valid range (-180° to 180°)"
            
        return result

    def parse_imu_config(self, data: bytes) -> Optional[Dict[str, Any]]:
        """Parse IMU configuration data"""
        if len(data) != 15:
            return None
            
        cmd = data[0]
        config = {
            "command": self._cmd_map.get(cmd, f"Unknown ({cmd})"),
            "accel_gyro_freq": data[1],
            "mag_freq": data[2],
            "accel_range": data[5],
            "gyro_range": data[6],
            "mag_range": data[7],
            "update_rate": struct.unpack('<H', data[11:13])[0]
        }
        
        # Validate configuration
        warnings = []
        for param, value in config.items():
            if param in self.imu_limits:
                limits = self.imu_limits[param]
                if not limits["min"] <= value <= limits["max"]:
                    warnings.append(
                        f"{param} value {value} outside valid range "
                        f"({limits['min']} - {limits['max']})"
                    )
        
        if warnings:
            config["warnings"] = warnings
            
        return config

    def _parse_config(self, data: bytes) -> str:
        """Parse configuration data"""
        config = self.parse_imu_config(data)
        if not config:
            return "Invalid configuration data"
            
        result = f"Configuration Data:\n"
        result += f"Command State: {config['command']}\n\n"
        
        for imu in range(1, 3):
            result += f"IMU{imu} Configuration:\n"
            result += "  Frequencies:\n"
            result += f"    Accelerometer & Gyroscope: {config['accel_gyro_freq']} Hz\n"
            result += f"    Magnetometer: {config['mag_freq']} Hz\n"
            result += "  Ranges:\n"
            result += f"    Accelerometer: ±{config['accel_range']}g\n"
            result += f"    Gyroscope: ±{config['gyro_range']} dps\n"
            result += f"    Magnetometer: ±{config['mag_range']} gauss\n\n"
            
        result += f"Sensor Update Rate: {config['update_rate']} ms"
        
        if "warnings" in config:
            result += "\n\nConfiguration Warnings:\n"
            for warning in config["warnings"]:
                result += f"- {warning}\n"
                
        return result

    def _parse_flex_sensor(self, data: bytes) -> str:
        """Parse flex sensor data with validation"""
        values = struct.unpack('<5f', data)
        result = "Flex Sensor Data (KOhm):\n"
        
        for i, v in enumerate(values):
            result += f"  Sensor {i+1}: {v:.2f}"
            
            # Validate sensor range (typical range 10-110 KOhm)
            if not 10 <= v <= 110:
                result += " (WARNING: Outside typical range)"
            result += "\n"
            
        return result

    def _parse_joystick(self, data: bytes) -> str:
        """Parse joystick data with validation"""
        x, y = struct.unpack('<hh', data[0:4])
        button = data[4]
        result = (
            f"Joystick Data:\n"
            f"  X axis: {x}\n"
            f"  Y axis: {y}\n"
            f"  Button: {'Pressed' if button == 1 else 'Not Pressed'}"
        )
        
        # Validate range (0-4095)
        if not (0 <= x <= 4095 and 0 <= y <= 4095):
            result += "\nWARNING: Values outside valid range (0-4095)"
            
        # Check center position (±1.5%)
        center_range = 4095 * 0.015  # 1.5%
        if abs(x - 2047) <= center_range and abs(y - 2047) <= center_range:
            result += "\nJoystick in center position"
            
        return result

    def _parse_overall_status(self, data: bytes) -> str:
        """Parse overall status with validation"""
        error = "No Error" if data[0] == 0 else "General Error"
        return (
            f"Overall Status:\n"
            f"  Status Code: {data[0]} ({error})\n"
            f"  Fuelgauge: {self._status_map.get(data[1], 'Unknown')}\n"
            f"  IMU1: {self._status_map.get(data[2], 'Unknown')}\n"
            f"  IMU2: {self._status_map.get(data[3], 'Unknown')}"
        )

    def _parse_buttons(self, data: bytes) -> str:
        """Parse button states"""
        return "\n".join([
            "Button States:",
            *(f"  Button {i+1}: {'Pressed' if state else 'Not Pressed'}"
              for i, state in enumerate(data))
        ])

    def _parse_force_sensor(self, data: bytes) -> str:
        """Parse force sensor data"""
        force = struct.unpack('<f', data)[0]
        return f"Force Sensor: {force:.2f} kOhm"

    def _parse_battery(self, data: bytes) -> str:
        """Parse battery level with validation"""
        level = data[0]
        icon = "🔋" if level > 20 else "🪫"
        result = f"Battery Level: {icon} {level}%"
        
        # Add warning for low battery
        if level <= 20:
            result += "\nWARNING: Low battery"
            
        return result

    def _parse_charging(self, data: bytes) -> str:
        """Parse charging state"""
        return f"Charging State: {self._charging_map.get(data[0], 'Unknown State')}"

    def _parse_device_info(self, data: bytes, uuid: str) -> str:
        """Parse device information"""
        try:
            text = data.decode('utf-8')
            if len(data) == 9:  # Version
                if uuid == self.config.get_characteristic_uuid("FIRMWARE_UUID"):
                    return f"Firmware Version: {text}"
                elif uuid == self.config.get_characteristic_uuid("HARDWARE_UUID"):
                    return f"Hardware Version: {text}"
                return f"Version: {text}"
            elif len(data) == 12:  # Model/Manufacturer
                if text == "DegapVrGlove":
                    return f"Model: {text}"
                elif text == "NUS/Seamless":
                    return f"Manufacturer: {text}"
            return f"Device Info: {text}"
        except:
            return self._format_raw_data(data)

    def _format_raw_data(self, data: bytes) -> str:
        """Format raw data in hex and ASCII"""
        hex_part = ' '.join(f'{b:02x}' for b in data)
        ascii_part = ''.join(chr(b) if 0x20 <= b <= 0x7E else '.' for b in data)
        return f"Data (Hex): {hex_part}\nASCII: {ascii_part}"