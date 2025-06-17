import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

class DebugLogger:
    """Debug logger for BLE operations"""
    
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
            
    def _setup_logger(self):
        """Setup logging configuration"""
        self.logger.setLevel(logging.DEBUG)
        
        # Create logs directory if it doesn't exist
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        # Create log file with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = log_dir / f'ble_debug_{timestamp}.log'
        
        # File handler
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
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