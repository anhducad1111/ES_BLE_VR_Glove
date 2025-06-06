import json
import os
from pathlib import Path

from src.model.imu import IMUData, IMUEulerData
from src.model.timestamp import TimestampData
from src.model.sensor import FlexSensorData, ForceSensorData
from src.model.gamepad import JoystickData, ButtonsData
from src.model.overall_status import OverallStatus

# Load GATT data from JSON file
gatt_path = Path(__file__).parent.parent.parent / 'gatt.json'
with open(gatt_path, 'r') as f:
    gatt_data = json.load(f)

class BLEConstants:
    # Required BLE services
    REQUIRED_SERVICES = gatt_data['required_services']
    
    # IMU Config mappings
    ACCEL_GYRO_FREQ_MAP = {int(k): v for k, v in gatt_data['imu_config']['accel_gyro_freq'].items()}
    MAG_FREQ_MAP = {int(k): v for k, v in gatt_data['imu_config']['mag_freq'].items()}
    ACCEL_RANGE_MAP = {int(k): v for k, v in gatt_data['imu_config']['accel_range'].items()}
    GYRO_RANGE_MAP = {int(k): v for k, v in gatt_data['imu_config']['gyro_range'].items()}
    MAG_RANGE_MAP = {int(k): v for k, v in gatt_data['imu_config']['mag_range'].items()}

    # Reverse maps for config writing
    ACCEL_GYRO_FREQ_REV_MAP = {v: k for k, v in ACCEL_GYRO_FREQ_MAP.items()}
    MAG_FREQ_REV_MAP = {v: k for k, v in MAG_FREQ_MAP.items()}
    ACCEL_RANGE_REV_MAP = {v: k for k, v in ACCEL_RANGE_MAP.items()}
    GYRO_RANGE_REV_MAP = {v: k for k, v in GYRO_RANGE_MAP.items()}
    MAG_RANGE_REV_MAP = {v: k for k, v in MAG_RANGE_MAP.items()}

    # Device UUIDs mapping
    char_data = gatt_data['characteristics']
    CHARACTERISTICS = {
        # Standard UUIDs
        "FIRMWARE_UUID": (char_data["FIRMWARE_UUID"], str),
        "MODEL_NUMBER_UUID": (char_data["MODEL_NUMBER_UUID"], str),
        "MANUFACTURER_UUID": (char_data["MANUFACTURER_UUID"], str),
        "HARDWARE_UUID": (char_data["HARDWARE_UUID"], str),

        # Battery UUIDs
        "BATTERY_LEVEL_UUID": (char_data["BATTERY_LEVEL_UUID"], None),
        "BATTERY_CHARGING_UUID": (char_data["BATTERY_CHARGING_UUID"], None),

        # Configuration UUID
        "CONFIG_UUID": (char_data["CONFIG_UUID"], None),

        # Device UUIDs
        "IMU1_CHAR_UUID": (char_data["IMU1_CHAR_UUID"], IMUData),
        "IMU2_CHAR_UUID": (char_data["IMU2_CHAR_UUID"], IMUData),
        "IMU1_EULER_UUID": (char_data["IMU1_EULER_UUID"], IMUEulerData),
        "IMU2_EULER_UUID": (char_data["IMU2_EULER_UUID"], IMUEulerData),
        "TIMESTAMP_CHAR_UUID": (char_data["TIMESTAMP_CHAR_UUID"], TimestampData),
        "OVERALL_STATUS_UUID": (char_data["OVERALL_STATUS_UUID"], OverallStatus),
        "FLEX_SENSOR_UUID": (char_data["FLEX_SENSOR_UUID"], FlexSensorData),
        "FORCE_SENSOR_UUID": (char_data["FORCE_SENSOR_UUID"], ForceSensorData),
        "JOYSTICK_UUID": (char_data["JOYSTICK_UUID"], JoystickData),
        "BUTTONS_UUID": (char_data["BUTTONS_UUID"], ButtonsData)
    }

