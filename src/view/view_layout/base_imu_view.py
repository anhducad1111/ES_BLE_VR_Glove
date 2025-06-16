from typing import Dict, List, Optional, Union

import customtkinter as ctk

from src.config.app_config import AppConfig
from src.view.view_component import ButtonComponent, CoordinateEntry
from src.view.view_interfaces import IMUViewInterface


class BaseIMUView(ctk.CTkFrame, IMUViewInterface):
    # Constants
    SENSOR_ENTRY_WIDTH = 120
    EULER_ENTRY_WIDTH = 100
    BUTTON_HEIGHT = 28
    HEADER_PADDING = 12
    FRAME_PADDING = 10
    DEFAULT_VALUE = 0.0

    # Sensor configurations
    SENSOR_CONFIGS = {
        "accel": {"label": "Accel (mg)", "axes": ["X", "Y", "Z"], "width": 120},
        "gyro": {"label": "Gyro (dps)", "axes": ["X", "Y", "Z"], "width": 120},
        "magn": {"label": "Magn (uT)", "axes": ["X", "Y", "Z"], "width": 120},
        "euler": {
            "label": "Euler (deg)",
            "axes": ["Pitch", "Roll", "Yaw"],
            "width": 100,
        },
    }

    def __init__(self, parent: ctk.CTk, title: str):
        self.config = AppConfig()  # Get singleton instance
        self.imu_service = None  # Will be set by presenter
        self.loop = None  # Will be set by presenter

        super().__init__(
            parent,
            fg_color=self.config.PANEL_COLOR,
            border_color=self.config.BORDER_COLOR,
            border_width=self.config.BORDER_WIDTH,
            corner_radius=self.config.CORNER_RADIUS,
        )

        self._setup_grid()
        self._create_header(title)
        self._create_data_frame()
        self._create_sensor_frames()

        self._create_button_container()

    def _setup_grid(self) -> None:
        """Setup the main grid configuration."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)

    def _create_header(self, title: str) -> None:
        """Create the header with title."""
        header_label = ctk.CTkLabel(
            self,
            text=title,
            font=self.config.HEADER_FONT,
            text_color=self.config.TEXT_COLOR,
        )
        header_label.grid(
            row=0,
            column=0,
            sticky="nw",
            padx=self.HEADER_PADDING,
            pady=(self.HEADER_PADDING, 0),
        )

    def _create_data_frame(self) -> None:
        """Create and configure the main data frame."""
        self.data_frame = ctk.CTkFrame(self, width=0, fg_color="transparent")
        self.data_frame.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=(self.HEADER_PADDING, 0),
            pady=(0, self.HEADER_PADDING),
        )
        self.data_frame.grid_columnconfigure(0, weight=0)
        self.data_frame.grid_rowconfigure((0, 1, 2, 3), weight=1)

    def _create_sensor_frames(self) -> None:
        """Create all sensor data frames."""
        self.sensor_entries = {}
        for idx, (sensor_type, config) in enumerate(self.SENSOR_CONFIGS.items()):
            self.sensor_entries[sensor_type] = self._create_sensor_frame(
                idx, config["label"], config["axes"], config["width"]
            )

    def _create_button_container(self) -> None:
        """Create and configure the button container."""
        button_container = ctk.CTkFrame(
            self,
            fg_color="transparent",
            width=0,
            height=self.BUTTON_HEIGHT,
        )
        button_container.grid(
            row=2, column=0, sticky="es", padx=self.FRAME_PADDING, pady=(0, 20)
        )
        button_container.grid_columnconfigure(2, weight=1)

        self._create_calibration_label(button_container)
        self._create_control_buttons(button_container)

    def _create_calibration_label(self, container: ctk.CTkFrame) -> None:
        """Create the calibration status label."""
        self.calib_status_label = ctk.CTkLabel(
            container,
            text="Calib Status: --",
            font=self.config.LABEL_FONT,
            text_color="#FFFFFF",
        )
        self.calib_status_label.grid(
            row=0, column=0, sticky="w", padx=self.FRAME_PADDING
        )

    def _create_control_buttons(self, container: ctk.CTkFrame) -> None:
        """Create configure and calibrate buttons."""
        self.button_config = ButtonComponent(
            container, "Configure", command=self._handle_config_click
        )
        self.button_config.grid(
            row=0, column=3, sticky="e", padx=(0, self.FRAME_PADDING), pady=0
        )

        self.button_calibrate = ButtonComponent(
            container, "Calibrate", command=self._on_calibrate
        )
        self.button_calibrate.grid(
            row=0, column=4, sticky="e", padx=(0, self.FRAME_PADDING), pady=0
        )

    def _create_sensor_frame(
        self, row: int, label_text: str, axis_labels: List[str], entry_width: int = 80
    ) -> Dict[str, CoordinateEntry]:
        """Create a frame for sensor data with coordinate entries."""
        frame = ctk.CTkFrame(
            self.data_frame,
            width=0,
            fg_color="transparent",
        )
        frame.grid(row=row, column=0, sticky="nsew", padx=(0, 0), pady=(0, 12))

        # Add sensor type label
        label = ctk.CTkLabel(
            frame,
            text=label_text,
            font=self.config.LABEL_FONT,
            text_color=self.config.TEXT_COLOR,
        )
        label.grid(row=0, column=0, sticky="nw", padx=10)

        # Create entries for each axis
        entries = {}
        for i, axis in enumerate(axis_labels):
            entry = CoordinateEntry(frame, axis, entry_width)
            entry.grid(row=0, column=i + 1, padx=(0, 10))
            entries[axis.lower()] = entry

        return entries

    # Sensor update methods
    def update_accel(self, x: float, y: float, z: float) -> None:
        """Update accelerometer values."""
        self._update_xyz_values("accel", x, y, z)

    def update_gyro(self, x: float, y: float, z: float) -> None:
        """Update gyroscope values."""
        self._update_xyz_values("gyro", x, y, z)

    def update_magn(self, x: float, y: float, z: float) -> None:
        """Update magnetometer values."""
        self._update_xyz_values("magn", x, y, z)

    def update_euler(self, pitch: float, roll: float, yaw: float) -> None:
        """Update euler angles."""
        entries = self.sensor_entries["euler"]
        entries["pitch"].set_value(pitch)
        entries["roll"].set_value(roll)
        entries["yaw"].set_value(yaw)

    def _update_xyz_values(
        self, sensor_type: str, x: float, y: float, z: float
    ) -> None:
        """Update XYZ values for a sensor type."""
        entries = self.sensor_entries[sensor_type]
        entries["x"].set_value(x)
        entries["y"].set_value(y)
        entries["z"].set_value(z)

    def set_button_states(self, enabled: bool) -> None:
        """Enable/disable buttons."""
        state = "normal" if enabled else "disabled"
        self.button_config.configure(state=state)
        self.button_calibrate.configure(state=state)

    def clear_values(self) -> None:
        """Clear all displayed values."""
        for sensor_type in self.SENSOR_CONFIGS:
            if sensor_type == "euler":
                self.update_euler(
                    self.DEFAULT_VALUE, self.DEFAULT_VALUE, self.DEFAULT_VALUE
                )
            else:
                self._update_xyz_values(
                    sensor_type,
                    self.DEFAULT_VALUE,
                    self.DEFAULT_VALUE,
                    self.DEFAULT_VALUE,
                )
        self.update_calib_status("--")

    def _handle_config_click(self) -> None:
        """Handle config button click by creating coroutine in event loop."""
        if self.loop:
            self.loop.create_task(self._on_config())

    async def _on_config(self):
        """Base method for configuration button click. Override in subclasses."""
        pass

    def _handle_config_apply(self, dialog):
        """Handle configuration dialog apply button click"""
        # Will be implemented when config handling is moved from presenter
        dialog.destroy()

    def _on_calibrate(self):
        """Base method for calibration button click. Override in subclasses."""
        pass

    def _handle_calibration_start(self, dialog):
        """Handle calibration start button click"""
        # Will be implemented when calibration handling is added
        pass

    def update_calib_status(self, status: Union[int, str]) -> None:
        """Update calibration status display."""
        self.calib_status_label.configure(text=f"Calib Status: {status}")

    def update_debug_text(self, text: str) -> None:
        """Update debug text display (empty implementation)."""
        pass
