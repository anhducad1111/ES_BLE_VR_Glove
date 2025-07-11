import customtkinter as ctk

from src.config.app_config import AppConfig
from src.view.view_component import ButtonComponent, CoordinateEntry, GraphView
from src.view.view_dialog import OtherConfigDialog


class GamepadView(ctk.CTkFrame):
    def __init__(self, parent):
        self.config = AppConfig()  # Get singleton instance
        self.service = None  # Will be set by presenter
        self.loop = None  # Will be set by presenter
        super().__init__(
            parent,
            fg_color=self.config.PANEL_COLOR,
            border_color=self.config.BORDER_COLOR,
            border_width=self.config.BORDER_WIDTH,
            corner_radius=self.config.CORNER_RADIUS,
        )
        self.grid_columnconfigure(0, weight=1)
        # self.grid_rowconfigure(1, weight=2)

        # Header wrapped in orange frame
        header_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )
        header_frame.grid(row=0, column=0, sticky="nw", padx=12)

        header_label = ctk.CTkLabel(
            header_frame,
            text="GAMEPAD",
            font=self.config.HEADER_FONT,
            text_color=self.config.TEXT_COLOR,
            fg_color="transparent",
        )
        header_label.pack(padx=5, pady=5)

        # Joystick label wrapped in yellow frame
        joystick_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )
        joystick_frame.grid(row=1, column=0, sticky="nw", padx=30)

        joystick_label = ctk.CTkLabel(
            joystick_frame,
            text="JOYSTICK",
            font=self.config.HEADER_FONT,
            text_color=self.config.TEXT_COLOR,
            fg_color="transparent",
        )
        joystick_label.pack(padx=5, pady=5)

        self.graph_view = GraphView(self)
        self.graph_view.grid(row=2, column=0, sticky="nesw", padx=30, pady=12)

        # Create xy container
        self.create_xy_container()
        self.update_xy_values(0000, 0000)
        self.update_joystick_button_state(False)

        # Separator
        separator = ctk.CTkFrame(
            self, height=2, width=0, fg_color=self.config.BORDER_COLOR
        )
        separator.grid(row=4, column=0, sticky="ew", padx=30, pady=(5, 20))

        # Button label
        button_label = ctk.CTkLabel(
            self,
            text="BUTTONS",
            font=self.config.HEADER_FONT,
            text_color=self.config.TEXT_COLOR,
            fg_color="transparent",
        )
        button_label.grid(row=5, column=0, sticky="nw", padx=30)

        # Button container
        button_container = ctk.CTkFrame(
            self,
            fg_color="transparent",
            width=0,
            height=28,
        )
        button_container.grid(row=6, column=0, sticky="ew", padx=30, pady=12)
        button_container.grid_columnconfigure((0, 2, 4, 6), weight=0)
        button_container.grid_columnconfigure((1, 3, 5, 7), weight=1)

        # Replace the button creation code with this:
        button_states = [False, False, False, False]  # Example states: TFTF
        self.button_frames = []  # Store frame references for later state updates

        for i, (name, state) in enumerate(zip(["B1", "B2", "B3", "B4"], button_states)):
            frame = self.create_button_frame(
                button_container,
                name,
                i * 2,  # Multiply by 2 because we use 2 columns per button
                state,
            )
            self.button_frames.append(frame)

        # The last button frame needs different padding
        self.button_frames[-1].grid(padx=0)  # Remove right padding for last button

        self.button_config = ButtonComponent(
            button_container, "Configure", command=self._handle_config_click
        )
        self.button_config.grid(
            row=1, column=0, columnspan=8, sticky="es", padx=(0, 5), pady=20
        )

    def _handle_config_click(self):
        """Handle config button click by creating coroutine in event loop"""
        if self.loop:
            self.loop.create_task(self._on_config())

    async def _on_config(self):
        """Handle configuration button click"""
        # Read current config
        data = await self.service.read_config()
        dialog = OtherConfigDialog(self)

        if data:
            # Get sensor update interval from bytes 11-12 (little endian)
            interval = int.from_bytes(data[11:13], "little")
            dialog.rate_entry.set_value(interval, keep_editable=True)

        dialog.set_cancel_callback(dialog.destroy)
        dialog.set_apply_callback(
            lambda: self.loop.create_task(self._handle_config_apply(dialog))
        )

    async def _handle_config_apply(self, dialog):
        """Handle configuration apply button click"""
        rate = dialog.get_rate_value()

        # Read current config to preserve other bytes
        data = await self.service.read_config()
        if data:
            # Create new 15-byte array with current config
            new_config = bytearray(data)
            # Update bytes 11-12 with new rate (little endian)
            new_config[11:13] = rate.to_bytes(2, "little")
            # Write updated config
            await self.service.write_config(new_config)

        dialog.destroy()

    def set_button_states(self, enabled):
        state = "normal" if enabled else "disabled"
        self.button_config.configure(state=state)

    def create_button_frame(
        self, container, button_name, column_start, is_active=False
    ):
        label = ctk.CTkLabel(
            container,
            text=button_name,
            font=self.config.LABEL_FONT,
            text_color=self.config.TEXT_COLOR,
            fg_color="transparent",
        )
        label.grid(row=0, column=column_start, sticky="nw", padx=(0, 10))

        frame = ctk.CTkFrame(
            container,
            fg_color=self.config.BUTTON_COLOR if is_active else self.config.FRAME_BG,
            width=0,
            height=28,
            border_color=self.config.BORDER_COLOR,
            border_width=self.config.BORDER_WIDTH,
            corner_radius=self.config.CORNER_RADIUS,
        )
        frame.grid(row=0, column=column_start + 1, sticky="ew", padx=(0, 5))
        return frame

    def update_button_state(self, button_index, is_active):
        if 0 <= button_index < len(self.button_frames):
            self.button_frames[button_index].configure(
                fg_color=self.config.BUTTON_COLOR if is_active else self.config.FRAME_BG
            )

    def create_xy_container(self):
        """Create the XY coordinate display container"""
        xy_frame = ctk.CTkFrame(
            self,
            fg_color=self.config.PANEL_COLOR,
            height=28,
            corner_radius=self.config.CORNER_RADIUS,
        )
        xy_frame.grid(row=3, column=0, sticky="w", padx=30, pady=12)

        # Create X and Y coordinate entries
        self.x_entry = CoordinateEntry(xy_frame, "X")
        self.y_entry = CoordinateEntry(xy_frame, "Y")

        self.x_entry.grid(row=0, column=0, padx=5, pady=5)
        self.y_entry.grid(row=0, column=1, padx=5, pady=5)

        self.joystick_button = ButtonComponent(
            xy_frame,
            "JS Button",
            height=28,
        )
        self.joystick_button.grid(row=0, column=2, padx=5, pady=5)

    def update_xy_values(self, x: float, y: float):
        """Update the X and Y coordinate values and graph position

        Args:
            x: X coordinate value
            y: Y coordinate value
        """
        self.x_entry.set_value(x)
        self.y_entry.set_value(y)

        # Update graph point position
        self.graph_view.update_xy(x, y)

    def update_joystick_button_state(self, is_active: bool):
        """Update joystick button visual state

        Args:
            is_active: True if button is pressed, False otherwise
        """
        self.joystick_button.configure(
            fg_color=self.config.BUTTON_COLOR if is_active else self.config.FRAME_BG,
            state="normal" if is_active else "disabled",
        )

    def clear_values(self):
        """Clear current gamepad values"""
        # Reset joystick position
        self.update_xy_values(0, 0)

        # Reset button states
        for i in range(4):
            self.update_button_state(i, False)

        # Reset joystick button state
        self.update_joystick_button_state(False)
