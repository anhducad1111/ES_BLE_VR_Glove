import asyncio
class DeviceManager:
    """Class for managing device services and notifications"""
    
    _instance = None
    
    def __new__(cls, ble_service=None, presenters=None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, ble_service=None, presenters=None):
        """Initialize device manager
        
        Args:
            ble_service: BLE service instance
            presenters: Dictionary containing presenter instances
        """
        if not hasattr(self, 'initialized'):
            self.service = ble_service
            self.presenters = presenters
            self._verify_required_presenters()
            self.initialized = True
        
    def _verify_required_presenters(self):
        """Verify all required presenters are available"""
        required = ['overall_status', 'imu1', 'imu2', 'timestamp', 'sensor', 'connection', 'gamepad']
        for name in required:
            if name not in self.presenters:
                raise KeyError(f"Missing required presenter: {name}")

    async def _start_service_with_retry(self, service_name, max_retries=3, delay=0.5):
        """Start a service with retry logic"""
        for attempt in range(max_retries):
            try:
                if await self.presenters[service_name].start_notifications():
                    print(f"✓ Started {service_name} notifications")
                    return True
                print(f"Retrying {service_name} notifications ({attempt + 1}/{max_retries})")
                await asyncio.sleep(delay)
            except Exception as e:
                print(f"Error starting {service_name} notifications: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(delay)
        print(f"❌ Failed to start {service_name} notifications after {max_retries} attempts")
        return False

    async def start_services(self):
        """Start all device services after connection with improved error handling"""
        try:
            # Wait for services to be fully discovered
            await asyncio.sleep(1.0)

            # Start services in sequence with delays
            services = [
                'overall_status',  # Start first for device monitoring
                'imu1',           # IMU services first
                'imu2',
                'sensor',         # Then sensors
                'gamepad'         # Finally gamepad
            ]

            failures = []
            for service in services:
                if not await self._start_service_with_retry(service):
                    failures.append(service)
                await asyncio.sleep(0.5)  # Delay between services

            # Even if some services fail, try to read timestamp
            await self.presenters['timestamp'].read_timestamp()

            # Return true only if all critical services started
            critical_services = {'imu1', 'imu2'}  # IMU services are critical
            failed_critical = critical_services.intersection(failures)
            
            if failed_critical:
                print(f"Critical IMU service(s) failed to start: {', '.join(failed_critical)}")
                await self.cleanup()
                return False
                
            if failures:
                # Log non-critical failures but continue
                non_critical = set(failures) - critical_services
                if non_critical:
                    print(f"Non-critical services failed to start: {', '.join(non_critical)}")
            return True

        except Exception as e:
            print(f"Error starting device services: {e}")
            await self.cleanup()
            return False
            
    async def cleanup(self):
        """Clean up all device services"""
        try:
            # Stop overall status notifications first
            await self.presenters['overall_status'].stop_notifications()
            
            # Stop IMU notifications
            await self.presenters['imu1'].stop_notifications()
            await self.presenters['imu2'].stop_notifications()
            
            # Stop sensor notifications
            await self.presenters['sensor'].stop_notifications()
            
            # Stop gamepad notifications
            await self.presenters['gamepad'].stop_notifications()
            
            # Clear displays
            self.presenters['imu1'].view.clear_values()
            self.presenters['imu2'].view.clear_values()
            self.presenters['sensor'].clear_values()
            self.presenters['gamepad'].clear_values()
            self.presenters['overall_status'].clear_status()
            
        except Exception as e:
            print(f"Error during device cleanup: {e}")

    async def connect(self, device_info):
        """Connect to a device and start services
        
        Args:
            device_info: Dictionary containing device info
        
        Returns:
            bool: True if connection and service start successful
        """
        # Convert device_info dict to BLEDeviceInfo
        from src.model.ble_service import BLEDeviceInfo
        ble_device = BLEDeviceInfo(
            address=device_info['address'],
            name=device_info['name'],
            rssi=device_info['rssi']
        )
        
        try:
            # Connect to device
            success = await self.presenters['connection'].connect_to_device(ble_device)
            if success:
                # Start device services
                return await self.start_services()
            return False
            
        except Exception as e:
            print(f"Error connecting to device: {e}")
            return False

    async def disconnect(self):
        """Disconnect from device and cleanup"""
        try:
            # Stop all services
            await self.cleanup()
            # Disconnect from device
            await self.presenters['connection'].disconnect()
        except Exception as e:
            print(f"Error disconnecting device: {e}")

    def is_connected(self):
        """Check if device is connected"""
        return self.service and self.service.is_connected()
