import asyncio

class ConnectionPresenter:
    """Presenter for handling device connections"""
    
    def __init__(self, view, ble_service, loop):
        self.view = view
        self.service = ble_service
        self.loop = loop
        
    async def scan_for_devices(self):
        """Scan for nearby BLE devices"""
        self.view.show_scanning()
        devices = await self.service.scan_devices()
        self.view.show_devices(devices)
        
    async def connect_to_device(self, device_info):
        """Connect to selected device"""
        # Attach view to device_info for notifications
        device_info.view = self.view
        
        result = await self.service.connect(device_info)
        if result:
            # Start device services after successful connection
            if hasattr(self.service, 'start_services'):
                result = await self.service.start_services()
            
            message = f"Connected to {device_info.name}"
            self.view.show_connection_status(result, device_info, message)
        else:
            message = "Connection failed"
            self.view.show_connection_status(result, None, message)
        return result
        
    async def disconnect(self):
        """Disconnect from current device"""
        if hasattr(self.service, 'stop_battery_notify'):
            await self.service.stop_battery_notify()
        result = await self.service.disconnect()
        self.view.show_connection_status(False, None, "Disconnected")
        return result
        
    def is_connected(self):
        """Check if device is connected"""
        return self.service.is_connected()
        
    def get_connected_device(self):
        """Get currently connected device info"""
        return self.service.connected_device
