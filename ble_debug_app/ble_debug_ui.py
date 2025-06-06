import asyncio
import customtkinter as ctk
from bleak import BleakScanner
from src.config.app_config import AppConfig
from src.view.view_dialog.connection_dialog import ConnectionDialog
from src.model.ble_service import BLEDeviceInfo
from .ble_debug_service import BLEDebugService

class BLEDebugView(ctk.CTkFrame):
    """Debug view for BLE data"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        # Initialize config
        self.config = AppConfig()  # Get singleton instance
        
        # Create main layout
        self.grid_columnconfigure(0, weight=1)
        
        # Test operations section
        test_frame = ctk.CTkFrame(self)
        test_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)
        
        test_label = ctk.CTkLabel(
            test_frame,
            text="Test Operations:",
            font=self.config.HEADER_FONT
        )
        test_label.pack(anchor="w", padx=5, pady=5)
        
        # UUID input
        uuid_frame = ctk.CTkFrame(test_frame, fg_color="transparent")
        uuid_frame.pack(fill="x", padx=5, pady=5)
        
        uuid_label = ctk.CTkLabel(
            uuid_frame,
            text="UUID:",
            font=self.config.LABEL_FONT
        )
        uuid_label.pack(side="left", padx=(5,10))
        
        self.uuid_entry = ctk.CTkEntry(
            uuid_frame,
            width=300
        )
        self.uuid_entry.pack(side="left", fill="x", expand=True)
        
        # Operation buttons
        button_frame = ctk.CTkFrame(test_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=5, pady=5)
        
        self.read_button = ctk.CTkButton(
            button_frame,
            text="Read",
            width=100,
            command=self._on_read_clicked
        )
        self.read_button.pack(side="left", padx=5)
        
        self.notify_button = ctk.CTkButton(
            button_frame,
            text="Start Notify",
            width=100,
            command=self._on_notify_clicked
        )
        self.notify_button.pack(side="left", padx=5)
        
        self.write_button = ctk.CTkButton(
            button_frame,
            text="Write",
            width=100,
            command=self._on_write_clicked
        )
        self.write_button.pack(side="left", padx=5)
        
        self.notifying = False
        
        # Services section
        services_frame = ctk.CTkFrame(self)
        services_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        services_label = ctk.CTkLabel(
            services_frame,
            text="Services & Characteristics:",
            font=self.config.HEADER_FONT
        )
        services_label.pack(anchor="w", padx=5, pady=5)
        
        self.services_text = ctk.CTkTextbox(
            services_frame,
            height=200,
            font=self.config.TEXT_FONT
        )
        self.services_text.pack(fill="x", padx=5, pady=5)
        
        # Raw data section
        raw_frame = ctk.CTkFrame(self)
        raw_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        
        raw_label = ctk.CTkLabel(
            raw_frame,
            text="Raw Data:",
            font=self.config.HEADER_FONT
        )
        raw_label.pack(anchor="w", padx=5, pady=5)
        
        self.raw_text = ctk.CTkTextbox(
            raw_frame,
            height=100,
            font=self.config.TEXT_FONT
        )
        self.raw_text.pack(fill="x", padx=5, pady=5)
        
        # Parsed data section
        parsed_frame = ctk.CTkFrame(self)
        parsed_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=5)
        
        parsed_label = ctk.CTkLabel(
            parsed_frame,
            text="Parsed Data:",
            font=self.config.HEADER_FONT
        )
        parsed_label.pack(anchor="w", padx=5, pady=5)
        
        self.parsed_text = ctk.CTkTextbox(
            parsed_frame,
            height=100,
            font=self.config.TEXT_FONT
        )
        self.parsed_text.pack(fill="x", padx=5, pady=5)
        
    def update_services(self, services_data):
        """Update services display"""
        text = ""
        for service_uuid, service_info in services_data.items():
            text += f"Service: {service_uuid}\n"
            for char_uuid, char_info in service_info['characteristics'].items():
                text += f"  Characteristic: {char_uuid}\n"
                text += f"  Properties: {', '.join(char_info['properties'])}\n"
            text += "\n"
            
        self.services_text.delete("1.0", "end")
        self.services_text.insert("1.0", text)
        
    def update_raw_data(self, data):
        """Update raw data display"""
        if not data:
            text = "No data"
        else:
            text = ' '.join(f'{b:02x}' for b in data)
            
        self.raw_text.delete("1.0", "end")
        self.raw_text.insert("1.0", text)
        
    def update_parsed_data(self, data):
        """Update parsed data display"""
        self.parsed_text.delete("1.0", "end")
        self.parsed_text.insert("1.0", data)
        
    def _on_read_clicked(self):
        """Handle read button click"""
        if self.on_read:
            uuid = self.uuid_entry.get().strip()
            if uuid:
                self.on_read(uuid)
                
    def _on_notify_clicked(self):
        """Handle notify button click"""
        if self.on_notify:
            uuid = self.uuid_entry.get().strip()
            if uuid:
                if not self.notifying:
                    self.notify_button.configure(text="Stop Notify")
                    self.notifying = True
                    self.on_notify(uuid, True)
                else:
                    self.notify_button.configure(text="Start Notify")
                    self.notifying = False
                    self.on_notify(uuid, False)
                    
    def _on_write_clicked(self):
        """Handle write button click"""
        if self.on_write:
            uuid = self.uuid_entry.get().strip()
            if uuid:
                self.on_write(uuid)
                
    def set_handlers(self, loop=None, on_read=None, on_write=None, on_notify=None):
        """Set handlers for button operations"""
        self.loop = loop
        self.on_read = on_read
        self.on_write = on_write
        self.on_notify = on_notify
        
    def set_button_states(self, enabled):
        """Enable/disable buttons"""
        state = "normal" if enabled else "disabled"
        self.read_button.configure(state=state)
        self.write_button.configure(state=state)
        self.notify_button.configure(state=state)

class DebugApp:
    def __init__(self):
        # Initialize config
        self.config = AppConfig()
        
        # Set appearance mode
        ctk.set_appearance_mode(self.config.APPEARANCE_MODE)
        
        # Create event loop
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        # Initialize BLE service
        self.ble_service = BLEDebugService()
        
        # Create window
        self.window = ctk.CTk()
        self.window.title("BLE Debug Tool")
        self.window.geometry(f"{self.config.WINDOW_WIDTH}x{self.config.WINDOW_HEIGHT}")
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=1)
        
        # Get screen dimensions
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        # Set window size to screen size
        self.window.geometry(f"{screen_width}x{screen_height}+0+0")
        self.window.after(0, lambda: self.window.state('zoomed'))

        # Create main content
        self.content = ctk.CTkFrame(self.window)
        self.content.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(1, weight=1)

        # Create header with buttons
        header = ctk.CTkFrame(self.content, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header.grid_columnconfigure(1, weight=1)

        # Add Device button
        self.add_button = ctk.CTkButton(
            header,
            text="Add Device",
            width=120,
            command=self._show_connection_dialog
        )
        self.add_button.grid(row=0, column=0, padx=5)

        # Connect/Disconnect button
        self.connect_button = ctk.CTkButton(
            header,
            text="Connect",
            width=120,
            state="disabled"
        )
        self.connect_button.grid(row=0, column=2, padx=5)
        
        # Create debug view
        self.debug_view = BLEDebugView(self.content)
        self.debug_view.grid(row=1, column=0, sticky="nsew")
        
        # Set operation handlers
        self.debug_view.set_handlers(
            loop=self.loop,
            on_read=lambda uuid: self.loop.create_task(self._handle_read(uuid)),
            on_write=lambda uuid: self.loop.create_task(self._handle_write(uuid)),
            on_notify=lambda uuid, enabled: self.loop.create_task(self._handle_notify(uuid, enabled))
        )
        
        # Connection dialog will be created when needed
        self.connection_dialog = None
        
        # Setup asyncio integration
        self._setup_asyncio_integration()
        
        # Setup window close handler
        self.window.protocol("WM_DELETE_WINDOW", self._on_closing)
        
    def _setup_asyncio_integration(self):
        """Setup asyncio integration with Tkinter"""
        def handle_asyncio():
            self.loop.stop()
            self.loop.run_forever()
            self.window.after(10, handle_asyncio)
        self.window.after(10, handle_asyncio)
        
    def _show_connection_dialog(self):
        """Show connection dialog"""
        self.connection_dialog = ConnectionDialog(
            self.window,
            self.loop,
            BleakScanner,
            self._handle_connection
        )
        
    def _handle_connection(self, device_info):
        """Handle device selection"""
        self.loop.create_task(self._connect_to_device(device_info))
        
    async def _connect_to_device(self, device_info):
        """Connect to selected device"""
        ble_device = BLEDeviceInfo(
            address=device_info["address"],
            name=device_info["name"],
            rssi=device_info["rssi"]
        )
        
        success = await self.ble_service.connect(ble_device)
        
        if success:
            # Show success and discover services
            self.connection_dialog.status_dialog.show_connected(ble_device)
            
            # Get and display services
            services = await self.ble_service.discover_services()
            self.debug_view.update_services(services)
            
            # Enable and update connect button
            self.connect_button.configure(
                text="Disconnect",
                command=self._disconnect_device,
                state="normal"
            )
            self.debug_view.set_button_states(True)
        else:
            # Show failure
            self.connection_dialog.status_dialog.show_failed()
            
    def _disconnect_device(self):
        """Disconnect from device"""
        async def disconnect():
            await self.ble_service.disconnect()
            # Reset buttons
            self.connect_button.configure(
                text="Connect",
                state="disabled"
            )
            # Clear displays and disable buttons
            self.debug_view.update_services({})
            self.debug_view.update_raw_data(None)
            self.debug_view.update_parsed_data("")
            self.debug_view.set_button_states(False)
            
        self.loop.create_task(disconnect())
        
    def _on_closing(self):
        """Handle window closing"""
        async def cleanup():
            await self.ble_service.disconnect()
            
        self.loop.run_until_complete(cleanup())
        self.loop.stop()
        self.window.quit()
        
    async def _handle_read(self, uuid):
        """Handle read operation"""
        try:
            data = await self.ble_service.read_characteristic(uuid)
            if data:
                self.debug_view.update_raw_data(data)
                parsed = self.ble_service.parse_imu_data(data)
                self.debug_view.update_parsed_data(parsed)
            else:
                self.debug_view.update_raw_data(None)
                self.debug_view.update_parsed_data("Read failed")
        except Exception as e:
            self.debug_view.update_parsed_data(f"Error: {e}")
            
    async def _handle_write(self, uuid):
        """Handle write operation"""
        try:
            # Write 9 zeros (18 bytes) as dummy IMU data
            data = bytes([0] * 18)
            success = await self.ble_service.write_characteristic(uuid, data)
            if success:
                self.debug_view.update_parsed_data("Write successful")
            else:
                self.debug_view.update_parsed_data("Write failed")
        except Exception as e:
            self.debug_view.update_parsed_data(f"Error: {e}")
            
    async def _handle_notify(self, uuid, enable):
        """Handle notify operation"""
        try:
            if enable:
                success = await self.ble_service.start_notify(
                    uuid, 
                    self._notification_handler
                )
                if success:
                    self.debug_view.update_parsed_data("Notifications started")
                else:
                    self.debug_view.update_parsed_data("Failed to start notifications")
                    self.debug_view.notify_button.configure(text="Start Notify")
                    self.debug_view.notifying = False
            else:
                success = await self.ble_service.stop_notify(uuid)
                if success:
                    self.debug_view.update_parsed_data("Notifications stopped")
                else:
                    self.debug_view.update_parsed_data("Failed to stop notifications")
                    self.debug_view.notify_button.configure(text="Stop Notify")
                    self.debug_view.notifying = True
        except Exception as e:
            self.debug_view.update_parsed_data(f"Error: {e}")
            
    def _notification_handler(self, sender, data):
        """Handle incoming notifications"""
        def update():
            self.debug_view.update_raw_data(data)
            parsed = self.ble_service.parse_imu_data(data)
            self.debug_view.update_parsed_data(parsed)
            
        # Schedule UI update on main thread
        self.window.after(0, update)
        
    def run(self):
        """Start the application"""
        self.window.mainloop()