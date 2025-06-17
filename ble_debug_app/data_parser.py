import struct
from typing import Optional, Union, Dict
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
    """Parser for BLE characteristic data"""
    
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
        values = struct.unpack('<9h', data)
        return (
            f"IMU Raw Data:\n"
            f"  Accel (mg): X={values[0]}, Y={values[1]}, Z={values[2]}\n"
            f"  Gyro (0.01 rad/s): X={values[3]}, Y={values[4]}, Z={values[5]}\n"
            f"  Mag (uT): X={values[6]}, Y={values[7]}, Z={values[8]}"
        )

    def _parse_imu_euler(self, data: bytes) -> str:
        euler = struct.unpack('<3f', data[0:12])
        calib = data[12]
        return (
            f"IMU Euler Data:\n"
            f"  Yaw (deg): {euler[0]:.2f}\n"
            f"  Pitch (deg): {euler[1]:.2f}\n"
            f"  Roll (deg): {euler[2]:.2f}\n"
            f"  Calibration Status: {calib}"
        )

    def _parse_config(self, data: bytes) -> str:
        cmd = data[0]
        cmd_str = self._cmd_map.get(cmd, f"Unknown ({cmd})")

        def get_imu_config(idx_start: int) -> Dict[str, str]:
            return {
                "ag_freq": self.config.get_imu_config("accel_gyro_freq", data[idx_start]),
                "mag_freq": self.config.get_imu_config("mag_freq", data[idx_start + 1]),
                "accel": self.config.get_imu_config("accel_range", data[idx_start + 4]),
                "gyro": self.config.get_imu_config("gyro_range", data[idx_start + 5]),
                "mag": self.config.get_imu_config("mag_range", data[idx_start + 6])
            }

        imu1 = get_imu_config(1)
        imu2 = get_imu_config(3)
        update_rate = struct.unpack('<H', data[11:13])[0]

        return (
            f"Configuration Data:\n"
            f"Command State: {cmd_str}\n\n"
            f"IMU1 Configuration:\n"
            f"  Frequencies:\n"
            f"    Accelerometer & Gyroscope: {imu1['ag_freq']}\n"
            f"    Magnetometer: {imu1['mag_freq']}\n"
            f"  Ranges:\n"
            f"    Accelerometer: ±{imu1['accel']}\n"
            f"    Gyroscope: ±{imu1['gyro']}\n"
            f"    Magnetometer: ±{imu1['mag']}\n\n"
            f"IMU2 Configuration:\n"
            f"  Frequencies:\n"
            f"    Accelerometer & Gyroscope: {imu2['ag_freq']}\n"
            f"    Magnetometer: {imu2['mag_freq']}\n"
            f"  Ranges:\n"
            f"    Accelerometer: ±{imu2['accel']}\n"
            f"    Gyroscope: ±{imu2['gyro']}\n"
            f"    Magnetometer: ±{imu2['mag']}\n\n"
            f"Sensor Update Rate: {update_rate} ms"
        )

    def _parse_flex_sensor(self, data: bytes) -> str:
        values = struct.unpack('<5f', data)
        return "\n".join([
            "Flex Sensor Data (KOhm):",
            *(f"  Sensor {i+1}: {v:.2f}" for i, v in enumerate(values))
        ])

    def _parse_joystick(self, data: bytes) -> str:
        x, y = struct.unpack('<hh', data[0:4])
        button = data[4]
        return (
            f"Joystick Data:\n"
            f"  X axis: {x}\n"
            f"  Y axis: {y}\n"
            f"  Button: {'Pressed' if button == 1 else 'Not Pressed'}"
        )

    def _parse_overall_status(self, data: bytes) -> str:
        error = "No Error" if data[0] == 0 else "General Error"
        return (
            f"Overall Status:\n"
            f"  Status Code: {data[0]} ({error})\n"
            f"  Fuelgauge: {self._status_map.get(data[1], 'Unknown')}\n"
            f"  IMU1: {self._status_map.get(data[2], 'Unknown')}\n"
            f"  IMU2: {self._status_map.get(data[3], 'Unknown')}"
        )

    def _parse_buttons(self, data: bytes) -> str:
        return "\n".join([
            "Button States:",
            *(f"  Button {i+1}: {'Pressed' if state else 'Not Pressed'}"
              for i, state in enumerate(data))
        ])

    def _parse_force_sensor(self, data: bytes) -> str:
        force = struct.unpack('<f', data)[0]
        return f"Force Sensor: {force:.2f} kOhm"

    def _parse_battery(self, data: bytes) -> str:
        level = data[0]
        icon = "🔋" if level > 20 else "🪫"
        return f"Battery Level: {icon} {level}%"

    def _parse_charging(self, data: bytes) -> str:
        return f"Charging State: {self._charging_map.get(data[0], 'Unknown State')}"

    def _parse_device_info(self, data: bytes, uuid: str) -> str:
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
        hex_part = ' '.join(f'{b:02x}' for b in data)
        ascii_part = ''.join(chr(b) if 0x20 <= b <= 0x7E else '.' for b in data)
        return f"Data (Hex): {hex_part}\nASCII: {ascii_part}"