class AppConfig:
    """Application configuration"""
    
    # UI appearance
    APPEARANCE_MODE = "dark"
    
    # Fonts
    HEADER_FONT = ("Helvetica", 14, "bold")
    LABEL_FONT = ("Helvetica", 12)
    TEXT_FONT = ("Helvetica", 10)
    
    # UI colors
    SUCCESS_COLOR = "#28a745"
    ERROR_COLOR = "#dc3545"
    WARNING_COLOR = "#ffc107"
    
    # Instance holder for singleton
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance