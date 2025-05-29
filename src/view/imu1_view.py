from src.view.base_imu_view import BaseIMUView
from src.view.imu_config_dialog import IMUConfigDialog
from src.view.imu_calibration_dialog import IMUCalibrationDialog

class IMU1View(BaseIMUView):
    def __init__(self, parent):
        super().__init__(parent, "IMU1")

    async def _on_config(self):
        """Handle IMU1 configuration button click"""
        # Read current config
        data = await self.imu_service.read_config()
        dialog = IMUConfigDialog(self, "IMU1")
        
        if data:
            # Set dialog values from IMU1 config bytes
            dialog.accel_gyro_rate_item.set(self.imu_service.ACCEL_GYRO_FREQ_MAP[data[1]])  # IMU1 accel/gyro freq
            dialog.mag_rate_item.set(self.imu_service.MAG_FREQ_MAP[data[2]])  # IMU1 mag freq
            dialog.accel_range_item.set(self.imu_service.ACCEL_RANGE_MAP[data[5]])  # IMU1 accel range
            dialog.gyro_range_item.set(self.imu_service.GYRO_RANGE_MAP[data[6]])  # IMU1 gyro range
            dialog.mag_range_item.set(self.imu_service.MAG_RANGE_MAP[data[7]])  # IMU1 mag range

        dialog.set_cancel_callback(dialog.destroy)
        dialog.set_apply_callback(lambda config: self.loop.create_task(self._handle_config_apply(dialog, config)))

    async def _handle_config_apply(self, dialog, config):
        """Handle IMU1 configuration dialog apply button click"""
        # Read current config to preserve other bytes
        data = await self.imu_service.read_config()
        if data:
            # Create new config array with current config
            new_config = bytearray(data)
            # Update IMU1 config bytes (1,2,5,6,7)
            new_config[1] = self.imu_service.ACCEL_GYRO_FREQ_REV_MAP[config['accel_gyro_rate']]
            new_config[2] = self.imu_service.MAG_FREQ_REV_MAP[config['mag_rate']]  
            new_config[5] = self.imu_service.ACCEL_RANGE_REV_MAP[config['accel_range']]
            new_config[6] = self.imu_service.GYRO_RANGE_REV_MAP[config['gyro_range']]
            new_config[7] = self.imu_service.MAG_RANGE_REV_MAP[config['mag_range']]

            # Write updated config 
            await self.imu_service.write_config(new_config)

        # Destroy dialog after writing config
        dialog.destroy()

    def _on_calibrate(self):
        """Handle IMU1 calibration button click"""
        dialog = IMUCalibrationDialog(self, "IMU1", self.imu_service)
        dialog.set_cancel_callback(dialog.destroy)
        dialog.set_start_callback(lambda: self._handle_calibration_start(dialog))
