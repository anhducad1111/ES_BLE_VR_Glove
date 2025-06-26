"""ESP32 BLE Service Implementation"""

import asyncio

from src.config.constant import BLEConstants as C
from src.model.ble_service import BLEService
from src.model.device_manager import DeviceManager


class ESP32BLEService(BLEService):
    """ESP32 BLE service for VR glove device"""

    REQUIRED_SERVICES = C.REQUIRED_SERVICES
    CHARACTERISTICS = C.CHARACTERISTICS

    # Config maps
    locals().update(
        {
            name: getattr(C, name)
            for name in [
                "ACCEL_GYRO_FREQ_MAP",
                "MAG_FREQ_MAP",
                "ACCEL_RANGE_MAP",
                "GYRO_RANGE_MAP",
                "MAG_RANGE_MAP",
                "ACCEL_GYRO_FREQ_REV_MAP",
                "MAG_FREQ_REV_MAP",
                "ACCEL_RANGE_REV_MAP",
                "GYRO_RANGE_REV_MAP",
                "MAG_RANGE_REV_MAP",
            ]
        }
    )

    # Notification types for dynamic method generation
    _NOTIFY_TYPES = [
        "imu1",
        "imu2",
        "imu1_euler",
        "imu2_euler",
        "flex_sensor",
        "force_sensor",
        "joystick",
        "buttons",
        "config",
        "overall_status",
        "battery_level",
        "battery_charging",
    ]

    def __init__(self):
        super().__init__()
        self._callbacks = {}
        self.loop = None

        # Set UUIDs as attributes
        for name, (uuid, _) in self.CHARACTERISTICS.items():
            setattr(self, name, uuid)
            self._callbacks[uuid] = None
            # Generate notification methods dynamically
        self._generate_notification_methods()

    def _generate_notification_methods(self):
        """Dynamically generate notification start/stop methods"""
        for notify_type in self._NOTIFY_TYPES:
            uuid_attr = f"{notify_type.upper()}_UUID"
            if hasattr(self, uuid_attr):
                uuid = getattr(self, uuid_attr)

                # Create start method
                def start_method(cb, u=uuid):
                    return self._start_notify_generic(u, cb)

                setattr(self, f"start_{notify_type}_notify", start_method)

                # Create stop method
                def stop_method(u=uuid):
                    return self._stop_notify_generic(u)

                setattr(self, f"stop_{notify_type}_notify", stop_method)

    def set_loop(self, loop):
        """Set event loop for async operations"""
        self.loop = loop

    async def start_services(self):
        """Start all device services"""

        device_manager = DeviceManager()
        return (
            await device_manager.start_services()
            if device_manager and hasattr(device_manager, "start_services")
            else False
        )

    async def check_services(self):
        """Check if device has all required services"""
        if not self.client or not self.client.is_connected:
            return False

        for attempt in range(5):
            await asyncio.sleep(0.2)
            if not self.client or not self.client.is_connected:
                return False

            if not self.client.services:
                continue

            services = {str(service.uuid).lower() for service in self.client.services}
            missing = [
                name
                for name, uuid in self.REQUIRED_SERVICES.items()
                if uuid.lower() not in services
            ]

            if not missing:
                return True
            elif attempt == 4:
                return False
        return True  # Generic data read/write methods

    async def _read_data(self, uuid):
        """Generic data reading"""
        if not self.is_connected():
            return None
        try:
            data = await self.read_characteristic(uuid)
            if not data:
                return None
            data_class = next(
                (cls for _, (u, cls) in self.CHARACTERISTICS.items() if u == uuid), None
            )
            return (
                data.decode("utf-8")
                if data_class == str
                else data_class.from_bytes(data) if data_class else None
            )
        except:
            return None

    async def _write_data(self, uuid, data):
        """Generic data writing"""
        if not self.is_connected() or not data:
            return False
        try:
            raw_data = data.raw_data if hasattr(data, "raw_data") else data
            await self.write_characteristic(uuid, raw_data)
            return True
        except:
            return False

    # Profile methods using generic read
    async def check_firmware_revision(self):
        return await self._read_data(self.FIRMWARE_UUID)

    async def check_model_number(self):
        return await self._read_data(self.MODEL_NUMBER_UUID)

    async def check_manufacturer(self):
        return await self._read_data(self.MANUFACTURER_UUID)

    async def check_hardware_revision(self):
        return await self._read_data(self.HARDWARE_UUID)  # Config methods

    async def read_config(self):
        """Read IMU and sensor configuration"""
        if not self.is_connected():
            return None
        try:
            data = await self.read_characteristic(self.CONFIG_UUID)
            return data if data and len(data) >= 15 else None
        except:
            return None

    async def write_config(self, data):
        """Write IMU and sensor configuration"""
        return (
            await self._write_data(self.CONFIG_UUID, data)
            if data and len(data) == 15
            else False
        )

    async def connect(self, device_info):
        """Connect to device with retry logic"""
        try:
            if self.is_connected():
                await self.disconnect()
                await asyncio.sleep(1.0)

            # Connection retry
            for attempt in range(3):
                try:
                    if await super().connect(device_info):
                        break
                    if attempt < 2:
                        await asyncio.sleep(0.5)
                except Exception:
                    if attempt < 2:
                        await asyncio.sleep(0.5)
                        continue
                    return False
            else:
                return False

            await asyncio.sleep(1.0)

            # Check services
            if not await self.check_services():
                await self.disconnect()
                return False

            await asyncio.sleep(0.5)

            # Read profiles
            try:
                device_info.firmware = await self.check_firmware_revision()
                device_info.model = await self.check_model_number()
                device_info.manufacturer = await self.check_manufacturer()
                device_info.hardware = await self.check_hardware_revision()
            except:
                pass  # Continue even if profile reading fails

            return True
        except:
            await self.disconnect()
            return False

    async def start_profile_notifications(self, view):
        """Start battery and charging notifications"""
        if not view:
            return False
        try:
            await self._start_notify_generic(
                self.BATTERY_LEVEL_UUID, view.update_battery
            )
            await self._start_notify_generic(
                self.BATTERY_CHARGING_UUID, view.update_charging
            )
            return True
        except:
            return False  # Simplified notification handler

    async def _notification_handler(self, sender, data, callback, data_class, uuid):
        """Unified notification handler"""
        try:
            if uuid == self.BATTERY_LEVEL_UUID:
                callback(int(data[0]))
            elif uuid == self.BATTERY_CHARGING_UUID:
                callback("Charging" if data[0] == 1 else "Not Charging")
            else:
                parsed_data = (
                    data.decode("utf-8")
                    if data_class == str
                    else data_class.from_bytes(data) if data_class else None
                )
                if parsed_data and callback:
                    await callback(sender, parsed_data)
        except:
            pass  # Silent fail for notifications

    async def _start_notify_generic(self, uuid, callback, retries=5):
        """Generic notification starter with retry"""
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
                    if self.loop and not self.loop.is_closed():
                        await self._notification_handler(
                            sender, data, callback, data_class, uuid
                        )

                await asyncio.sleep(0.1)
                await self.client.start_notify(uuid, handler)
                return True
            except:
                if attempt < retries - 1:
                    await asyncio.sleep(0.2)
                    continue
        return False

    async def _stop_notify_generic(self, uuid):
        """Generic notification stopper"""
        if not self.client:
            self._callbacks[uuid] = None
            return True
        try:
            await self.client.stop_notify(uuid)
            self._callbacks[uuid] = None
            return True
        except:
            self._callbacks[uuid] = None
            return False  # Data reading methods using generic reader

    def read_imu1(self):
        return self._read_data(self.IMU1_CHAR_UUID)

    def read_imu2(self):
        return self._read_data(self.IMU2_CHAR_UUID)

    def read_timestamp(self):
        return self._read_data(self.TIMESTAMP_CHAR_UUID)

    def write_timestamp(self, data):
        return self._write_data(self.TIMESTAMP_CHAR_UUID, data)

    def read_device_name(self):
        return (
            self.read_characteristic(self.MODEL_NUMBER_UUID)
            if self.is_connected()
            else None
        )
