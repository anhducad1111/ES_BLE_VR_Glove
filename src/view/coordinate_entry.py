import customtkinter as ctk
from src.config.app_config import AppConfig

class CoordinateEntry(ctk.CTkFrame):
    def __init__(self, parent, label_text, entry_width=120):
        super().__init__(
            parent,
            fg_color="transparent",
            # width=300  # Set fixed width for the frame
        )
        
        self.config = AppConfig()  # Get singleton instance

        # Create label
        self.label = ctk.CTkLabel(
            self,
            text=label_text,
            font=self.config.LABEL_FONT,
            text_color=self.config.TEXT_COLOR,
            fg_color="transparent"
        )
        self.label.grid(row=0, column=0, sticky="nw", padx=(0, 10))

        # Create entry
        self.entry = ctk.CTkEntry(
            self,
            width=entry_width,  # Fixed width for the entry
            height=25,
            font=self.config.TEXT_FONT,
            text_color=self.config.TEXT_COLOR,
            fg_color=self.config.FRAME_BG,
        )
        self.entry.grid(row=0, column=1, sticky="ew")
        self.entry.insert(0, "0")
        # self.entry.configure(state="readonly")

    def set_value(self, value: float):
        """Update the coordinate value"""
        self.entry.configure(state="normal")
        self.entry.delete(0, "end")
        self.entry.insert(0, f"{value:.2f}")
        self.entry.configure(state="readonly")

    def get_value(self) -> float:
        """Get the current coordinate value"""
        try:
            return float(self.entry.get())
        except ValueError:
            return 0.0
