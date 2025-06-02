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
        
    async def _start_delayed_services(self, device_info, message):
        """Start services and update views after connection delay"""
        # 1. Start device services
        if hasattr(self.service, 'start_services'):
            result = await self.service.start_services()
            if not result:
                message = "Service initialization failed"
                if hasattr(self.view, 'connection_dialog') and self.view.connection_dialog:
                    self.view.connection_dialog.connection_success = False
                    self.view.connection_dialog.status_dialog.show_failed()
                await self.disconnect()
                return False

            # 2. Update main view after services start
            self.view.update_connection_status(True, device_info, message)
            self.view.start_heartbeat()

            # 3. Start battery notifications last
            await self.service.start_battery_notifications(device_info)

        return True

    async def connect_to_device(self, device_info):
        """Connect to selected device with delayed main view updates"""
        # 1. Basic connection only
        device_info.view = self.view
        result = await self.service.connect(device_info)
        if not result:
            message = "Connection failed"
            if hasattr(self.view, 'connection_dialog') and self.view.connection_dialog:
                self.view.connection_dialog.connection_success = False
                self.view.connection_dialog.status_dialog.show_failed()
            return False

        # 2. Show connection success in dialog immediately
        message = f"Connected to {device_info.name}"
        if hasattr(self.view, 'connection_dialog') and self.view.connection_dialog:
            self.view.connection_dialog.connection_success = True
            self.view.connection_dialog.status_dialog.show_connected(device_info)

        # 3. Delay before starting services and updating main view
        await asyncio.sleep(5)  # 5 second delay

        # 4. Start delayed services and updates
        return await self._start_delayed_services(device_info, message)

        
    async def disconnect(self):
        """Disconnect from current device"""
        try:
            # Stop heartbeat monitoring before disconnecting
            self.view.stop_heartbeat()
            
            # Stop battery notifications
            await self.service.stop_battery_notifications()

            # Clear all displays including battery status
            self.view.clear_displays()

            # Disconnect from device
            result = await self.service.disconnect()
            return result
            
        except Exception as e:
            print(f"Error during disconnect: {e}")
            return False
        
    def is_connected(self):
        """Check if device is connected"""
        return self.service.is_connected()
        
    def get_connected_device(self):
        """Get currently connected device info"""
        return self.service.connected_device
