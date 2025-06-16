import asyncio
from dataclasses import dataclass
from typing import Optional

import customtkinter as ctk

from src.config.app_config import AppConfig
from src.view.view_layout import (
    DeviceMonitorView,
    FooterComponent,
    GamepadView,
    IMU1View,
    IMU2View,
    LogView,
    OverallStatusView,
    SensorView,
)


@dataclass
class ViewConfig:
    """Configuration for view layout"""

    left_column_weight: int = 1
    right_column_weight: int = 2
    imu_padding: int = 10
    content_padding: int = 10
    top_margin: int = 20


class MainView:
    """Main application window that manages all UI components"""

    def __init__(self, root_window: ctk.CTk):
        self.window = root_window
        self.config = AppConfig()
        self.view_config = ViewConfig()

        self._init_variables()
        self._setup_window()
        self._setup_theme()
        self._create_layout()

    def _init_variables(self) -> None:
        """Initialize instance variables"""
        self.device_monitor: Optional[DeviceMonitorView] = None
        self.gamepad_view: Optional[GamepadView] = None
        self.overall_status_view: Optional[OverallStatusView] = None
        self.imu1_view: Optional[IMU1View] = None
        self.imu2_view: Optional[IMU2View] = None
        self.sensor_view: Optional[SensorView] = None
        self.log_view: Optional[LogView] = None
        self.footer: Optional[FooterComponent] = None
        self.loop = asyncio.get_event_loop()

    def _setup_window(self) -> None:
        """Configure main window properties"""
        self.window.title(self.config.WINDOW_TITLE)
        self.window.geometry(f"{self.config.WINDOW_WIDTH}x{self.config.WINDOW_HEIGHT}")
        if self.config.WINDOW_MAXIMIZED:
            self.window.state("zoomed")

    def _setup_theme(self) -> None:
        """Configure global theme settings"""
        ctk.set_widget_scaling(self.config.DISPLAY_SCALING)
        ctk.set_window_scaling(self.config.WINDOW_SCALING)
        ctk.set_appearance_mode(self.config.APPEARANCE_MODE)
        self.window.configure(fg_color=self.config.BACKGROUND_COLOR)

    def _create_layout(self) -> None:
        """Create main application layout"""
        self._create_top_container()
        
        # Create main content area
        main_content = ctk.CTkFrame(self.window, fg_color="transparent")
        main_content.pack(fill="both", expand=True)
        
        content_frame = self._create_content_frame(main_content)
        self._setup_content_grid(content_frame)
        self._create_left_section(content_frame)
        self._create_right_section(content_frame)
        self._create_footer()

    def _create_top_container(self) -> None:
        """Create top container with device monitor and log view in 5:1 ratio"""
        container = ctk.CTkFrame(self.window, fg_color="transparent")
        container.pack(
            fill="x",
            padx=self.config.WINDOW_PADDING,
            pady=(self.config.WINDOW_PADDING, 0),
        )
        container.grid_columnconfigure(0, weight=4)
        container.grid_columnconfigure(1, weight=1)

        # Create device monitor and log view
        self.device_monitor = DeviceMonitorView(container)
        self.device_monitor.grid(row=0, column=0, sticky="nsew")
        
        self.log_view = LogView(container)
        self.log_view.grid(row=0, column=1, sticky="nsew", padx=(20, 0))

    def _create_content_frame(self, parent: ctk.CTkFrame) -> ctk.CTkFrame:
        """Create main content frame"""
        content_frame = ctk.CTkFrame(parent, fg_color="transparent")
        content_frame.pack(
            fill="both", expand=True,
            padx=self.config.WINDOW_PADDING,
            pady=(self.view_config.top_margin, self.config.WINDOW_PADDING)
        )
        return content_frame

    def _setup_content_grid(self, frame: ctk.CTkFrame) -> None:
        """Configure content frame grid"""
        frame.grid_columnconfigure(0, weight=self.view_config.left_column_weight)
        frame.grid_columnconfigure(1, weight=self.view_config.right_column_weight)

    def _create_left_section(self, parent: ctk.CTkFrame) -> None:
        """Create left section with gamepad view"""
        container = self._create_left_container(parent)
        self._create_gamepad_view(container)

    def _create_left_container(self, parent: ctk.CTkFrame) -> ctk.CTkFrame:
        """Create container for left section"""
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.grid(row=0, column=0, rowspan=3, sticky="nsew")
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)
        return container

    def _create_gamepad_view(self, container: ctk.CTkFrame) -> None:
        """Create gamepad view"""
        self.gamepad_view = GamepadView(container)
        self.gamepad_view.grid(row=0, column=0, sticky="nsew")

    def _create_right_section(self, parent: ctk.CTkFrame) -> None:
        """Create right section with status and sensors"""
        container = self._create_right_container(parent)
        self._create_status_view(container)
        self._create_imu_section(container)
        self._create_sensor_view(container)

    def _create_right_container(self, parent: ctk.CTkFrame) -> ctk.CTkFrame:
        """Create container for right section"""
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.grid(
            row=0,
            column=1,
            rowspan=3,
            sticky="nsew",
            padx=(self.view_config.content_padding, 0),
        )
        self._configure_right_container(container)
        return container

    def _configure_right_container(self, container: ctk.CTkFrame) -> None:
        """Configure right container grid"""
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=0)
        container.grid_rowconfigure(2, weight=1)
        container.grid_rowconfigure(3, weight=0)

    def _create_status_view(self, container: ctk.CTkFrame) -> None:
        """Create overall status view"""
        self.overall_status_view = OverallStatusView(container)
        self.overall_status_view.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(self.view_config.content_padding, 0),
            pady=(0, self.view_config.content_padding),
        )

    def _create_imu_section(self, container: ctk.CTkFrame) -> None:
        """Create IMU section with both IMU views"""
        frame = self._create_imu_frame(container)
        self._create_imu_views(frame)

    def _create_imu_frame(self, parent: ctk.CTkFrame) -> ctk.CTkFrame:
        """Create frame for IMU views"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=(self.view_config.content_padding, 0),
            pady=self.view_config.content_padding,
        )
        self._configure_imu_frame(frame)
        return frame

    def _configure_imu_frame(self, frame: ctk.CTkFrame) -> None:
        """Configure IMU frame grid"""
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

    def _create_imu_views(self, frame: ctk.CTkFrame) -> None:
        """Create both IMU views"""
        self.imu1_view = IMU1View(frame)
        self.imu1_view.grid(
            row=0, column=0, sticky="nsew", padx=(0, self.view_config.imu_padding)
        )

        self.imu2_view = IMU2View(frame)
        self.imu2_view.grid(
            row=0, column=1, sticky="nsew", padx=(self.view_config.imu_padding, 0)
        )

    def _create_sensor_view(self, container: ctk.CTkFrame) -> None:
        """Create sensor view"""
        self.sensor_view = SensorView(container)
        self.sensor_view.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=(self.view_config.content_padding, 0),
            pady=self.view_config.content_padding,
        )

    def _create_footer(self) -> None:
        """Create footer component"""
        self.footer = FooterComponent(self.window)
        self.footer.loop = self.loop
        self.footer.pack(side="bottom", fill="x", expand=False)

