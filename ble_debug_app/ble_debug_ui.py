import asyncio
import customtkinter as ctk
from bleak import BleakScanner
from src.config.app_config import AppConfig
from src.view.view_dialog.connection_dialog import ConnectionDialog
from src.model.ble_service import BLEDeviceInfo
from .ble_service import BLEService

class BLEDebugView(ctk.CTkFrame):
    """Debug view for BLE data"""
    
    def __init__(self, parent, ble_service: BLEService):
        super().__init__(parent)
        
        # Store BLE service
        self.ble_service = ble_service
        
        # Initialize config
        self.config = AppConfig()
        
        # Create main layout
        self._init_ui()
        
    def _init_ui(self):
        """Initialize UI components"""
        self.grid_columnconfigure(0, weight=1)
        
        # Test operations section
        self._init_test_section()
        
        # Services section  
        self._init_services_section()
        
        # Create info sections
        self._init_info_section()
        
    def _init_test_section(self):
        """Initialize test operations section"""
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
        
        self.uuid_entry = ctk.CTkEntry(uuid_frame, width=300)
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
        
    def _init_services_section(self):
        """Initialize services section"""
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
        
    def _init_info_section(self):
        """Initialize info section with raw and parsed data"""
        info_container = ctk.CTkFrame(self)
        info_container.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        info_container.grid_columnconfigure(0, weight=1)
        info_container.grid_columnconfigure(1, weight=1)

        # Left column - Raw & Device Info
        left_column = ctk.CTkFrame(info_container, fg_color="transparent")
        left_column.grid(row=0, column=0, sticky="nsew", padx=5)
        left_column.grid_columnconfigure(0, weight=1)

        self._init_raw_data_panel(left_column)
        self._init_device_info_panel(left_column)

        # Right column - Parsed Data
        right_column = ctk.CTkFrame(info_container, fg_color="transparent")
        right_column.grid(row=0, column=1, sticky="nsew", padx=5)
        right_column.grid_columnconfigure(0, weight=1)
        
        self._init_parsed_data_panel(right_column)
        
    def _init_raw_data_panel(self, parent):
        """Initialize raw data panel"""
        raw_frame = ctk.CTkFrame(parent)
        raw_frame.grid(row=0, column=0, sticky="nsew", pady=(0,5))
        
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
        
    def _init_device_info_panel(self, parent):
        """Initialize device info panel"""
        device_frame = ctk.CTkFrame(parent)
        device_frame.grid(row=1, column=0, sticky="nsew")
        
        device_label = ctk.CTkLabel(
            device_frame,
            text="Device Information:",
            font=self.config.HEADER_FONT
        )
        device_label.pack(anchor="w", padx=5, pady=5)
        
        # Battery frame
        battery_frame = ctk.CTkFrame(device_frame, fg_color="transparent")
        battery_frame.pack(fill="x", padx=5)
        
        self.battery_label = ctk.CTkLabel(
            battery_frame,
            text="Battery: --",
            font=self.config.TEXT_FONT
        )
        self.battery_label.pack(side="left", padx=5)
        
        self.charging_label = ctk.CTkLabel(
            battery_frame,
            text="Status: --",
            font=self.config.TEXT_FONT
        )
        self.charging_label.pack(side="right", padx=5)
        
        # Device details
        self.device_info = ctk.CTkTextbox(
            device_frame,
            height=80,
            font=self.config.TEXT_FONT
        )
        self.device_info.pack(fill="x", padx=5, pady=5)
        
    def _init_parsed_data_panel(self, parent):
        """Initialize parsed data panel"""
        parsed_frame = ctk.CTkFrame(parent)
        parsed_frame.grid(row=0, column=0, sticky="nsew")
        
        parsed_label = ctk.CTkLabel(
            parsed_frame,
            text="Parsed Data:",
            font=self.config.HEADER_FONT
        )
        parsed_label.pack(anchor="w", padx=5, pady=5)
        
        self.parsed_text = ctk.CTkTextbox(
            parsed_frame,
            height=200,
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
        if isinstance(data, str):
            # Update device info if applicable
            if any(key in data for key in ["Firmware Version:", "Hardware Version:", "Model:", "Manufacturer:"]):
                self.device_info.insert("end", data + "\n")
                return
            elif "Battery Level:" in data:
                self.battery_label.configure(text=data)
                return
            elif "Charging State:" in data:
                self.charging_label.configure(text=data)
                return
                
        # Update parsed text for other data
        self.parsed_text.delete("1.0", "end")
        self.parsed_text.insert("1.0", data)
        
    def set_button_states(self, enabled):
        """Enable/disable buttons"""
        state = "normal" if enabled else "disabled"
        self.read_button.configure(state=state)
        self.write_button.configure(state=state)
        self.notify_button.configure(state=state)
        
        # Reset device info when disconnecting
        if not enabled:
            self.battery_label.configure(text="Battery: --")
            self.charging_label.configure(text="Status: --")
            self.device_info.delete("1.0", "end")

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
        self.ble_service = BLEService()
        
        # Create window
        self._init_window()
        
        # Setup asyncio integration
        self._setup_asyncio_integration()
        
    def _init_window(self):
        """Initialize main window"""
        self.window = ctk.CTk()
        self.window.title("BLE Debug Tool")
        self.window.geometry(f"{self.config.WINDOW_WIDTH}x{self.config.WINDOW_HEIGHT}")
        
        # Setup grid
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=1)
        
        # Set window size to screen size
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        self.window.geometry(f"{screen_width}x{screen_height}+0+0")
        self.window.after(0, lambda: self.window.state('zoomed'))
        
        # Create main content
        self._init_content()
        
        # Setup close handler
        self.window.protocol("WM_DELETE_WINDOW", self._on_closing)
        
    def _init_content(self):
        """Initialize main content"""
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
        self.debug_view = BLEDebugView(self.content, self.ble_service)
        self.debug_view.grid(row=1, column=0, sticky="nsew")
        
        # Set operation handlers
        self.debug_view.set_handlers(
            loop=self.loop,
            on_read=lambda uuid: self.loop.create_task(self._handle_read(uuid)),
            on_write=lambda uuid: self.loop.create_task(self._handle_write(uuid)),
            on_notify=lambda uuid, enabled: self.loop.create_task(self._handle_notify(uuid, enabled))
        )
        
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
        
        success = await self.ble_service.connect(ble_device.address)
        
        if success:
            # Show success and discover services
            self.connection_dialog.status_dialog.show_connected(ble_device)
            
            # Get and display services
            services = await self.ble_service.discover_services()
            self.debug_view.update_services(services)
            
            # Read device information
            try:
                # Read device info characteristics
                for char_name in ["FIRMWARE_UUID", "HARDWARE_UUID", 
                                "MODEL_NUMBER_UUID", "MANUFACTURER_UUID"]:
                    uuid = self.ble_service.get_characteristic_uuid(char_name)
                    if uuid:
                        data = await self.ble_service.read_characteristic(uuid)
                        if data:
                            parsed = self.ble_service.parse_data(data, uuid)
                            self.debug_view.update_parsed_data(parsed)
                            await asyncio.sleep(0.1)  # Small delay between reads
                
                # Start battery notifications
                battery_uuid = self.ble_service.get_characteristic_uuid("BATTERY_LEVEL_UUID")
                charging_uuid = self.ble_service.get_characteristic_uuid("BATTERY_CHARGING_UUID")
                
                if battery_uuid:
                    await self.ble_service.start_notify(battery_uuid, self._notification_handler)
                if charging_uuid:
                    await self.ble_service.start_notify(charging_uuid, self._notification_handler)
                    
            except Exception as e:
                print(f"Error reading device info: {e}")
            
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
                parsed = self.ble_service.parse_data(data, uuid)
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
            
    def _notification_handler(self, uuid: str, sender: any, data: bytes):
        """Handle incoming notifications"""
        def update():
            self.debug_view.update_raw_data(data)
            parsed = self.ble_service.parse_data(data, uuid)
            self.debug_view.update_parsed_data(parsed)
            
        # Schedule UI update on main thread
        self.window.after(0, update)
        
    def run(self):
        """Start the application"""
        self.window.mainloop()