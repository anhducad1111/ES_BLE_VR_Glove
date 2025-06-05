import customtkinter as ctk
from dataclasses import dataclass
from typing import Callable, Optional
from src.config.app_config import AppConfig
from src.view.button_component import ButtonComponent
from src.view.coordinate_entry import CoordinateEntry

@dataclass
class DialogConfig:
    """Configuration for dialog appearance"""
    width: int = 450
    height: int = 300
    fg_color: str = "#1F1F1F"
    content_bg: str = "#141414"
    border_color: str = "#333333"
    input_bg: str = "#1F1F1F"
    input_border: str = "#2A2A2A"
    description_color: str = "#666666"
    default_rate: int = 1000

class OtherConfigDialog(ctk.CTkToplevel):
    """Dialog for configuring other settings"""
    
    def __init__(self, parent: ctk.CTk):
        super().__init__(parent)
        self.config = DialogConfig()
        self._destroyed = False
        self.rate_entry: Optional[CoordinateEntry] = None
        self.apply_button: Optional[ButtonComponent] = None
        self.cancel_button: Optional[ButtonComponent] = None
        
        self._setup_window(parent)
        self._create_main_layout()

    def _setup_window(self, parent: ctk.CTk) -> None:
        """Configure window properties"""
        self.overrideredirect(True)
        self.configure(fg_color=self.config.fg_color)
        self.geometry(f"{self.config.width}x{self.config.height}")
        self._center_window(parent)
        self._make_modal(parent)

    def _center_window(self, parent: ctk.CTk) -> None:
        """Center dialog relative to parent window"""
        root = parent.winfo_toplevel()
        
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        root_x = root.winfo_x()
        root_y = root.winfo_y()
        root_width = root.winfo_width()
        root_height = root.winfo_height()
        
        x = root_x + (root_width - self.config.width) // 2
        y = root_y + (root_height - self.config.height) // 2
        
        x = max(0, min(x, screen_width - self.config.width))
        y = max(0, min(y, screen_height - self.config.height))
        
        self.geometry(f"+{x}+{y}")

    def _make_modal(self, parent: ctk.CTk) -> None:
        """Make dialog modal"""
        self.transient(parent)
        self.grab_set()

    def _create_main_layout(self) -> None:
        """Create main dialog layout"""
        main_frame = self._create_main_frame()
        content = self._create_content_frame(main_frame)
        self._create_header(content)
        self._create_rate_section(content)
        self._create_button_section(content)

    def _create_main_frame(self) -> ctk.CTkFrame:
        """Create main frame with border"""
        frame = ctk.CTkFrame(
            self,
            fg_color=self.config.content_bg,
            border_color=self.config.border_color,
            border_width=1,
            corner_radius=8
        )
        frame.pack(fill="both", expand=True, padx=2, pady=2)
        return frame

    def _create_content_frame(self, parent: ctk.CTkFrame) -> ctk.CTkFrame:
        """Create content frame with padding"""
        content = ctk.CTkFrame(parent, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=25, pady=25)
        return content

    def _create_header(self, parent: ctk.CTkFrame) -> None:
        """Create header section"""
        header = ctk.CTkLabel(
            parent,
            text="OTHER Configuration",
            font=("Inter Bold", 18),
            text_color="white"
        )
        header.pack(anchor="w", pady=(0, 30))

    def _create_rate_section(self, parent: ctk.CTkFrame) -> None:
        """Create rate input section"""
        container = self._create_rate_container(parent)
        content = self._create_rate_content(container)
        self._create_rate_description(content)
        self._create_rate_input(content)

    def _create_rate_container(self, parent: ctk.CTkFrame) -> ctk.CTkFrame:
        """Create container for rate input"""
        container = ctk.CTkFrame(
            parent,
            fg_color=self.config.input_bg,
            corner_radius=12,
            border_width=1,
            border_color=self.config.input_border
        )
        container.pack(fill="x", pady=(0, 30), ipady=20)
        return container

    def _create_rate_content(self, parent: ctk.CTkFrame) -> ctk.CTkFrame:
        """Create content frame for rate input"""
        content = ctk.CTkFrame(parent, fg_color="transparent")
        content.pack(fill="x", padx=20, pady=5)
        return content

    def _create_rate_description(self, parent: ctk.CTkFrame) -> None:
        """Create rate description label"""
        description = ctk.CTkLabel(
            parent,
            text="Rate (ms)",
            font=("Inter", 12),
            text_color=self.config.description_color
        )
        description.pack(anchor="w", pady=(0, 10))

    def _create_rate_input(self, parent: ctk.CTkFrame) -> None:
        """Create rate input field"""
        self.rate_entry = CoordinateEntry(
            parent, 
            "Joystick, flex, force sensor cap buttons", 
            entry_width=120
        )
        self.rate_entry.pack(anchor="w")
        self.rate_entry.entry.configure(state="normal")
        self.rate_entry.set_value(self.config.default_rate, keep_editable=True)

    def _create_button_section(self, parent: ctk.CTkFrame) -> None:
        """Create button section"""
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", side="bottom")

        button_frame = ctk.CTkFrame(container, fg_color="transparent")
        button_frame.pack(side="right")

        self._create_cancel_button(button_frame)
        self._create_apply_button(button_frame)

    def _create_cancel_button(self, parent: ctk.CTkFrame) -> None:
        """Create cancel button"""
        self.cancel_button = ButtonComponent(
            parent,
            "Cancel",
            fg_color="transparent",
            hover_color="#424242",
            text_color="white",
        )
        self.cancel_button.pack(side="left", padx=10)

    def _create_apply_button(self, parent: ctk.CTkFrame) -> None:
        """Create apply button"""
        self.apply_button = ButtonComponent(
            parent,
            "Apply",
            fg_color="#0094FF",
            hover_color="#0078CC",
            text_color="white",
        )
        self.apply_button.pack(side="left")

    # Public interface methods
    def get_rate_value(self) -> int:
        """Get the entered rate value"""
        try:
            return int(self.rate_entry.get_value())
        except ValueError:
            return self.config.default_rate

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