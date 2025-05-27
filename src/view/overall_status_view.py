import customtkinter as ctk
from src.config.app_config import AppConfig

class OverallStatusView(ctk.CTkFrame):
    def __init__(self, parent):
        self.config = AppConfig()  # Get singleton instance
        super().__init__(
            parent,
            fg_color=self.config.PANEL_COLOR,
            border_color=self.config.BORDER_COLOR,
            border_width=self.config.BORDER_WIDTH,
            corner_radius=self.config.CORNER_RADIUS
        )
        # Configure base grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Create UI Components
        self.create_header()
        self.create_status_container()
        self.update_status(False, True, False)

    def create_header(self):
        """Create the header section"""
        header_label = ctk.CTkLabel(
            self,
            text="OVERALL STATUS",
            font=self.config.HEADER_FONT,
            text_color=self.config.TEXT_COLOR
        )
        header_label.grid(row=0, column=0, sticky="nw", padx=12, pady=(12, 0))

    def create_status_container(self):
        """Create the status indicator container"""
        # Create container frame
        status_container = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )
        status_container.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        
        # Configure grid columns
        status_container.grid_columnconfigure((1, 3, 5), weight=1)  # Status columns
        status_container.grid_columnconfigure((0, 2, 4), weight=0)  # Label columns

        # Store status labels for updates
        self.status_labels = {}

        # Create status indicators
        status_configs = [
            ("Fuelgause:", "fuelgause", 0),
            ("IMU1:", "imu1", 2),
            ("IMU2:", "imu2", 4)
        ]

        for label_text, key, start_col in status_configs:
            self.create_status_pair(
                status_container,
                label_text,
                key,
                start_col
            )

    def create_status_pair(self, parent, label_text, key, start_col):
        """Create a status indicator pair (label + status)"""
        # Create label
        label = ctk.CTkLabel(
            parent,
            text=label_text,
            font=self.config.TEXT_FONT,
            text_color=self.config.TEXT_COLOR,
        )
        label.grid(
            row=0, 
            column=start_col, 
            sticky="w", 
            padx=(12 if start_col == 0 else 20, 10), 
            pady=12
        )
        
        # Create status
        status = ctk.CTkLabel(
            parent,
            text="NONE",
            font=self.config.TEXT_FONT,
            text_color="red",
        )
        status.grid(
            row=0, 
            column=start_col + 1, 
            sticky="w", 
            padx=10, 
            pady=12
        )
        
        # Store reference
        self.status_labels[key] = status

    def update_status(self, fuelgause: bool, imu1: bool, imu2: bool):
        """Update all status indicators at once
        
        Args:
            fuelgause: Status of fuelgause
            imu1: Status of IMU1
            imu2: Status of IMU2
        """
        status_values = {
            "fuelgause": fuelgause,
            "imu1": imu1,
            "imu2": imu2
        }
        
        for key, is_running in status_values.items():
            self.status_labels[key].configure(
                text="RUNNING" if is_running else "NONE",
                text_color=self.config.BUTTON_COLOR if is_running else "red"
            )
