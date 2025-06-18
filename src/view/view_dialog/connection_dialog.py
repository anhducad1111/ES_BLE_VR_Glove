import asyncio
from typing import Any, Dict, Optional, TypedDict

import customtkinter as ctk
from bleak import BleakScanner

from src.config.app_config import AppConfig
from src.view.view_component.button_component import ButtonComponent

from .base_dialog import BaseDialog, DialogConfig, DialogStyle


class DeviceInfo(TypedDict):
    """Type definition for device information"""

    name: str
    address: str
    rssi: int


class DeviceListHeader(ctk.CTkFrame):
    def __init__(self, parent: ctk.CTkBaseClass):
        super().__init__(parent, fg_color="transparent")
        self.config = AppConfig()  # Get singleton instance
        self._setup_layout()
        self._create_headers()

    def _setup_layout(self) -> None:
        self.pack(fill="x")
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, minsize=200)
        self.grid_columnconfigure(2, minsize=120)

    def _create_headers(self) -> None:
        headers = ["NAME", "ADDRESS", "RSSI"]
        for i, text in enumerate(headers):
            label = ctk.CTkLabel(
                self, text=text, font=("Inter Bold", 12), text_color="white"
            )
            label.grid(row=0, column=i, sticky="w", padx=15, pady=10)


class ScrollableDeviceFrame(ctk.CTkScrollableFrame):
    def __init__(
        self,
        master: ctk.CTkBaseClass,
        command: Optional[callable] = None,
        **kwargs: Any,
    ):
        super().__init__(master, **kwargs)
        self.config = AppConfig()
        self.grid_columnconfigure(0, weight=1)
        self.command = command
        self.selected_row: Optional[int] = None
        self.rows: list[ctk.CTkFrame] = []
        self.devices: Dict[str, DeviceInfo] = {}
        self._destroyed = False

    def add_device(self, name: str, address: str, rssi: int) -> None:
        if self._destroyed:
            return

        if address in self.devices:
            return

        row = len(self.rows)
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=row, column=0, sticky="ew", padx=5, pady=2)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, minsize=200)
        frame.grid_columnconfigure(2, minsize=100)

        device_info: DeviceInfo = {"name": name, "address": address, "rssi": rssi}

        for col, text in enumerate([name, address, str(rssi)]):
            label = ctk.CTkLabel(
                frame, text=text, font=("Inter Medium", 12), text_color="white"
            )
            label.grid(row=0, column=col, sticky="w", padx=15, pady=5)

        self._bind_row_events(frame, row, device_info)
        self.rows.append(frame)
        self.devices[address] = device_info

    def _bind_row_events(
        self, frame: ctk.CTkFrame, row: int, device_info: DeviceInfo
    ) -> None:
        frame.bind("<Button-1>", lambda e: self._on_select(row, device_info))
        for widget in frame.winfo_children():
            widget.bind("<Button-1>", lambda e: self._on_select(row, device_info))

    def _on_select(self, row: int, device_info: DeviceInfo) -> None:
        if self._destroyed:
            return

        if self.selected_row is not None:
            self.rows[self.selected_row].configure(fg_color="transparent")

        self.selected_row = row
        self.rows[row].configure(fg_color=("#3D3F41", "#3D3F41"))

        if self.command:
            self.command(device_info)

    def clear(self) -> None:
        if self._destroyed:
            return

        for row in self.rows:
            row.destroy()
        self.rows.clear()
        self.devices.clear()
        self.selected_row = None

    def destroy(self) -> None:
        self._destroyed = True
        super().destroy()


class ConnectionDialog(BaseDialog):
    def __init__(
        self,
        parent: ctk.CTk,
        loop: asyncio.AbstractEventLoop,
        ble_scanner: BleakScanner,
        callback: Optional[callable] = None,
    ):
        config = DialogConfig(
            title="Connection",
            width=569,
            height=443,
            style=DialogStyle(
                fg_color="#1F1F1F",
                content_bg="#2B2D30",
                border_color="#777777",
                border_width=1,
                corner_radius=8,
            ),
        )

        self.loop = loop
        self.ble_scanner = ble_scanner
        self.callback = callback
        self.selected_device: Optional[DeviceInfo] = None
        self.device_list: Optional[ScrollableDeviceFrame] = None
        self.scan_btn: Optional[ButtonComponent] = None
        self.connect_btn: Optional[ButtonComponent] = None
        self.info_label: Optional[ctk.CTkLabel] = None

        super().__init__(parent, config)

        # Start scanning after UI is fully created
        self.after(100, lambda: self.loop.create_task(self._start_scanning()))

    def _create_title_section(self) -> None:
        """Override base dialog's title section to add scan button"""
        title_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 15))
        title_frame.grid_columnconfigure(1, weight=1)

        header = ctk.CTkLabel(
            title_frame,
            text=self.config.title,
            font=self.config.style.title_font,
            text_color=self.config.style.text_color,
        )
        header.grid(row=0, column=0, sticky="w")

        self.scan_btn = ButtonComponent(
            title_frame, "Scan Again", command=self._on_scan_again, width=100, height=32
        )
        self.scan_btn.grid(row=0, column=2, sticky="e")

    def _create_content(self) -> None:
        """Create main dialog content"""
        container = ctk.CTkFrame(self.content_frame, fg_color="transparent", height=294)
        container.pack(fill="x", pady=(0, 15))
        container.pack_propagate(False)

        list_frame = ctk.CTkFrame(
            container,
            fg_color=self.config.style.content_bg,
            border_color=self.config.style.border_color,
            border_width=self.config.style.border_width,
            corner_radius=self.config.style.corner_radius,
        )
        list_frame.pack(fill="both", expand=True, padx=2, pady=2)

        content = ctk.CTkFrame(list_frame, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=5, pady=5)

        DeviceListHeader(content)

        self.device_list = ScrollableDeviceFrame(
            content,
            command=self._show_device_info,
            fg_color="transparent",
            corner_radius=0,
            width=516,
            height=215,
        )
        self.device_list.pack(fill="both", expand=True)

        # Create bottom section
        bottom_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        bottom_frame.pack(fill="x")
        bottom_frame.grid_columnconfigure(0, weight=1)

        # Info section
        self.info_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        self.info_frame.grid(row=0, column=0, sticky="w")

        self.info_label = ctk.CTkLabel(
            self.info_frame, text="", font=("Inter Medium", 12), text_color="white"
        )
        self.info_label.pack(anchor="w")

        # Button section
        button_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        button_frame.grid(row=0, column=1, sticky="e")

        self.cancel_btn = ButtonComponent(
            button_frame,
            "Cancel",
            command=self.destroy,
            fg_color="transparent",
            hover_color="gray20",
        )
        self.cancel_btn.pack(side="left", padx=(0, 20))

        self.connect_btn = ButtonComponent(
            button_frame,
            "Connect",
            command=self._on_connect,
            state="disabled",
            fg_color="#0078D4",
            hover_color="#006CBE",
        )
        self.original_connect_text = "Connect"
        self.connect_btn.pack(side="left")

    async def _start_scanning(self) -> None:
        if self._destroyed:
            return

        self.device_list.clear()
        self.scan_btn.configure(state="disabled", text="Scanning...")
        self.info_label.configure(text="Scanning for devices...")

        async def detection_callback(device: Any, advertisement_data: Any) -> None:
            if not self._destroyed and device.name:
                self.after(
                    0,
                    lambda: self.device_list.add_device(
                        device.name, device.address, advertisement_data.rssi
                    ),
                )

        try:
            async with self.ble_scanner(detection_callback) as scanner:
                await asyncio.sleep(5)  # Scan for 5 seconds

            if len(self.device_list.rows) == 0:
                self.info_label.configure(text="No devices found")
            else:
                self.info_label.configure(text="Select a device to connect")

            self.scan_btn.configure(state="normal", text="Scan Again")

        except Exception as e:
            error_msg = str(e)
            if "WinError -2147020577" in error_msg:
                error_msg = "Please turn on Bluetooth"

            if not self._destroyed:
                self.info_label.configure(text=error_msg)
                self.scan_btn.configure(state="normal", text="Scan Again")

    def _show_device_info(self, device_info: DeviceInfo) -> None:
        if self._destroyed:
            return

        info_text = (
            f"{device_info['name']}, {device_info['address']}, {device_info['rssi']}"
        )
        self.info_label.configure(text=info_text)
        self.connect_btn.configure(state="normal")
        self.selected_device = device_info

    def _on_scan_again(self) -> None:
        if self._destroyed:
            return

        self.info_label.configure(text="")
        self.connect_btn.configure(state="disabled")
        self.selected_device = None

        self.loop.create_task(self._start_scanning())

    def _on_connect(self) -> None:
        if self._destroyed or not self.selected_device:
            return

        # Record connection start time
        # self.connect_start_time = asyncio.get_event_loop().time()

        self.connect_btn.configure(state="disabled", text="Connecting...")

        from .connection_status_dialog import ConnectionStatusDialog

        self.status_dialog = ConnectionStatusDialog(self)
        self.status_dialog.bind("<Destroy>", self._on_status_dialog_closed)
        self.status_dialog.show_connecting()

        if self.callback:
            self.callback(self.selected_device)

    def _on_status_dialog_closed(self, event: Any) -> None:
        if self._destroyed:
            return

        # Reset button state unless connection was successful
        if not hasattr(self, "connection_success") or not self.connection_success:
            self.connect_btn.configure(
                state="normal", text=self.original_connect_text
            )
            self.status_dialog.grab_release()
            self.grab_set()
        elif self.connection_success:
            self.destroy()
