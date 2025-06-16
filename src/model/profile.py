class DeviceProfile:
    """Model class representing complete device profile information"""

    _instance = None

    def __new__(cls, address=None, name="Unknown", rssi=0):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, address=None, name="Unknown", rssi=0):
        if self._initialized:
            return
        self._initialized = True
        # Basic device info
        self.address = address
        self.name = name
        self.rssi = rssi

        # Device identification
        self.firmware = "--"
        self.model = "--"
        self.manufacturer = "--"
        self.hardware = "--"

        # Status information
        self.connection_status = "Disconnected"
        self.battery_level = 0
        self.charging_state = "Not Charging"

    @classmethod
    def get_instance(cls):
        """Get the singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def from_discovered_device(cls, device):
        """Create from discovered BLE device"""
        return cls(
            address=device.address,
            name=device.name or "Unknown Device",
            rssi=device.rssi or 0,
        )

    def update_battery(self, level):
        """Update battery level"""
        self.battery_level = level

    def update_charging(self, state):
        """Update charging state"""
        self.charging_state = state

    def update_connection_status(self, status):
        """Update connection status"""
        self.connection_status = status

    def update_device_info(
        self, firmware=None, model=None, manufacturer=None, hardware=None
    ):
        """Update device identification information"""
        if firmware:
            self.firmware = firmware
        if model:
            self.model = model
        if manufacturer:
            self.manufacturer = manufacturer
        if hardware:
            self.hardware = hardware

    def get_display_info(self):
        """Get information formatted for display"""
        return {
            "name": self.name,
            "status": self.connection_status,
            "battery": f"{self.battery_level}%" if self.battery_level else "--",
            "charging": self.charging_state,
            "firmware": self.firmware,
            "model": self.model,
            "manufacturer": self.manufacturer,
            "hardware": self.hardware,
        }
