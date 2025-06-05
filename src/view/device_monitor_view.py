import customtkinter as ctk
from bleak import BleakScanner
from PIL import Image
from src.config.app_config import AppConfig
from src.view.connection_dialog import ConnectionDialog
from src.view.button_component import ButtonComponent
from src.view.coordinate_entry import CoordinateEntry
from src.view.view_interfaces import ConnectionViewInterface
from src.util.log_manager import LogManager
import asyncio
from customtkinter import filedialog

class DeviceMonitorView(ctk.CTkFrame, ConnectionViewInterface):
    """View class for monitoring device information"""

    # region Initialization
    def __init__(self, master) -> None:
        """Initialize the device monitor view"""
        super().__init__(master, fg_color="transparent")
        self.config = AppConfig()
        self.pack(fill="both", expand=True, padx=self.config.WINDOW_PADDING, pady=self.config.WINDOW_PADDING)

        # UI Components
        self.info_frame = None
        self.device_button = None
        self.path_entry = None
        self.value_labels = {}
        self.log_manager = LogManager.instance()

        # Connection State
        self.is_connected = False
        self.connection_dialog = None
        self.loop = None
        self._destroyed = False
        self.current_device_address = None
        self._heartbeat_handler = None
        self._heartbeat_task = None

        # Logging State
        self.imu1_presenter = None
        self.imu2_presenter = None

        # Initialize UI
        self._create_layout()
    # endregion

    # region Connect itf
    def set_heartbeat_handler(self, handler):
        """Set handler for heartbeat monitoring"""
        self._heartbeat_handler = handler

    def start_heartbeat(self):
        """Start heartbeat monitoring"""
        if self._heartbeat_handler:
            self._heartbeat_task = asyncio.create_task(self._heartbeat_handler())

    def stop_heartbeat(self):
        """Stop heartbeat monitoring"""
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            self._heartbeat_task = None

    def show_connection_lost(self):
        """Show UI elements for lost connection"""
        self.device_button.configure(fg_color="red")

    def update_connection_status(self, connected, device_info=None, message=""):
        """Update connection status display"""
        self.is_connected = connected
        
        # Stop heartbeat monitoring if disconnecting
        if not connected:
            self.stop_heartbeat()
        
        if connected:
            # Store device address for reconnection
            if device_info and hasattr(device_info, 'address'):
                self.current_device_address = device_info.address
            
            # Update button state
            self.device_button.configure(
                text="Disconnect",
                fg_color="#8B0000",
                hover_color="#B22222"
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
            # Reset button state
            self.device_button.configure(
                text="Add device",
                fg_color=self.config.BUTTON_COLOR,
                hover_color=self.config.BUTTON_HOVER_COLOR
            )
            
            # Reset all fields
            self.clear_values()
    # endregion

    # region UI Layout
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
        for i in range(13):
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
            fg_color="transparent",
        )
        button_container.grid(row=0, column=9, rowspan=3, columnspan=4, sticky="e", padx=2, pady=2)

        button_container.grid_columnconfigure(0, weight=0)  
        button_container.grid_columnconfigure(1, weight=0) 

        # Add device button
        self.device_button = ButtonComponent(
            button_container,
            "Add device",
            command=self._handle_device_button
        )
        self.device_button.grid(row=2, column=1, pady=(8, 8), padx=12, sticky="e", )

        # Path container
        path_container = ctk.CTkFrame(button_container, fg_color="transparent") 
        path_container.grid(row=1, column=1, pady=(0, 8), padx=12, sticky="e")
        
        # Configure grid in path_container
        path_container.grid_columnconfigure(0, weight=0)  # For folder icon
        path_container.grid_columnconfigure(1, weight=0)  # For entry field
        
        # Create folder icon
        icon = Image.open("assets/folder.png")
        folder_image = ctk.CTkImage(
            light_image=icon,
            dark_image=icon,
            size=(20, 20)
        )
        
        # Create clickable icon label
        folder_label = ctk.CTkLabel(
            path_container,
            text="",
            image=folder_image,
            cursor="hand2"
        )
        folder_label.grid(row=0, column=0, padx=(0, 10), sticky="w")
        folder_label.bind("<Button-1>", lambda e: self._on_choose_folder())

        # Path entry field
        self.path_entry = CoordinateEntry(
            path_container,
            "",
            entry_width=200
        )
        self.path_entry.grid(row=0, column=1, sticky="e")

        # Set path from LogManager
        self.path_entry.entry.delete(0, "end")
        self.path_entry.entry.insert(0, self.log_manager.get_selected_folder())
        self.path_entry.entry.configure(
            state="readonly",
            cursor="arrow"
        )
    
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
    # endregion

    # region UI Updates
    def update_value(self, field_id, value):
        """Update the value of a specific field"""
        if field_id in self.value_labels:
            self.value_labels[field_id].configure(text=str(value))

    def clear_values(self):
        """Clear all values"""
        fields_to_clear = [
            "name", "status", "battery", "charging",
            "firmware", "model", "manufacturer", "hardware"
        ]
        for field_id in fields_to_clear:
            if field_id in self.value_labels:
                self.update_value(field_id, "--")
    # endregion

    # region Connection 
    def _handle_device_button(self):
        """Handle button click based on connection state"""
        print(f"Device button clicked, is_connected: {self.is_connected}")
        if self.is_connected:
            self._disconnect_device()
        else:
            print("Showing connection dialog...")
            self._show_connection_dialog()

    async def _disconnect_async(self):
        """Async disconnect handler"""
        if hasattr(self, 'disconnect_command'):
            self.stop_heartbeat()  # Stop heartbeat monitoring
                
            try:
                await self.disconnect_command()
            finally:
                # Reset connection state and UI
                self.is_connected = False
                self.device_button.configure(
                    text="Add device",
                    state="normal",
                    fg_color=self.config.BUTTON_COLOR,
                    hover_color=self.config.BUTTON_HOVER_COLOR
                )
                # Reset connection dialog reference
                self.connection_dialog = None

    def _disconnect_device(self):
        """Handle device disconnection"""
            
        # Update UI immediately
        self.device_button.configure(text="Disconnecting...", state="disabled")
        self.clear_values()  # Clear all values immediately
        self.is_connected = False  # Update connection state immediately
        
        # Run disconnect in background
        if self.loop:
            asyncio.run_coroutine_threadsafe(self._disconnect_async(), self.loop)

    def _show_connection_dialog(self):
        """Show the connection dialog"""
        if not self.loop:
            print("Error: No event loop available")
            return
            
        try:
            # Clean up any existing dialog
            if self.connection_dialog:
                try:
                    self.connection_dialog.destroy()
                except:
                    pass
            
            # Create and show dialog
            self.connection_dialog = ConnectionDialog(
                self.winfo_toplevel(),  # Use top-level window as parent
                self.loop,
                BleakScanner,
                self._handle_connection
            )
            
            # Make dialog modal
            self.connection_dialog.transient(self.winfo_toplevel())
            self.connection_dialog.grab_set()
            self.connection_dialog.focus_set()
            
        except Exception as e:
            print(f"Error showing connection dialog: {e}")
            import traceback
            traceback.print_exc()

    def _handle_connection(self, device_info):
        """Handle device connection callback"""
        if hasattr(self, 'connect_command'):
            async def connect_wrapper():
                await self.connect_command(device_info)
            asyncio.run_coroutine_threadsafe(connect_wrapper(), self.loop)
    # endregion

    # region Resource 
    def show_connection_status(self, result, device_info=None, message=""):
        """Show connection status"""
        # Update the UI
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

    def update_battery(self, level):
        """Update battery level display"""
        # Use after to update UI from any thread
        self.after(0, lambda: self.update_value("battery", f"{level}%"))

    def update_charging(self, state):
        """Update charging state display"""
        # Use after to update UI from any thread
        self.after(0, lambda: self.update_value("charging", state))

    def _on_choose_folder(self):
        """Handle choose folder button click"""
        if not self._is_any_logger_active():
            # Tạm thời enable entry để có thể thay đổi nội dung
            self.path_entry.entry.configure(state="normal")
            
            folder = filedialog.askdirectory(initialdir=self.log_manager.get_selected_folder())
            if folder:
                self.path_entry.entry.delete(0, "end")
                self.path_entry.entry.insert(0, folder)
                self.log_manager.setup_logging_folder(folder)
            
            # Set lại readonly sau khi đã thay đổi
            self.path_entry.entry.configure(
                state="readonly",
                cursor="arrow"
            )
        
    def _is_any_logger_active(self):
        """Check if any logger is currently active"""
        return (self.log_manager.get_imu1_logger().is_logging or
                self.log_manager.get_imu2_logger().is_logging or 
                self.log_manager.get_sensor_logger().is_logging)
        
    def set_path_entry_state(self, state):
        """Enable/disable path entry based on logging state"""
        self.path_entry.entry.configure(state=state)
        
    def destroy(self):
        """Clean up resources before destroying widget"""
        # Clean up connection dialog
        if self.connection_dialog:
            try:
                self.connection_dialog.destroy()
            except:
                pass
            self.connection_dialog = None
            
        # Stop heartbeat monitoring
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            self._heartbeat_task = None
            
        # Mark as destroyed
        self._destroyed = True
        
        # Call parent destroy
        super().destroy()
    # endregion
