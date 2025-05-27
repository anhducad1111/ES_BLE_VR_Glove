import customtkinter as ctk
from src.config.app_config import AppConfig
from src.view.button_component import ButtonComponent

class IMUCalibrationDialog(ctk.CTkToplevel):
    def __init__(self, parent, imu_label: str):
        self.config = AppConfig()  # Get singleton instance
        super().__init__(parent)
        self._destroyed = False
        self._countdown_running = False
        self._current_count = 10
        self._setup_window(parent)
        self._create_main_layout(imu_label)

    def _setup_window(self, parent):
        self.overrideredirect(False)  
        self.configure(fg_color="#1F1F1F")
        self.geometry("400x300")  
        self._center_window(parent)
        self._make_modal(parent)

    def _center_window(self, parent):
        """Center the dialog on the main window"""
        # Get the root window (main window)
        root = parent.winfo_toplevel()
        
        # Calculate screen width and height
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        # Get the root window position and dimensions
        root_x = root.winfo_x()
        root_y = root.winfo_y()
        root_width = root.winfo_width()
        root_height = root.winfo_height()
        
        # Calculate center position within the root window
        x = root_x + (root_width - 400) // 2  # 400 is dialog width
        y = root_y + (root_height - 300) // 2  # 300 is dialog height
        
        # Ensure the dialog stays within screen bounds
        x = max(0, min(x, screen_width - 400))
        y = max(0, min(y, screen_height - 300))
        
        self.geometry(f"+{x}+{y}")

    def _make_modal(self, parent):
        self.transient(parent)
        self.grab_set()

    def _create_main_layout(self, imu_label):
        main_frame = ctk.CTkFrame(
            self,
            fg_color="#1F1F1F",
            border_color="#1F1F1F",  
            border_width=1,
            corner_radius=8
        )
        main_frame.pack(fill="both", expand=True, padx=2, pady=2)

        # Content frame
        content = ctk.CTkFrame(main_frame, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=20)

        # Title section
        title_frame = ctk.CTkFrame(content, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 20))
        header = ctk.CTkLabel(
            title_frame,
            text=f"{imu_label} Calibration",
            font=("Inter Bold", 16),
            text_color="white"
        )
        header.pack(side="left")

        # Warning message (red, centered, larger font)
        warning = ctk.CTkLabel(
            content,
            text="Please place the device stable on flat surface\nbefore starting the calibration process",
            font=("Inter", 14),
            text_color="#FF4B4B"  # Red color
        )
        warning.pack(pady=(0, 20))

        # Description (white, centered)
        description = ctk.CTkLabel(
            content,
            text="Calibration gyroscope, accelerometer and magnetometer",
            font=("Inter", 13),
            text_color="white"
        )
        description.pack(pady=(0, 20))

        # Countdown/Status label
        self.status_label = ctk.CTkLabel(
            content,
            text="",  # Initially empty
            font=("Inter Bold", 24),  # Larger font for countdown
            text_color="white"
        )
        self.status_label.pack(pady=(0, 30))

        # Button container at bottom
        button_frame = ctk.CTkFrame(content, fg_color="transparent")
        button_frame.pack(fill="x", side="bottom", pady=(10, 0))

        # Cancel button (left)
        self.cancel_button = ButtonComponent(
            button_frame,
            "Cancel",
            command=self.destroy,
            fg_color="#232323",
            hover_color="#333333"
        )
        self.cancel_button.pack(side="left")

        # Start button (right)
        self.start_button = ButtonComponent(
            button_frame,
            "START",
            command=self._on_start,
            fg_color="#0094FF",
            hover_color="#0078CC"
        )
        self.start_button.pack(side="right")

        # Stop button (center, disabled)
        self.stop_button = ButtonComponent(
            button_frame,
            "STOP",
            command=self._on_stop,
            fg_color="#666666",
            hover_color="#666666",
            state="disabled"
        )
        self.stop_button.pack(side="right", padx=10)

    def _update_countdown(self):
        """Update the countdown display"""
        if not self._countdown_running:
            return
            
        if self._current_count >= 0:
            self.status_label.configure(text=str(self._current_count))
            self._current_count -= 1
            self.after(1000, self._update_countdown)
        else:
            self.status_label.configure(text="OPEN TOOL")
            self._on_stop()

    def _on_start(self):
        """Handle start button click"""
        self.start_button.configure(state="disabled")
        self.stop_button.configure(
            state="normal",
            fg_color="#666666",
            hover_color="#777777"
        )
        self._countdown_running = True
        self._current_count = 10
        self._update_countdown()

    def _on_stop(self):
        """Handle stop button click"""
        self._countdown_running = False
        self.stop_button.configure(
            state="disabled",
            fg_color="#666666",
            hover_color="#666666"
        )
        self.start_button.configure(state="normal")
        if self.status_label.cget("text") != "OPEN TOOL":
            self.status_label.configure(text="")

    def set_cancel_callback(self, callback):
        self.cancel_button.configure(command=callback)

    def set_start_callback(self, callback):
        self._start_callback = callback  # Store for use after countdown

    def destroy(self):
        self._countdown_running = False
        self._destroyed = True
        super().destroy()
