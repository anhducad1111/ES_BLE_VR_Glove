from typing import Optional, Callable, Dict, Any
from datetime import datetime, timedelta
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
    """BLE service for device communication with verification logging"""
    
    def __init__(self):
        """Initialize BLE service"""
        self.config = BLEConfig()
        self.parser = DataParser(self.config)
        self.logger = DebugLogger()
        self.client: Optional[BleakClient] = None
        self.callbacks: Dict[str, NotifyCallback] = {}
        self._connected = False
        self.connect_time: Optional[datetime] = None
        self.reconnect_attempts = 0
        self.discovery_start: Optional[datetime] = None
        self.logger.start_test()
        
    @property
    def connected(self) -> bool:
        """Get connection status"""
        return self._connected
        
    async def connect(self, address: str) -> bool:
        """Connect to device"""
        try:
            start_time = datetime.now()
            
            # Track discovery time on first attempt
            if not self.discovery_start:
                self.discovery_start = start_time
                self.logger.info(f"Starting device discovery: {address}")
            
            self.logger.info(f"Connecting to device: {address}")
            self.client = BleakClient(address)
            await self.client.connect()
            self._connected = True
            self.connect_time = datetime.now()
            
            # Log metrics
            connect_time = (self.connect_time - start_time).total_seconds()
            self.logger.log_connection(address, connect_time)
            
            if self.discovery_start:
                discovery_time = (self.connect_time - self.discovery_start).total_seconds()
                self.logger.log_discovery(address, discovery_time)
            
            # Reset reconnection count on successful connection
            if self.reconnect_attempts > 0:
                self.logger.info(f"Successfully reconnected after {self.reconnect_attempts} attempts")
                self.reconnect_attempts = 0
                
            return True
            
        except Exception as e:
            self.logger.error(f"Connection error: {e}")
            self._connected = False
            
            # Track reconnection attempts
            if self.reconnect_attempts < 5:
                self.reconnect_attempts += 1
                time_taken = (datetime.now() - start_time).total_seconds()
                self.logger.log_reconnection(address, time_taken, self.reconnect_attempts)
                
            return False
            
    async def disconnect(self) -> None:
        """Disconnect from device"""
        if self.client and self.connect_time:
            self.logger.info("Disconnecting device...")
            # Calculate uptime
            uptime = datetime.now() - self.connect_time
            
            # Stop all notifications
            for uuid in list(self.callbacks.keys()):
                await self.stop_notify(uuid)
                
            await self.client.disconnect()
            self._connected = False
            
            # Log disconnection metrics
            if hasattr(self.client, "address"):
                self.logger.log_disconnect(self.client.address, uptime)
                
            self.client = None
            self.connect_time = None
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
            
        # Log discovered services
        self.logger.debug(f"Discovered services: {services}")
        return services
        
    async def read_characteristic(self, uuid: str) -> Optional[bytes]:
        """Read characteristic value"""
        if not self.client:
            return None
            
        try:
            start_time = datetime.now()
            data = await self.client.read_gatt_char(uuid)
            
            if data:
                # Get characteristic type from UUID
                char_type = self._get_characteristic_type(uuid)
                
                # Parse and log data
                parsed = self.parser.parse_data(data, uuid)
                self.logger.log_data(uuid, data, parsed)
                
                # Log control metrics if needed
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                if char_type in ["joystick", "buttons"]:
                    metric_data = {
                        "response_time": response_time,
                        "data": parsed
                    }
                    self.logger.log_control_data(char_type.title(), metric_data)
                
                return data
                
        except Exception as e:
            self.logger.error(f"Read error: {e}")
            return None
            
    def _get_characteristic_type(self, uuid: str) -> str:
        """Get characteristic type from UUID"""
        for name, char_uuid in self.config.characteristics.items():
            if char_uuid == uuid:
                return name.lower().replace("_uuid", "")
        return "unknown"
        
    async def write_characteristic(self, uuid: str, data: bytes) -> bool:
        """Write to characteristic"""
        if not self.client:
            return False
            
        try:
            start_time = datetime.now()
            self.logger.debug(f"Writing to {uuid}: {' '.join(f'{b:02x}' for b in data)}")
            
            await self.client.write_gatt_char(uuid, data)
            
            # Log write timing
            write_time = (datetime.now() - start_time).total_seconds() * 1000
            self.logger.debug(f"Write successful in {write_time:.2f}ms")
            return True
            
        except Exception as e:
            self.logger.error(f"Write error: {e}")
            return False
            
    async def start_notify(self, uuid: str, callback: Callable[[str, Any, bytes], None]) -> bool:
        """Start notifications for characteristic"""
        if not self.client:
            return False
            
        try:
            self.logger.info(f"Starting notifications for {uuid}")
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