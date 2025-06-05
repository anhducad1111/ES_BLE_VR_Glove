import os
import csv
import time
import queue
import threading
import datetime
from src.model.log_abs import LogABS
from src.model.profile import DeviceProfile
from src.util.log_manager import LogManager

class BaseLog(LogABS):
    """Base logger class with common functionality for queue processing"""
    
    _instance = None
    
    def __init__(self):
        super().__init__()
        self.is_logging = False
        self.stop_thread = False
        self.file = None
        self.writer = None
        self.row_count = 0
        self.queue = queue.Queue(maxsize=1000)
        self.thread = None
        self.log_manager = LogManager.instance()

    def _process_queue(self):
        """Process data queue"""
        while not self.stop_thread:
            try:
                data = self.queue.get(timeout=0.1)
                if self.writer:
                    self._write_row(data)
                self.queue.task_done()
            except queue.Empty:
                continue

    def setup_header(self, writer=None, file=None):
        """Write CSV file header with common format and specific columns"""
        if not writer:
            writer = self.writer
        if not file:
            file = self.file
        if not writer:
            return
            
        try:
            profile = DeviceProfile.get_instance()
            
            # Write common header
            now = datetime.datetime.now()
            writer.writerow([f"{now.strftime('%H:%M:%S_%Y%m%d')} version 00.00.01"])
            writer.writerow([f"Device: {profile.name}, Firmware: {profile.firmware}"])
            writer.writerow([])
            
            # Write specific headers - to be implemented by subclasses
            headers = self._get_headers()
            if headers:
                writer.writerow(headers)
            file.flush()
        except:
            pass

    def setup_footer(self, writer=None, file=None, row_count=None):
        """Write CSV file footer with common format"""
        if not writer:
            writer = self.writer
        if not file:
            file = self.file
        if row_count is None:
            row_count = self.row_count
        if not writer:
            return
            
        try:
            writer.writerow([])
            writer.writerow(['Summary'])
            writer.writerow([f'Total rows: {row_count}'])
            writer.writerow(['End of recording'])
            file.flush()
        except:
            pass

    def _initialize_log_file(self, filename):
        """Initialize a new log file with common setup"""
        file_path = os.path.join(self.folder_path, filename)
        file = open(file_path, 'w', newline='')
        writer = csv.writer(file)
        return file, writer

    def _create_log_folder(self, base_folder):
        """Create timestamped log folder"""
        now = datetime.datetime.now()
        subfolder = now.strftime("%d%m%Y_%H%M%S_vr_glove")
        self.folder_path = os.path.join(base_folder, subfolder)
        os.makedirs(self.folder_path, exist_ok=True)

    def start_logging(self, base_folder):
        """Start logging - Template method for subclasses"""
        self._create_log_folder(base_folder)
        self.is_logging = True
        self.stop_thread = False
        self.log_manager.register_logger()
        return True

    def stop_logging(self):
        """Stop logging - Template method for subclasses"""
        self.is_logging = False
        self.stop_thread = True
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        self.log_manager.unregister_logger()

    def _write_row(self, data):
        """Write a single row of data to CSV - Must be implemented by subclasses"""
        raise NotImplementedError

    def _get_headers(self):
        """Get headers for CSV file - Must be implemented by subclasses"""
        raise NotImplementedError