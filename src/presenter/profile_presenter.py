from src.model.profile import DeviceProfile

class ProfilePresenter:
    """Presenter for handling device profile information"""
    
    def __init__(self, view, esp32_service):
        """Initialize the presenter"""
        self.view = view
        self.esp32_service = esp32_service
        self.device_profile = None

    async def start_notifications(self):
        """Start profile-related notifications"""
        if not self.esp32_service or not self.view:
            return False
            
        try:
            # Start battery notifications with direct view updates
            await self.esp32_service.start_profile_notifications(self.view)
            return True
        except Exception as e:
            print(f"Error starting profile notifications: {e}")
            return False
            
    async def stop_notifications(self):
        """Stop profile-related notifications"""
        if not self.esp32_service:
            return False
            
        try:
            # Stop battery notifications
            await self.esp32_service.stop_battery_notifications()
            
            # Clear view synchronously if available
            if self.view:
                self.view.clear_values()
                
            return True
        except Exception as e:
            print(f"Error stopping profile notifications: {e}")
            return False

    def create_profile(self, device_info):
        """Create new device profile from device info"""
        # Handle both dict and object inputs
        address = device_info['address'] if isinstance(device_info, dict) else device_info.address
        name = device_info['name'] if isinstance(device_info, dict) else device_info.name
        rssi = device_info['rssi'] if isinstance(device_info, dict) else device_info.rssi
        
        self.device_profile = DeviceProfile(
            address=address,
            name=name,
            rssi=rssi
        )
        return self.device_profile

    def update_view(self):
        """Update view with current profile information"""
        if not self.device_profile or not self.view:
            return
            
        info = self.device_profile.get_display_info()
        for field, value in info.items():
            self.view.update_value(field, value)