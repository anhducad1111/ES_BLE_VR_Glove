from src.model.overall_status import OverallStatus
import asyncio

class OverallStatusPresenter:
    """Presenter class for handling overall status updates"""

    def __init__(self, view, esp32_service):
        """Initialize the presenter
        
        Args:
            view: Reference to the overall status view
            esp32_service: Reference to the ESP32 BLE service
        """
        self.view = view
        self.esp32_service = esp32_service
        self._current_status = None

    async def start_notifications(self):
        """Start overall status notifications with retry logic"""
        if not self.esp32_service:
            return False

        max_retries = 5
        delay = 0.2  # Longer delay between retries

        for attempt in range(max_retries):
            try:
                result = await self.esp32_service.start_overall_status_notify(self._handle_status_update)
                if result:
                    return True
                await asyncio.sleep(delay)
            except Exception:
                if attempt < max_retries - 1:
                    await asyncio.sleep(delay)
        return False

    async def stop_notifications(self):
        """Stop overall status notifications"""
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
                status_data.imu2 == OverallStatus.RUNNING
            )

    def clear_status(self):
        """Clear current status"""
        self._current_status = None
        if self.view:
            self.view.update_status(False, False, False)
