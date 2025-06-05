import os
import datetime

class LogManager:
    """Singleton manager for handling shared log folder selection"""
    
    _instance = None
    
    @classmethod
    def instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        self.selected_folder = "C:/ProjectIT/ES_iot/log"  # Default path
        self.folder_path = None
        self.active_loggers = 0
        self._folder_change_callbacks = []
        self._notify_folder_change()  # Notify about default path

    def add_folder_change_callback(self, callback):
        """Add callback to be notified of folder changes"""
        if callback not in self._folder_change_callbacks:
            self._folder_change_callbacks.append(callback)

    def remove_folder_change_callback(self, callback):
        """Remove folder change callback"""
        if callback in self._folder_change_callbacks:
            self._folder_change_callbacks.remove(callback)

    def _notify_folder_change(self):
        """Notify all registered callbacks of folder change"""
        for callback in self._folder_change_callbacks:
            try:
                callback(self.selected_folder)
            except:
                pass
        
    def setup_logging_folder(self, base_folder):
        """Set up logging folder path"""
        # Update selected folder and notify
        self.selected_folder = base_folder if base_folder else "C:/ProjectIT/ES_iot/log"
        self._notify_folder_change()
        return True
    
    def get_logging_folder(self):
        """Get current logging folder path"""
        return self.folder_path
        
    def get_selected_folder(self):
        """Get base folder selected by user"""
        return self.selected_folder
        
    def clear_logging(self):
        """Reset logging state"""
        self.folder_path = None
        self.active_loggers = 0
        
    def register_logger(self):
        """Register a new active logger"""
        self.active_loggers += 1
        
    def unregister_logger(self):
        """Unregister an active logger"""
        if self.active_loggers > 0:
            self.active_loggers -= 1
            
        # If no more active loggers, clear the folder selection
        if self.active_loggers == 0:
            self.clear_logging()