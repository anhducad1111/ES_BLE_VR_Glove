import struct
from bleak import BleakClient

class BLEDebugService:
    """Simple BLE service for debugging purposes"""
    
    def __init__(self):
        self.client = None
        self.connected = False
        
    async def connect(self, device_info):
        """Connect to BLE device"""
        try:
            self.client = BleakClient(device_info.address)
            await self.client.connect()
            self.connected = True
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            self.connected = False
            return False
            
    async def disconnect(self):
        """Disconnect from device"""
        if self.client:
            await self.client.disconnect()
            self.connected = False
            self.client = None
            
    async def discover_services(self):
        """Get all services and characteristics"""
        services = {}
        if not self.client:
            return services
            
        for service in self.client.services:
            chars = {}
            for char in service.characteristics:
                chars[str(char.uuid)] = {
                    'uuid': str(char.uuid),
                    'properties': [p for p in char.properties]
                }
            services[str(service.uuid)] = {
                'uuid': str(service.uuid),
                'characteristics': chars
            }
        return services
        
    async def read_characteristic(self, char_uuid):
        """Read characteristic value"""
        if not self.client:
            return None
        try:
            return await self.client.read_gatt_char(char_uuid)
        except Exception as e:
            print(f"Read error: {e}")
            return None
            
    async def write_characteristic(self, char_uuid, data):
        """Write to characteristic"""
        if not self.client:
            return False
        try:
            await self.client.write_gatt_char(char_uuid, data)
            return True
        except Exception as e:
            print(f"Write error: {e}")
            return False
            
    async def start_notify(self, char_uuid, callback):
        """Start notifications for characteristic"""
        if not self.client:
            return False
        try:
            await self.client.start_notify(char_uuid, callback)
            return True
        except Exception as e:
            print(f"Start notify error: {e}")
            return False
            
    async def stop_notify(self, char_uuid):
        """Stop notifications for characteristic"""
        if not self.client:
            return False
        try:
            await self.client.stop_notify(char_uuid)
            return True
        except Exception as e:
            print(f"Stop notify error: {e}")
            return False
            
    def parse_imu_data(self, data):
        """Parse BLE data based on characteristic format"""
        if not data:
            return "No data"

        # Try to parse based on data length
        try:
            if len(data) == 18:  # IMU1/IMU2 raw data
                values = struct.unpack('<9h', data)
                return (
                    f"IMU Raw Data:\n"
                    f"  Accel (mg): X={values[0]}, Y={values[1]}, Z={values[2]}\n"
                    f"  Gyro (0.01 rad/s): X={values[3]}, Y={values[4]}, Z={values[5]}\n" 
                    f"  Mag (uT): X={values[6]}, Y={values[7]}, Z={values[8]}"
                )

            elif len(data) == 13:  # IMU1/IMU2 euler angles and calibration
                euler = struct.unpack('<3f', data[0:12])  # 3 floats for yaw, pitch, roll
                calib = data[12]  # Last byte is calibration status
                return (
                    f"IMU Euler Data:\n"
                    f"  Yaw (deg): {euler[0]:.2f}\n"
                    f"  Pitch (deg): {euler[1]:.2f}\n"
                    f"  Roll (deg): {euler[2]:.2f}\n"
                    f"  Calibration Status: {calib}"
                )

            elif len(data) == 20:  # Flex sensor data
                values = struct.unpack('<5f', data)  # 5 float values
                return (
                    f"Flex Sensor Data (KOhm):\n"
                    f"  Sensor 1: {values[0]:.2f}\n"
                    f"  Sensor 2: {values[1]:.2f}\n"
                    f"  Sensor 3: {values[2]:.2f}\n"
                    f"  Sensor 4: {values[3]:.2f}\n"
                    f"  Sensor 5: {values[4]:.2f}"
                )

            elif len(data) == 15:  # Config data
                cmd = data[0]
                imu1_ag_freq = data[1]
                imu1_mag_freq = data[2]
                imu2_ag_freq = data[3]
                imu2_mag_freq = data[4]
                imu1_accel_range = data[5]
                imu1_gyro_range = data[6]
                imu1_mag_range = data[7]
                imu2_accel_range = data[8]
                imu2_gyro_range = data[9]
                imu2_mag_range = data[10]
                update_rate = struct.unpack('<H', data[11:13])[0]
                return (
                    f"Config Data:\n"
                    f"  Command: {cmd}\n"
                    f"  IMU1: AG Freq={imu1_ag_freq}, Mag Freq={imu1_mag_freq}\n"
                    f"  IMU2: AG Freq={imu2_ag_freq}, Mag Freq={imu2_mag_freq}\n"
                    f"  IMU1 Ranges: Accel={imu1_accel_range}, Gyro={imu1_gyro_range}, Mag={imu1_mag_range}\n"
                    f"  IMU2 Ranges: Accel={imu2_accel_range}, Gyro={imu2_gyro_range}, Mag={imu2_mag_range}\n"
                    f"  Update Rate: {update_rate}ms"
                )

            elif len(data) == 5:  # Joystick data
                x, y = struct.unpack('<hh', data[0:4])
                button = data[4]
                return (
                    f"Joystick Data:\n"
                    f"  X axis: {x}\n"
                    f"  Y axis: {y}\n"
                    f"  Button: {'Pressed' if button == 1 else 'Not Pressed'}"
                )

            elif len(data) == 4:  # Overall status or Force sensor or Buttons
                if all(x <= 3 for x in data):  # Likely overall status or buttons
                    if max(data) <= 1:  # Likely buttons
                        return (
                            f"Button States:\n"
                            f"  Button 1: {'Pressed' if data[0] else 'Not Pressed'}\n"
                            f"  Button 2: {'Pressed' if data[1] else 'Not Pressed'}\n"
                            f"  Button 3: {'Pressed' if data[2] else 'Not Pressed'}\n"
                            f"  Button 4: {'Pressed' if data[3] else 'Not Pressed'}"
                        )
                    else:  # Overall status
                        return (
                            f"Overall Status:\n"
                            f"  Status Code: {data[0]} ({self._get_error_desc(data[0])})\n"
                            f"  Fuelgauge: {self._get_component_status(data[1])}\n"
                            f"  IMU1: {self._get_component_status(data[2])}\n"
                            f"  IMU2: {self._get_component_status(data[3])}"
                        )
                else:  # Force sensor
                    force = struct.unpack('<f', data)[0]
                    return f"Force Sensor: {force:.2f} kOhm"

            elif len(data) == 1:  # Battery level or charging state
                if data[0] <= 100:  # Battery level
                    return f"Battery Level: {data[0]}%"
                else:  # Charging state
                    states = {0: "Not Charging", 1: "Charging", 2: "Fully Charged"}
                    return f"Charging State: {states.get(data[0], 'Unknown')}"

            # Default case - show hex and ASCII
            hex_part = ' '.join(f'{b:02x}' for b in data)
            ascii_part = ''.join(chr(b) if 0x20 <= b <= 0x7E else '.' for b in data)
            return f"Data (Hex): {hex_part}\nASCII: {ascii_part}"

        except Exception as e:
            return f"Parse error: {e}"

    def _get_error_desc(self, code):
        """Get description for status code"""
        return "No Error" if code == 0 else "General Error"

    def _get_component_status(self, status):
        """Get component status description"""
        states = {
            0: "Not Detected",
            1: "Failed",
            2: "Idle",
            3: "Running"
        }
        return states.get(status, "Unknown")

    def is_connected(self):
        """Check connection status"""
        return self.connected