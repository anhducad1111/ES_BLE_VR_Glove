class OverallStatus:
    """Model class representing overall system status"""
    
    # Status codes
    NO_ERROR = 0
    GENERAL_ERROR = 1
    
    # Sensor states
    NOT_DETECT = 0
    FAILED = 1
    IDLE = 2
    RUNNING = 3
    
    def __init__(self, fuelgause=NOT_DETECT, 
                 imu1=NOT_DETECT, imu2=NOT_DETECT, raw_data=None):
        self.fuelgause = fuelgause
        self.imu1 = imu1
        self.imu2 = imu2
        self.raw_data = raw_data
        
    @classmethod
    def from_bytes(cls, data):
        """Create OverallStatus object from byte array"""
        if not data or len(data) != 4:  # 4 uint8 values
            return None
            
        try:
            return cls(
                fuelgause=data[1],  # Skip status_code at data[0]
                imu1=data[2],
                imu2=data[3],
                raw_data=data
            )
        except Exception as e:
            print(f"Error parsing Overall Status data: {e}")
            return None
            
    def to_hex_string(self):
        """Convert raw data to hex string representation"""
        if not self.raw_data:
            return ""
        return ' '.join(f'{b:02x}' for b in self.raw_data)
        
    def get_debug_text(self):
        """Get formatted debug text"""
        status_texts = {
            self.NOT_DETECT: "Not Detect",
            self.FAILED: "Failed",
            self.IDLE: "Idle", 
            self.RUNNING: "Running"
        }
        
        debug_text = f"Fuelgause: {status_texts.get(self.fuelgause, 'Unknown')}\n"
        debug_text += f"IMU1: {status_texts.get(self.imu1, 'Unknown')}\n" 
        debug_text += f"IMU2: {status_texts.get(self.imu2, 'Unknown')}\n"
        debug_text += f"Raw data: {self.to_hex_string()}"
        return debug_text
