import customtkinter as ctk

class IMUConfigListItem(ctk.CTkFrame):
    def __init__(self, parent, label_text, values, default=None, **kwargs):
        super().__init__(parent, fg_color="transparent", corner_radius=6, **kwargs)
        self.label = ctk.CTkLabel(self, text=label_text, width=120, anchor="w", text_color="white", font=("Inter", 13))
        self.label.grid(row=0, column=0, sticky="w", pady=6, padx=(12, 0))
        self.combobox = ctk.CTkComboBox(
            self,
            width=260,
            values=values,
            fg_color="#444444",
            border_color="#444",
            button_color="#444",
            dropdown_fg_color="#444444",
            dropdown_text_color="white",
            dropdown_hover_color="#333",
            state="readonly"
        )
        if default:
            self.combobox.set(default)
        else:
            if values:
                self.combobox.set(values[0])
        self.combobox.grid(row=0, column=1, sticky="ew", pady=6, padx=(0, 12))
        self.grid_columnconfigure(1, weight=1)

    def get(self):
        return self.combobox.get()

    def set(self, value):
        self.combobox.set(value)