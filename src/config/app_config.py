class AppConfig:
    """Configuration settings for the Device Monitor application"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
        
    def __init__(self):
        if not hasattr(self, 'initialized'):
            # Application settings
            self.APP_VERSION = "1.0.0"
            
            # Initialize all other settings
            self._init_settings()
            self.initialized = True
    
    def _init_settings(self):
    
        # Display scaling
        self.DISPLAY_SCALING = 0.9
        self.WINDOW_SCALING = 0.9

        # Window settings
        self.WINDOW_TITLE = "Device Monitor"
        self.WINDOW_WIDTH = 1700
        self.WINDOW_HEIGHT = 900
        self.WINDOW_MAXIMIZED = True
        self.WINDOW_PADDING = 24

        # Info Panel dimensions
        self.INFO_PANEL_WIDTH = 1636
        self.INFO_PANEL_HEIGHT = 116

        # Theme colors
        self.APPEARANCE_MODE = "dark"
        self.BACKGROUND_COLOR = "#1F1F1F"
        self.PANEL_COLOR = "#2B2D30"
        self.BORDER_COLOR = "#373737"
        self.BUTTON_COLOR = "#0078D4"
        self.BUTTON_HOVER_COLOR = "#0063AD"  
        self.DISCONNECT_COLOR = "darkred"
        self.DISCONNECT_HOVER_COLOR = "#8B0000"
        self.TEXT_COLOR = "white"
        self.LABEL_COLOR = "#DEDEDE"
        self.TEXTBOX_COLOR = "#373737"
        self.FRAME_BG = "#5D5D5D"

        # Typography
        self.FONT_FAMILY = "Inter"
        self.FONT_SIZE_HEADER = 16
        self.FONT_SIZE_NORMAL = 12
        
        self.FONT_WEIGHT_NORMAL = "normal"
        self.FONT_WEIGHT_BOLD = "bold"
        
        self.HEADER_FONT = (self.FONT_FAMILY + " Bold", self.FONT_SIZE_HEADER)
        self.LABEL_FONT = (self.FONT_FAMILY, self.FONT_SIZE_NORMAL)
        self.VALUE_FONT = (self.FONT_FAMILY + " Bold", self.FONT_SIZE_NORMAL)
        self.TEXT_FONT = (self.FONT_FAMILY, self.FONT_SIZE_NORMAL)
        self.BUTTON_FONT = (self.FONT_FAMILY, self.FONT_SIZE_NORMAL)
        
        # Component styling
        self.BORDER_WIDTH = 1
        self.CORNER_RADIUS = 8
        self.BUTTON_CORNER_RADIUS = 8  
        
        # Button dimensions
        self.BUTTON_WIDTH = 112
        self.BUTTON_HEIGHT = 38

        # Footer settings
        self.FOOTER_HEIGHT = 50
        self.FOOTER_COLOR = "#181818"
        self.FOOTER_PADDING = 20
