import datetime
import logging
import os
from src.model.log_abs import LogABS


class SystemLog(LogABS):
    """Logger for capturing all system output using Python's logging module"""

    _instance = None

    def __init__(self):
        super().__init__()
        self.logger = None
        self.handler = None
        self.is_logging = False
        self.row_count = 0

    @classmethod
    def get_instance(cls):
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = SystemLog()
        return cls._instance

    def setup_header(self, *args, **kwargs):
        """Set up log file header"""
        if not self.logger:
            return
            
        self.logger.info("=== System Log Started at %s ===", datetime.datetime.now())

    def setup_footer(self, *args, **kwargs):
        """Set up log file footer"""
        if not self.logger:
            return
            
        self.logger.info("=== System Log Ended at %s ===", datetime.datetime.now())
        self.logger.info("Total messages: %d", self.row_count)

    def write_csv(self, *args, **kwargs):
        """Write message to log file"""
        if not self.is_logging:
            return False

        message = kwargs.get('message', '')
        if message is None:
            return False
            
        message = str(message).strip()
        if not message:
            return False

        try:
            self.logger.info(message)
            self.row_count += 1
            return True
        except Exception as e:
            print(f"Failed to write log: {e}")
            return False

    def start_logging(self, base_folder=None):
        """Start logging to timestamped file"""
        try:
            # Create logs folder in project root
            curr_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            logs_folder = os.path.join(curr_dir, "logs")
            os.makedirs(logs_folder, exist_ok=True)

            # Create timestamped filename
            now = datetime.datetime.now()
            file_name = now.strftime("%d%m%Y_%H%M%S_vr_glove") + ".log"
            log_file = os.path.join(logs_folder, file_name)

            # Setup logger
            self.logger = logging.getLogger('system_logger')
            self.logger.setLevel(logging.INFO)

            # Setup file handler with formatter that includes timestamp
            self.handler = logging.FileHandler(log_file, encoding='utf-8')
            formatter = logging.Formatter('%(asctime)s | %(message)s',
                                       datefmt='%Y-%m-%d %H:%M:%S')
            self.handler.setFormatter(formatter)
            self.logger.addHandler(self.handler)

            self.is_logging = True
            self.row_count = 0
            
            # Write header
            self.setup_header()
            return True

        except Exception as e:
            print(f"Failed to start logging: {e}")
            return False

    def stop_logging(self):
        """Stop logging and close handlers"""
        if not self.is_logging:
            return

        try:
            if self.logger:
                self.setup_footer()
                if self.handler:
                    self.handler.close()
                    self.logger.removeHandler(self.handler)
                self.handler = None
                self.logger = None
            self.is_logging = False
            self.row_count = 0
        except Exception as e:
            print(f"Failed to stop logging: {e}")

    def log_message(self, message: str):
        """Log a system message"""
        if message is None:
            return
        self.write_csv(message=str(message))