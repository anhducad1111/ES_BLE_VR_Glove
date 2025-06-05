import customtkinter as ctk
from dataclasses import dataclass
from typing import Callable, Optional
from src.config.app_config import AppConfig
from src.view.view_component.button_component import ButtonComponent
from src.view.view_component.coordinate_entry import CoordinateEntry
from .base_dialog import BaseDialog, DialogConfig, DialogStyle

@dataclass
class OtherConfigSettings:
    """Configuration for other settings dialog"""
    input_bg: str = "#1F1F1F"
    input_border: str = "#2A2A2A"
    description_color: str = "#666666"
    default_rate: int = 1000

class OtherConfigDialog(BaseDialog):
    """Dialog for configuring other settings"""
    
    def __init__(self, parent: ctk.CTk):
        self.settings = OtherConfigSettings()
        self._destroyed = False
        self.rate_entry: Optional[CoordinateEntry] = None
        self.apply_button: Optional[ButtonComponent] = None
        self.cancel_button: Optional[ButtonComponent] = None

        config = DialogConfig(
            title="",  # Empty to prevent default header
            width=450,
            height=300,
            style=DialogStyle(
                fg_color="#1F1F1F",
                content_bg="#141414",
                border_color="#333333",
                border_width=1,
                corner_radius=8
            )
        )
        super().__init__(parent, config)
        
        # Override window settings
        # self.overrideredirect(True)  # Remove window decorations

    def _create_title_section(self) -> None:
        """Create custom header section"""
        header = ctk.CTkLabel(
            self.content_frame,
            text="OTHER Configuration",
            font=("Inter Bold", 18),
            text_color="white"
        )
        header.pack(anchor="w", pady=(0, 30))

    def _create_content(self) -> None:
        """Create dialog content"""
        self._create_rate_section()

    def _create_rate_section(self) -> None:
        """Create rate input section"""
        # Container with border
        container = ctk.CTkFrame(
            self.content_frame,
            fg_color=self.settings.input_bg,
            corner_radius=12,
            border_width=1,
            border_color=self.settings.input_border
        )
        container.pack(fill="x", pady=(0, 30), ipady=20)

        # Content with padding
        content = ctk.CTkFrame(container, fg_color="transparent")
        content.pack(fill="x", padx=20, pady=5)

        # Rate description
        description = ctk.CTkLabel(
            content,
            text="Rate (ms)",
            font=("Inter", 12),
            text_color=self.settings.description_color
        )
        description.pack(anchor="w", pady=(0, 10))

        # Rate input
        self.rate_entry = CoordinateEntry(
            content,
            "Joystick, flex, force sensor cap buttons",
            entry_width=120
        )
        self.rate_entry.pack(anchor="w")
        self.rate_entry.entry.configure(state="normal")
        self.rate_entry.set_value(self.settings.default_rate, keep_editable=True)

    def _create_button_section(self, parent: Optional[ctk.CTkFrame] = None) -> None:
        """Override base dialog's button section"""
        container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        container.pack(fill="x", side="bottom")

        button_frame = ctk.CTkFrame(container, fg_color="transparent")
        button_frame.pack(side="right")

        # Cancel button
        self.cancel_button = ButtonComponent(
            button_frame,
            "Cancel",
            fg_color="transparent",
            hover_color="#424242",
            text_color="white",
        )
        self.cancel_button.pack(side="left", padx=10)

        # Apply button
        self.apply_button = ButtonComponent(
            button_frame,
            "Apply",
            fg_color="#0094FF",
            hover_color="#0078CC",
            text_color="white",
        )
        self.apply_button.pack(side="left")

    def get_rate_value(self) -> int:
        """Get the entered rate value"""
        try:
            return int(self.rate_entry.get_value())
        except ValueError:
            return self.settings.default_rate

    def set_cancel_callback(self, callback: Callable[[], None]) -> None:
        """Set callback for cancel button"""
        self.cancel_button.configure(command=callback)

    def set_apply_callback(self, callback: Callable[[], None]) -> None:
        """Set callback for apply button"""
        self.apply_button.configure(command=callback)

    def destroy(self) -> None:
        """Clean up resources"""
        self._destroyed = True
        super().destroy()