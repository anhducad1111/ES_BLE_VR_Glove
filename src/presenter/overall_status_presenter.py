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

        max_retries = 3
        delay = 1.0  # Longer delay between retries

        for attempt in range(max_retries):
            try:
                print(f"\nStarting overall status notifications (attempt {attempt + 1}/{max_retries})")
                result = await self.esp32_service.start_overall_status_notify(self._handle_status_update)
                if result:
                    print("✓ Overall status notifications started successfully")
                    return True
                print("Failed to start overall status notifications, retrying...")
                await asyncio.sleep(delay)
            except Exception as e:
                print(f"Error starting overall status notifications: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(delay)

        print("❌ Failed to start overall status notifications after all retries")
        return False

    async def stop_notifications(self):
        """Stop overall status notifications with error handling"""
        if not self.esp32_service:
            return

        try:
            print("\nStopping overall status notifications")
            await self.esp32_service.stop_overall_status_notify()
        except Exception as e:
            print(f"Error stopping overall status notifications: {e}")

    async def _handle_status_update(self, sender, status_data):
        """Handle status updates from the BLE service with validation
        
        Args:
            sender: The characteristic that sent the notification
            status_data: OverallStatus object containing the status data
        """
        try:
            if not status_data:
                print("Received empty status data")
                return

            if not isinstance(status_data, OverallStatus):
                print(f"Invalid status data type: {type(status_data)}")
                return

            self._current_status = status_data
            # Update view with new status
            self.view.update_status(
                status_data.fuelgause == OverallStatus.RUNNING,
                status_data.imu1 == OverallStatus.RUNNING,
                status_data.imu2 == OverallStatus.RUNNING
            )
            print(f"Status updated: {status_data.get_debug_text()}")

        except Exception as e:
            print(f"Error handling status update: {e}")

    def clear_status(self):
        """Clear current status"""
        self._current_status = None
        if self.view:
            self.view.update_status(False, False, False)
