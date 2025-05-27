import customtkinter as ctk
from src.config.app_config import AppConfig
from src.view.device_monitor_view import DeviceMonitorView
from src.view.gamepad_view import GamepadView
from src.view.overall_status_view import OverallStatusView
from src.view.imu1_view import IMU1View
from src.view.imu2_view import IMU2View
from src.view.sensor_view import SensorView
from src.view.footer_view import FooterComponent

class MainView:
    """Class for setting up the main UI components"""

    def __init__(self, root_window):
        self.window = root_window
        self.device_monitor = None
        self.config = AppConfig()  # Get singleton instance

        self._setup_window()
        self._setup_theme()
        self._setup_views()

    def _setup_window(self):
        """Configure main window properties"""
        self.window.title(self.config.WINDOW_TITLE)
        self.window.geometry(
            f"{self.config.WINDOW_WIDTH}x{self.config.WINDOW_HEIGHT}")
        if self.config.WINDOW_MAXIMIZED:
            self.window.state("zoomed")

    def _setup_theme(self):
        """Configure global theme settings"""
        ctk.set_widget_scaling(self.config.DISPLAY_SCALING)
        ctk.set_window_scaling(self.config.WINDOW_SCALING)
        ctk.set_appearance_mode(self.config.APPEARANCE_MODE)
        self.window.configure(fg_color=self.config.BACKGROUND_COLOR)

    def _setup_views(self):
        """Initialize and setup application views"""
        self.device_monitor = DeviceMonitorView(self.window)

        content_frame = ctk.CTkFrame(
            self.device_monitor, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, pady=(20, 0))

        content_frame.grid_columnconfigure(0, weight=1)  # Left section
        content_frame.grid_columnconfigure(1, weight=2)  # Right section

        # Left container with gamepad view
        left_container = ctk.CTkFrame(content_frame, fg_color="transparent")
        left_container.grid(row=0, column=0, rowspan=3, sticky="nsew")
        left_container.grid_columnconfigure(0, weight=1)
        left_container.grid_rowconfigure(0, weight=1)

        self.gamepad_view = GamepadView(left_container)
        self.gamepad_view.grid(row=0, column=0, sticky="nsew")

        # Right container with status and sensors
        right_container = ctk.CTkFrame(content_frame, fg_color="transparent")
        right_container.grid(row=0, column=1, rowspan=3,
                             sticky="nsew", padx=(10, 0))
        right_container.grid_columnconfigure(0, weight=1)
        right_container.grid_rowconfigure(1, weight=0)
        right_container.grid_rowconfigure(2, weight=1)
        right_container.grid_rowconfigure(3, weight=0)

        self.overall_status_view = OverallStatusView(right_container)
        self.overall_status_view.grid(
            row=0, column=0, sticky="nsew", padx=(10, 0), pady=(0, 10))

        imu_frame = ctk.CTkFrame(right_container, fg_color="transparent")
        imu_frame.grid(row=1, column=0, sticky="nsew", padx=(10, 0), pady=10)
        imu_frame.grid_columnconfigure(0, weight=1)
        imu_frame.grid_columnconfigure(1, weight=1)
        imu_frame.grid_rowconfigure(0, weight=1)
        imu_frame.grid_rowconfigure(1, weight=1)

        self.imu1_view = IMU1View(imu_frame)
        self.imu1_view.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.imu2_view = IMU2View(imu_frame)
        self.imu2_view.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        self.sensor_view = SensorView(right_container)
        self.sensor_view.grid(row=2, column=0, sticky="nsew", padx=(10, 0), pady=10)

        self.footer = FooterComponent(self.window)
        self.footer.pack(side="bottom", fill="x")
