import csv
import os
import time

class IMULogger:
    def __init__(self, path):
        """Initialize IMU logger with path for CSV files
        
        Args:
            path: Directory path where CSV files will be created
        """
        self.path = path
        self.imu1_file = None
        self.imu2_file = None
        self.imu1_writer = None
        self.imu2_writer = None
        self.is_logging = False
        
        # CSV headers
        self.headers = ['timestamp', 'ax', 'ay', 'az', 'gx', 'gy', 'gz', 'mx', 'my', 'mz', 'ex', 'ey', 'ez']
        
    def start_logging(self):
        """Start logging IMU data to CSV files"""
        try:
            # Create CSV files with headers
            self.imu1_file = open(os.path.join(self.path, 'imu1.csv'), 'w', newline='')
            self.imu2_file = open(os.path.join(self.path, 'imu2.csv'), 'w', newline='')
            
            self.imu1_writer = csv.writer(self.imu1_file)
            self.imu2_writer = csv.writer(self.imu2_file)
            
            # Write headers
            self.imu1_writer.writerow(self.headers)
            self.imu2_writer.writerow(self.headers)
            
            self.is_logging = True
            return True
        except Exception as e:
            self.stop_logging()
            return False
            
    def log_imu_data(self, imu_number, imu_data, euler_data):
        """Log IMU and Euler data to corresponding CSV file
        
        Args:
            imu_number: 1 or 2 indicating which IMU data to log
            imu_data: IMUData object containing accelerometer, gyroscope and magnetometer data
            euler_data: IMUEulerData object containing euler angles
        """
        if not self.is_logging:
            return
            
        try:
            # Get raw timestamp in milliseconds
            timestamp = int(time.time() * 1000)
            
            # Prepare row data
            row = [
                timestamp,
                imu_data.accel['x'], imu_data.accel['y'], imu_data.accel['z'],
                imu_data.gyro['x'], imu_data.gyro['y'], imu_data.gyro['z'],
                imu_data.mag['x'], imu_data.mag['y'], imu_data.mag['z'],
                euler_data.euler['yaw'], euler_data.euler['pitch'], euler_data.euler['roll']
            ]
            
            # Write to appropriate file
            if imu_number == 1:
                self.imu1_writer.writerow(row)
                self.imu1_file.flush()  # Ensure data is written immediately
            else:
                self.imu2_writer.writerow(row)
                self.imu2_file.flush()  # Ensure data is written immediately
                
        except Exception as e:
            pass
            
    def stop_logging(self):
        """Stop logging and close CSV files"""
        self.is_logging = False
        
        # Close files if open
        if self.imu1_file:
            self.imu1_file.close()
            self.imu1_file = None
            
        if self.imu2_file:
            self.imu2_file.close()
            self.imu2_file = None
        
        self.imu1_writer = None
        self.imu2_writer = None
