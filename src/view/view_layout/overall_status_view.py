from dataclasses import dataclass
from typing import Dict

import customtkinter as ctk

from src.config.app_config import AppConfig
from src.util.log_manager import LogManager
from src.view.view_component import ButtonComponent


@dataclass
class StatusConfig:
    label_text: str
    key: str
    start_col: int


class OverallStatusView(ctk.CTkFrame):
    """A view component that displays overall system status and logging controls"""

    STATUS_CONFIGS = [
        StatusConfig("Fuelgause:", "fuelgause", 0),
        StatusConfig("IMU1:", "imu1", 2),
        StatusConfig("IMU2:", "imu2", 4),
    ]

    def __init__(self, parent: ctk.CTk):
        self.config = AppConfig()
        self.log_manager = LogManager.instance()
        self.status_labels: Dict[str, ctk.CTkLabel] = {}

        super().__init__(
            parent,
            fg_color=self.config.PANEL_COLOR,
            border_color=self.config.BORDER_COLOR,
            border_width=self.config.BORDER_WIDTH,
            corner_radius=self.config.CORNER_RADIUS,
        )

        self._init_variables()
        self._setup_layout()
        self._init_components()

    def _init_variables(self) -> None:
        """Initialize instance variables"""
        self.selected_folder = None
        self.log_button = None
        self.presenter = None

    def _setup_layout(self) -> None:
        """Configure the basic grid layout"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

    def _init_components(self) -> None:
        """Initialize all UI components"""
        self._create_header()
        self._create_status_container()
        self.update_status(False, False, False)

    def _create_header(self) -> None:
        """Create the header section"""
        header_label = ctk.CTkLabel(
            self,
            text="OVERALL STATUS",
            font=self.config.HEADER_FONT,
            text_color=self.config.TEXT_COLOR,
        )
        header_label.grid(row=0, column=0, sticky="nw", padx=12, pady=(12, 0))

    def _create_status_container(self) -> None:
        """Create and configure the status container"""
        container = self._create_status_frame()
        self._configure_status_grid(container)
        self._create_status_indicators(container)

    def _create_status_frame(self) -> ctk.CTkFrame:
        """Create the status container frame"""
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        return container

    def _configure_status_grid(self, container: ctk.CTkFrame) -> None:
        """Configure the grid layout for status indicators"""
        for i in range(7):
            weight = 1 if i % 2 == 1 else 0
            container.grid_columnconfigure(i, weight=weight)

    def _create_status_indicators(self, container: ctk.CTkFrame) -> None:
        """Create all status indicator pairs"""
        for config in self.STATUS_CONFIGS:
            self._create_status_pair(container, config)

    def _create_status_pair(self, parent: ctk.CTkFrame, config: StatusConfig) -> None:
        """Create a label and status indicator pair"""
        label = self._create_status_label(parent, config)
        status = self._create_status_indicator(parent, config)
        self.status_labels[config.key] = status

    def _create_status_label(
        self, parent: ctk.CTkFrame, config: StatusConfig
    ) -> ctk.CTkLabel:
        """Create a status label"""
        label = ctk.CTkLabel(
            parent,
            text=config.label_text,
            font=self.config.TEXT_FONT,
            text_color=self.config.TEXT_COLOR,
        )
        label.grid(
            row=0,
            column=config.start_col,
            sticky="w",
            padx=(12 if config.start_col == 0 else 20, 10),
            pady=12,
        )
        return label

    def _create_status_indicator(
        self, parent: ctk.CTkFrame, config: StatusConfig
    ) -> ctk.CTkLabel:
        """Create a status indicator"""
        status = ctk.CTkLabel(
            parent,
            text="NONE",
            font=self.config.TEXT_FONT,
            text_color="red",
        )
        status.grid(row=0, column=config.start_col + 1, sticky="w", padx=10, pady=12)
        return status

    def update_status(self, fuelgause: bool, imu1: bool, imu2: bool) -> None:
        """Update all status indicators"""
        status_values = {"fuelgause": fuelgause, "imu1": imu1, "imu2": imu2}

        for key, is_running in status_values.items():
            self._update_status_indicator(key, is_running)

    def _update_status_indicator(self, key: str, is_running: bool) -> None:
        """Update a single status indicator"""
        self.status_labels[key].configure(
            text="RUNNING" if is_running else "NONE",
            text_color=self.config.BUTTON_COLOR if is_running else "red",
        )

    # Public interface methods
    def clear_values(self) -> None:
        """Reset all status indicators"""
        self.update_status(False, False, False)
