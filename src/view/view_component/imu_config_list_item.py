from typing import List, Optional

import customtkinter as ctk


class IMUConfigListItem(ctk.CTkFrame):
    """A custom frame component for IMU configuration items with a label and combobox."""

    # Constants for styling
    LABEL_WIDTH = 120
    COMBOBOX_WIDTH = 260
    CORNER_RADIUS = 6
    PADDING_Y = 6
    LABEL_PADDING_X = (12, 0)
    COMBOBOX_PADDING_X = (0, 12)

    # Style configuration
    LABEL_STYLE = {"anchor": "w", "text_color": "white", "font": ("Inter", 13)}

    COMBOBOX_STYLE = {
        "fg_color": "#444444",
        "border_color": "#444",
        "button_color": "#444",
        "dropdown_fg_color": "#444444",
        "dropdown_text_color": "white",
        "dropdown_hover_color": "#333",
        "state": "readonly",
    }

    def __init__(
        self, parent: ctk.CTk, label_text: str, values: List[str], **kwargs
    ) -> None:
        """Initialize a new IMU configuration list item.

        Args:
            parent: Parent widget
            label_text: Text to display in the label
            values: List of possible values for the combobox
            **kwargs: Additional arguments passed to CTkFrame

        Note:
        - Values come from BLEConstants configuration maps
        - Initial value will be set via set() method to reflect device state
        """
        super().__init__(
            parent, fg_color="transparent", corner_radius=self.CORNER_RADIUS, **kwargs
        )

        self._create_label(label_text)
        self._create_combobox(values)
        self._configure_grid()

    def _create_label(self, label_text: str) -> None:
        """Create and configure the label."""
        self.label = ctk.CTkLabel(
            self, text=label_text, width=self.LABEL_WIDTH, **self.LABEL_STYLE
        )
        self.label.grid(
            row=0, column=0, sticky="w", pady=self.PADDING_Y, padx=self.LABEL_PADDING_X
        )

    def _create_combobox(self, values: List[str]) -> None:
        """Create and configure the combobox with possible values.

        Note: No initial value is set - it will be set later via set() method
        to reflect the actual device state.
        """
        self.combobox = ctk.CTkComboBox(
            self, width=self.COMBOBOX_WIDTH, values=values, **self.COMBOBOX_STYLE
        )

        self.combobox.grid(
            row=0,
            column=1,
            sticky="ew",
            pady=self.PADDING_Y,
            padx=self.COMBOBOX_PADDING_X,
        )

    def _configure_grid(self) -> None:
        """Configure the grid layout."""
        self.grid_columnconfigure(1, weight=1)

    def get(self) -> str:
        """Get the current value from combobox.

        Returns:
            The currently selected value
        """
        return self.combobox.get()

    def set(self, value: str) -> None:
        """Set the combobox value.

        Args:
            value: Value to set in the combobox
        """
        self.combobox.set(value)
