from typing import Optional, Callable, Dict, Any
from bleak import BleakClient
from .ble_config import BLEConfig
from .data_parser import DataParser, DataType
from .debug_logger import DebugLogger

class NotifyCallback:
    """Callback wrapper for notifications"""
    def __init__(self, uuid: str, callback: Callable):
        self.uuid = uuid
        self.callback = callback
        
    def __call__(self, sender: Any, data: bytes):
        self.callback(self.uuid, sender, data)

class BLEService:
    """BLE service for device communication"""
    
    def __init__(self):
        """Initialize BLE service"""
        self.config = BLEConfig()
        self.parser = DataParser(self.config)
        self.logger = DebugLogger()
        self.client: Optional[BleakClient] = None
        self.callbacks: Dict[str, NotifyCallback] = {}
        self._connected = False
        self.logger.info("BLE Service initialized")
        
    @property
    def connected(self) -> bool:
        """Get connection status"""
        return self._connected
        
    async def connect(self, address: str) -> bool:
        """Connect to device"""
        try:
            self.logger.info(f"Connecting to device: {address}")
            self.client = BleakClient(address)
            await self.client.connect()
            self._connected = True
            self.logger.info("Device connected successfully")
            return True
        except Exception as e:
            self.logger.error(f"Connection error: {e}")
            self._connected = False
            return False
            
    async def disconnect(self) -> None:
        """Disconnect from device"""
        if self.client:
            self.logger.info("Disconnecting device...")
            # Stop all notifications first
            for uuid in list(self.callbacks.keys()):
                await self.stop_notify(uuid)
                
            await self.client.disconnect()
            self._connected = False
            self.client = None
            self.logger.info("Device disconnected")
            
    async def discover_services(self) -> Dict[str, Any]:
        """Get all services and characteristics"""
        services = {}
        if not self.client:
            return services
            
        for service in self.client.services:
            chars = {}
            for char in service.characteristics:
                chars[str(char.uuid)] = {
                    'uuid': str(char.uuid),
                    'properties': [p for p in char.properties]
                }
            services[str(service.uuid)] = {
                'uuid': str(service.uuid),
                'characteristics': chars
            }
        return services
        
    async def read_characteristic(self, uuid: str) -> Optional[bytes]:
        """Read characteristic value"""
        if not self.client:
            return None
        try:
            data = await self.client.read_gatt_char(uuid)
            if data:
                parsed = self.parser.parse_data(data, uuid)
                self.logger.log_data(uuid, data, parsed)
            return data
        except Exception as e:
            self.logger.error(f"Read error: {e}")
            return None
            
    async def write_characteristic(self, uuid: str, data: bytes) -> bool:
        """Write to characteristic"""
        if not self.client:
            return False
        try:
            self.logger.debug(f"Writing to {uuid}: {' '.join(f'{b:02x}' for b in data)}")
            await self.client.write_gatt_char(uuid, data)
            self.logger.debug("Write successful")
            return True
        except Exception as e:
            self.logger.error(f"Write error: {e}")
            return False
            
    async def start_notify(self, uuid: str, 
                          callback: Callable[[str, Any, bytes], None]) -> bool:
        """Start notifications for characteristic"""
        if not self.client:
            return False
        try:
            self.logger.info(f"Starting notifications for {uuid}")
            # Wrap callback to include UUID
            wrapped = NotifyCallback(uuid, callback)
            self.callbacks[uuid] = wrapped
            
            await self.client.start_notify(uuid, wrapped)
            self.logger.info("Notifications started successfully")
            return True
        except Exception as e:
            self.logger.error(f"Start notify error: {e}")
            if uuid in self.callbacks:
                del self.callbacks[uuid]
            return False
            
    async def stop_notify(self, uuid: str) -> bool:
        """Stop notifications for characteristic"""
        if not self.client:
            return False
        try:
            self.logger.info(f"Stopping notifications for {uuid}")
            await self.client.stop_notify(uuid)
            if uuid in self.callbacks:
                del self.callbacks[uuid]
            self.logger.info("Notifications stopped successfully")
            return True
        except Exception as e:
            self.logger.error(f"Stop notify error: {e}")
            return False
            
    def parse_data(self, data: bytes, uuid: str = "") -> str:
        """Parse received data"""
        return self.parser.parse_data(data, uuid)
        
    def get_characteristic_uuid(self, name: str) -> str:
        """Get UUID by characteristic name"""
        return self.config.get_characteristic_uuid(name)
        
    def get_service_uuid(self, name: str) -> str:
        """Get UUID by service name"""
        return self.config.get_service_uuid(name)