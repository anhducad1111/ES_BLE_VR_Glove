import customtkinter as ctk
from src.config.app_config import AppConfig
from src.view.button_component import ButtonComponent
from src.view.imu_config_list_item import IMUConfigListItem

class IMUConfigDialog(ctk.CTkToplevel):
    def __init__(self, parent, imu_label: str):
        super().__init__(parent)
        self.config = AppConfig()  # Get singleton instance
        self._destroyed = False
        self._setup_window(parent)
        self._create_main_layout(imu_label)

    def _setup_window(self, parent):
        self.title("IMU Configuration")
        self.overrideredirect(False)  # Keep window decorations
        self.configure(fg_color="#1F1F1F")  # Dark background
        self.geometry("453x476")  # Adjust size as needed
        self.resizable(False, False)  # Fix window size
        self.protocol("WM_DELETE_WINDOW", self.destroy)  # Handle window close button
        self._center_window(parent)
        self._make_modal(parent)
        
        # Force as top-level window
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

        # Content frame
        content = ctk.CTkFrame(main_frame, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=20)

        # Title section
        self._create_title_section(content, imu_label)
        # Configuration sections
        self._create_config_sections(content)
        # Bottom section with buttons
        self._create_bottom_section(content)

    def _create_title_section(self, parent, imu_label):
        title_frame = ctk.CTkFrame(parent, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 15))
        header = ctk.CTkLabel(
            title_frame,
            text=f"{imu_label} Configuration",
            font=("Inter Bold", 16),
            text_color="white"
        )
        header.pack(side="left")

    def _create_config_sections(self, parent):
        self.config_frame = ctk.CTkFrame(
            parent,
            fg_color="transparent",
            border_width=0
        )
        self.config_frame.pack(fill="both", expand=True, padx=0, pady=0)

        # Frequency group
        freq_group = ctk.CTkFrame(self.config_frame, fg_color="#2B2D30", corner_radius=10, border_width=0)
        freq_group.pack(fill="x", pady=(0, 15))
        freq_label = ctk.CTkLabel(freq_group, text="Frequency", font=("Inter", 14, "bold"), text_color="white", bg_color="#2B2D30")
        freq_label.pack(anchor="w", pady=(8, 0), padx=16)
        freq_inner = ctk.CTkFrame(freq_group, fg_color="transparent")
        freq_inner.pack(fill="x", padx=0, pady=8)
        self.accel_gyro_rate_item = IMUConfigListItem(freq_inner, "Accel & Gyro", [
            "LSM6DS_RATE_SHUTDOWN",
            "LSM6DS_RATE_12_5_HZ",
            "LSM6DS_RATE_26_HZ",
            "LSM6DS_RATE_52_HZ",
            "LSM6DS_RATE_104_HZ",
            "LSM6DS_RATE_208_HZ",
            "LSM6DS_RATE_416_HZ"
        ], default="LSM6DS_RATE_SHUTDOWN", bg_color="transparent")
        self.accel_gyro_rate_item.pack(fill="x", pady=2)
        self.mag_rate_item = IMUConfigListItem(freq_inner, "Magnet", [
            "LIS3MDL_DATARATE_0_625_HZ",
            "LIS3MDL_DATARATE_1_25_HZ",
            "LIS3MDL_DATARATE_2_5_HZ",
            "LIS3MDL_DATARATE_5_HZ",
            "LIS3MDL_DATARATE_10_HZ",
            "LIS3MDL_DATARATE_20_HZ",
            "LIS3MDL_DATARATE_40_HZ",
            "LIS3MDL_DATARATE_80_HZ"
        ], default="LIS3MDL_DATARATE_0_625_HZ", bg_color="transparent")
        self.mag_rate_item.pack(fill="x", pady=2)

        # Range group
        range_group = ctk.CTkFrame(self.config_frame, fg_color="#2B2D30", corner_radius=10, border_width=0)
        range_group.pack(fill="x", pady=(0, 0))
        range_label = ctk.CTkLabel(range_group, text="Range", font=("Inter", 14, "bold"), text_color="white", bg_color="#2B2D30")
        range_label.pack(anchor="w", pady=(8, 0), padx=16)
        range_inner = ctk.CTkFrame(range_group, fg_color="transparent")
        range_inner.pack(fill="x", padx=0, pady=8)
        self.accel_range_item = IMUConfigListItem(range_inner, "Accel", [
            "LSM6DS_ACCEL_RANGE_2_G",
            "LSM6DS_ACCEL_RANGE_4_G",
            "LSM6DS_ACCEL_RANGE_8_G",
            "LSM6DS_ACCEL_RANGE_16_G"
        ], default="LSM6DS_ACCEL_RANGE_2_G", bg_color="transparent")
        self.accel_range_item.pack(fill="x", pady=2)
        self.gyro_range_item = IMUConfigListItem(range_inner, "Gyro", [
            "LSM6DS_GYRO_RANGE_125_DPS",
            "LSM6DS_GYRO_RANGE_250_DPS",
            "LSM6DS_GYRO_RANGE_500_DPS",
            "LSM6DS_GYRO_RANGE_1000_DPS",
            "LSM6DS_GYRO_RANGE_2000_DPS"
        ], default="LSM6DS_GYRO_RANGE_125_DPS", bg_color="transparent")
        self.gyro_range_item.pack(fill="x", pady=2)
        self.mag_range_item = IMUConfigListItem(range_inner, "Mag", [
            "LIS3MDL_RANGE_4_GAUSS",
            "LIS3MDL_RANGE_8_GAUSS",
            "LIS3MDL_RANGE_12_GAUSS",
            "LIS3MDL_RANGE_16_GAUSS"
        ], default="LIS3MDL_RANGE_4_GAUSS", bg_color="transparent")
        self.mag_range_item.pack(fill="x", pady=2)

    def _create_bottom_section(self, parent):
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
