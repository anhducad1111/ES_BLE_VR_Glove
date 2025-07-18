from src.model.sensor import FlexSensorData, ForceSensorData


class SensorPresenter:
    """Presenter for handling sensor data"""

    def __init__(self, view, ble_service, loop):
        """Initialize sensor presenter

        Args:
            view: Reference to the sensor view
            ble_service: Reference to the BLE service
            loop: Event loop for async operations
        """
        self.view = view
        self.service = ble_service
        self.view.service = ble_service  # Set service for configuration
        self.view.loop = loop  # Set event loop for async operations
        self._current_flex_data = None
        self._current_force_data = None
        self.sensor_logger = None

        # Initially disable buttons until connection is established
        self.view.set_button_states(False)

    async def start_notifications(self):
        """Start sensor notifications"""
        if self.service:
            flex_success = await self.service.start_flex_sensor_notify(
                self._handle_flex_update
            )
            force_success = await self.service.start_force_sensor_notify(
                self._handle_force_update
            )
            if flex_success and force_success:
                self.view.set_button_states(True)
                return True
            return False
        return False

    async def stop_notifications(self):
        """Stop sensor notifications"""
        try:
            if self.service:
                # Stop notifications first to prevent new data
                await self.service.stop_flex_sensor_notify()
                await self.service.stop_force_sensor_notify()

                # Then stop logging if active
                if self.sensor_logger and self.sensor_logger.is_logging:
                    self.sensor_logger.stop_logging()
                    # Reset log button state
                    self.view.reset_log_button()

                self.view.set_button_states(False)

                # Clear current data
                self._current_flex_data = None
                self._current_force_data = None
        except Exception as e:
            print(f"Error stopping sensor notifications: {e}")

    def set_logger(self, logger):
        """Set sensor logger instance"""
        self.sensor_logger = logger

    async def _handle_flex_update(self, sender, flex_data):
        """Handle flex sensor data updates

        Args:
            sender: The characteristic that sent the notification
            flex_data: FlexSensorData object containing sensor data
        """
        if flex_data and isinstance(flex_data, FlexSensorData):
            self._current_flex_data = flex_data
            # Update view with new values
            for i, value in enumerate(flex_data.values, 1):
                self.view.update_flex_sensor(i, value)

            # Write to log if force data is also available
            if (
                self._current_force_data
                and self.sensor_logger
                and self.sensor_logger.is_logging
            ):
                self.sensor_logger.write_csv(
                    flex_data.values, self._current_force_data.value
                )

    async def _handle_force_update(self, sender, force_data):
        """Handle force sensor data updates

        Args:
            sender: The characteristic that sent the notification
            force_data: ForceSensorData object containing sensor data
        """
        if force_data and isinstance(force_data, ForceSensorData):
            self._current_force_data = force_data
            # Update view with new value
            self.view.update_force_sensor(force_data.value)

            # Write to log if flex data is also available
            if (
                self._current_flex_data
                and self.sensor_logger
                and self.sensor_logger.is_logging
            ):
                self.sensor_logger.write_csv(
                    self._current_flex_data.values, force_data.value
                )
