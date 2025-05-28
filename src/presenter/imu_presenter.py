import asyncio
from src.model.imu import IMUData, IMUEulerData
from src.view.imu_config_dialog import IMUConfigDialog

class IMUPresenter:
    """Presenter for IMU data operations"""
    
    def __init__(self, view, ble_service, characteristic_uuid, loop):
        self.view = view
        self.service = ble_service
        self.view.imu_service = ble_service  # Set service for configuration
        self.view.loop = loop  # Set event loop for async operations
        ble_service.set_loop(loop)  # Set event loop for service notifications
        self.char_uuid = characteristic_uuid
        self.euler_uuid = characteristic_uuid.replace("CHAR", "EULER")
        self.loop = loop
        self.notifying = False
        self.euler_notifying = False
        self.log_dialog = None
        self.latest_imu_data = None
        self.latest_euler_data = None
        
        # Initially disable buttons until connection is established
        self.view.set_button_states(False)
        
    async def read_data(self):
        """Read IMU data once"""
        if not self.service.is_connected():
            return False
            
        data = await self.service.read_characteristic(self.char_uuid)
        if data:
            imu_data = IMUData.from_bytes(data)
            if imu_data:
                self._update_view(imu_data)
                return True
        return False
        
    async def start_notifications(self):
        """Start notifications"""
        if not self.service.is_connected():
            self.view.set_button_states(False)
            return False
            
        # First stop any existing notifications to ensure clean state
        if self.notifying:
            await self.stop_notifications()
            
        result = await self.service.start_notify(
            self.char_uuid, 
            self._notification_handler
        )
        
        if result:
            self.notifying = True
            self.view.set_button_states(True)
            
            # Optionally start Euler notifications too
            if hasattr(self.view, 'update_euler'):
                await self.start_euler_notifications()
                
        return result

    async def start_euler_notifications(self):
        """Start Euler angle notifications"""
        if not self.service.is_connected():
            return False

        # First stop any existing notifications to ensure clean state
        if self.euler_notifying:
            await self.stop_euler_notifications()

        # Get UUIDs from service
        imu1_char = self.service.IMU1_CHAR_UUID
        imu2_char = self.service.IMU2_CHAR_UUID
            
        if self.char_uuid == imu1_char:
            result = await self.service.start_imu1_euler_notify(self._euler_notification_handler)
        else:
            result = await self.service.start_imu2_euler_notify(self._euler_notification_handler)
            
        if result:
            self.euler_notifying = True
        return result

    async def stop_notifications(self):
        """Stop notifications"""
        if not self.service.is_connected():
            self.view.set_button_states(False)
            return False
            
        success = True
            
        # Stop main notifications if they're active
        if self.notifying:
            result = await self.service.stop_notify(self.char_uuid)
            if result:
                self.notifying = False
                self.view.set_button_states(False)
            else:
                success = False
                
        # Always try to stop Euler notifications to ensure clean state
        result = await self.stop_euler_notifications()
        if not result:
            success = False

        return success

    async def stop_euler_notifications(self):
        """Stop Euler angle notifications"""
        if not self.service.is_connected():
            return False

        try:
            # Get UUIDs from service
            imu1_char = self.service.IMU1_CHAR_UUID
            imu2_char = self.service.IMU2_CHAR_UUID
            
            if self.char_uuid == imu1_char:
                result = await self.service.stop_imu1_euler_notify()
                self.euler_notifying = False if result else self.euler_notifying
                return result
            else:
                result = await self.service.stop_imu2_euler_notify()
                self.euler_notifying = False if result else self.euler_notifying
                return result
                
        except Exception as e:
            print(f"Error stopping Euler notifications: {e}")
            return False
            
    def set_log_dialog(self, dialog):
        """Set the IMU log dialog for data logging"""
        self.log_dialog = dialog
        if not dialog:
            self.latest_imu_data = None
            self.latest_euler_data = None

    async def _notification_handler(self, sender, data):
        """Handle incoming notifications"""
        imu_data = IMUData.from_bytes(data)
        if imu_data:
            self.latest_imu_data = imu_data
            # Use event loop to update UI from notification callback
            self.loop.create_task(self._update_view_async(imu_data))
            # Try to log if we have both IMU and Euler data
            await self._try_log_data()

    async def _euler_notification_handler(self, sender, euler_data):
        """Handle incoming Euler angle notifications"""
        if euler_data and isinstance(euler_data, IMUEulerData):
            self.latest_euler_data = euler_data
            # Use event loop to update UI from notification callback
            self.loop.create_task(self._update_euler_async(euler_data))
            # Try to log if we have both IMU and Euler data
            await self._try_log_data()
            
    async def _try_log_data(self):
        """Try to log data if both IMU and Euler data are available"""
        if self.log_dialog and self.latest_imu_data and self.latest_euler_data:
            # Get UUIDs from service
            imu1_char = self.service.IMU1_CHAR_UUID
            imu1_euler = self.service.IMU1_EULER_UUID
            imu2_char = self.service.IMU2_CHAR_UUID
            imu2_euler = self.service.IMU2_EULER_UUID

            # Determine IMU number from characteristic UUID
            if self.char_uuid in [imu1_char, imu1_euler]:
                imu_number = 1
            else:
                imu_number = 2
            self.log_dialog.log_imu_data(imu_number, self.latest_imu_data, self.latest_euler_data)

    async def _update_euler_async(self, euler_data):
        """Update view with Euler angles asynchronously"""
        if hasattr(self.view, 'update_euler'):
            self.view.update_euler(
                euler_data.euler['pitch'],
                euler_data.euler['roll'],
                euler_data.euler['yaw']
            )
            
    async def _update_view_async(self, imu_data):
        """Update view asynchronously (safe for callbacks)"""
        self._update_view(imu_data)
        
    def _update_view(self, imu_data):
        """Update view with IMU data"""
        self.view.update_accel(
            imu_data.accel['x'], 
            imu_data.accel['y'], 
            imu_data.accel['z']
        )
        self.view.update_gyro(
            imu_data.gyro['x'], 
            imu_data.gyro['y'], 
            imu_data.gyro['z']
        )
        self.view.update_magn(
            imu_data.mag['x'], 
            imu_data.mag['y'], 
            imu_data.mag['z']
        )
        
    def is_notifying(self):
        """Check if notifications are active"""
        return self.notifying
