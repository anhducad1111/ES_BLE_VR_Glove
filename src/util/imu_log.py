import time
import queue
import threading
from src.util.base_log import BaseLog

class IMULog(BaseLog):
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
            filename = f'imu{imu_number}.csv'
            self.files[imu_number], self.writers[imu_number] = self._initialize_log_file(filename)
            self.queues[imu_number] = queue.Queue(maxsize=1000)
            self.row_counts[imu_number] = 0
            
            self.setup_header(writer=self.writers[imu_number], file=self.files[imu_number])
            
            thread = threading.Thread(
                target=self._process_imu_queue,
                args=(imu_number,),
                daemon=True
            )
            self.threads[imu_number] = thread
            thread.start()
            
        except Exception as e:
            if imu_number in self.files:
                self.files[imu_number].close()
                del self.files[imu_number]
    
    def _process_imu_queue(self, imu_number):
        """Process queue for an IMU"""
        while not self.stop_thread:
            try:
                data = self.queues[imu_number].get(timeout=0.1)
                if imu_number in self.writers:
                    self._write_imu_row(imu_number, data)
                self.queues[imu_number].task_done()
            except queue.Empty:
                continue
    
    def _write_imu_row(self, imu_number, data):
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

    def _get_headers(self):
        """Get headers for IMU CSV file"""
        return ['timestamp',
                'ax', 'ay', 'az',
                'gx', 'gy', 'gz',
                'mx', 'my', 'mz',
                'ex', 'ey', 'ez']

    def start_logging(self, base_folder):
        """Start logging with new timestamped folder"""
        # Clean up any previous logging
        self.stop_logging()
        
        super().start_logging(base_folder)
        return True
    
    def stop_logging(self):
        """Stop logging and cleanup"""
        self.is_logging = False
        self.stop_thread = True
        
        # Wait for threads to finish
        for thread in self.threads.values():
            if thread and thread.is_alive():
                thread.join(timeout=1.0)
        
        # Write footers and close files
        for imu_number in list(self.files.keys()):
            try:
                self.setup_footer(
                    writer=self.writers[imu_number],
                    file=self.files[imu_number],
                    row_count=self.row_counts[imu_number]
                )
                self.files[imu_number].close()
            except:
                pass
        
        # Clear resources
        self.queues.clear()
        self.threads.clear()
        self.files.clear()
        self.writers.clear()
        self.row_counts.clear()
        
        super().stop_logging()