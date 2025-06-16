from dataclasses import dataclass
from typing import Any, Dict, Optional

import customtkinter as ctk

from src.config.app_config import AppConfig
from src.view.view_component import ButtonComponent, CoordinateEntry
from src.view.view_dialog import OtherConfigDialog


@dataclass
class SensorConfig:
    """Configuration for sensor layout"""

    label_text: str
    row: int
    entry_count: int
    entry_width: int = 120
    pady: tuple = (0, 0)


class SensorView(ctk.CTkFrame):
    """View component for displaying and configuring sensors"""

    FLEX_SENSOR_CONFIG = SensorConfig(
        label_text="Flex Sensor (kOhm):", row=0, entry_count=5
    )

    FORCE_SENSOR_CONFIG = SensorConfig(
        label_text="Force Sensor (kOhm):", row=1, entry_count=1, pady=(20, 20)
    )

    def __init__(self, parent: ctk.CTk):
        self.config = AppConfig()
        self._init_variables()

        super().__init__(
            parent,
            fg_color=self.config.PANEL_COLOR,
            border_color=self.config.BORDER_COLOR,
            border_width=self.config.BORDER_WIDTH,
            corner_radius=self.config.CORNER_RADIUS,
        )

        self._init_ui()

    def _init_variables(self) -> None:
        """Initialize instance variables"""
        self.service: Optional[Any] = None
        self.loop: Optional[Any] = None
        self.flex_entries: Dict[int, CoordinateEntry] = {}
        self.force_entry: Optional[CoordinateEntry] = None

    def _init_ui(self) -> None:
        """Initialize all UI components"""
        self._setup_layout()
        self._create_header()
        self._create_main_content()

    def _setup_layout(self) -> None:
        """Configure initial grid layout"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

    def _create_header(self) -> None:
        """Create header label"""
        header_label = ctk.CTkLabel(
            self,
            text="SENSOR",
            font=self.config.HEADER_FONT,
            text_color=self.config.TEXT_COLOR,
        )
        header_label.grid(row=0, column=0, sticky="nw", padx=12, pady=(12, 0))

    def _create_main_content(self) -> None:
        """Create main content including sensors and button"""
        main_frame = self._create_main_frame()
        self._create_sensor_section(main_frame, self.FLEX_SENSOR_CONFIG)
        self._create_sensor_section(main_frame, self.FORCE_SENSOR_CONFIG)
        self._create_button_section()

    def _create_main_frame(self) -> ctk.CTkFrame:
        """Create and configure main container frame"""
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.grid(row=1, column=0, sticky="nsew", padx=12, pady=12)
        main_frame.grid_columnconfigure((1, 2, 3, 4, 5), weight=0)
        return main_frame

    def _create_sensor_section(
        self, parent: ctk.CTkFrame, config: SensorConfig
    ) -> None:
        """Create a sensor section with label and entries"""
        self._create_sensor_label(parent, config)
        self._create_sensor_entries(parent, config)

    def _create_sensor_label(self, parent: ctk.CTkFrame, config: SensorConfig) -> None:
        """Create label for sensor section"""
        label = ctk.CTkLabel(
            parent,
            text=config.label_text,
            font=self.config.LABEL_FONT,
            text_color=self.config.TEXT_COLOR,
        )
        label.grid(row=config.row, column=0, sticky="w")

    def _create_sensor_entries(
        self, parent: ctk.CTkFrame, config: SensorConfig
    ) -> None:
        """Create entries for sensor section"""
        if config.entry_count == 1:
            self._create_force_entry(parent, config)
        else:
            self._create_flex_entries(parent, config)

    def _create_flex_entries(self, parent: ctk.CTkFrame, config: SensorConfig) -> None:
        """Create multiple entries for flex sensors"""
        for i in range(config.entry_count):
            sensor_num = i + 1
            entry = CoordinateEntry(
                parent, str(sensor_num), entry_width=config.entry_width
            )
            entry.grid(row=config.row, column=i + 1, sticky="ew", padx=5)
            self.flex_entries[sensor_num] = entry

    def _create_force_entry(self, parent: ctk.CTkFrame, config: SensorConfig) -> None:
        """Create single entry for force sensor"""
        self.force_entry = CoordinateEntry(parent, "", entry_width=config.entry_width)
        self.force_entry.grid(
            row=config.row, column=1, columnspan=2, sticky="ew", pady=config.pady
        )

    def _create_button_section(self) -> None:
        """Create button container and configure button"""
        container = self._create_button_container()
        self.button_config = ButtonComponent(
            container, "Configure", command=self._handle_config_click
        )
        self.button_config.grid(row=2, column=0, sticky="es", pady=(0, 0), padx=(0, 20))

    def _create_button_container(self) -> ctk.CTkFrame:
        """Create container for buttons"""
        container = ctk.CTkFrame(
            self,
            fg_color="transparent",
            width=0,
            height=28,
        )
        container.grid(row=2, column=0, sticky="es", padx=10, pady=(0, 20))
        container.grid_columnconfigure((0, 1, 2), weight=0)
        return container

    async def _on_config(self) -> None:
        """Handle configuration button click"""
        data = await self.service.read_config()
        dialog = OtherConfigDialog(self)

        if data:
            interval = int.from_bytes(data[11:13], "little")
            dialog.rate_entry.set_value(interval, keep_editable=True)

        dialog.set_cancel_callback(dialog.destroy)
        dialog.set_apply_callback(
            lambda: self.loop.create_task(self._handle_config_apply(dialog))
        )

    async def _handle_config_apply(self, dialog: OtherConfigDialog) -> None:
        """Handle configuration apply button click"""
        data = await self.service.read_config()
        if data:
            new_config = self._create_updated_config(data, dialog.get_rate_value())
            await self.service.write_config(new_config)
        dialog.destroy()

    def _create_updated_config(self, current_config: bytes, rate: int) -> bytearray:
        """Create updated configuration with new rate"""
        new_config = bytearray(current_config)
        new_config[11:13] = rate.to_bytes(2, "little")
        return new_config

    def _handle_config_click(self) -> None:
        """Handle config button click"""
        if self.loop:
            self.loop.create_task(self._on_config())

    # Public interface methods
    def update_flex_sensor(self, sensor_id: int, value: float) -> None:
        """Update flex sensor value"""
        if sensor_id in self.flex_entries:
            self.flex_entries[sensor_id].set_value(value)

    def update_force_sensor(self, value: float) -> None:
        """Update force sensor value"""
        self.force_entry.set_value(value)

    def set_button_states(self, enabled: bool) -> None:
        """Enable/disable buttons"""
        state = "normal" if enabled else "disabled"
        self.button_config.configure(state=state)

    def clear_values(self) -> None:
        """Clear all sensor values"""
        for sensor_id in self.flex_entries:
            self.flex_entries[sensor_id].set_value(0)
        self.force_entry.set_value(0)

    def destroy(self) -> None:
        """Clean up resources before destroying widget"""
        super().destroy()
