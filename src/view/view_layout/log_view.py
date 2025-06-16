import customtkinter as ctk


class LogView(ctk.CTkFrame):
    """View component that displays log information"""

    def __init__(self, parent: ctk.CTkFrame, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(fg_color=("gray85", "gray17"))

        self.label = ctk.CTkLabel(
            self,
            text="Log View",
            text_color=("gray10", "gray90"),
            font=("Roboto", 14, "bold"),
        )
        self.label.pack(pady=10)