import customtkinter as ctk
from bleak import BleakScanner
from src.config.app_config import AppConfig
from src.view.connection_dialog import ConnectionDialog
from src.view.button_component import ButtonComponent
from src.view.connection_status_dialog import ConnectionStatusDialog
from src.view.view_interfaces import ConnectionViewInterface
from src.view.imu_log_dialog import IMULogDialog
from src.model.imu_logger import IMULogger
import os
import datetime
import time

class DeviceMonitorView(ctk.CTkFrame, ConnectionViewInterface):
    """View class for monitoring device information"""

    def __init__(self, master) -> None:
        super().__init__(master, fg_color="transparent")
        self.config = AppConfig()  # Get singleton instance
        self.pack(fill="both", expand=True, padx=self.config.WINDOW_PADDING, pady=self.config.WINDOW_PADDING)

        # Store references to value labels
        self.value_labels = {}
        self.is_connected = False
        self.connection_dialog = None
        self.loop = None  # Will be set by presenter
        self.log_button = None  # Will be created in _create_layout
        self.imu1_presenter = None
        self.imu2_presenter = None
        self.selected_folder = None
        self.imu_logger = None
        self.last_battery_notification = None
        self.reconnect_button = None
        self.notification_check_timer = None
        self.current_device_address = None  # Store address for reconnection
        
        self._create_layout()
        # Initially hide log button
        self.show_log_button(False)

    async def update_battery(self, level):
        """Update battery level"""
        self.update_value("battery", f"{level}%")

    async def update_charging(self, state):
        """Update charging state"""
        # Update last notification time
        self.last_battery_notification = time.time()
        # Start timer if not already running
        if not self.notification_check_timer:
            self.notification_check_timer = self.after(3000, self._check_notification_timeout)
        self.update_value("charging", state)

    def _check_notification_timeout(self):
        """Check if battery notification timeout occurred"""
        if self.is_connected and self.last_battery_notification:
            current_time = time.time()
            if current_time - self.last_battery_notification > 3:
                # Show reconnect UI
                self.device_button.configure(fg_color="red")
                self.reconnect_button.grid()
            # Schedule next check
            self.notification_check_timer = self.after(3000, self._check_notification_timeout)

    def _handle_reconnect(self):
        """Handle reconnect button click"""
        if hasattr(self, 'connect_command') and self.current_device_address:
            # Get info for last connected device
            current_device = {
                'name': self.value_labels['name'].cget('text'),
                'address': self.current_device_address,
                'rssi': 0  # RSSI not critical for reconnect
            }
            # Reuse existing connect flow
            self.connect_command(current_device)

    def _create_layout(self):
        """Create the main layout of the view"""
        self._create_info_panel()

    def _create_info_panel(self):
        """Create the information panel section"""
        self.info_frame = ctk.CTkFrame(
            self,
            fg_color=self.config.PANEL_COLOR,
            corner_radius=self.config.CORNER_RADIUS
        )
        self.info_frame.pack(fill="x")
        self.info_frame.configure(height=self.config.INFO_PANEL_HEIGHT)
        self.info_frame.pack_propagate(False)

        # Configure grid columns
        for i in range(12):
            self.info_frame.grid_columnconfigure(i, weight=1, uniform="col")

        self._create_info_header()
        self._create_add_button()
        self._create_info_fields()

    def _create_info_header(self):
        """Create the header section of info panel"""
        left_section = ctk.CTkFrame(
            self.info_frame,
            fg_color="transparent"
        )
        left_section.grid(row=0, column=0, columnspan=9, sticky="nsew", padx=2, pady=2)
        
        info_label = ctk.CTkLabel(
            left_section,
            text="INFORMATION",
            font=self.config.HEADER_FONT,
            text_color=self.config.TEXT_COLOR
        )
        info_label.pack(anchor="w", padx=12, pady=7)

    def _create_add_button(self):
        """Create the Add Device/Disconnect button"""
        button_container = ctk.CTkFrame(
            self.info_frame,
            fg_color="transparent"
        )
        button_container.grid(row=0, column=9, rowspan=3, columnspan=3, sticky="e", padx=2, pady=2)

        # Create reconnect button (initially hidden)
        self.reconnect_button = ButtonComponent(
            button_container,
            "Reconnect",
            command=self._handle_reconnect,
            fg_color="green",
            hover_color="darkgreen"
        )
        self.reconnect_button.grid(row=1, column=0, padx=(12, 12))
        self.reconnect_button.grid_remove()  # Initially hidden

        self.device_button = ButtonComponent(
            button_container,
            "Add device",
            command=self._handle_device_button
        )
        self.device_button.grid(row=1, column=1, padx=12)
        
        self.log_button = ButtonComponent(
            button_container,
            "Log",
            command=self._on_log
        )
        self.log_button.grid(row=2, column=1, columnspan=2, padx=12, pady=(12, 0))
        
    def _create_info_fields(self):
        """Create the information fields grid"""
        fields = [
            # Row 1 (4 columns)
            [("name", "Name:"), ("status", "Status:"),
             ("battery", "Battery:"), ("charging", "Charging:")],
            # Row 2 (4 columns)
            [("firmware", "Firmware:"), ("model", "Model number:"),
             ("manufacturer", "Manufacturer:"), ("hardware", "Hardware:")]
        ]

        for row_idx, row_fields in enumerate(fields, start=1):
            for col_idx, (field_id, label_text) in enumerate(row_fields):
                self._create_info_field(row_idx, col_idx, field_id, label_text)

    def _create_info_field(self, row, col, field_id, label_text):
        """Create a single information field"""
        grid_col = col * 2
        field_container = ctk.CTkFrame(self.info_frame, fg_color="transparent")
        field_container.grid(row=row, column=grid_col, columnspan=2, padx=30, pady=(0, 15), sticky="w")

        # Label
        label_container = ctk.CTkFrame(field_container, fg_color="transparent")
        label_container.pack(side="left")
        label = ctk.CTkLabel(
            label_container,
            text=label_text,
            font=self.config.LABEL_FONT,
            text_color=self.config.LABEL_COLOR
        )
        label.pack(padx=2, pady=2)

        # Value
        value_container = ctk.CTkFrame(field_container, fg_color="transparent")
        value_container.pack(side="left", padx=(4, 0))
        value = ctk.CTkLabel(
            value_container,
            text="--",
            font=self.config.VALUE_FONT,
            text_color=self.config.TEXT_COLOR
        )
        value.pack(padx=2, pady=2)

        # Store reference
        self.value_labels[field_id] = value

    def update_value(self, field_id, value):
        """Update the value of a specific field"""
        if field_id in self.value_labels:
            self.value_labels[field_id].configure(text=str(value))

    def _handle_device_button(self):
        """Handle button click based on connection state"""
        if self.is_connected:
            self._disconnect_device()
        else:
            self._show_connection_dialog()

    def _disconnect_device(self):
        """Handle device disconnection"""
        # Reset will be handled by show_connection_status
        if hasattr(self, 'disconnect_command'):
            self.disconnect_command()

    def _show_connection_dialog(self):
        """Show the connection dialog"""
        self.connection_dialog = ConnectionDialog(
            self, 
            self.loop,
            BleakScanner,
            self._handle_connection
        )

    def _handle_connection(self, device_info):
        """Handle device connection callback"""
        if hasattr(self, 'connect_command'):  
            self.connect_command(device_info)

    def set_imu_presenters(self, imu1_presenter, imu2_presenter):
        """Set IMU presenters for logging"""
        self.imu1_presenter = imu1_presenter
        self.imu2_presenter = imu2_presenter

    def _on_log(self):
        """Handle log button click"""
        if not self.imu1_presenter or not self.imu2_presenter:
            return

        # If currently logging, stop logging
        if self.imu_logger:
            self._stop_logging()
            return

        # If folder is selected, start logging
        if self.selected_folder:
            self._start_logging()
            return
            
        # Otherwise show folder selection dialog
        try:
            def create_dialog():
                self.log_dialog = IMULogDialog(self.winfo_toplevel())
                
                def on_cancel():
                    self.log_dialog.destroy()
                    self.log_dialog = None
                
                def on_apply():
                    self.selected_folder = self.log_dialog.get_path()
                    self.log_button.configure(text="Start Log")
                    self.log_dialog.destroy()
                    self.log_dialog = None
                
                self.log_dialog.set_cancel_callback(on_cancel)
                self.log_dialog.set_apply_callback(on_apply)
            
            # Use after_idle to create dialog after event loop is free
            self.after_idle(create_dialog)
            
        except Exception as e:
            pass

    def _start_logging(self):
        """Start logging IMU data"""
        try:
            # Create timestamped subfolder
            now = datetime.datetime.now()
            subfolder_name = now.strftime("%d%m%Y_%H%M%S_vr_glove")
            full_path = os.path.join(self.selected_folder, subfolder_name)
            os.makedirs(full_path, exist_ok=True)
            
            # Create logger
            self.imu_logger = IMULogger(full_path)
            if self.imu_logger.start_logging():
                # Update button
                self.log_button.configure(text="Stop Log", fg_color="darkred", hover_color="#8B0000")
                # Connect presenters
                self.imu1_presenter.set_log_dialog(self)
                self.imu2_presenter.set_log_dialog(self)
            else:
                self.imu_logger = None
                
        except Exception as e:
            self.imu_logger = None

    def _stop_logging(self):
        """Stop logging IMU data"""
        if self.imu_logger:
            self.imu_logger.stop_logging()
            self.imu_logger = None
            self.imu1_presenter.set_log_dialog(None)
            self.imu2_presenter.set_log_dialog(None)
            self.selected_folder = None  # Reset folder selection
            self.log_button.configure(text="Log", fg_color=self.config.BUTTON_COLOR, hover_color=self.config.BUTTON_HOVER_COLOR)

    def log_imu_data(self, imu_number, imu_data, euler_data):
        """Log IMU and Euler data to CSV files"""
        if self.imu_logger and self.imu_logger.is_logging:
            self.imu_logger.log_imu_data(imu_number, imu_data, euler_data)

    def show_log_button(self, show: bool):
        """Show or hide the log button"""
        if show:
            self.log_button.grid()
        else:
            self.log_button.grid_remove()

    def update_connection_status(self, connected, device_info=None, message=""):
        """Update connection status display (required by ConnectionViewInterface)"""
        self.is_connected = connected
        
        # Reset notification tracking
        self.last_battery_notification = None
        if self.notification_check_timer:
            self.after_cancel(self.notification_check_timer)
            self.notification_check_timer = None
        self.reconnect_button.grid_remove()
        
        if connected:
            # Store device address for reconnection
            if device_info and hasattr(device_info, 'address'):
                self.current_device_address = device_info.address

            self.show_log_button(True)  # Show log button when connected
            self.log_button.configure(text="Log")  # Reset log button text
            self.selected_folder = None  # Reset folder selection
            
            # Update button state
            self.device_button.configure(
                text="Disconnect",
                fg_color="darkred",
                hover_color="#8B0000"
            )
            
            # Update device info
            self.update_value("name", device_info.name if device_info else "--")
            self.update_value("status", "Connected")
            self.update_value("battery", "--")
            self.update_value("charging", "--")

            self.update_value("firmware", device_info.firmware if device_info else "--")
            self.update_value("model", device_info.model if device_info else "--")
            self.update_value("manufacturer", device_info.manufacturer if device_info else "--")
            self.update_value("hardware", device_info.hardware if device_info else "--")
            
        else:
            # Stop logging if active
            if self.imu_logger:
                self._stop_logging()
            
            # Reset folder selection
            self.selected_folder = None

            # Reset button state
            self.device_button.configure(
                text="Add device",
                fg_color=self.config.BUTTON_COLOR,
                hover_color=self.config.BUTTON_HOVER_COLOR
            )
            
            # Reset all fields
            for field_id in self.value_labels:
                self.update_value(field_id, "--")
            self.show_log_button(False)  # Hide log button when disconnected

    def show_connection_status(self, result, device_info=None, message=""):
        """Show connection status (required by ConnectionPresenter)"""
        # First update the UI
        self.update_connection_status(result, device_info, message)
        
        # Only update status dialog during connection attempts
        if hasattr(self, 'connection_dialog') and self.connection_dialog and message != "Disconnected":
            if result:
                self.connection_dialog.connection_success = True
                self.connection_dialog.status_dialog.show_connected(device_info)
            else:
                self.connection_dialog.connection_success = False
                self.connection_dialog.status_dialog.show_failed()

    def set_handlers(self, connect_command, disconnect_command):
        """Set connection command handlers"""
        self.connect_command = connect_command
        self.disconnect_command = disconnect_command
        
    def clear_displays(self):
        """Clear all displays (required by ConnectionViewInterface)"""
        # Reset all fields to --
        for field_id in self.value_labels:
            self.update_value(field_id, "--")
