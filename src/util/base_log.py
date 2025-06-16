import csv
import datetime
import os
import queue
import threading
import time

from src.model.log_abs import LogABS
from src.model.profile import DeviceProfile


class BaseLog(LogABS):
    """Base logger class with common functionality for queue processing"""

    def __init__(self):
        super().__init__()
        self.is_logging = False
        self.stop_thread = False
        self.file = None
        self.writer = None
        self.row_count = 0
        self.queue = queue.Queue(maxsize=1000)
        self.thread = None

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

        # Sau khi nhận lệnh stop, xử lý nốt dữ liệu còn trong queue
        self._process_remaining_data()

    def _process_remaining_data(self):
        """Process any remaining data in the queue before stopping"""
        try:
            while True:
                # Get data without waiting (non-blocking)
                data = self.queue.get_nowait()
                if self.writer:
                    self._write_row(data)
                self.queue.task_done()
        except queue.Empty:
            pass

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
            writer.writerow(["Summary"])
            writer.writerow([f"Total rows: {row_count}"])
            writer.writerow(["End of recording"])
            file.flush()
        except:
            pass

    def _initialize_log_file(self, filename):
        """Initialize a new log file with common setup"""
        file_path = os.path.join(self.folder_path, filename)
        file = open(file_path, "w", newline="")
        writer = csv.writer(file)
        return file, writer

    def _create_log_folder(self, base_folder):
        """Create timestamped log folder"""
        now = datetime.datetime.now()
        subfolder = now.strftime("%d%m%Y_%H%M%S_vr_glove")
        self.folder_path = os.path.join(base_folder, subfolder)
        os.makedirs(self.folder_path, exist_ok=True)

    def _get_filename(self):
        """Get filename for log file - Must be implemented by subclasses"""
        raise NotImplementedError

    def start_logging(self, base_folder):
        """Start logging - Common implementation"""
        # Create new queue and thread
        self.queue = queue.Queue(maxsize=1000)
        self.stop_thread = False
        self.is_logging = True

        # Create log folder and file
        self._create_log_folder(base_folder)
        self.file, self.writer = self._initialize_log_file(self._get_filename())
        self.setup_header()

        # Start processing thread
        self.thread = threading.Thread(target=self._process_queue, daemon=True)
        self.thread.start()
        return True

    def stop_logging(self):
        """Stop logging - Common implementation"""
        if not self.is_logging:
            return

        # Signal thread to stop and wait for remaining data
        self.is_logging = False
        self.stop_thread = True

        if self.thread and self.thread.is_alive():
            # Wait for thread to finish processing queue
            self.queue.join()
            self.thread.join(timeout=1.0)

        # Write footer and close file
        if self.writer:
            self.setup_footer()
        if self.file:
            self.file.close()

        # Reset all attributes
        self.thread = None
        self.file = None
        self.writer = None
        self.row_count = 0

    def _write_row(self, data):
        """Write a single row of data to CSV - Must be implemented by subclasses"""
        raise NotImplementedError

    def _get_headers(self):
        """Get headers for CSV file - Must be implemented by subclasses"""
        raise NotImplementedError
