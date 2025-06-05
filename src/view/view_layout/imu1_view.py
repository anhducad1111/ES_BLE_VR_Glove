from src.view.view_layout.base_imu_view import BaseIMUView
from src.view.view_dialog.imu_config_dialog import IMUConfigDialog
from src.view.view_dialog.imu_calibration_dialog import IMUCalibrationDialog
from src.util.imu_config import IMUConfigUtil

class IMU1View(BaseIMUView):
    def __init__(self, parent):
        super().__init__(parent, "IMU1")

    async def _on_config(self):
        """Handle IMU1 configuration button click"""
        # Read current config
        data = await self.imu_service.read_config()
        dialog = IMUConfigDialog(self, "IMU1")
        
        if data:
            # Set dialog values from config using utility
            config = IMUConfigUtil.get_config_from_bytes(data, 1)
            dialog.set_config_values(config)

        dialog.set_cancel_callback(dialog.destroy)
        dialog.set_apply_callback(lambda config: self.loop.create_task(self._handle_config_apply(dialog, config)))

    async def _handle_config_apply(self, dialog, config):
        """Handle IMU1 configuration dialog apply button click"""
        # Read current config to preserve other bytes
        data = await self.imu_service.read_config()
        if data:
            # Update config bytes using utility
            new_config = IMUConfigUtil.update_config_bytes(data, 1, config)

            # Write updated config 
            await self.imu_service.write_config(new_config)

        # Destroy dialog after writing config
        dialog.destroy()

    def _on_calibrate(self):
        """Handle IMU1 calibration button click"""
        dialog = IMUCalibrationDialog(self, "IMU1", self.imu_service)
        dialog.set_cancel_callback(dialog.destroy)
        dialog.set_start_callback(lambda: self._handle_calibration_start(dialog))
