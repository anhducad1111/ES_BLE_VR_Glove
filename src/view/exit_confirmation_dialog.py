import customtkinter as ctk
from src.config.app_config import AppConfig
from src.view.button_component import ButtonComponent

class ExitConfirmationDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.config = AppConfig()  # Get singleton instance
        self.loop = None  # Will be set by caller
        self._destroyed = False
        
        # Check if parent App has active connection
        self.has_device = hasattr(parent, 'ble_service') and parent.ble_service.is_connected()
        
        self._setup_window(parent)
        self._create_main_layout()
        
        # Bind escape key
        self.bind("<Escape>", lambda e: self.destroy())
        
    def _setup_window(self, parent):
        """Setup window properties"""
        self.title("Exit Application")
        self.overrideredirect(False)  # Keep window decorations
        self.configure(fg_color="#1F1F1F")  # Dark background
        self.geometry("400x200")  # Adjust size as needed
        self.resizable(False, False)  # Fix window size
        self.protocol("WM_DELETE_WINDOW", self.destroy)  # Handle window close button
        self._center_window(parent)
        self.attributes("-topmost", True)  # Keep on top
        
        # Add border frame
        border_frame = ctk.CTkFrame(
            self,
            fg_color=self.config.BACKGROUND_COLOR,
            border_color=("#777777", "#777777"),
            border_width=1,
            corner_radius=8
        )
        border_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Content frame
        self.content_frame = ctk.CTkFrame(border_frame, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        title = ctk.CTkLabel(
            self.content_frame,
            text="Exit Application",
            font=("Inter Bold", 16),
            text_color="white"
        )
        title.pack(pady=(0, 20))
        
    def _center_window(self, parent):
        """Center dialog relative to parent"""
        x = parent.winfo_rootx() + (parent.winfo_width() - 400) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - 200) // 2
        self.geometry(f"+{x}+{y}")
        
    def _create_main_layout(self):
        """Create dialog layout"""
        # Center container
        center_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        center_frame.pack(fill="both", expand=True)
        
        # Message
        message = ctk.CTkLabel(
            self.content_frame,
            text="Do you want to exit?" +
                 ("\nDevice will be disconnected." if self.has_device else ""),
            font=self.config.HEADER_FONT,
            text_color=self.config.TEXT_COLOR,
            justify="center"
        )
        message.pack(expand=True)
        
        # Button container centered at bottom
        button_container = ctk.CTkFrame(center_frame, fg_color="transparent")
        button_container.pack(fill="x", pady=(0, 20))
        button_container.grid_columnconfigure(0, weight=1)
        
        # Button frame for horizontal centering
        button_frame = ctk.CTkFrame(button_container, fg_color="transparent")
        button_frame.grid(row=0, column=0)
        
        # Cancel button
        self.cancel_btn = ButtonComponent(
            button_frame,
            "Cancel",
            command=self.destroy,
            width=120,
            fg_color="transparent",
            hover_color="gray20",
            cursor="hand2"
        )
        self.cancel_btn.pack(side="left", padx=10)
        
        # Yes button
        self.yes_btn = ButtonComponent(
            button_frame,
            "Yes",
            command=self._handle_yes,
            width=120,
            fg_color="#0078D4",
            hover_color="#006CBE",
            cursor="hand2"
        )
        self.yes_btn.pack(side="left", padx=10)
        
        # Make dialog focusable for keyboard events
        self.focus_set()
        
    def set_on_yes_callback(self, callback):
        """Set callback for yes button"""
        self.on_yes = callback
        
    def _handle_yes(self):
        """Handle yes button click"""
        if hasattr(self, 'on_yes'):
            self.on_yes()
            
    def destroy(self):
        """Handle dialog destruction"""
        self._destroyed = True
        super().destroy()
