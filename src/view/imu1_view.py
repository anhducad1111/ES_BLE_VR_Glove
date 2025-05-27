from src.view.base_imu_view import BaseIMUView
from src.view.imu_config_dialog import IMUConfigDialog
from src.view.imu_calibration_dialog import IMUCalibrationDialog

class IMU1View(BaseIMUView):
    def __init__(self, parent):
        super().__init__(parent, "IMU1")

    def _on_config(self):
        """Handle IMU1 configuration button click"""
        dialog = IMUConfigDialog(self, "IMU1")
        dialog.set_cancel_callback(dialog.destroy)
        dialog.set_apply_callback(lambda: self._handle_config_apply(dialog))

    def _on_calibrate(self):
        """Handle IMU1 calibration button click"""
        dialog = IMUCalibrationDialog(self, "IMU1")
        dialog.set_cancel_callback(dialog.destroy)
        dialog.set_start_callback(lambda: self._handle_calibration_start(dialog))
