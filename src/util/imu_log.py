import os
import csv
import time
import queue
import threading
import datetime
from src.model.log_abs import LogABS
from src.model.profile import DeviceProfile
from src.util.log_manager import LogManager

class IMULog(LogABS):
    """IMU logger with thread queue processing"""
    
    _instance = None
    
    @classmethod
    def instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        super().__init__()
        if not hasattr(IMULog, '_instance'):
            IMULog._instance = self
            
        self.queues = {}
        self.threads = {}
        self.files = {}
        self.writers = {}
        self.row_counts = {}
        self.is_logging = False
        self.stop_threads = False
        self.log_manager = LogManager.instance()
    
    def write_csv(self, imu_number, imu_data, euler_data):
        """Queue IMU data for writing"""
        if not self.is_logging:
            return
            
        # Initialize IMU resources if needed
        if imu_number not in self.queues:
            self._setup_imu(imu_number)
        
        # Queue data
        if imu_number in self.queues:
            try:
                data = {
                    'timestamp': int(time.time() * 1000),
                    'imu_data': imu_data,
                    'euler_data': euler_data
                }
                self.queues[imu_number].put(data, block=False)
            except queue.Full:
                pass
    
    def _setup_imu(self, imu_number):
        """Set up resources for an IMU"""
        try:
            # Create CSV file
            filename = f'imu{imu_number}.csv'
            file_path = os.path.join(self.folder_path, filename)
            
            self.files[imu_number] = open(file_path, 'w', newline='')
            self.writers[imu_number] = csv.writer(self.files[imu_number])
            self.queues[imu_number] = queue.Queue(maxsize=1000)
            self.row_counts[imu_number] = 0
            
            # Write header
            self.setup_header(imu_number)
            
            # Start processing thread
            thread = threading.Thread(
                target=self._process_queue,
                args=(imu_number,),
                daemon=True
            )
            self.threads[imu_number] = thread
            thread.start()
            
        except Exception as e:
            if imu_number in self.files:
                self.files[imu_number].close()
                del self.files[imu_number]
    
    def _process_queue(self, imu_number):
        """Process queue for an IMU"""
        while not self.stop_threads:
            try:
                data = self.queues[imu_number].get(timeout=0.1)
                if imu_number in self.writers:
                    self._write_data(imu_number, data)
                self.queues[imu_number].task_done()
            except queue.Empty:
                continue
    
    def _write_data(self, imu_number, data):
        """Write IMU data row to CSV"""
        try:
            imu_data = data['imu_data']
            euler_data = data['euler_data']
            
            row = [data['timestamp'],
                   imu_data.accel['x'], imu_data.accel['y'], imu_data.accel['z'],
                   imu_data.gyro['x'], imu_data.gyro['y'], imu_data.gyro['z'],
                   imu_data.mag['x'], imu_data.mag['y'], imu_data.mag['z'],
                   euler_data.euler['yaw'], euler_data.euler['pitch'], euler_data.euler['roll']]
                   
            self.writers[imu_number].writerow(row)
            self.files[imu_number].flush()
            self.row_counts[imu_number] += 1
        except:
            pass
    
    def setup_header(self, imu_number):
        """Write CSV file header"""
        if imu_number not in self.writers:
            return
            
        try:
            profile = DeviceProfile.get_instance()
            writer = self.writers[imu_number]
            
            now = datetime.datetime.now()
            writer.writerow([f"{now.strftime('%H:%M:%S_%Y%m%d')} version 00.00.01"])
            writer.writerow([f"Device: {profile.name}, Firmware: {profile.firmware}"])
            writer.writerow([])
            
            headers = ['timestamp',
                      'ax', 'ay', 'az',
                      'gx', 'gy', 'gz',
                      'mx', 'my', 'mz',
                      'ex', 'ey', 'ez']
            writer.writerow(headers)
            self.files[imu_number].flush()
        except:
            pass
        
    def setup_footer(self, imu_number):
        """Write CSV file footer"""
        if imu_number not in self.writers:
            return
            
        try:
            writer = self.writers[imu_number]
            writer.writerow([])
            writer.writerow(['Summary'])
            writer.writerow([f'Total rows: {self.row_counts.get(imu_number, 0)}'])
            writer.writerow(['End of recording'])
            self.files[imu_number].flush()
        except:
            pass
    
    def start_logging(self, base_folder):
        """Start logging with new timestamped folder"""
        # Use the provided folder to create timestamped subfolder
        now = datetime.datetime.now()
        subfolder = now.strftime("%d%m%Y_%H%M%S_vr_glove")
        self.folder_path = os.path.join(base_folder, subfolder)
        os.makedirs(self.folder_path, exist_ok=True)
        
        # Clean up any previous logging
        self.stop_logging()
        
        self.is_logging = True
        self.stop_threads = False
        self.log_manager.register_logger()
        return True
    
    def stop_logging(self):
        """Stop logging and cleanup"""
        self.is_logging = False
        self.stop_threads = True
        
        # Wait for threads to finish
        for thread in self.threads.values():
            if thread and thread.is_alive():
                thread.join(timeout=1.0)
        
        # Write footers and close files
        for imu_number in list(self.files.keys()):
            try:
                self.setup_footer(imu_number)
                self.files[imu_number].close()
            except:
                pass
        
        # Clear resources
        self.queues.clear()
        self.threads.clear()
        self.files.clear()
        self.writers.clear()
        self.row_counts.clear()
        
        self.log_manager.unregister_logger()