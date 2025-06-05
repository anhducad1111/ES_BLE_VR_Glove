import customtkinter as ctk
from dataclasses import dataclass
from typing import Optional, Callable, Protocol
from src.config.app_config import AppConfig
from src.view.view_component.button_component import ButtonComponent
from .base_dialog import BaseDialog, DialogConfig, DialogStyle

class YesCallback(Protocol):
    """Protocol for yes button callback"""
    def __call__(self) -> None: ...

class ExitConfirmationDialog(BaseDialog):
    def __init__(self, parent: ctk.CTk):
        # Check if parent App has active connection - fixed check
        self.has_device = False
        if hasattr(parent, 'ble_service'):
            if callable(getattr(parent.ble_service, 'is_connected', None)):
                self.has_device = parent.ble_service.is_connected()
        
        self._destroyed = False
        self.loop = None  # Will be set by caller
        self.on_yes: Optional[YesCallback] = None

        config = DialogConfig(
            title="",  # Empty title to prevent header
            width=400,
            height=200,
            style=DialogStyle(
                fg_color="#1F1F1F",
                content_bg=AppConfig().BACKGROUND_COLOR,
                border_color="#777777",
                border_width=1,
                corner_radius=8
            )
        )
        super().__init__(parent, config)
        
        # Match original window setup
        self.title("Exit Application")
        self.attributes("-topmost", True)
        self.bind("<Escape>", lambda e: self.destroy())

    def _create_title_section(self) -> None:
        """Override to create title in original position"""
        title = ctk.CTkLabel(
            self.content_frame,
            text="Exit Application",
            font=("Inter Bold", 16),
            text_color="white"
        )
        title.pack(pady=(0, 20))

    def _create_content(self) -> None:
        """Create dialog content matching original exactly"""
        # Center container - main container for message and buttons
        center_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        center_frame.pack(fill="both", expand=True)

        # Create message text
        message_text = "Do you want to exit?"

        # Message - in center_frame with proper wrapping
        message = ctk.CTkLabel(
            center_frame,
            text=message_text,
            font=self.app_config.HEADER_FONT,
            text_color=self.app_config.TEXT_COLOR,
            justify="center",
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

    def set_on_yes_callback(self, callback: YesCallback) -> None:
        """Set callback for yes button"""
        self.on_yes = callback

    def _handle_yes(self) -> None:
        """Handle yes button click"""
        if self.on_yes:
            self.on_yes()

    def destroy(self) -> None:
        """Handle dialog destruction"""
        self._destroyed = True
        super().destroy()
