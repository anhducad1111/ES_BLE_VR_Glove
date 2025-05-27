from src.model.timestamp import TimestampData

class TimestampPresenter:
    """Presenter for timestamp operations"""
    
    def __init__(self, view, ble_service, characteristic_uuid):
        self.view = view
        self.service = ble_service
        self.char_uuid = characteristic_uuid
        
    async def read_timestamp(self):
        """Read timestamp from device"""
        if not self.service.is_connected():
            return False
            
        data = await self.service.read_characteristic(self.char_uuid)
        if data:
            timestamp = TimestampData.from_bytes(data)
            if timestamp and hasattr(self.view, 'set_device_timestamp'):
                self.view.set_device_timestamp(timestamp.unix_timestamp)
                return True
        return False
        
    async def write_current_time(self):
        """Write current time to device"""
        if not self.service.is_connected():
            return False
            
        timestamp = TimestampData.current()
        success = await self.service.write_characteristic(
            self.char_uuid, 
            timestamp.raw_data
        )
        
        # If write was successful, read back the value to display it
        if success:
            await self.read_timestamp()
            
        return success
