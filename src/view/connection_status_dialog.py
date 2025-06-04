import customtkinter as ctk
import asyncio
from src.config.app_config import AppConfig

class ConnectionStatusDialog(ctk.CTkToplevel):
    """Dialog to show connection status"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.parent = parent
        self._destroyed = False
        self.config = AppConfig()  # Get singleton instance
        self.countdown_after_id = None
        
        self._setup_window()
        self._create_layout()
        
    def _setup_window(self):
        """Configure dialog window"""
        self.title("Connecting")
        self.overrideredirect(False)  # Keep window decorations
        self.configure(fg_color="#1F1F1F")  # Dark background
        self.geometry("400x200")  # Adjust size as needed
        self.resizable(False, False)  # Fix window size
        self.protocol("WM_DELETE_WINDOW", self.destroy)  # Handle window close button
        self._center_window()
        self._make_modal()
        
        
    def _center_window(self):
        """Center dialog on parent window"""
        x = self.parent.winfo_x() + (self.parent.winfo_width() - 450) // 2
        y = self.parent.winfo_y() + (self.parent.winfo_height() - 350) // 2
        self.geometry(f"+{max(0, x)}+{max(0, y)}")
        
    def _make_modal(self):
        """Make dialog modal"""
        self.transient(self.parent)
        self.grab_set()
        
    def _create_layout(self):
        """Create dialog layout"""
        # Border frame
        border_frame = ctk.CTkFrame(
            self,
            fg_color=("#2B2D30", "#2B2D30"),
            border_color=("#777777", "#777777"),
            border_width=1,
            corner_radius=8
        )
        border_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Main frame with padding
        main_frame = ctk.CTkFrame(border_frame, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            main_frame,
            text="Connecting...",
            font=self.config.TEXT_FONT
        )
        self.status_label.pack(pady=20)
        
        # Initialize button component but don't use it
        self.ok_button = None
        
    def show_connecting(self):
        """Show connecting state"""
        self.status_label.configure(text="Connecting...", font=self.config.LARGE_FONT)
        
    async def _countdown(self, device_info):
        """Show countdown after connection"""
        info_text = f"Connected to:\n{device_info.name}\nRSSI: {device_info.rssi} dBm"
        
        # Show initial connection success
        self.status_label.configure(text=info_text)
        await asyncio.sleep(1)
        
        # Countdown
        for i in range(3, 0, -1):
            self.status_label.configure(text=f"{info_text}\n\nStarting in {i}", font=self.config.LARGE_FONT)
            await asyncio.sleep(0.5)
            
        # Trigger the callback to start application
        if hasattr(self, 'ok_callback') and self.ok_callback:
            self.ok_callback()
            
        # Close both dialogs
        self.destroy()  # This will close connection status dialog
        if hasattr(self.parent, 'destroy'):  # This will close connection dialog
            self.parent.destroy()

    def show_connected(self, device_info):
        """Show connected state with device info and start countdown"""
        # Create async task for countdown
        asyncio.create_task(self._countdown(device_info))
        
    def show_failed(self):
        """Show connection failed state"""
        self.status_label.configure(text="Connection failed")
        
    def set_ok_callback(self, callback):
        """Set callback for auto-start after countdown"""
        self.ok_callback = callback

    def destroy(self):
        """Override destroy to handle cleanup"""
        self._destroyed = True
        super().destroy()
