import os
import csv
import time
import queue
import threading
import datetime
from src.model.log_abs import LogABS
from src.model.profile import DeviceProfile
from src.util.log_manager import LogManager

class SensorLog(LogABS):
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
            
        self.queue = queue.Queue(maxsize=1000)
        self.thread = None
        self.file = None
        self.writer = None
        self.row_count = 0
        self.is_logging = False
        self.stop_thread = False
        self.log_manager = LogManager.instance()
    
    def write_csv(self, flex_values, force_value):
        """Write sensor data to CSV file - Implementation of abstract method"""
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
            
    def _process_queue(self):
        """Process sensor data queue"""
        while not self.stop_thread:
            try:
                data = self.queue.get(timeout=0.1)
                if self.writer:
                    self._write_row(data)
                self.queue.task_done()
            except queue.Empty:
                continue
                
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
            
    def setup_header(self):
        """Write CSV file header"""
        if not self.writer:
            return
            
        try:
            profile = DeviceProfile.get_instance()
            
            now = datetime.datetime.now()
            self.writer.writerow([f"{now.strftime('%H:%M:%S_%Y%m%d')} version 00.00.01"])
            self.writer.writerow([f"Device: {profile.name}, Firmware: {profile.firmware}"])
            self.writer.writerow([])
            
            headers = ['timestamp']
            headers.extend([f'flex{i+1}' for i in range(5)])
            headers.append('force')
            self.writer.writerow(headers)
            self.file.flush()
        except:
            pass
    
    def setup_footer(self):
        """Write CSV file footer"""
        if not self.writer:
            return
            
        try:
            self.writer.writerow([])
            self.writer.writerow(['Summary'])
            self.writer.writerow([f'Total rows: {self.row_count}'])
            self.writer.writerow(['End of recording'])
            self.file.flush()
        except:
            pass
    
    def start_logging(self, base_folder=None):
        """Start logging sensor data"""
        try:
            # Use existing folder if one is already set up
            if not base_folder and self.log_manager.get_selected_folder():
                folder_path = self.log_manager.get_logging_folder()
            else:
                # Set up new logging folder
                if not self.log_manager.setup_logging_folder(base_folder):
                    return False
                folder_path = self.log_manager.get_logging_folder()
            
            # Create sensor log file
            file_path = os.path.join(folder_path, 'sensors.csv')
            self.file = open(file_path, 'w', newline='')
            self.writer = csv.writer(self.file)
            
            # Write header
            self.setup_header()
            
            # Start processing thread
            self.stop_thread = False
            self.thread = threading.Thread(
                target=self._process_queue,
                daemon=True
            )
            self.thread.start()
            
            self.is_logging = True
            self.log_manager.register_logger()
            return True
            
        except:
            if self.file:
                self.file.close()
            self.file = None
            self.writer = None
            self.is_logging = False
            return False
    
    def stop_logging(self):
        """Stop logging and cleanup"""
        self.is_logging = False
        self.stop_thread = True
        
        # Wait for thread to finish
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        
        # Write footer and close file
        if self.writer:
            self.setup_footer()
        if self.file:
            self.file.close()
        
        # Clear resources
        self.queue = queue.Queue(maxsize=1000)
        self.thread = None
        self.file = None
        self.writer = None
        self.row_count = 0
        self.log_manager.unregister_logger()