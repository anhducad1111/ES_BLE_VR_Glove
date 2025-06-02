import asyncio

class ConnectionPresenter:
    """Presenter for handling device connections"""
    
    def __init__(self, view, ble_service, loop):
        self.view = view
        self.service = ble_service
        self.loop = loop
        
        # Setup heartbeat handler
        self.view.set_heartbeat_handler(self._check_connection)
        
    async def _check_connection(self):
        """Periodic check of connection status with auto-reconnection"""
        MAX_RECONNECT_ATTEMPTS = 5
        RECONNECT_DELAY = 5  # seconds

        while self.service.is_connected():
            try:
                await asyncio.sleep(3)  # Check every 3 seconds
                name = await self.service.read_device_name()
                if not name:
                    device_info = self.get_connected_device()
                    if not device_info:
                        print("No device info available for reconnection")
                        await self.disconnect()
                        break

                    print("\nConnection lost, attempting auto-reconnection...")
                    self.view.show_connection_lost()

                    # Stop services before attempting reconnection
                    if hasattr(self.service, 'start_services'):
                        await self.service.disconnect()
                        await asyncio.sleep(1)  # Wait for cleanup

                    # Try reconnecting up to MAX_RECONNECT_ATTEMPTS times
                    for attempt in range(MAX_RECONNECT_ATTEMPTS):
                        print(f"\nAuto-reconnection attempt {attempt + 1}/{MAX_RECONNECT_ATTEMPTS}")
                        
                        # Attempt to reconnect
                        if await self.service.connect(device_info):
                            # Start device services after reconnection
                            if hasattr(self.service, 'start_services'):
                                if await self.service.start_services():
                                    print("Auto-reconnection successful")
                                    break
                            
                        if attempt < MAX_RECONNECT_ATTEMPTS - 1:
                            print(f"Waiting {RECONNECT_DELAY} seconds before next attempt...")
                            await asyncio.sleep(RECONNECT_DELAY)
                    else:
                        print("\nAuto-reconnection failed after all attempts")
                        await self.disconnect()
                        break

            except Exception as e:
                print(f"Connection check error: {e}")
                # Don't disconnect immediately on single error
                continue
        
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
                
            if result:
                # Start heartbeat monitoring after successful connection
                self.view.start_heartbeat()
            
            message = f"Connected to {device_info.name}"
            self.view.show_connection_status(result, device_info, message)
        else:
            message = "Connection failed"
            self.view.show_connection_status(result, None, message)
        return result
        
    async def disconnect(self):
        """Disconnect from current device"""
        # Stop heartbeat monitoring before disconnecting
        self.view.stop_heartbeat()
        
        # Disconnect from device
        result = await self.service.disconnect()
        self.view.show_connection_status(False, None, "Disconnected")
        return result
        
    def is_connected(self):
        """Check if device is connected"""
        return self.service.is_connected()
        
    def get_connected_device(self):
        """Get currently connected device info"""
        return self.service.connected_device
