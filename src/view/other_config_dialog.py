import customtkinter as ctk
from src.config.app_config import AppConfig
from src.view.button_component import ButtonComponent
from src.view.coordinate_entry import CoordinateEntry

class OtherConfigDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self._destroyed = False
        self._setup_window(parent)
        self._create_main_layout()

    def _setup_window(self, parent):
        self.overrideredirect(True)  # Remove window decorations
        self.configure(fg_color="#1F1F1F")  # Dark background
        self.geometry("450x300")  # Adjust size
        self._center_window(parent)
        self._make_modal(parent)

    def _center_window(self, parent):
        """Center the dialog on the main window"""
        # Get the root window (main window)
        root = parent.winfo_toplevel()
        
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        root_x = root.winfo_x()
        root_y = root.winfo_y()
        root_width = root.winfo_width()
        root_height = root.winfo_height()
        
        x = root_x + (root_width - 450) // 2
        y = root_y + (root_height - 280) // 2
        
        x = max(0, min(x, screen_width - 450))
        y = max(0, min(y, screen_height - 280))
        
        self.geometry(f"+{x}+{y}")

    def _make_modal(self, parent):
        self.transient(parent)
        self.grab_set()

    def _create_main_layout(self):
        # Main frame with border
        main_frame = ctk.CTkFrame(
            self,
            fg_color="#141414",
            border_color="#333333",
            border_width=1,
            corner_radius=8
        )
        main_frame.pack(fill="both", expand=True, padx=2, pady=2)

        # Content frame with padding
        content = ctk.CTkFrame(main_frame, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=25, pady=25)

        # Title - left aligned
        header = ctk.CTkLabel(
            content,
            text="OTHER Configuration",
            font=("Inter Bold", 18),
            text_color="white"
        )
        header.pack(anchor="w", pady=(0, 30))

        # Rate input container with darker background
        rate_container = ctk.CTkFrame(
            content,
            fg_color="#1F1F1F",  # Darker than main background
            corner_radius=12,
            border_width=1,
            border_color="#2A2A2A"
        )
        rate_container.pack(fill="x", pady=(0, 30), ipady=20)

        # Inner padding frame
        rate_content = ctk.CTkFrame(rate_container, fg_color="transparent")
        rate_content.pack(fill="x", padx=20, pady=5)

        # Description label
        description = ctk.CTkLabel(
            rate_content,
            text="Rate (ms)",
            font=("Inter", 12),
            text_color="#666666"  # Very subtle gray for description
        )
        description.pack(anchor="w", pady=(0, 10))

        # Rate input field with label
        self.rate_entry = CoordinateEntry(rate_content, "Joystick, flex, force sensor cap buttons", entry_width=120)
        self.rate_entry.pack(anchor="w")
        self.rate_entry.entry.configure(state="normal")  # Cho phép chỉnh sửa
        self.rate_entry.set_value(1000)  # Default value

        # Right-aligned button container
        button_container = ctk.CTkFrame(content, fg_color="transparent")
        button_container.pack(fill="x", side="bottom")

        # Create a frame for right-aligned buttons
        button_right_frame = ctk.CTkFrame(button_container, fg_color="transparent")
        button_right_frame.pack(side="right")

        # Cancel button
        self.cancel_button = ButtonComponent(
            button_right_frame,
            "Cancel",
            fg_color="transparent",
            hover_color="#424242",
            text_color="white",
        )
        self.cancel_button.pack(side="left", padx=10)

        # Apply button
        self.apply_button = ButtonComponent(
            button_right_frame,
            "Apply",
            fg_color="#0094FF",
            hover_color="#0078CC",
            text_color="white",
        )
        self.apply_button.pack(side="left", padx=(0, 0),)

    def get_rate_value(self):
        """Get the entered rate value"""
        try:
            return int(self.rate_entry.get_value())
        except ValueError:
            return 1000  # Return default if invalid

    def set_cancel_callback(self, callback):
        self.cancel_button.configure(command=callback)

    def set_apply_callback(self, callback):
        self.apply_button.configure(command=callback)

    def destroy(self):
        self._destroyed = True
        super().destroy()
