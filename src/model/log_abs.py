from abc import ABC, abstractmethod

class LogABS(ABC):
    """Abstract base class for logging management"""
    
    def __init__(self, folder_path=None):
        """Initialize logger with folder path
        
        Args:
            folder_path: Directory where log files will be created
        """
        self.folder_path = folder_path
    
    @abstractmethod
    def setup_header(self, *args, **kwargs):
        """Set up file header - must be implemented by child classes"""
        pass
    
    @abstractmethod
    def setup_footer(self, *args, **kwargs):
        """Set up file footer - must be implemented by child classes"""
        pass
        
    @abstractmethod
    def write_csv(self, *args, **kwargs):
        """Write data to CSV file - must be implemented by child classes"""
        pass
