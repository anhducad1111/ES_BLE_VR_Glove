import struct

class JoystickData:
    """Model class representing joystick data"""
    
    def __init__(self, x=0, y=0, button_state=0, raw_data=None):
        # X and Y axis values (int16)
        self.x = x
        self.y = y
        # Button state (0 = Not detected, 1 = detected)
        self.button_state = button_state
        self.raw_data = raw_data
        
    @classmethod
    def from_bytes(cls, data):
        """Create JoystickData object from byte array
        
        Data format (5 bytes total):
        - X axis: int16 (2 bytes)
        - Y axis: int16 (2 bytes)
        - Button state: uint8 (1 byte)
        """
        if not data or len(data) != 5:
            return None
            
        try:
            # Unpack 2 int16 values and 1 uint8
            x, y = struct.unpack('<2h', data[0:4])
            button = data[4]
            return cls(x=x, y=y, button_state=button, raw_data=data)
        except Exception as e:
            print(f"Error parsing joystick data: {e}")
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
        debug_text += f"X: {self.x}\n"
        debug_text += f"Y: {self.y}\n"
        debug_text += f"Button: {'Pressed' if self.button_state else 'Released'}"
        return debug_text

class ButtonsData:
    """Model class representing buttons data"""
    
    def __init__(self, states=None, raw_data=None):
        # Array of 4 button states (0 = Not detected, 1 = detected)
        self.states = states if states else [0] * 4
        self.raw_data = raw_data
        
    @classmethod
    def from_bytes(cls, data):
        """Create ButtonsData object from byte array
        
        Data format (4 bytes total):
        - Button 1-4 states: uint8 (1 byte each)
        """
        if not data or len(data) != 4:
            return None
            
        try:
            # Each byte represents one button state
            states = list(data)
            return cls(states=states, raw_data=data)
        except Exception as e:
            print(f"Error parsing buttons data: {e}")
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
        for i, state in enumerate(self.states, 1):
            debug_text += f"Button {i}: {'Pressed' if state else 'Released'}\n"
        return debug_text
