from src.util.log_manager import LogManager

class LogPresenter:
    """Presenter for handling log view operations"""

    def __init__(self, view, ble_service, loop, imu1_presenter, imu2_presenter, sensor_presenter):
        """Initialize the presenter
        
        Args:
            view: Reference to the log view
            ble_service: Reference to the ESP32 BLE service
            loop: Event loop for async operations 
            imu1_presenter: Reference to IMU1 presenter
            imu2_presenter: Reference to IMU2 presenter
            sensor_presenter: Reference to sensor presenter
        """
        self.view = view
        self.service = ble_service 
        self.loop = loop
        self.imu1_presenter = imu1_presenter
        self.imu2_presenter = imu2_presenter
        self.sensor_presenter = sensor_presenter

        # Get LogManager instance
        self.log_manager = LogManager.instance()

        # Set references in view
        self.view.service = ble_service
        self.view.loop = loop

        # Initially disable buttons until services are started
        self.view.set_button_states(False)

        # Set presenter reference in view
        self.view.set_presenter(self)

    async def start_notifications(self):
        """Start notifications and enable log button when services are ready"""
        if not self.service.is_connected():
            return False

        try:
            # Enable button when services are started
            self.view.set_button_states(True)
            print("✓ Started log service")
            return True
        except Exception as e:
            print(f"Error starting log service: {e}")
            return False

    async def stop_notifications(self):
        """Stop notifications and disable log button"""
        self.view.set_button_states(False)
        return True

    def start_all_logging(self):
        """Start logging for all components"""
        if not self.service.is_connected():
            return False

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
        return True