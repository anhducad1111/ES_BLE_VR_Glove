import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

class DebugLogger:
    """Debug logger for BLE operations with verification support"""
    
    _instance: Optional['DebugLogger'] = None
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
        
    def __init__(self):
        """Initialize logger if not already initialized"""
        if not hasattr(self, 'logger'):
            self.logger = logging.getLogger('BLEDebug')
            self._setup_logger()
            
        # Test metrics
        self.test_start_time: Optional[datetime] = None
        self.discovery_times: Dict[str, float] = {}
        self.connection_times: Dict[str, float] = {}
        self.reconnect_times: Dict[str, float] = {}
        self.disconnect_count = 0
        self.total_uptime = timedelta()
            
    def _setup_logger(self):
        """Setup logging configuration"""
        self.logger.setLevel(logging.DEBUG)
        
        # Create logs directory if it doesn't exist
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        # Create test directory with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.test_dir = log_dir / f'test_{timestamp}'
        self.test_dir.mkdir(exist_ok=True)
        
        # Create separate log files for different components
        self._setup_log_handlers([
            ('ble', 'Connection and BLE operations'),
            ('imu', 'IMU data and configuration'),
            ('controls', 'Joystick, buttons and sensors'),
            ('metrics', 'Test metrics and performance data')
        ])
        
    def _setup_log_handlers(self, components):
        """Setup log handlers for each component"""
        self.handlers = {}
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        for name, desc in components:
            # Create component log file
            log_file = self.test_dir / f'{name}.log'
            handler = logging.FileHandler(log_file, encoding='utf-8')
            handler.setLevel(logging.DEBUG)
            handler.setFormatter(formatter)
            self.handlers[name] = handler
            self.logger.addHandler(handler)
            
            # Log file header
            handler.emit(logging.LogRecord(
                'BLEDebug', logging.INFO, '', 0,
                f"=== {desc} ===\nTest started at: {datetime.now()}\n",
                (), None
            ))
            
        # Console handler for immediate feedback
        console = logging.StreamHandler(sys.stdout)
        console.setLevel(logging.INFO)
        console.setFormatter(formatter)
        self.logger.addHandler(console)

    def start_test(self):
        """Start a new test session"""
        self.test_start_time = datetime.now()
        self.info(f"Starting new test session at {self.test_start_time}")
        
    def log_discovery(self, device_addr: str, time_taken: float):
        """Log device discovery time"""
        self.discovery_times[device_addr] = time_taken
        self.debug(f"Device {device_addr} discovered in {time_taken:.2f}s")
        if time_taken > 3.0:
            self.warning(f"Discovery time exceeds 3s requirement: {time_taken:.2f}s")
            
    def log_connection(self, device_addr: str, time_taken: float):
        """Log connection time"""
        self.connection_times[device_addr] = time_taken
        self.debug(f"Connected to {device_addr} in {time_taken:.2f}s")
        if time_taken > 10.0:
            self.warning(f"Connection time exceeds 10s requirement: {time_taken:.2f}s")
            
    def log_reconnection(self, device_addr: str, time_taken: float, attempt: int):
        """Log reconnection attempt"""
        self.reconnect_times[device_addr] = time_taken
        self.debug(f"Reconnection attempt {attempt} to {device_addr} took {time_taken:.2f}s")
        if time_taken > 5.0:
            self.warning(f"Reconnection time exceeds 5s requirement: {time_taken:.2f}s")
            
    def log_disconnect(self, device_addr: str, uptime: timedelta):
        """Log device disconnection"""
        self.disconnect_count += 1
        self.total_uptime += uptime
        self.debug(
            f"Device {device_addr} disconnected\n"
            f"Uptime: {uptime}\n"
            f"Total disconnects: {self.disconnect_count}"
        )

    def log_imu_config(self, imu_id: int, config_data: Dict[str, Any]):
        """Log IMU configuration"""
        handler = self.handlers.get('imu')
        if handler:
            msg = f"\nIMU {imu_id} Configuration:\n"
            for key, value in config_data.items():
                msg += f"  {key}: {value}\n"
            self._log_to_handler(handler, msg)

    def log_control_data(self, control_type: str, data: Dict[str, Any]):
        """Log control data with validation"""
        handler = self.handlers.get('controls')
        if handler:
            msg = f"\n{control_type} Data:\n"
            for key, value in data.items():
                msg += f"  {key}: {value}\n"
            
            # Validate against requirements
            if control_type == "Joystick":
                if not (0 <= data.get('x', 0) <= 4095 and 0 <= data.get('y', 0) <= 4095):
                    msg += "WARNING: Values outside 0-4095 range\n"
            elif control_type == "Buttons":
                response_time = data.get('response_time', 0)
                if response_time > 50:
                    msg += f"WARNING: Response time {response_time}ms exceeds 50ms requirement\n"
                    
            self._log_to_handler(handler, msg)

    def log_test_metrics(self):
        """Log test metrics summary"""
        handler = self.handlers.get('metrics')
        if handler and self.test_start_time:
            test_duration = datetime.now() - self.test_start_time
            msg = "\nTest Metrics Summary:\n"
            msg += f"Test Duration: {test_duration}\n"
            msg += f"Total Uptime: {self.total_uptime}\n"
            msg += f"Disconnection Count: {self.disconnect_count}\n\n"
            
            msg += "Discovery Times:\n"
            for addr, time in self.discovery_times.items():
                msg += f"  {addr}: {time:.2f}s\n"
                
            msg += "\nConnection Times:\n"
            for addr, time in self.connection_times.items():
                msg += f"  {addr}: {time:.2f}s\n"
                
            msg += "\nReconnection Times:\n"
            for addr, time in self.reconnect_times.items():
                msg += f"  {addr}: {time:.2f}s\n"
                
            self._log_to_handler(handler, msg)
            
    def _log_to_handler(self, handler: logging.Handler, msg: str):
        """Log message to specific handler"""
        record = logging.LogRecord(
            'BLEDebug', logging.DEBUG, '', 0, msg, (), None
        )
        handler.emit(record)
            
    def debug(self, msg: str):
        """Log debug message"""
        self.logger.debug(msg)
        
    def info(self, msg: str):
        """Log info message"""
        self.logger.info(msg)
        
    def warning(self, msg: str):
        """Log warning message"""
        self.logger.warning(msg)
        
    def error(self, msg: str):
        """Log error message"""
        self.logger.error(msg)
        
    def critical(self, msg: str):
        """Log critical message"""
        self.logger.critical(msg)
        
    def log_data(self, uuid: str, data: bytes, parsed: str):
        """Log BLE data"""
        hex_data = ' '.join(f'{b:02x}' for b in data)
        self.debug(
            f"\nCharacteristic: {uuid}"
            f"\nRaw Data: {hex_data}"
            f"\nParsed Data:\n{parsed}"
            f"\n{'-'*50}"
        )