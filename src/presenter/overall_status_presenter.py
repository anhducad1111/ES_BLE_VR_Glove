import asyncio

from src.model.overall_status import OverallStatus


class OverallStatusPresenter:
    """Presenter class for handling overall status updates"""

    def __init__(
        self, view, esp32_service, imu1_presenter, imu2_presenter, sensor_presenter
    ):
        """Initialize the presenter

        Args:
            view: Reference to the overall status view
            esp32_service: Reference to the ESP32 BLE service
            imu1_presenter: Reference to IMU1 presenter
            imu2_presenter: Reference to IMU2 presenter
            sensor_presenter: Reference to sensor presenter
        """
        self.view = view
        self.esp32_service = esp32_service
        self.imu1_presenter = imu1_presenter
        self.imu2_presenter = imu2_presenter
        self.sensor_presenter = sensor_presenter
        self._current_status = None

        # Get LogManager instance
        from src.util.log_manager import LogManager

        self.log_manager = LogManager.instance()


    async def start_notifications(self):
        """Start overall status notifications with retry logic"""
        if not self.esp32_service:
            return False

        max_retries = 5
        delay = 0.2  # Longer delay between retries

        for attempt in range(max_retries):
            try:
                result = await self.esp32_service.start_overall_status_notify(
                    self._handle_status_update
                )
                if result:
                    self.view.set_button_states(True)
                    return True
                await asyncio.sleep(delay)
            except Exception:
                if attempt < max_retries - 1:
                    await asyncio.sleep(delay)
        return False

    async def stop_notifications(self):
        """Stop overall status notifications"""
        self.view.clear_values()
        if not self.esp32_service:
            return
        await self.esp32_service.stop_overall_status_notify()

    async def _handle_status_update(self, sender, status_data):
        """Handle status updates from the BLE service"""
        if status_data and isinstance(status_data, OverallStatus):
            self._current_status = status_data
            self.view.update_status(
                status_data.fuelgause == OverallStatus.RUNNING,
                status_data.imu1 == OverallStatus.RUNNING,
                status_data.imu2 == OverallStatus.RUNNING,
            )

    def start_all_logging(self):
        """Start logging for all components"""
        if self.log_manager.start_all_logging():
            # Set loggers in presenters
            self.imu1_presenter.set_logger(self.log_manager.get_imu1_logger())
            self.imu2_presenter.set_logger(self.log_manager.get_imu2_logger())
            self.sensor_presenter.set_logger(self.log_manager.get_sensor_logger())
            return True
        return False

    def stop_all_logging(self):
        """Stop logging for all components"""
        self.imu1_presenter.set_logger(None)
        self.imu2_presenter.set_logger(None)
        self.sensor_presenter.set_logger(None)
        self.log_manager.stop_all_logging()
