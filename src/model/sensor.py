import struct

class FlexSensorData:
    """Model class representing flex sensor data"""
    
    def __init__(self, values=None, raw_data=None):
        # Array of 5 resistance values in kOhm
        self.values = values if values else [0.0] * 5
        self.raw_data = raw_data
        
    @classmethod
    def from_bytes(cls, data):
        """Create FlexSensorData object from byte array"""
        if not data or len(data) != 20:  # 5 float32 values
            return None
            
        try:
            # Unpack 5 float32 values
            values = list(struct.unpack('<5f', data))
            return cls(values=values, raw_data=data)
        except Exception as e:
            print(f"Error parsing flex sensor data: {e}")
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
        debug_text += "Flex sensor values (kOhm):\n"
        for i, value in enumerate(self.values, 1):
            debug_text += f"Sensor {i}: {value:.2f}\n"
        return debug_text


class ForceSensorData:
    """Model class representing force sensor data"""
    
    def __init__(self, value=0.0, raw_data=None):
        # Resistance value in kOhm
        self.value = value
        self.raw_data = raw_data
        
    @classmethod
    def from_bytes(cls, data):
        """Create ForceSensorData object from byte array"""
        if not data or len(data) != 4:  # 1 float32 value
            return None
            
        try:
            # Unpack float32 value
            value = struct.unpack('<f', data)[0]
            return cls(value=value, raw_data=data)
        except Exception as e:
            print(f"Error parsing force sensor data: {e}")
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
        debug_text += f"Force sensor value (kOhm): {self.value:.2f}"
        return debug_text
