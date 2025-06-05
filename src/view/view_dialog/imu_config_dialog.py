import customtkinter as ctk
from dataclasses import dataclass
from typing import Dict, Optional, Callable, TypedDict
from src.config.app_config import AppConfig
from src.config.constant import BLEConstants
from src.view.view_component.button_component import ButtonComponent
from src.view.view_component.imu_config_list_item import IMUConfigListItem
from .base_dialog import BaseDialog, DialogConfig, DialogStyle

class IMUConfig(TypedDict):
    """Type definition for IMU configuration values"""
    accel_gyro_rate: str
    mag_rate: str
    accel_range: str
    gyro_range: str
    mag_range: str

@dataclass
class IMUConfigStyle:
    """Style configuration for IMU dialog"""
    group_color: str = "#2B2D30"
    group_font: tuple = ("Inter", 14, "bold")

class IMUConfigDialog(BaseDialog):
    """Dialog for configuring IMU settings."""
    
    # Config options from BLEConstants
    ACCEL_GYRO_RATES = list(BLEConstants.ACCEL_GYRO_FREQ_MAP.values())
    MAG_RATES = list(BLEConstants.MAG_FREQ_MAP.values())
    ACCEL_RANGES = list(BLEConstants.ACCEL_RANGE_MAP.values())
    GYRO_RANGES = list(BLEConstants.GYRO_RANGE_MAP.values())
    MAG_RANGES = list(BLEConstants.MAG_RANGE_MAP.values())
    
    def __init__(self, parent: ctk.CTk, imu_label: str):
        config = DialogConfig(
            title="", # Empty to prevent default header
            width=453,
            height=500,
            style=DialogStyle(
                fg_color="#1F1F1F",
                content_bg="#1F1F1F",
                border_color="#777777",
                border_width=1,
                corner_radius=8
            )
        )
        
        self._destroyed = False
        self.imu_label = imu_label
        self.style = IMUConfigStyle()
        self._apply_callback: Optional[Callable[[IMUConfig], None]] = None
        
        # Config item references
        self.accel_gyro_rate_item: Optional[IMUConfigListItem] = None
        self.mag_rate_item: Optional[IMUConfigListItem] = None
        self.accel_range_item: Optional[IMUConfigListItem] = None
        self.gyro_range_item: Optional[IMUConfigListItem] = None
        self.mag_range_item: Optional[IMUConfigListItem] = None
        
        super().__init__(parent, config)
        self.title("IMU Configuration")
        self.attributes('-topmost', True)

    def _create_title_section(self) -> None:
        """Create custom title section"""
        title_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 15))
        
        header = ctk.CTkLabel(
            title_frame,
            text=f"{self.imu_label} Configuration",
            font=("Inter Bold", 16),
            text_color="white"
        )
        header.pack(side="left")

    def _create_content(self) -> None:
        """Create main dialog content"""
        # Main config frame
        self.config_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent",
            border_width=0
        )
        self.config_frame.pack(fill="both", expand=True, padx=0, pady=0)

        # Frequency section
        freq_group = self._create_group_frame("Frequency")
        freq_inner = self._create_inner_frame(freq_group)
        
        self.accel_gyro_rate_item = IMUConfigListItem(
            freq_inner,
            "Accel & Gyro",
            self.ACCEL_GYRO_RATES,
            bg_color="transparent"
        )
        self.accel_gyro_rate_item.pack(fill="x", pady=2)
        
        self.mag_rate_item = IMUConfigListItem(
            freq_inner,
            "Magnet",
            self.MAG_RATES,
            bg_color="transparent"
        )
        self.mag_rate_item.pack(fill="x", pady=2)

        # Range section
        range_group = self._create_group_frame("Range")
        range_inner = self._create_inner_frame(range_group)
        
        self.accel_range_item = IMUConfigListItem(
            range_inner,
            "Accel",
            self.ACCEL_RANGES,
            bg_color="transparent"
        )
        self.accel_range_item.pack(fill="x", pady=2)
        
        self.gyro_range_item = IMUConfigListItem(
            range_inner,
            "Gyro",
            self.GYRO_RANGES,
            bg_color="transparent"
        )
        self.gyro_range_item.pack(fill="x", pady=2)
        
        self.mag_range_item = IMUConfigListItem(
            range_inner,
            "Mag",
            self.MAG_RANGES,
            bg_color="transparent"
        )
        self.mag_range_item.pack(fill="x", pady=2)

        # Bottom button section
        button_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        button_frame.pack(fill="x", side="bottom", pady=(10, 0))
        
        self.apply_button = ButtonComponent(
            button_frame,
            "Apply",
            command=self._on_apply,
            fg_color=self.app_config.BUTTON_COLOR,
            hover_color=self.app_config.BUTTON_HOVER_COLOR
        )
        self.apply_button.pack(side="right", padx=(0, 0))
        
        self.cancel_button = ButtonComponent(
            button_frame,
            "Cancel",
            command=self.destroy,
            fg_color="#232323",
            hover_color="#333333"
        )
        self.cancel_button.pack(side="right", padx=(0, 10))

    def _create_group_frame(self, title: str) -> ctk.CTkFrame:
        """Create a configuration group frame with title"""
        group = ctk.CTkFrame(
            self.config_frame,
            fg_color=self.style.group_color,
            corner_radius=10,
            border_width=0
        )
        group.pack(fill="x", pady=(0, 15))
        
        label = ctk.CTkLabel(
            group,
            text=title,
            font=self.style.group_font,
            text_color="white",
            bg_color=self.style.group_color
        )
        label.pack(anchor="w", pady=(8, 0), padx=16)
        
        return group

    def _create_inner_frame(self, parent: ctk.CTkFrame) -> ctk.CTkFrame:
        """Create an inner frame for configuration items"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=0, pady=8)
        return frame

    def _on_apply(self) -> None:
        """Handle apply button click"""
        if self._apply_callback:
            config = self.get_config_values()
            self._apply_callback(config)

    def set_config_values(self, config: IMUConfig) -> None:
        """Set all configuration values from device state"""
        if not isinstance(config, dict):
            raise ValueError("Config must be a dictionary")
            
        required_keys = ['accel_gyro_rate', 'mag_rate', 'accel_range', 'gyro_range', 'mag_range']
        if not all(key in config for key in required_keys):
            raise ValueError(f"Config must contain all required keys: {required_keys}")
            
        self.accel_gyro_rate_item.set(config['accel_gyro_rate'])
        self.mag_rate_item.set(config['mag_rate'])
        self.accel_range_item.set(config['accel_range'])
        self.gyro_range_item.set(config['gyro_range'])
        self.mag_range_item.set(config['mag_range'])

    def get_config_values(self) -> IMUConfig:
        """Get all current configuration values"""
        return {
            'accel_gyro_rate': self.accel_gyro_rate_item.get(),
            'mag_rate': self.mag_rate_item.get(),
            'accel_range': self.accel_range_item.get(),
            'gyro_range': self.gyro_range_item.get(),
            'mag_range': self.mag_range_item.get()
        }

    def set_cancel_callback(self, callback: Callable[[], None]) -> None:
        """Set callback for cancel button"""
        self.cancel_button.configure(command=callback)

    def set_apply_callback(self, callback: Callable[[IMUConfig], None]) -> None:
        """Set callback for apply button"""
        self._apply_callback = callback

    def destroy(self) -> None:
        """Clean up resources"""
        self._destroyed = True
        super().destroy()
