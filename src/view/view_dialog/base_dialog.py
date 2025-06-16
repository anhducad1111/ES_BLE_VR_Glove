from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Protocol, Tuple

import customtkinter as ctk

from src.config.app_config import AppConfig
from src.view.view_component.button_component import ButtonComponent


@dataclass
class DialogStyle:
    """Dialog styling configuration"""

    fg_color: str = "#1F1F1F"
    content_bg: str = "#2B2D30"
    border_color: str = "#777777"
    border_width: int = 1
    corner_radius: int = 8
    button_spacing: int = 10
    content_padding: Tuple[int, int] = field(default_factory=lambda: (20, 20))
    title_font: Tuple[str, int] = field(default_factory=lambda: ("Inter Bold", 16))
    text_color: str = "white"


@dataclass
class DialogConfig:
    """Dialog configuration settings"""

    title: str
    width: int
    height: int
    resizable: bool = False
    keep_on_top: bool = False
    show_border: bool = True
    style: DialogStyle = field(default_factory=DialogStyle)


class DialogCallback(Protocol):
    """Protocol for dialog callbacks"""

    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...


class BaseDialog(ctk.CTkToplevel):
    """Base class for all dialogs with common functionality"""

    def __init__(self, parent: ctk.CTk, config: DialogConfig) -> None:
        super().__init__(parent)
        self.app_config = AppConfig()  # Get singleton instance
        self.parent = parent
        self.config = config
        self._destroyed: bool = False

        self._setup_window()
        self._create_main_layout()

    def _setup_window(self) -> None:
        """Configure window properties"""
        self.title(self.config.title)
        self.overrideredirect(False)
        self.configure(fg_color=self.config.style.fg_color)
        self.geometry(f"{self.config.width}x{self.config.height}")
        self.resizable(self.config.resizable, self.config.resizable)
        self.protocol("WM_DELETE_WINDOW", self.destroy)

        if self.config.keep_on_top:
            self.attributes("-topmost", True)

        self._center_window()
        self._make_modal()

    def _center_window(self) -> None:
        """Center dialog relative to parent window"""
        root = self.parent.winfo_toplevel()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        root_x = root.winfo_x()
        root_y = root.winfo_y()
        root_width = root.winfo_width()
        root_height = root.winfo_height()

        x = root_x + (root_width - self.config.width) // 2
        y = root_y + (root_height - self.config.height) // 2

        # Ensure dialog stays within screen bounds
        x = max(0, min(x, screen_width - self.config.width))
        y = max(0, min(y, screen_height - self.config.height))

        self.geometry(f"+{x}+{y}")

    def _make_modal(self) -> None:
        """Make dialog modal"""
        self.transient(self.parent)
        self.grab_set()

    def _create_main_layout(self) -> None:
        """Create main dialog layout"""
        if self.config.show_border:
            self.border_frame = self._create_border_frame()
            self.content_frame = self._create_content_frame(self.border_frame)
        else:
            self.content_frame = self._create_content_frame(self)

        self._create_title_section()
        self._create_content()
        self._create_button_section()

    def _create_border_frame(self) -> ctk.CTkFrame:
        """Create border frame"""
        frame = ctk.CTkFrame(
            self,
            fg_color=self.config.style.content_bg,
            border_color=self.config.style.border_color,
            border_width=self.config.style.border_width,
            corner_radius=self.config.style.corner_radius,
        )
        frame.pack(fill="both", expand=True, padx=2, pady=2)
        return frame

    def _create_content_frame(self, parent: ctk.CTkBaseClass) -> ctk.CTkFrame:
        """Create content frame with padding"""
        content = ctk.CTkFrame(parent, fg_color="transparent")
        content.pack(
            fill="both",
            expand=True,
            padx=self.config.style.content_padding[0],
            pady=self.config.style.content_padding[1],
        )
        return content

    def _create_title_section(self) -> None:
        """Create title section - override in subclass if needed"""
        if not hasattr(self, "_title_created"):
            title_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
            title_frame.pack(fill="x", pady=(0, 15))

            header = ctk.CTkLabel(
                title_frame,
                text=self.config.title,
                font=self.config.style.title_font,
                text_color=self.config.style.text_color,
            )
            header.pack(side="left")
            self._title_created = True

    def _create_content(self) -> None:
        """Create dialog content - override in subclass"""
        pass

    def _create_button_section(self) -> None:
        """Create button section - override in subclass"""
        pass

    def create_button(
        self,
        parent: ctk.CTkBaseClass,
        text: str,
        command: Optional[Callable[[], None]] = None,
        **kwargs: Any,
    ) -> ButtonComponent:
        """Utility method to create standard buttons"""
        return ButtonComponent(
            parent, text, command=command or (lambda: None), **kwargs
        )

    def destroy(self) -> None:
        """Clean up resources"""
        self._destroyed = True
        super().destroy()
