import time
import queue
import threading
from src.util.base_log import BaseLog

class SensorLog(BaseLog):
    """Sensor logger with thread queue processing"""
    
    _instance = None
    
    @classmethod
    def instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        super().__init__()
        if not hasattr(SensorLog, '_instance'):
            SensorLog._instance = self
    
    def write_csv(self, flex_values, force_value):
        """Write sensor data to CSV file"""
        if not self.is_logging:
            return
            
        try:
            data = {
                'timestamp': int(time.time() * 1000),
                'flex_values': flex_values,
                'force_value': force_value
            }
            self.queue.put(data, block=False)
        except queue.Full:
            pass

    def _write_row(self, data):
        """Write a single row of sensor data to CSV"""
        try:
            flex_values = data['flex_values']
            row = [data['timestamp']]
            row.extend(flex_values)
            row.append(data['force_value'])
            
            self.writer.writerow(row)
            self.file.flush()
            self.row_count += 1
        except:
            pass

    def _get_headers(self):
        """Get headers for sensor CSV file"""
        headers = ['timestamp']
        headers.extend([f'flex{i+1}' for i in range(5)])
        headers.append('force')
        return headers

    def start_logging(self, base_folder):
        """Start logging sensor data"""
        super().start_logging(base_folder)
        
        self.file, self.writer = self._initialize_log_file('sensors.csv')
        self.setup_header()
        
        self.thread = threading.Thread(
            target=self._process_queue,
            daemon=True
        )
        self.thread.start()
        return True

    def stop_logging(self):
        """Stop logging and cleanup"""
        if self.writer:
            self.setup_footer()
        if self.file:
            self.file.close()
        
        self.queue = queue.Queue(maxsize=1000)
        self.thread = None
        self.file = None
        self.writer = None
        self.row_count = 0
        
        super().stop_logging()