
class LogManager:
    """Singleton manager for handling shared log folder selection and loggers"""
    
    _instance = None
    
    @classmethod
    def instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        self.selected_folder = "C:/ProjectIT/ES_iot/log"  # Default path
        self.folder_path = None
        self._folder_change_callbacks = []
        
        # Logger instances will be created when needed
        self.imu1_logger = None
        self.imu2_logger = None
        self.sensor_logger = None
        
        self._notify_folder_change()  # Notify about default path

    def add_folder_change_callback(self, callback):
        """Add callback to be notified of folder changes"""
        if callback not in self._folder_change_callbacks:
            self._folder_change_callbacks.append(callback)

    def remove_folder_change_callback(self, callback):
        """Remove folder change callback"""
        if callback in self._folder_change_callbacks:
            self._folder_change_callbacks.remove(callback)

    def _notify_folder_change(self):
        """Notify all registered callbacks of folder change"""
        for callback in self._folder_change_callbacks:
            try:
                callback(self.selected_folder)
            except:
                pass
        
    def setup_logging_folder(self, base_folder):
        """Set up logging folder path"""
        # Update selected folder and notify
        self.selected_folder = base_folder if base_folder else "C:/ProjectIT/ES_iot/log"
        self._notify_folder_change()
        return True
    
    def get_logging_folder(self):
        """Get current logging folder path"""
        return self.folder_path
        
    def get_selected_folder(self):
        """Get base folder selected by user"""
        return self.selected_folder
        
    def clear_logging(self):
        """Reset logging state"""
        self.folder_path = None
            
    def get_imu1_logger(self):
        """Get IMU1 logger instance"""
        if not self.imu1_logger:
            from src.util.imu_log import IMULog
            self.imu1_logger = IMULog(1)
        return self.imu1_logger
            
    def get_imu2_logger(self):
        """Get IMU2 logger instance"""
        if not self.imu2_logger:
            from src.util.imu_log import IMULog
            self.imu2_logger = IMULog(2)
        return self.imu2_logger
            
    def get_sensor_logger(self):
        """Get sensor logger instance"""
        if not self.sensor_logger:
            from src.util.sensor_log import SensorLog
            self.sensor_logger = SensorLog.instance()
        return self.sensor_logger

    def start_all_logging(self):
        """Start logging for all loggers"""
        if not self.selected_folder:
            return False
            
        try:
            # Start IMU1 logging
            if not self.get_imu1_logger().start_logging(self.selected_folder):
                return False
                
            # Start IMU2 logging
            if not self.get_imu2_logger().start_logging(self.selected_folder):
                self.imu1_logger.stop_logging()
                return False
                
            # Start sensor logging
            if not self.get_sensor_logger().start_logging(self.selected_folder):
                self.imu1_logger.stop_logging()
                self.imu2_logger.stop_logging()
                return False
                
            return True
            
        except Exception as e:
            print(f"Error starting logging: {e}")
            self.stop_all_logging()
            return False

    def stop_all_logging(self):
        """Stop logging for all loggers"""
        try:
            if self.imu1_logger:
                self.imu1_logger.stop_logging()
            if self.imu2_logger:
                self.imu2_logger.stop_logging()
            if self.sensor_logger:
                self.sensor_logger.stop_logging()
        except:
            pass