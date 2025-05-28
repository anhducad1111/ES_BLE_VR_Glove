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
        dialog.set_apply_callback(lambda: self._handle_config_apply(dialog))

    def _on_calibrate(self):
        """Handle IMU1 calibration button click"""
        dialog = IMUCalibrationDialog(self, "IMU1")
        dialog.set_cancel_callback(dialog.destroy)
        dialog.set_start_callback(lambda: self._handle_calibration_start(dialog))
