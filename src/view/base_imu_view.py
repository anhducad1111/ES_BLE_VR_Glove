import customtkinter as ctk
from src.config.app_config import AppConfig
from src.view.coordinate_entry import CoordinateEntry
from src.view.button_component import ButtonComponent
from src.view.view_interfaces import IMUViewInterface

class BaseIMUView(ctk.CTkFrame, IMUViewInterface):
    def __init__(self, parent, title: str):
        self.config = AppConfig()  # Get singleton instance
        self.imu_service = None  # Will be set by presenter
        super().__init__(
            parent,
            fg_color=self.config.PANEL_COLOR,
            border_color=self.config.BORDER_COLOR,
            border_width=self.config.BORDER_WIDTH,
            corner_radius=self.config.CORNER_RADIUS,
        )

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.loop = None  # Will be set by presenter

        # Create header
        header_label = ctk.CTkLabel(
            self,
            text=title,
            font=self.config.HEADER_FONT,
            text_color=self.config.TEXT_COLOR,
        )
        header_label.grid(row=0, column=0, sticky="nw", padx=12, pady=(12, 0))

        # Create main data frame
        self.data_frame = ctk.CTkFrame(self, width=0, fg_color="transparent")
        self.data_frame.grid(row=1, column=0, sticky="nsew",
                             padx=(12, 0), pady=(0, 12))
        self.data_frame.grid_columnconfigure(0, weight=0)
        self.data_frame.grid_rowconfigure((0, 1, 2, 3), weight=1) 

        # Create sensor data frames
        self.accel_entries = self._create_sensor_frame(
            0, "Accel (mg)", ["X", "Y", "Z"], 120)
        self.gyro_entries = self._create_sensor_frame(
            1, "Gyro (dps)", ["X", "Y", "Z"], 120)
        self.magn_entries = self._create_sensor_frame(
            2, "Magn (uT)", ["X", "Y", "Z"], 120)
        self.euler_entries = self._create_sensor_frame(
            3, "Euler (deg)", ["Pitch", "Roll", "Yaw"], 100)
        
        # Button container
        button_container = ctk.CTkFrame(
            self,
            fg_color="transparent",
            width=0,
            height=28,
        )
        button_container.grid(row=2, column=0, sticky="es", padx=10, pady=(0, 20))
        button_container.grid_columnconfigure((0, 1), weight=0)  # Ensure buttons stay at their minimal width

        # Create Configure button with _on_config callback
        self.button_config = ButtonComponent(button_container, "Configure", command=self._handle_config_click)
        self.button_config.grid(row=0, column=0, sticky="es", padx=(0, 10), pady=0)

        # Create Calibrate button with _on_calibrate callback
        self.button_calibrate = ButtonComponent(button_container, "Calibrate", command=self._on_calibrate)
        self.button_calibrate.grid(row=0, column=1, sticky="es", padx=(0, 10), pady=0)


    def _create_sensor_frame(self, row: int, label_text: str, axis_labels: list, entry_width: int = 80) -> dict:
        """Create a frame for sensor data with three coordinate entries.

        Args:
            row: Row position in the main data frame
            label_text: Label for the sensor type
            axis_labels: List of labels for each axis (e.g., ["X", "Y", "Z"])
            entry_width: Width of the entry fields

        Returns:
            Dictionary containing the coordinate entry widgets
        """
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
            entry.grid(row=0, column=i+1, padx=(0, 10))
            entries[axis.lower()] = entry

        return entries

    def update_accel(self, x: float, y: float, z: float):
        """Update accelerometer values"""
        self.accel_entries['x'].set_value(x)
        self.accel_entries['y'].set_value(y)
        self.accel_entries['z'].set_value(z)

    def update_gyro(self, x: float, y: float, z: float):
        """Update gyroscope values"""
        self.gyro_entries['x'].set_value(x)
        self.gyro_entries['y'].set_value(y)
        self.gyro_entries['z'].set_value(z)

    def update_magn(self, x: float, y: float, z: float):
        """Update magnetometer values"""
        self.magn_entries['x'].set_value(x)
        self.magn_entries['y'].set_value(y)
        self.magn_entries['z'].set_value(z)

    def update_euler(self, pitch: float, roll: float, yaw: float):
        """Update euler angles"""
        self.euler_entries['pitch'].set_value(pitch)
        self.euler_entries['roll'].set_value(roll)
        self.euler_entries['yaw'].set_value(yaw)

    def set_button_states(self, enabled):
        """Enable/disable buttons"""
        state = "normal" if enabled else "disabled"
        self.button_config.configure(state=state)
        self.button_calibrate.configure(state=state)


    def clear_values(self):
        """Clear all displayed values"""
        self.update_accel(0, 0, 0)
        self.update_gyro(0, 0, 0)
        self.update_magn(0, 0, 0)
        self.update_euler(0, 0, 0)  # This will set euler to 0 as implemented

    def _handle_config_click(self):
        """Handle config button click by creating coroutine in event loop"""
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

    def update_debug_text(self, text):
        """Update debug text display (empty implementation)"""
        pass
