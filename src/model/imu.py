import struct

class IMUEulerData:
    """Model class representing IMU Euler angles data"""
    
    def __init__(self, yaw=0, pitch=0, roll=0, calib_status=0, raw_data=None):
        # Euler angles in degrees
        self.euler = {
            'yaw': yaw,
            'pitch': pitch,
            'roll': roll
        }
        # Calibration status
        self.calib_status = calib_status
        # Raw binary data
        self.raw_data = raw_data
    
    @classmethod
    def from_bytes(cls, data):
        """Create IMUEulerData object from byte array"""
        if not data or len(data) != 13:  # 3 float32 + 1 uint8
            return None
        
        try:
            # Unpack 3 float32 values for euler angles
            yaw, pitch, roll = struct.unpack('<3f', data[0:12])
            # Last byte is calibration status
            calib = data[12]
            return cls(yaw, pitch, roll, calib, data)
        except Exception as e:
            print(f"Error parsing IMU Euler data: {e}")
            return None
    
    def to_bytes(self):
        """Convert to byte array"""
        try:
            return struct.pack('<3fB',
                self.euler['yaw'],
                self.euler['pitch'],
                self.euler['roll'],
                self.calib_status
            )
        except Exception as e:
            print(f"Error packing IMU Euler data: {e}")
            return None

class IMUData:
    """Model class representing IMU sensor data"""
    
    def __init__(self, accel_x=0, accel_y=0, accel_z=0, 
                 gyro_x=0, gyro_y=0, gyro_z=0,
                 mag_x=0, mag_y=0, mag_z=0, raw_data=None):
        # Accelerometer data
        self.accel = {
            'x': accel_x,
            'y': accel_y,
            'z': accel_z
        }
        
        # Gyroscope data
        self.gyro = {
            'x': gyro_x,
            'y': gyro_y,
            'z': gyro_z
        }
        
        # Magnetometer data
        self.mag = {
            'x': mag_x,
            'y': mag_y,
            'z': mag_z
        }
        
        # Raw binary data
        self.raw_data = raw_data
    
    @classmethod
    def from_bytes(cls, data):
        """Create IMUData object from byte array"""
        if not data or len(data) != 18:  # 9 int16 values
            return None
        
        try:
            values = struct.unpack('<9h', data)
            return cls(
                accel_x=values[0], accel_y=values[1], accel_z=values[2],
                gyro_x=values[3], gyro_y=values[4], gyro_z=values[5],
                mag_x=values[6], mag_y=values[7], mag_z=values[8],
                raw_data=data
            )
        except Exception as e:
            print(f"Error parsing IMU data: {e}")
            return None
    
    def to_bytes(self):
        """Convert to byte array"""
        try:
            return struct.pack('<9h',
                self.accel['x'], self.accel['y'], self.accel['z'],
                self.gyro['x'], self.gyro['y'], self.gyro['z'],
                self.mag['x'], self.mag['y'], self.mag['z']
            )
        except Exception as e:
            print(f"Error packing IMU data: {e}")
            return None
