import customtkinter as ctk
from src.config.app_config import AppConfig

class ButtonComponent(ctk.CTkButton):
    def __init__(self, parent, button_text: str, **kwargs):
        self.config = AppConfig()  # Get singleton instance
        # Set default values
        default_settings = {
            "text": button_text,
            "font": self.config.BUTTON_FONT,
            "text_color": self.config.TEXT_COLOR,
            "fg_color": self.config.BUTTON_COLOR,
            "width": self.config.BUTTON_WIDTH,
            "height": self.config.BUTTON_HEIGHT,
            "corner_radius": self.config.BUTTON_CORNER_RADIUS,
        }
        
        # Update defaults with any provided kwargs
        default_settings.update(kwargs)
        
        # Initialize with combined settings
        super().__init__(parent, **default_settings)
