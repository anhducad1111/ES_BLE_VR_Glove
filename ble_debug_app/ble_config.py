import json
from pathlib import Path
from typing import Dict, Any

class BLEConfig:
    """Configuration loader for BLE service"""
    
    def __init__(self):
        """Initialize configuration"""
        self.services: Dict[str, str] = {}
        self.characteristics: Dict[str, str] = {}
        self.imu_config: Dict[str, Dict[int, str]] = {
            "accel_gyro_freq": {},
            "mag_freq": {},
            "accel_range": {},
            "gyro_range": {},
            "mag_range": {}
        }
        self.load_config()

    def load_config(self) -> None:
        """Load configuration from gatt.json"""
        try:
            gatt_path = Path(__file__).parent.parent / "gatt.json"
            with open(gatt_path) as f:
                config = json.load(f)
                
            # Load service and characteristic UUIDs
            self.services = config["required_services"]
            self.characteristics = config["characteristics"]
            
            # Load IMU configuration mappings with integer keys
            imu = config["imu_config"]
            for key in self.imu_config.keys():
                self.imu_config[key] = {int(k): v for k, v in imu[key].items()}
                
        except Exception as e:
            print(f"Error loading GATT configuration: {e}")
            
    def get_service_uuid(self, name: str) -> str:
        """Get service UUID by name"""
        return self.services.get(name, "")
        
    def get_characteristic_uuid(self, name: str) -> str:
        """Get characteristic UUID by name"""
        return self.characteristics.get(name, "")
        
    def get_imu_config(self, config_type: str, value: int) -> str:
        """Get IMU configuration string by type and value"""
        configs = self.imu_config.get(config_type, {})
        return configs.get(value, f"Unknown ({value})")