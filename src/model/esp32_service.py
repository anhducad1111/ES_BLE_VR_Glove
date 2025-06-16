import asyncio

from src.config.constant import BLEConstants
from src.model.ble_service import BLEService


class ESP32BLEService(BLEService):
    """ESP32-specific BLE service implementation"""

    REQUIRED_SERVICES = BLEConstants.REQUIRED_SERVICES
    CHARACTERISTICS = BLEConstants.CHARACTERISTICS

    # Configuration maps from BLEConstants
    ACCEL_GYRO_FREQ_MAP = BLEConstants.ACCEL_GYRO_FREQ_MAP
    MAG_FREQ_MAP = BLEConstants.MAG_FREQ_MAP
    ACCEL_RANGE_MAP = BLEConstants.ACCEL_RANGE_MAP
    GYRO_RANGE_MAP = BLEConstants.GYRO_RANGE_MAP
    MAG_RANGE_MAP = BLEConstants.MAG_RANGE_MAP

    # Reverse maps for config writing
    ACCEL_GYRO_FREQ_REV_MAP = BLEConstants.ACCEL_GYRO_FREQ_REV_MAP
    MAG_FREQ_REV_MAP = BLEConstants.MAG_FREQ_REV_MAP
    ACCEL_RANGE_REV_MAP = BLEConstants.ACCEL_RANGE_REV_MAP
    GYRO_RANGE_REV_MAP = BLEConstants.GYRO_RANGE_REV_MAP
    MAG_RANGE_REV_MAP = BLEConstants.MAG_RANGE_REV_MAP

    def __init__(self):
        super().__init__()
        # Create UUID class attributes and initialize callbacks dictionary
        self._callbacks = {}
        self.loop = None  # Event loop set by presenter
        for name, (uuid, _) in self.CHARACTERISTICS.items():
            setattr(self, name, uuid)
            self._callbacks[uuid] = None

    def set_loop(self, loop):
        """Set event loop for async operations"""
        self.loop = loop

    async def start_services(self):
        """Start all device services - delegates to DeviceManager"""
        # Find the DeviceManager instance
        from src.model.device_manager import DeviceManager

        device_manager = DeviceManager()
        if device_manager and hasattr(device_manager, "start_services"):
            return await device_manager.start_services()
        return False

    async def check_services(self):
        """Check if device has all required services"""
        try:
            if not self.client or not self.client.is_connected:
                return False

            # Get available services
            print("\nChecking device services...")

            # Discovery delay and retry
            max_retries = 5
            for attempt in range(max_retries):
                # Wait for services to be discovered
                await asyncio.sleep(0.2)

                # Check if still connected
                if not self.client or not self.client.is_connected:
                    print("Lost connection during service discovery")
                    return False

                # Instead of get_services(), access services directly
                if not self.client.services:
                    print("No services found, waiting for discovery...")
                    continue

                print(
                    f"\nChecking required services (attempt {attempt + 1}/{max_retries}):"
                )
                # Get all services
                services = {
                    str(service.uuid).lower() for service in self.client.services
                }

                # Print available services
                print("Available services:")
                for service in self.client.services:
                    print(f"- {service.uuid}")

                # Check each required service
                missing_services = []
                for name, uuid in self.REQUIRED_SERVICES.items():
                    if uuid.lower() not in services:
                        print(f"❌ Missing {name} service ({uuid})")
                        missing_services.append(name)
                    else:
                        print(f"✓ Found {name} service ({uuid})")

                if not missing_services:
                    return True
                elif attempt < max_retries - 1:
                    print(f"\nRetrying service discovery...")
                else:
                    print(f"\nMissing required services: {', '.join(missing_services)}")
                    return False

            return True
        except Exception as e:
            print(f"Error checking services: {e}")
            return False

    # Implement required abstract methods
    async def check_firmware_revision(self):
        """Check firmware revision string"""
        return await self._read_characteristic_data(self.FIRMWARE_UUID)

    async def check_model_number(self):
        """Check model number string"""
        return await self._read_characteristic_data(self.MODEL_NUMBER_UUID)

    async def check_manufacturer(self):
        """Check manufacturer string"""
        return await self._read_characteristic_data(self.MANUFACTURER_UUID)

    async def check_hardware_revision(self):
        """Check hardware revision string"""
        return await self._read_characteristic_data(self.HARDWARE_UUID)

    async def read_config(self):
        """Read IMU and sensor configuration"""
        if not self.is_connected():
            return None
        try:
            data = await self.read_characteristic(self.CONFIG_UUID)
            if not data or len(data) < 15:  # Must have at least 15 bytes
                return None
            return data
        except Exception as e:
            print(f"Error reading config: {e}")
            return None

    async def write_config(self, data):
        """Write IMU and sensor configuration

        Args:
            data (bytes): 15 bytes configuration data
        Returns:
            bool: True if successful
        """
        if not self.is_connected() or not data or len(data) != 15:
            return False
        try:
            await self.write_characteristic(self.CONFIG_UUID, data)
            return True
        except Exception as e:
            print(f"Error writing config: {e}")
            return False

    async def connect(self, device_info):
        """Connect to a BLE device and check profiles with improved error handling"""
        try:
            # Clean up any existing connection and notifications
            if self.is_connected():
                await self.disconnect()
                await asyncio.sleep(1.0)  # Wait for cleanup

            # Attempt connection with retry
            max_connect_retries = 5
            result = False

            for attempt in range(max_connect_retries):
                try:
                    result = await super().connect(device_info)
                    if result:
                        break
                    if attempt < max_connect_retries - 1:
                        print(f"Connection attempt {attempt + 1} failed, retrying...")
                        await asyncio.sleep(0.5)
                except Exception as e:
                    print(f"Connection error on attempt {attempt + 1}: {e}")
                    if attempt < max_connect_retries - 1:
                        await asyncio.sleep(0.5)
                        continue
                    result = False
                    break

            if not result:
                print("Failed to establish connection after retries")
                return False

            # Wait for connection stability
            await asyncio.sleep(1.0)

            # Check for required services
            has_services = await self.check_services()
            if not has_services:
                print("Required services not found")
                await self.disconnect()
                return False

            # Additional wait for service stability
            await asyncio.sleep(0.5)

            try:
                # Read device profiles
                print("Reading device profiles...")
                device_info.firmware = await self.check_firmware_revision()
                device_info.model = await self.check_model_number()
                device_info.manufacturer = await self.check_manufacturer()
                device_info.hardware = await self.check_hardware_revision()
            except Exception as e:
                print(f"Warning: Error reading device profiles: {e}")
                # Continue even if profile reading fails

            return True

        except Exception as e:
            print(f"Fatal error during connection process: {e}")
            await self.disconnect()
            return False

    async def start_profile_notifications(self, view):
        """Start all profile-related notifications"""
        if not view:
            return False

        try:
            # Pass non-async view methods directly
            await self._start_notify_generic(
                self.BATTERY_LEVEL_UUID, view.update_battery
            )
            await self._start_notify_generic(
                self.BATTERY_CHARGING_UUID, view.update_charging
            )
            return True
        except Exception as e:
            print(f"Error starting profile notifications: {e}")
            return False

    async def _read_characteristic_data(self, uuid):
        """Generic method to read and parse characteristic data"""
        if not self.is_connected():
            return None

        try:
            data = await self.read_characteristic(uuid)
            if not data:
                return None

            # Get the data class for this UUID
            data_class = next(
                (cls for _, (u, cls) in self.CHARACTERISTICS.items() if u == uuid), None
            )
            if not data_class:
                return None

            # Handle string data types
            if data_class == str:
                return data.decode("utf-8")

            # Handle data model classes
            return data_class.from_bytes(data)

        except Exception as e:
            print(f"Error reading characteristic {uuid}: {e}")
            return None

    async def _write_characteristic_data(self, uuid, data):
        """Generic method to write characteristic data"""
        if not self.is_connected() or not data:
            return False

        try:
            # Handle data objects with raw_data attribute
            raw_data = data.raw_data if hasattr(data, "raw_data") else data
            await self.write_characteristic(uuid, raw_data)
            return True
        except Exception as e:
            print(f"Error writing characteristic {uuid}: {e}")
            return False

    async def _generic_notification_handler(
        self, sender, data, callback, data_class, uuid
    ):
        """Generic handler for notifications"""
        try:
            # Handle battery notifications directly (non-async)
            if uuid == self.BATTERY_LEVEL_UUID:
                callback(int(data[0]))  # Raw battery level (0-100)
                return
            elif uuid == self.BATTERY_CHARGING_UUID:
                callback("Charging" if data[0] == 1 else "Not Charging")
                return

            # For other notifications that need data classes
            if data_class is None:
                print(f"No data class for UUID {uuid}")
                return

            if data_class == str:
                parsed_data = data.decode("utf-8")
            else:
                parsed_data = data_class.from_bytes(data)

            if parsed_data and callback:
                await callback(sender, parsed_data)

        except Exception as e:
            # Get characteristic name for better error messages
            char_name = next(
                (name for name, (u, _) in self.CHARACTERISTICS.items() if u == uuid),
                str(uuid),
            )
            print(f"Error in {char_name} notification handler: {e}")

    async def _start_notify_generic(self, uuid, callback, retries=5, delay=0.2):
        """Generic method to start notifications with retry logic"""
        if not self.is_connected():
            return False

        for attempt in range(retries):
            try:
                data_class = next(
                    (cls for _, (u, cls) in self.CHARACTERISTICS.items() if u == uuid),
                    None,
                )
                self._callbacks[uuid] = callback

                async def handler(sender, data):
                    try:
                        if self.loop and not self.loop.is_closed():
                            await self._generic_notification_handler(
                                sender, data, callback, data_class, uuid
                            )
                    except Exception as e:
                        print(f"Error in notification handler for {uuid}: {e}")

                await asyncio.sleep(0.1)  # Small delay before starting
                await self.client.start_notify(uuid, handler)
                print(f"✓ Started notifications for {uuid}")
                return True

            except Exception as e:
                print(
                    f"Error starting notifications for {uuid} (attempt {attempt + 1}/{retries}): {e}"
                )
                if attempt < retries - 1:
                    await asyncio.sleep(delay)
                    print(f"Retrying...")
                continue

        print(f"❌ Failed to start notifications for {uuid} after {retries} attempts")
        return False

    async def _stop_notify_generic(self, uuid):
        """Generic method to stop notifications"""
        if not self.client:  # Already disconnected
            self._callbacks[uuid] = None
            return True

        try:
            await self.client.stop_notify(uuid)
            self._callbacks[uuid] = None
            return True
        except Exception as e:
            if hasattr(e, "args") and len(e.args) > 0:
                err_code = str(e.args[0])
                if err_code == "61":  # Already stopped
                    self._callbacks[uuid] = None
                    return True
            print(f"Error stopping notifications for {uuid}: {e}")
            return False

    async def _start_battery_notifications(self, view):
        """Start battery notifications using view directly"""
        await self._start_notify_generic(self.BATTERY_LEVEL_UUID, view.update_battery)
        await self._start_notify_generic(
            self.BATTERY_CHARGING_UUID, view.update_charging
        )

    async def stop_battery_notifications(self):
        """Stop battery and charging notifications"""
        await self._stop_notify_generic(self.BATTERY_LEVEL_UUID)
        await self._stop_notify_generic(self.BATTERY_CHARGING_UUID)

    # IMU Methods
    async def start_imu1_notify(self, callback):
        """Start IMU1 notifications"""
        return await self._start_notify_generic(self.IMU1_CHAR_UUID, callback)

    async def start_imu2_notify(self, callback):
        """Start IMU2 notifications"""
        return await self._start_notify_generic(self.IMU2_CHAR_UUID, callback)

    async def stop_imu1_notify(self):
        """Stop IMU1 notifications"""
        return await self._stop_notify_generic(self.IMU1_CHAR_UUID)

    async def stop_imu2_notify(self):
        """Stop IMU2 notifications"""
        return await self._stop_notify_generic(self.IMU2_CHAR_UUID)

    # IMU Euler Methods
    async def start_imu1_euler_notify(self, callback):
        """Start IMU1 Euler angles notifications"""
        return await self._start_notify_generic(self.IMU1_EULER_UUID, callback)

    async def start_imu2_euler_notify(self, callback):
        """Start IMU2 Euler angles notifications"""
        return await self._start_notify_generic(self.IMU2_EULER_UUID, callback)

    async def stop_imu1_euler_notify(self):
        """Stop IMU1 Euler angles notifications"""
        return await self._stop_notify_generic(self.IMU1_EULER_UUID)

    async def stop_imu2_euler_notify(self):
        """Stop IMU2 Euler angles notifications"""
        return await self._stop_notify_generic(self.IMU2_EULER_UUID)

    # Overall Status Methods
    async def start_overall_status_notify(self, callback):
        """Start overall status notifications"""
        return await self._start_notify_generic(self.OVERALL_STATUS_UUID, callback)

    async def stop_overall_status_notify(self):
        """Stop overall status notifications"""
        return await self._stop_notify_generic(self.OVERALL_STATUS_UUID)

    # Sensor Notification Methods
    async def start_flex_sensor_notify(self, callback):
        """Enable flex sensor data notifications"""
        return await self._start_notify_generic(self.FLEX_SENSOR_UUID, callback)

    async def start_force_sensor_notify(self, callback):
        """Enable force sensor data notifications"""
        return await self._start_notify_generic(self.FORCE_SENSOR_UUID, callback)

    async def stop_flex_sensor_notify(self):
        """Disable flex sensor data notifications"""
        return await self._stop_notify_generic(self.FLEX_SENSOR_UUID)

    async def stop_force_sensor_notify(self):
        """Disable force sensor data notifications"""
        return await self._stop_notify_generic(self.FORCE_SENSOR_UUID)

    # Gamepad Input Methods
    async def start_joystick_notify(self, callback):
        """Enable joystick input notifications"""
        return await self._start_notify_generic(self.JOYSTICK_UUID, callback)

    async def start_buttons_notify(self, callback):
        """Enable button press notifications"""
        return await self._start_notify_generic(self.BUTTONS_UUID, callback)

    async def stop_joystick_notify(self):
        """Disable joystick input notifications"""
        return await self._stop_notify_generic(self.JOYSTICK_UUID)

    async def stop_buttons_notify(self):
        """Disable button press notifications"""
        return await self._stop_notify_generic(self.BUTTONS_UUID)

    # Configuration Methods
    async def start_config_notify(self, callback):
        """Enable configuration change notifications"""
        return await self._start_notify_generic(self.CONFIG_UUID, callback)

    async def stop_config_notify(self):
        """Disable configuration change notifications"""
        return await self._stop_notify_generic(self.CONFIG_UUID)

    # Data Reading Methods
    async def read_imu1(self):
        """Read current IMU1 sensor data"""
        return await self._read_characteristic_data(self.IMU1_CHAR_UUID)

    async def read_imu2(self):
        """Read current IMU2 sensor data"""
        return await self._read_characteristic_data(self.IMU2_CHAR_UUID)

    async def read_timestamp(self):
        """Read current timestamp value"""
        return await self._read_characteristic_data(self.TIMESTAMP_CHAR_UUID)

    async def write_timestamp(self, timestamp_data):
        """Update device timestamp"""
        return await self._write_characteristic_data(
            self.TIMESTAMP_CHAR_UUID, timestamp_data
        )

    async def read_device_name(self):
        """Read device name for connection heartbeat"""
        try:
            return await self.read_characteristic(self.MODEL_NUMBER_UUID)
        except Exception:
            return None
