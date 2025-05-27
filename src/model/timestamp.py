from datetime import datetime

class TimestampData:
    """Model class representing timestamp data"""
    
    def __init__(self, unix_timestamp=0, raw_data=None):
        self.unix_timestamp = unix_timestamp
        self.raw_data = raw_data
        
    @property
    def datetime(self):
        """Convert timestamp to datetime object"""
        return datetime.fromtimestamp(self.unix_timestamp)
        
    @property
    def formatted_datetime(self):
        """Get formatted datetime string"""
        return self.datetime.strftime('%Y-%m-%d %H:%M:%S')
        
    @classmethod
    def from_bytes(cls, data):
        """Create TimestampData object from byte array"""
        if not data or len(data) != 8:  # 64-bit timestamp
            return None
            
        try:
            timestamp = int.from_bytes(data, byteorder='little')
            return cls(unix_timestamp=timestamp, raw_data=data)
        except Exception as e:
            print(f"Error parsing timestamp data: {e}")
            return None
            
    @classmethod
    def current(cls):
        """Create TimestampData with current time"""
        import time
        current_time = int(time.time())
        data = current_time.to_bytes(8, byteorder='little')
        return cls(unix_timestamp=current_time, raw_data=data)
    def to_hex_string(self):
        """Convert raw data to hex string representation"""
        if not self.raw_data:
            return ""
        return ' '.join(f'{b:02x}' for b in self.raw_data)
        
    def get_formatted_display(self):
        """Get formatted text for display"""
        try:
            return (
                f"UNIX Timestamp: {self.unix_timestamp}\n"
                f"Date/Time: {self.formatted_datetime}\n"
                f"Raw bytes: {self.to_hex_string()}"
            )
        except Exception as e:
            return f"Error formatting timestamp: {e}"