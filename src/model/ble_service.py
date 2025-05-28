from bleak import BleakScanner, BleakClient
import asyncio
from src.model.imu import IMUData
from src.model.timestamp import TimestampData

class BLEDeviceInfo:
    """Model class for BLE device information"""
    
    def __init__(self, address, name="Unknown", rssi=0):
        self.address = address
        self.name = name
        self.rssi = rssi
        
    @classmethod
    def from_discovered_device(cls, device):
        """Create from discovered BLE device"""
        return cls(
            address=device.address,
            name=device.name or "Unknown Device",
            rssi=device.rssi or 0
        )

from abc import ABC, abstractmethod

class BLEProfileChecker(ABC):
    """Abstract class for checking BLE profiles"""
    
    @abstractmethod
    def check_firmware_revision(self):
        """Check firmware revision string"""
        pass
        
    @abstractmethod
    def check_model_number(self):
        """Check model number string"""
        pass
        
    @abstractmethod
    def check_manufacturer(self):
        """Check manufacturer string"""
        pass
        
    @abstractmethod
    def check_hardware_revision(self):
        """Check hardware revision string"""
        pass

class BLEService(BLEProfileChecker):
    """Model for BLE service operations"""
    
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.client = None
            self._connected = False
            self.connected_device = None
            self.initialized = True
        
    async def scan_devices(self):
        """Scan for available BLE devices"""
        try:
            devices = await BleakScanner.discover()
            return [BLEDeviceInfo.from_discovered_device(device) for device in devices]
        except Exception as e:
            print(f"Error scanning for devices: {e}")
            return []
        
    async def connect(self, device_info):
        """Connect to a BLE device"""
        try:
            self.client = BleakClient(device_info.address)
            await self.client.connect()
            if not self.client.is_connected:
                return False
                
            # Wait for service discovery
            max_retries = 3
            for attempt in range(max_retries):
                await asyncio.sleep(0.5)
                if self.client.services:
                    break
                if attempt < max_retries - 1:
                    print("Waiting for services...")
                    
            if not self.client.services:
                print("No services discovered")
                return False
                    
            self._connected = True
            self.connected_device = device_info
            return True
        except Exception as e:
            self._connected = False
            print(f"Connection error: {e}")
            return False
            
    async def disconnect(self):
        """Disconnect from the device"""
        if not self.is_connected():
            return True
            
        try:
            await self.client.disconnect()
            return True
        except Exception as e:
            print(f"Disconnection error: {e}")
            return False
        finally:
            # Always cleanup client state
            self.client = None
            self._connected = False
            self.connected_device = None
            
    def is_connected(self):
        """Check if device is connected"""
        return self.client is not None and self._connected
    
    async def read_characteristic(self, uuid):
        """Read characteristic value"""
        if not self.is_connected():
            return None
            
        try:
            return await self.client.read_gatt_char(uuid)
        except Exception as e:
            print(f"Error reading characteristic {uuid}: {e}")
            return None
            
    async def write_characteristic(self, uuid, data):
        """Write characteristic value"""
        if not self.is_connected():
            return False
            
        try:
            await self.client.write_gatt_char(uuid, data)
            return True
        except Exception as e:
            print(f"Error writing characteristic {uuid}: {e}")
            return False
            
    async def start_notify(self, uuid, callback):
        """Start notifications for a characteristic"""
        if not self.is_connected():
            return False
            
        try:
            await self.client.start_notify(uuid, callback)
            return True
        except Exception as e:
            print(f"Error starting notifications for {uuid}: {e}")
            return False
            
    async def stop_notify(self, uuid):
        """Stop notifications for a characteristic"""
        if not self.client:  # Already disconnected
            return True
            
        try:
            await self.client.stop_notify(uuid)
            return True
        except Exception as e:
            if hasattr(e, 'args') and len(e.args) > 0:
                err_code = str(e.args[0])
                if err_code == "61":  # Already stopped
                    return True
            print(f"Error stopping notifications for {uuid}: {e}")
            return False
