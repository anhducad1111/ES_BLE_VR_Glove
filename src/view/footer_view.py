import customtkinter as ctk
from src.config.app_config import AppConfig
import time
from datetime import datetime

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
        self.after(300, self._start_time_update)  # Update every second
        
    def _update_time(self):
        """Update the time display and check sync status"""
        current_time = datetime.now()
        
        if not self.is_synced and self.device_timestamp:
            # If device time differs by more than 5 seconds, show blinking
            time_diff = abs(time.time() - self.device_timestamp)
            if time_diff > 5:
                # Toggle color for blinking effect
                self.blink_state = not self.blink_state
                color = "red" if self.blink_state else self.config.TEXT_COLOR
                self.timestamp_label.configure(text_color=color)
        
        # Update displayed time
        if self.is_synced:
            # Show PC time when synced
            self.timestamp_label.configure(
                text=current_time.strftime('%Y-%m-%d %H:%M:%S'),
                text_color=self.config.TEXT_COLOR
            )
        elif self.device_timestamp:
            # Show device time when not synced
            device_time = datetime.fromtimestamp(self.device_timestamp)
            self.timestamp_label.configure(text=device_time.strftime('%Y-%m-%d %H:%M:%S'))
            
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
