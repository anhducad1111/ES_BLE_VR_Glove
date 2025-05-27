from src.model.overall_status import OverallStatus

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
        """Start overall status notifications"""
        if self.esp32_service:
            await self.esp32_service.start_overall_status_notify(self._handle_status_update)

    async def stop_notifications(self):
        """Stop overall status notifications"""
        if self.esp32_service:
            await self.esp32_service.stop_overall_status_notify()

    async def _handle_status_update(self, sender, status_data):
        """Handle status updates from the BLE service
        
        Args:
            sender: The characteristic that sent the notification
            status_data: OverallStatus object containing the status data
        """
        if status_data and isinstance(status_data, OverallStatus):
            self._current_status = status_data
            # Update view with new status
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
