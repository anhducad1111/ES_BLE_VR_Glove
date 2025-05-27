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
        # Calibration status (stored for future use)
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
            
    def to_hex_string(self):
        """Convert raw data to hex string representation"""
        if not self.raw_data:
            return ""
        return ' '.join(f'{b:02x}' for b in self.raw_data)
        
    def get_debug_text(self):
        """Get formatted debug text"""
        hex_str = self.to_hex_string()
        debug_text = f"Raw data ({len(self.raw_data)} bytes):\n{hex_str}\n\n"
        debug_text += f"Parsed values:\n"
        debug_text += f"Yaw: {self.euler['yaw']}°\n"
        debug_text += f"Pitch: {self.euler['pitch']}°\n"
        debug_text += f"Roll: {self.euler['roll']}°\n"
        debug_text += f"Calibration: {self.calib_status}"
        return debug_text

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
            
    def to_hex_string(self):
        """Convert raw data to hex string representation"""
        if not self.raw_data:
            return ""
        return ' '.join(f'{b:02x}' for b in self.raw_data)
        
    def get_debug_text(self):
        """Get formatted debug text"""
        hex_str = self.to_hex_string()
        debug_text = f"Raw data ({len(self.raw_data)} bytes):\n{hex_str}\n\n"
        debug_text += f"Parsed values:\n"
        debug_text += f"Accel: ({self.accel['x']}, {self.accel['y']}, {self.accel['z']})\n"
        debug_text += f"Gyro: ({self.gyro['x']}, {self.gyro['y']}, {self.gyro['z']})\n"
        debug_text += f"Mag: ({self.mag['x']}, {self.mag['y']}, {self.mag['z']})"
        return debug_text
