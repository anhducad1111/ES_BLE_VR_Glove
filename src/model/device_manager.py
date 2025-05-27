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

    async def start_services(self):
        """Start all device services after connection"""
        try:
            # Start overall status notifications first
            await self.presenters['overall_status'].start_notifications()
            
            # Start IMU notifications
            await self.presenters['imu1'].start_notifications()
            await self.presenters['imu2'].start_notifications()
            
            # Start sensor notifications
            await self.presenters['sensor'].start_notifications()
            
            # Start gamepad notifications
            await self.presenters['gamepad'].start_notifications()
            
            # Read initial device timestamp
            await self.presenters['timestamp'].read_timestamp()
            
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
