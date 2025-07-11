import subprocess
from typing import Callable, Optional

import customtkinter as ctk

from src.config.app_config import AppConfig
from src.view.view_component.button_component import ButtonComponent

from .base_dialog import BaseDialog, DialogConfig, DialogStyle


class IMUCalibrationDialog(BaseDialog):
    def __init__(self, parent: ctk.CTk, imu_label: str, imu_service):
        config = DialogConfig(
            title="",  # Empty to prevent default header
            width=500,
            height=350,
            style=DialogStyle(
                fg_color="#1F1F1F",
                content_bg="#1F1F1F",
                border_color="#1F1F1F",
                border_width=1,
                corner_radius=8,
            ),
        )

        self._destroyed = False
        self._countdown_running = False
        self._current_count = 10
        self.imu_label = imu_label
        self.imu_service = imu_service
        self.open_tool_button: Optional[ButtonComponent] = None
        self.start_button: Optional[ButtonComponent] = None
        self.stop_button: Optional[ButtonComponent] = None
        self.cancel_button: Optional[ButtonComponent] = None
        self.debug_label: Optional[ctk.CTkLabel] = None
        self.status_label: Optional[ctk.CTkLabel] = None

        super().__init__(parent, config)
        self.title("IMU Calibration")

        # Start debug updates after UI is created
        self._start_debug_updates()

    def _create_title_section(self) -> None:
        """Create custom title section"""
        title_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 20))

        header = ctk.CTkLabel(
            title_frame,
            text=f"{self.imu_label} Calibration",
            font=("Inter Bold", 16),
            text_color="white",
        )
        header.pack(side="left")

    def _create_content(self) -> None:
        """Create main dialog content"""
        # Debug label for CMD status (yellow text)
        self.debug_label = ctk.CTkLabel(
            self.content_frame,
            text="CMD: --",
            font=("Inter", 12),
            text_color="#FFD700",  # Gold color
        )
        self.debug_label.pack(pady=(0, 5))

        # Warning message
        warning = ctk.CTkLabel(
            self.content_frame,
            text="Please place the device stable on flat surface\nbefore starting the calibration process",
            font=("Inter", 14),
            text_color="#FF4B4B",  # Red color
        )
        warning.pack(pady=(0, 20))

        # Description
        description = ctk.CTkLabel(
            self.content_frame,
            text="Calibration gyroscope, accelerometer and magnetometer",
            font=("Inter", 13),
            text_color="white",
        )
        description.pack(pady=(0, 20))

        # Countdown/Status label
        self.status_label = ctk.CTkLabel(
            self.content_frame, text="", font=("Inter Bold", 24), text_color="white"
        )
        self.status_label.pack(pady=(0, 30))

        # Button container
        button_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        button_frame.pack(fill="x", side="bottom", pady=(10, 0))

        # Cancel button
        self.cancel_button = ButtonComponent(
            button_frame,
            "Cancel",
            command=self.destroy,
            fg_color="#232323",
            hover_color="#333333",
        )
        self.cancel_button.pack(side="left")

        # Start button
        self.start_button = ButtonComponent(
            button_frame,
            "START",
            command=self._on_start,
            fg_color="#0094FF",
            hover_color="#0078CC",
        )
        self.start_button.pack(side="right")

        # Stop button
        self.stop_button = ButtonComponent(
            button_frame,
            "STOP",
            command=self._on_stop,
            fg_color="#666666",
            hover_color="#666666",
            state="disabled",
        )
        self.stop_button.pack(side="right", padx=10)

    async def _write_cmd(self, cmd_value: int) -> bool:
        """Write command value to config while preserving other settings"""
        try:
            data = await self.imu_service.read_config()
            if data:
                new_config = bytearray(data)
                new_config[0] = cmd_value
                await self.imu_service.write_config(new_config)
                return True
        except Exception as e:
            print(f"[ERROR] Cannot write command: {e}")
            return False

    def _launch_tool(self) -> None:
        """Launch calibration tool"""
        try:
            # Write appropriate CMD value based on IMU label
            cmd_value = 2 if self.imu_label == "IMU1" else 3
            if hasattr(self, "imu_service"):
                self.imu_service.loop.create_task(self._write_cmd(cmd_value))
            # Launch MotionCal
            subprocess.Popen(["MotionCal.exe"], shell=True)
        except Exception as e:
            print(f"[ERROR] Cannot launch MotionCal.exe: {e}")

    def _update_countdown(self) -> None:
        """Update countdown timer"""
        if not self._countdown_running:
            return

        if self._current_count >= 0:
            self.status_label.configure(text=str(self._current_count))
            self._current_count -= 1
            self.after(1000, self._update_countdown)
        else:
            self.status_label.pack_forget()  # Hide countdown label
            self.open_tool_button = ButtonComponent(
                self.status_label.master,
                "OPEN TOOL",
                command=self._launch_tool,
                fg_color="transparent",
                hover_color="#333333",
                text_color="#00FF00",  # Bright green
                font=("Inter Bold", 18),
            )
            self.open_tool_button.pack()

            # Enable STOP button
            self.stop_button.configure(
                state="normal", fg_color="#FF4B4B", hover_color="#CC0000"
            )

    def _on_start(self) -> None:
        """Handle start button click"""
        self.start_button.configure(state="disabled")
        self.stop_button.configure(
            state="disabled", fg_color="#666666", hover_color="#666666"
        )
        self._countdown_running = True
        self._current_count = 10
        self._update_countdown()

    def _on_stop(self) -> None:
        """Handle stop button click"""
        self._countdown_running = False
        self.stop_button.configure(
            state="disabled", fg_color="#666666", hover_color="#666666"
        )
        self.start_button.configure(state="normal")
        if self.status_label.cget("text") != "OPEN TOOL":
            self.status_label.configure(text="")

        # Set CMD to RUN (1) before closing
        if hasattr(self, "imu_service"):
            self.imu_service.loop.create_task(self._write_cmd(1))
        self.destroy()

    def set_cancel_callback(self, callback: Callable[[], None]) -> None:
        """Set callback for cancel button"""
        self.cancel_button.configure(command=callback)

    def set_start_callback(self, callback: Callable[[], None]) -> None:
        """Set callback for start"""
        self._start_callback = callback

    async def _update_debug_label(self) -> None:
        """Read and update CMD value in debug label"""
        try:
            data = await self.imu_service.read_config()
            if data:
                cmd_value = data[0]
                cmd_text = {0: "IDLE", 1: "RUN", 2: "IMU1 CALIB", 3: "IMU2 CALIB"}.get(
                    cmd_value, f"Unknown ({cmd_value})"
                )
                self.debug_label.configure(text=f"CMD: {cmd_text}")
        except Exception as e:
            self.debug_label.configure(text=f"CMD: Error ({str(e)})")

    def _start_debug_updates(self) -> None:
        """Start periodic debug label updates"""
        if hasattr(self, "imu_service"):
            self.imu_service.loop.create_task(self._update_debug_label())
            if not self._destroyed:
                self.after(3000, self._start_debug_updates)  # Update every 3 seconds

    def destroy(self) -> None:
        """Clean up resources"""
        self._countdown_running = False
        self._destroyed = True
        super().destroy()
