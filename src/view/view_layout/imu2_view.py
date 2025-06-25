from src.util.imu_config import IMUConfigUtil
from src.view.view_dialog import IMUCalibrationDialog, IMUConfigDialog
from src.view.view_layout.base_imu_view import BaseIMUView
import asyncio


class IMU2View(BaseIMUView):
    def __init__(self, parent):
        super().__init__(parent, "IMU2")

    async def _on_config(self):
        """Handle IMU2 configuration button click"""
        # Add small delay to ensure BLE characteristic is ready
        await asyncio.sleep(0.1)
        
        # Read current config with retry
        retries = 2
        data = None
        for _ in range(retries):
            data = await self.imu_service.read_config()
            if data:
                break
            await asyncio.sleep(0.1)
        dialog = IMUConfigDialog(self, "IMU2")
        if data:
            # Set dialog values from config using utility
            # Set dialog values from config using utility
            config = IMUConfigUtil.get_config_from_bytes(data, 2)
            dialog.set_config_values(config)

        dialog.set_cancel_callback(dialog.destroy)
        dialog.set_apply_callback(
            lambda config: self.loop.create_task(
                self._handle_config_apply(dialog, config)
            )
        )

    async def _handle_config_apply(self, dialog, config):
        """Handle IMU2 configuration dialog apply button click"""
        # Read current config to preserve other bytes
        data = await self.imu_service.read_config()
        if data:
            # Update config bytes using utility
            new_config = IMUConfigUtil.update_config_bytes(data, 2, config)

            # Write updated config
            await self.imu_service.write_config(new_config)

        # Destroy dialog after writing config
        dialog.destroy()

    def _on_calibrate(self):
        """Handle IMU2 calibration button click"""
        dialog = IMUCalibrationDialog(self, "IMU2", self.imu_service)
        dialog.set_cancel_callback(dialog.destroy)
        dialog.set_start_callback(lambda: self._handle_calibration_start(dialog))
