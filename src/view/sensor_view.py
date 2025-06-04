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
        self.selected_folder = None  # For log folder selection
        
        # Set up log manager callback
        from src.util.log_manager import LogManager
        self.log_manager = LogManager.instance()
        self.log_manager.add_folder_change_callback(self._on_folder_change)
        
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
        button_container.grid_columnconfigure((0, 1, 2), weight=0)

        self.button_config = ButtonComponent(button_container, "Configure", command=self._handle_config_click)
        self.button_config.grid(row=2, column=0, sticky="es", pady=(0, 0), padx=(0, 20))

        self.button_log = ButtonComponent(button_container, "Log Sensors", command=self._handle_log_click)
        self.button_log.grid(row=2, column=1, sticky="es", pady=(0, 0), padx=(0, 20))

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
        self.button_log.configure(state=state)
        
    def clear_values(self):
        """Clear all sensor values"""
        for sensor_id in self.flex_entries:
            self.flex_entries[sensor_id].set_value(0)
        self.force_entry.set_value(0)
        
    def _on_folder_change(self, folder):
        """Handle folder selection changes from LogManager"""
        self.selected_folder = folder
        if folder:
            self.button_log.configure(text="Start Log Sensors")
        else:
            self.button_log.configure(text="Log Sensors")

    def _handle_log_click(self):
        """Handle log button click"""
        if not self.service or not self.loop:
            return

        # Get singleton logger instance
        from src.util.sensor_log import SensorLog
        from src.util.log_manager import LogManager
        sensor_logger = SensorLog.instance()
        log_manager = LogManager.instance()

        # If currently logging, stop logging
        if sensor_logger.is_logging:
            sensor_logger.stop_logging()
            if log_manager.get_selected_folder():
                self.button_log.configure(text="Start Log Sensors")
            else:
                self.button_log.configure(text="Log Sensors")
            self.button_log.configure(fg_color=self.config.BUTTON_COLOR,
                                    hover_color=self.config.BUTTON_HOVER_COLOR)
            return

        # If folder is selected, start logging
        if log_manager.get_selected_folder() or self.selected_folder:
            folder = log_manager.get_selected_folder() or self.selected_folder
            if sensor_logger.start_logging(folder):
                self.selected_folder = folder  # Store folder path for future use
                self.button_log.configure(text="Stop Log",
                                        fg_color="darkred",
                                        hover_color="#8B0000")
            return

        # Otherwise show folder selection dialog
        try:
            from src.view.imu_log_dialog import IMULogDialog
            def create_dialog():
                self.log_dialog = IMULogDialog(self.winfo_toplevel())
                
                def on_cancel():
                    self.log_dialog.destroy()
                    self.log_dialog = None
                
                def on_apply():
                    folder = self.log_dialog.get_path()
                    if self.log_manager.setup_logging_folder(folder):
                        self.selected_folder = folder
                        self.button_log.configure(text="Start Log Sensors")
                    self.log_dialog.destroy()
                    self.log_dialog = None
                
                self.log_dialog.set_cancel_callback(on_cancel)
                self.log_dialog.set_apply_callback(on_apply)
            
            # Use after_idle to create dialog after event loop is free
            self.after_idle(create_dialog)
            
        except Exception as e:
            pass
            
    def destroy(self):
        """Clean up resources before destroying widget"""
        # Remove folder change callback
        if hasattr(self, 'log_manager'):
            self.log_manager.remove_folder_change_callback(self._on_folder_change)
        super().destroy()
