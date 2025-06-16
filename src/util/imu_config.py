from src.config.constant import BLEConstants


class IMUConfigUtil:
    # Byte positions in config array
    IMU1_ACCEL_GYRO_FREQ_POS = 1
    IMU1_MAG_FREQ_POS = 2
    IMU2_ACCEL_GYRO_FREQ_POS = 3
    IMU2_MAG_FREQ_POS = 4
    IMU1_ACCEL_RANGE_POS = 5
    IMU1_GYRO_RANGE_POS = 6
    IMU1_MAG_RANGE_POS = 7
    IMU2_ACCEL_RANGE_POS = 8
    IMU2_GYRO_RANGE_POS = 9
    IMU2_MAG_RANGE_POS = 10

    @staticmethod
    def get_imu_config_positions(imu_number: int) -> dict:
        """Get byte positions for IMU configuration parameters.

        Args:
            imu_number: IMU number (1 or 2)

        Returns:
            Dictionary containing byte positions for the IMU config
        """
        if imu_number == 1:
            return {
                "accel_gyro_freq": IMUConfigUtil.IMU1_ACCEL_GYRO_FREQ_POS,
                "mag_freq": IMUConfigUtil.IMU1_MAG_FREQ_POS,
                "accel_range": IMUConfigUtil.IMU1_ACCEL_RANGE_POS,
                "gyro_range": IMUConfigUtil.IMU1_GYRO_RANGE_POS,
                "mag_range": IMUConfigUtil.IMU1_MAG_RANGE_POS,
            }
        elif imu_number == 2:
            return {
                "accel_gyro_freq": IMUConfigUtil.IMU2_ACCEL_GYRO_FREQ_POS,
                "mag_freq": IMUConfigUtil.IMU2_MAG_FREQ_POS,
                "accel_range": IMUConfigUtil.IMU2_ACCEL_RANGE_POS,
                "gyro_range": IMUConfigUtil.IMU2_GYRO_RANGE_POS,
                "mag_range": IMUConfigUtil.IMU2_MAG_RANGE_POS,
            }
        else:
            raise ValueError("IMU number must be 1 or 2")

    @staticmethod
    def get_config_from_bytes(data: bytearray, imu_number: int) -> dict:
        """Extract IMU configuration values from config bytes.

        Args:
            data: Configuration byte array
            imu_number: IMU number (1 or 2)

        Returns:
            Dictionary containing configuration values
        """
        positions = IMUConfigUtil.get_imu_config_positions(imu_number)

        return {
            "accel_gyro_rate": BLEConstants.ACCEL_GYRO_FREQ_MAP[
                data[positions["accel_gyro_freq"]]
            ],
            "mag_rate": BLEConstants.MAG_FREQ_MAP[data[positions["mag_freq"]]],
            "accel_range": BLEConstants.ACCEL_RANGE_MAP[data[positions["accel_range"]]],
            "gyro_range": BLEConstants.GYRO_RANGE_MAP[data[positions["gyro_range"]]],
            "mag_range": BLEConstants.MAG_RANGE_MAP[data[positions["mag_range"]]],
        }

    @staticmethod
    def update_config_bytes(
        data: bytearray, imu_number: int, config: dict
    ) -> bytearray:
        """Update configuration byte array with new IMU config values.

        Args:
            data: Original configuration byte array
            imu_number: IMU number (1 or 2)
            config: Dictionary containing new configuration values

        Returns:
            Updated configuration byte array
        """
        positions = IMUConfigUtil.get_imu_config_positions(imu_number)
        new_config = bytearray(data)

        # Update config bytes with new values
        new_config[positions["accel_gyro_freq"]] = BLEConstants.ACCEL_GYRO_FREQ_REV_MAP[
            config["accel_gyro_rate"]
        ]
        new_config[positions["mag_freq"]] = BLEConstants.MAG_FREQ_REV_MAP[
            config["mag_rate"]
        ]
        new_config[positions["accel_range"]] = BLEConstants.ACCEL_RANGE_REV_MAP[
            config["accel_range"]
        ]
        new_config[positions["gyro_range"]] = BLEConstants.GYRO_RANGE_REV_MAP[
            config["gyro_range"]
        ]
        new_config[positions["mag_range"]] = BLEConstants.MAG_RANGE_REV_MAP[
            config["mag_range"]
        ]

        return new_config
