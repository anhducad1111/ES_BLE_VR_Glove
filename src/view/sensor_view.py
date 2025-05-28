import customtkinter as ctk
from src.config.app_config import AppConfig
from src.view.coordinate_entry import CoordinateEntry
from src.view.button_component import ButtonComponent
from src.view.other_config_dialog import OtherConfigDialog

class SensorView(ctk.CTkFrame):
    def __init__(self, parent):
        self.config = AppConfig()  # Get singleton instance
        self.service = None  # Will be set by presenter
        self.loop = None  # Will be set by presenter
        super().__init__(
            parent,
            fg_color=self.config.PANEL_COLOR,
            border_color=self.config.BORDER_COLOR,
            border_width=self.config.BORDER_WIDTH,
            corner_radius=self.config.CORNER_RADIUS
        )
        self._setup_layout()
        self._create_header()
        self._create_main_content()

    def _setup_layout(self):
        """Configure initial grid layout"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

    def _create_header(self):
        """Create header label"""
        header_label = ctk.CTkLabel(
            self,
            text="SENSOR",
            font=self.config.HEADER_FONT,
            text_color=self.config.TEXT_COLOR
        )
        header_label.grid(row=0, column=0, sticky="nw", padx=12, pady=(12, 0))

    def _create_main_content(self):
        """Create main content including sensors and button"""
        # Create main container
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.grid(row=1, column=0, sticky="nsew", padx=12, pady=12)
        main_frame.grid_columnconfigure((1, 2, 3, 4, 5), weight=0)

        # Create flex sensor section
        flex_label = ctk.CTkLabel(
            main_frame,
            text="Flex Sensor (kOhm):",
            font=self.config.LABEL_FONT,
            text_color=self.config.TEXT_COLOR
        )
        flex_label.grid(row=0, column=0, sticky="w")

        # Create flex sensor entries
        self.flex_entries = {}
        for i in range(5):
            sensor_num = i + 1
            entry_label = f"{sensor_num}"
            self.flex_entries[sensor_num] = CoordinateEntry(main_frame, entry_label, entry_width=120)
            self.flex_entries[sensor_num].grid(row=0, column=i+1, sticky="ew", padx=5)

        # Create force sensor section
        force_label = ctk.CTkLabel(
            main_frame,
            text="Force Sensor (kOhm):",
            font=self.config.LABEL_FONT,
            text_color=self.config.TEXT_COLOR
        )
        force_label.grid(row=1, column=0, sticky="w")

        # Create force sensor entry
        self.force_entry = CoordinateEntry(main_frame, "", entry_width=120)
        self.force_entry.grid(row=1, column=1, columnspan=2, sticky="ew", pady=(20, 20))

        # Create button container and configure button
        button_container = ctk.CTkFrame(
            self,
            fg_color="transparent",
            width=0,
            height=28,
        )
        button_container.grid(row=2, column=0, sticky="es", padx=10, pady=(0, 20))
        button_container.grid_columnconfigure((0, 1), weight=0)

        self.button_config = ButtonComponent(button_container, "Configure", command=self._handle_config_click)
        self.button_config.grid(row=2, column=0, sticky="es", pady=(0, 0), padx=(0, 20))

    async def _on_config(self):
        """Handle configuration button click"""
        # Read current config
        data = await self.service.read_config()
        dialog = OtherConfigDialog(self)
        
        if data:
            # Get sensor update interval from bytes 11-12 (little endian)
            interval = int.from_bytes(data[11:13], 'little')
            dialog.rate_entry.set_value(interval, keep_editable=True)
            
        dialog.set_cancel_callback(dialog.destroy)
        dialog.set_apply_callback(lambda: self.loop.create_task(self._handle_config_apply(dialog)))

    async def _handle_config_apply(self, dialog):
        """Handle configuration apply button click"""
        rate = dialog.get_rate_value()
        
        # Read current config to preserve other bytes
        data = await self.service.read_config()
        if data:
            # Create new 15-byte array with current config
            new_config = bytearray(data)
            # Update bytes 11-12 with new rate (little endian)
            new_config[11:13] = rate.to_bytes(2, 'little')
            # Write updated config
            await self.service.write_config(new_config)
            
        dialog.destroy()
    def _handle_config_click(self):
        """Handle config button click by creating coroutine in event loop"""
        if self.loop:
            self.loop.create_task(self._on_config())

    def update_flex_sensor(self, sensor_id: int, value: float):
        """Update flex sensor value"""
        if sensor_id in self.flex_entries:
            self.flex_entries[sensor_id].set_value(value)

    def update_force_sensor(self, value: float):
        """Update force sensor value"""
        self.force_entry.set_value(value)
        
    def set_button_states(self, enabled):
        """Enable/disable buttons"""
        state = "normal" if enabled else "disabled"
        self.button_config.configure(state=state)
