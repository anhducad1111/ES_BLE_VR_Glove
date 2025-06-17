import asyncio

from src.model.device_manager import DeviceManager


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
                    profile = self.get_connected_device()
                    if not profile:
                        print("No device profile available for reconnection")
                        await self.disconnect()
                        break

                    print("\nConnection lost, attempting auto-reconnection...")
                    profile.update_connection_status("Connection Lost")

                    # Stop logging if active before showing connection lost
                    if hasattr(self.view, "_stop_logging"):
                        self.view._stop_logging()

                    self.view.show_connection_lost()

                    # Stop services before attempting reconnection
                    if hasattr(self.service, "start_services"):
                        await self.service.disconnect()
                        await asyncio.sleep(1)  # Wait for cleanup

                    # Try reconnecting up to MAX_RECONNECT_ATTEMPTS times
                    for attempt in range(MAX_RECONNECT_ATTEMPTS):
                        print(
                            f"\nAuto-reconnection attempt {attempt + 1}/{MAX_RECONNECT_ATTEMPTS}"
                        )
                        profile.update_connection_status(
                            f"Reconnecting (Attempt {attempt + 1})"
                        )

                        # Attempt to reconnect
                        if await self.service.connect(profile):
                            # Start device services after reconnection
                            if hasattr(self.service, "start_services"):
                                if await self.service.start_services():
                                    print("Auto-reconnection successful")
                                    break

                        if attempt < MAX_RECONNECT_ATTEMPTS - 1:
                            print(
                                f"Waiting {RECONNECT_DELAY} seconds before next attempt..."
                            )
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

    async def _start_delayed_services(self, profile, message):
        """Start services and update views after OK is clicked"""

        device_manager = DeviceManager()
        self.view.update_connection_status(True, profile, message)
        result = await device_manager.start_device_services()

        if not result:
            message = "Service initialization failed"
            profile.update_connection_status("Failed")
            await self.disconnect()
            return False

        self.view.start_heartbeat()

        return True

    def _on_ok_clicked(self, profile, message):
        """Handle OK button click in connection dialog"""
        # Start services in background
        if self.loop:
            profile.update_connection_status("Starting services...")
            self.loop.create_task(self._start_delayed_services(profile, message))

    async def connect_to_device(self, device_info):
        """Connect to selected device with delayed main view updates"""
        # Create device profile through presenter
        device_manager = DeviceManager()
        profile = device_manager.presenters["profile"].create_profile(device_info)
        profile.update_connection_status("Connecting...")

        # 1. Basic connection only
        result = await self.service.connect(profile)
        if not result:
            message = "Connection failed"
            if hasattr(self.view, "connection_dialog") and self.view.connection_dialog:
                self.view.connection_dialog.connection_success = False
                self.view.connection_dialog.status_dialog.show_failed()
            return False

        # 2. Show connection success and start countdown
        message = f"Connected to {profile.name}"
        profile.update_connection_status("Connected")

        if hasattr(self.view, "connection_dialog") and self.view.connection_dialog:
            self.view.connection_dialog.connection_success = True
            # Set callback for countdown completion
            self.view.connection_dialog.status_dialog.set_ok_callback(
                lambda: self._on_ok_clicked(profile, message)
            )
            # Show connected state and start countdown
            self.view.connection_dialog.status_dialog.show_connected(profile)

        return True

    async def disconnect(self):
        """Disconnect from current device"""
        try:
            print("[ConnectionPresenter] Starting disconnect")
            
            # Stop heartbeat monitoring before disconnecting
            self.view.stop_heartbeat()

            # Stop logging if active before disconnecting
            if hasattr(self.view, "_stop_logging"):
                print("[ConnectionPresenter] Calling _stop_logging")
                self.view._stop_logging()
            else:
                print("[ConnectionPresenter] No _stop_logging method found")

            # Get profile before disconnecting
            profile = self.get_connected_device()
            if profile:
                profile.update_connection_status("Disconnecting...")

            # Clear all displays
            print("[ConnectionPresenter] Calling clear_values")
            self.view.clear_values()

            # Disconnect from device (this will stop all notifications)
            result = await self.service.disconnect()

            # Update profile status after disconnect
            if profile:
                profile.update_connection_status("Disconnected")

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
