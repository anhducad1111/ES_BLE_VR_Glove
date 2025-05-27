class BatteryLevelData:
    """Model class for battery level data"""
    
    def __init__(self, level=0, raw_data=None):
        self.level = level  # 0-100
        self.raw_data = raw_data

    @classmethod
    def from_bytes(cls, data):
        """Create BatteryLevelData from byte array"""
        if not data:
            return None
        try:
            level = int(data[0])  # Get first byte as integer (0-100)
            return cls(level, data)
        except Exception as e:
            print(f"Error parsing battery level data: {e}")
            return None


class BatteryStateData:
    """Model class for battery charging state data"""
    
    STATES = ["Not Charging", "Charging", "Fully Charged"]
    
    def __init__(self, state=0, raw_data=None):
        # state: 0=Not Charging, 1=Charging, 2=Fully Charged
        self.state = state
        self.raw_data = raw_data
        
    @property
    def state_text(self):
        """Get state as text"""
        return self.STATES[self.state] if 0 <= self.state < len(self.STATES) else "Unknown"

    @classmethod
    def from_bytes(cls, data):
        """Create BatteryStateData from byte array"""
        if not data:
            return None
        try:
            state = int(data[0])
            return cls(state, data)
        except Exception as e:
            print(f"Error parsing battery state data: {e}")
            return None
