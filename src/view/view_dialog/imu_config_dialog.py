import customtkinter as ctk
from src.config.app_config import AppConfig
from src.config.constant import BLEConstants
from src.view.view_component.button_component import ButtonComponent
from src.view.view_component.imu_config_list_item import IMUConfigListItem

class IMUConfigDialog(ctk.CTkToplevel):
    """Dialog for configuring IMU settings."""
    
    # Style constants
    DIALOG_WIDTH = 453
    DIALOG_HEIGHT = 500
    DIALOG_COLOR = "#1F1F1F"
    GROUP_COLOR = "#2B2D30"
    TITLE_FONT = ("Inter Bold", 16)
    LABEL_FONT = ("Inter", 14, "bold")
    
    # Config options from BLEConstants
    ACCEL_GYRO_RATES = list(BLEConstants.ACCEL_GYRO_FREQ_MAP.values())
    MAG_RATES = list(BLEConstants.MAG_FREQ_MAP.values())
    ACCEL_RANGES = list(BLEConstants.ACCEL_RANGE_MAP.values())
    GYRO_RANGES = list(BLEConstants.GYRO_RANGE_MAP.values())
    MAG_RANGES = list(BLEConstants.MAG_RANGE_MAP.values())
    
    def __init__(self, parent, imu_label: str):
        super().__init__(parent)
        self.config = AppConfig()  # Get singleton instance
        self._destroyed = False
        self._setup_window(parent)
        self._create_main_layout(imu_label)

    def _setup_window(self, parent: ctk.CTk) -> None:
        """Setup the window properties."""
        self.title("IMU Configuration")
        self.overrideredirect(False)  # Keep window decorations
        self.configure(fg_color=self.DIALOG_COLOR)
        self.geometry(f"{self.DIALOG_WIDTH}x{self.DIALOG_HEIGHT}")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self._center_window(parent)
        self._make_modal(parent)
        self.attributes('-topmost', True)

    def _center_window(self, parent):
        """Center the dialog on the main window"""
        # Get the root window (main window)
        root = parent.winfo_toplevel()
        
        # Calculate screen width and height
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        # Get the root window position and dimensions
        root_x = root.winfo_x()
        root_y = root.winfo_y()
        root_width = root.winfo_width()
        root_height = root.winfo_height()
        
        # Calculate center position within the root window
        x = root_x + (root_width - 453) // 2
        y = root_y + (root_height - 446) // 2
        
        # Ensure the dialog stays within screen bounds
        x = max(0, min(x, screen_width - 453))
        y = max(0, min(y, screen_height - 446))
        
        self.geometry(f"+{x}+{y}")

    def _make_modal(self, parent):
        self.transient(parent)
        self.grab_set()

    def _create_main_layout(self, imu_label):
        # Outer border frame
        main_frame = ctk.CTkFrame(
            self,
            fg_color="#1F1F1F",
            border_color="#777777",
            border_width=1,
            corner_radius=8
        )
        main_frame.pack(fill="both", expand=True, padx=2, pady=2)

        content = self._create_content_frame(main_frame)
        self._create_title_section(content, imu_label)
        self._create_config_sections(content)
        self._create_bottom_section(content)

    def _create_content_frame(self, parent: ctk.CTkFrame) -> ctk.CTkFrame:
        """Create the main content frame."""
        content = ctk.CTkFrame(parent, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        return content

    def _create_title_section(self, parent, imu_label):
        """Create the title section of the dialog."""
        title_frame = ctk.CTkFrame(parent, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 15))
        
        header = ctk.CTkLabel(
            title_frame,
            text=f"{imu_label} Configuration",
            font=self.TITLE_FONT,
            text_color="white"
        )
        header.pack(side="left")

    def _create_config_sections(self, parent: ctk.CTkFrame) -> None:
        """Create the configuration sections."""
        self.config_frame = self._create_config_frame(parent)
        
        # Frequency section
        freq_group = self._create_group_frame(self.config_frame, "Frequency")
        freq_inner = self._create_inner_frame(freq_group)
        self.accel_gyro_rate_item = IMUConfigListItem(
            freq_inner,
            "Accel & Gyro",
            self.ACCEL_GYRO_RATES,
            **{"bg_color": "transparent"}
        )
        self.accel_gyro_rate_item.pack(fill="x", pady=2)
        self.mag_rate_item = IMUConfigListItem(
            freq_inner,
            "Magnet",
            self.MAG_RATES,
            **{"bg_color": "transparent"}
        )
        self.mag_rate_item.pack(fill="x", pady=2)

        # Range section
        range_group = self._create_group_frame(self.config_frame, "Range")
        range_inner = self._create_inner_frame(range_group)
        self.accel_range_item = IMUConfigListItem(
            range_inner,
            "Accel",
            self.ACCEL_RANGES,
            **{"bg_color": "transparent"}
        )
        self.accel_range_item.pack(fill="x", pady=2)
        self.gyro_range_item = IMUConfigListItem(
            range_inner,
            "Gyro",
            self.GYRO_RANGES,
            **{"bg_color": "transparent"}
        )
        self.gyro_range_item.pack(fill="x", pady=2)
        self.mag_range_item = IMUConfigListItem(
            range_inner,
            "Mag",
            self.MAG_RANGES,
            **{"bg_color": "transparent"}
        )
        self.mag_range_item.pack(fill="x", pady=2)

    def _create_config_frame(self, parent: ctk.CTkFrame) -> ctk.CTkFrame:
        """Create the main configuration frame."""
        frame = ctk.CTkFrame(
            parent,
            fg_color="transparent",
            border_width=0
        )
        frame.pack(fill="both", expand=True, padx=0, pady=0)
        return frame

    def _create_group_frame(self, parent: ctk.CTkFrame, title: str) -> ctk.CTkFrame:
        """Create a configuration group frame with title."""
        group = ctk.CTkFrame(
            parent,
            fg_color=self.GROUP_COLOR,
            corner_radius=10,
            border_width=0
        )
        group.pack(fill="x", pady=(0, 15))
        
        label = ctk.CTkLabel(
            group,
            text=title,
            font=self.LABEL_FONT,
            text_color="white",
            bg_color=self.GROUP_COLOR
        )
        label.pack(anchor="w", pady=(8, 0), padx=16)
        
        return group

    def _create_inner_frame(self, parent: ctk.CTkFrame) -> ctk.CTkFrame:
        """Create an inner frame for configuration items."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=0, pady=8)
        return frame

    def _create_bottom_section(self, parent: ctk.CTkFrame) -> None:
        """Create the bottom section with buttons."""
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(fill="x", side="bottom", pady=(10, 0))
        self.apply_button = ButtonComponent(
            button_frame,
            "Apply",
            command=self._on_apply,
            fg_color=self.config.BUTTON_COLOR,
            hover_color=self.config.BUTTON_HOVER_COLOR
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

    def _on_apply(self):
        if hasattr(self, '_apply_callback'):
            config = self.get_config_values()
            self._apply_callback(config)

    def set_config_values(self, config: dict) -> None:
        """Set all configuration values from device state.
        
        Args:
            config: Dictionary containing configuration values with keys:
                   accel_gyro_rate, mag_rate, accel_range, gyro_range, mag_range
                   
        Note: Values come from the device's current configuration state
        """
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

    def get_config_values(self):
        """Get all current configuration values"""
        return {
            'accel_gyro_rate': self.accel_gyro_rate_item.get(),
            'mag_rate': self.mag_rate_item.get(),
            'accel_range': self.accel_range_item.get(), 
            'gyro_range': self.gyro_range_item.get(),
            'mag_range': self.mag_range_item.get()
        }

    def set_cancel_callback(self, callback):
        self.cancel_button.configure(command=callback)

    def set_apply_callback(self, callback):
        self._apply_callback = callback

    def destroy(self):
        self._destroyed = True
        super().destroy()
