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
        self.selected_folder = None
        self.folder_path = None
        self.active_loggers = 0
        self._folder_change_callbacks = []

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
        """Set up logging folder and return the path"""
        try:
            # Create timestamped folder
            now = datetime.datetime.now()
            subfolder = now.strftime("%d%m%Y_%H%M%S_vr_glove")
            self.folder_path = os.path.join(base_folder, subfolder)
            os.makedirs(self.folder_path, exist_ok=True)
            self.selected_folder = base_folder
            self._notify_folder_change()  # Notify observers
            return True
        except:
            self.folder_path = None
            self.selected_folder = None
            return False
    
    def get_logging_folder(self):
        """Get current logging folder path"""
        return self.folder_path
        
    def get_selected_folder(self):
        """Get base folder selected by user"""
        return self.selected_folder
        
    def clear_logging(self):
        """Clear logging state"""
        self.selected_folder = None
        self.folder_path = None
        self._notify_folder_change()  # Notify observers
        
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