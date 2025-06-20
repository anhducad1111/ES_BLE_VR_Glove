import asyncio
from dataclasses import dataclass
from typing import Any, Optional, Protocol

import customtkinter as ctk

from .base_dialog import BaseDialog, DialogConfig, DialogStyle


@dataclass
class DeviceStatus:
    """Information about connected device"""

    name: str
    rssi: int


class OkCallback(Protocol):
    """Protocol for ok callback"""

    def __call__(self) -> None: ...


class ConnectionStatusDialog(BaseDialog):
    """Dialog to show connection status"""

    def __init__(self, parent: ctk.CTk):
        config = DialogConfig(
            title="",
            width=400,
            height=200,
            style=DialogStyle(
                fg_color="#1F1F1F",
                content_bg="#2B2D30",
                border_color="#777777",
                border_width=1,
                corner_radius=8,
            ),
        )

        self._destroyed = False
        self.countdown_after_id: Optional[str] = None
        self.ok_button: Optional[ctk.CTkButton] = None
        self.status_label: Optional[ctk.CTkLabel] = None
        self.ok_callback: Optional[OkCallback] = None

        super().__init__(parent, config)
        self.title("Connecting")  # Set window title after init

    def _create_title_section(self) -> None:
        """Override to prevent title section creation"""
        pass

    def _create_content(self) -> None:
        """Create dialog content with exact same layout as original"""
        self.status_label = ctk.CTkLabel(
            self.content_frame, text="Connecting...", font=self.app_config.TEXT_FONT
        )
        self.status_label.pack(pady=20)

    def show_connecting(self) -> None:
        """Show connecting state"""
        if not self._destroyed:
            self.status_label.configure(
                text="Connecting...", font=self.app_config.LARGE_FONT
            )

    async def _countdown(self, device_info: DeviceStatus) -> None:
        """Show countdown after connection"""
        if self._destroyed:
            return

        info_text = f"Connected to:\n{device_info.name}\nRSSI: {device_info.rssi} dBm"

        # Show initial connection success
        self.status_label.configure(text=info_text)
        await asyncio.sleep(1)

        # Countdown
        for i in range(3, 0, -1):
            if self._destroyed:
                return
            self.status_label.configure(
                text=f"{info_text}\n\nStarting in {i}", font=self.app_config.LARGE_FONT
            )
            await asyncio.sleep(0.5)

        # Trigger the callback to start application
        if not self._destroyed and self.ok_callback:
            self.ok_callback()

        # Close both dialogs
        self.destroy()  # This will close connection status dialog
        if hasattr(self.parent, "destroy"):  # This will close connection dialog
            self.parent.destroy()

    def show_connected(self, device_info: Any) -> None:
        """Show connected state with device info and start countdown"""
        if not self._destroyed:
            # Calculate connection duration if start time exists
            if hasattr(self.parent, "connect_start_time"):
                duration = (
                    asyncio.get_event_loop().time() - self.parent.connect_start_time
                )
                print(f"[Connection] Connection established in {duration:.2f} seconds")

            status = DeviceStatus(name=device_info.name, rssi=device_info.rssi)
            asyncio.create_task(self._countdown(status))

    def show_failed(self) -> None:
        """Show connection failed state"""
        if not self._destroyed:
            self.status_label.configure(text="Connection failed")

    def set_ok_callback(self, callback: OkCallback) -> None:
        """Set callback for auto-start after countdown"""
        self.ok_callback = callback
