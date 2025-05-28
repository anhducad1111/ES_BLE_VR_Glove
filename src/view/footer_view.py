import customtkinter as ctk
from src.config.app_config import AppConfig
import time
from datetime import datetime
from bleak import BleakScanner

class FooterComponent(ctk.CTkFrame):
    def __init__(self, parent):
        self.config = AppConfig()  # Get singleton instance
        super().__init__(
            parent,
            height=self.config.FOOTER_HEIGHT,
            fg_color=self.config.FOOTER_COLOR,
            corner_radius=0
        )
        self.pack_propagate(False)
        self.device_timestamp = None
        self.is_synced = False
        self.blink_state = False
        self.loop = None  # Event loop for async operations
        self._create_footer()
        self._start_time_update()

    def _create_footer(self):
        """Create the footer content with version and timestamp labels"""
        self.version_label = ctk.CTkLabel(
            self,
            text=f"Version {self.config.APP_VERSION}",
            font=self.config.LABEL_FONT,
            text_color=self.config.TEXT_COLOR
        )
        self.version_label.pack(side="left", padx=self.config.FOOTER_PADDING, pady=0)

        self.ble_status = ctk.CTkLabel(
            self,
            text="BLE OFF",
            font=self.config.LABEL_FONT,
            text_color="red"
        )
        self.ble_status.pack(side="left", padx=self.config.FOOTER_PADDING, pady=0)
        
        # Create timestamp label with click binding
        self.timestamp_label = ctk.CTkLabel(
            self,
            text="",  # Will be updated by _update_time
            font=self.config.LABEL_FONT,
            text_color=self.config.TEXT_COLOR,
            cursor="hand2"  # Show hand cursor on hover
        )
        self.timestamp_label.pack(side="right", padx=self.config.FOOTER_PADDING, pady=0)
        self.timestamp_label.bind("<Button-1>", self._on_timestamp_click)
        
    def _start_time_update(self):
        """Start the time update cycle"""
        self._update_time()
        self._check_ble_status()
        self.after(300, self._start_time_update)  # Update every 300ms
        
    async def _check_ble_status_async(self):
        """Check BLE adapter status asynchronously"""
        try:
            scanner = BleakScanner()
            await scanner.discover(timeout=0.1)
            self.ble_status.configure(text="BLE ON", text_color=self.config.TEXT_COLOR)
        except Exception as e:
            error_msg = str(e)
            if "bluetooth" in error_msg.lower() or "WinError -2147020577" in error_msg:
                self.ble_status.configure(text="BLE OFF", text_color="red")
            else:
                self.ble_status.configure(text="BLE OFF", text_color="red")
                
    def _check_ble_status(self):
        """Check BLE adapter status"""
        if self.loop:
            self.loop.create_task(self._check_ble_status_async())
        
    def _update_time(self):
        """Update the time display and check sync status"""
        current_time = datetime.now()
        
        # Default to showing current PC time
        display_time = current_time
        text_color = self.config.TEXT_COLOR
        
        if not self.is_synced and self.device_timestamp:
            # If we have device timestamp and not synced, show device time
            display_time = datetime.fromtimestamp(self.device_timestamp)
            
            # Check for time drift
            time_diff = abs(time.time() - self.device_timestamp)
            if time_diff > 5:
                # Toggle color for blinking effect
                self.blink_state = not self.blink_state
                text_color = "red" if self.blink_state else self.config.TEXT_COLOR
        
        # Update the timestamp label
        self.timestamp_label.configure(
            text=display_time.strftime('%Y-%m-%d %H:%M:%S'),
            text_color=text_color
        )
            
    def set_device_timestamp(self, unix_timestamp):
        """Set the device timestamp and update display"""
        self.device_timestamp = unix_timestamp
        self.is_synced = False
        self._update_time()
        
    def sync_with_pc_time(self):
        """Switch to PC time display"""
        self.is_synced = True
        self.timestamp_label.configure(text_color=self.config.TEXT_COLOR)
        
    def _on_timestamp_click(self, event):
        """Handle timestamp label click"""
        if not self.is_synced and hasattr(self, 'on_timestamp_click'):
            self.on_timestamp_click()
