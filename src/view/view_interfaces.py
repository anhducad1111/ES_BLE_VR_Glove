from abc import ABC, abstractmethod

class IMUViewInterface(ABC):
    """Interface for IMU data display views"""
    
    @abstractmethod
    def update_accel(self, x, y, z):
        """Update accelerometer values"""
        pass
        
    @abstractmethod
    def update_gyro(self, x, y, z):
        """Update gyroscope values"""
        pass
        
    @abstractmethod
    def update_magn(self, x, y, z):
        """Update magnetometer values"""
        pass
        
    @abstractmethod
    def update_debug_text(self, text):
        """Update debug text display"""
        pass
    
    @abstractmethod
    def set_button_states(self, enabled):
        """Enable/disable buttons"""
        pass

class ConnectionViewInterface(ABC):
    """Interface for connection-related UI"""
    
    @abstractmethod
    def update_connection_status(self, connected, device_info=None, message=""):
        """Update connection status display"""
        pass
    
    @abstractmethod
    def clear_values(self):
        """Clear all values"""
        pass
        
    @abstractmethod
    def set_heartbeat_handler(self, handler):
        """Set handler for heartbeat monitoring"""
        pass
        
    @abstractmethod
    def start_heartbeat(self):
        """Start heartbeat monitoring"""
        pass
        
    @abstractmethod
    def stop_heartbeat(self):
        """Stop heartbeat monitoring"""
        pass
        
    @abstractmethod
    def show_connection_lost(self):
        """Show UI elements for lost connection"""
        pass
        

class TimestampViewInterface(ABC):
    """Interface for timestamp display"""
    
    @abstractmethod
    def update_timestamp_display(self, formatted_text):
        """Update timestamp display with formatted text"""
        pass
    
    @abstractmethod
    def set_button_states(self, enabled):
        """Enable/disable timestamp buttons"""
        pass
