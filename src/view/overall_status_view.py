import customtkinter as ctk
from src.config.app_config import AppConfig
from src.view.button_component import ButtonComponent
from src.util.log_manager import LogManager

class OverallStatusView(ctk.CTkFrame):
    def __init__(self, parent):
        self.config = AppConfig()  # Get singleton instance
        
        # Set up log manager
        self.log_manager = LogManager.instance()
        self.log_manager.add_folder_change_callback(self._on_folder_change)
        
        super().__init__(
            parent,
            fg_color=self.config.PANEL_COLOR,
            border_color=self.config.BORDER_COLOR,
            border_width=self.config.BORDER_WIDTH,
            corner_radius=self.config.CORNER_RADIUS
        )
        # Initialize variables
        self.imu1_presenter = None
        self.imu2_presenter = None
        self.selected_folder = None
        self.log_button = None

        # Configure base grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Create UI Components
        self.create_header()
        self.create_status_container()
        self.update_status(False, False, False)

    def create_header(self):
        """Create the header section"""
        header_label = ctk.CTkLabel(
            self,
            text="OVERALL STATUS",
            font=self.config.HEADER_FONT,
            text_color=self.config.TEXT_COLOR
        )
        header_label.grid(row=0, column=0, sticky="nw", padx=12, pady=(12, 0))

    def create_status_container(self):
        """Create the status indicator container"""
        # Create container frame
        status_container = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )
        status_container.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        
        # Configure grid columns
        status_container.grid_columnconfigure((1, 3, 5), weight=1)  # Status columns
        status_container.grid_columnconfigure((0, 2, 4, 6), weight=0)  # Label columns

        # Store status labels for updates
        self.status_labels = {}

        # Create status indicators
        status_configs = [
            ("Fuelgause:", "fuelgause", 0),
            ("IMU1:", "imu1", 2),
            ("IMU2:", "imu2", 4)
        ]

        for label_text, key, start_col in status_configs:
            self.create_status_pair(
                status_container,
                label_text,
                key,
                start_col
            )
        self._create_log_button(status_container)

    def create_status_pair(self, parent, label_text, key, start_col):
        """Create a status indicator pair (label + status)"""
        # Create label
        label = ctk.CTkLabel(
            parent,
            text=label_text,
            font=self.config.TEXT_FONT,
            text_color=self.config.TEXT_COLOR,
        )
        label.grid(
            row=0, 
            column=start_col, 
            sticky="w", 
            padx=(12 if start_col == 0 else 20, 10), 
            pady=12
        )
        
        # Create status
        status = ctk.CTkLabel(
            parent,
            text="NONE",
            font=self.config.TEXT_FONT,
            text_color="red",
        )
        status.grid(
            row=0, 
            column=start_col + 1, 
            sticky="w", 
            padx=10, 
            pady=12
        )
        
        # Store reference
        self.status_labels[key] = status

    def update_status(self, fuelgause: bool, imu1: bool, imu2: bool):
        """Update all status indicators at once
        
        Args:
            fuelgause: Status of fuelgause
            imu1: Status of IMU1
            imu2: Status of IMU2
        """
        status_values = {
            "fuelgause": fuelgause,
            "imu1": imu1,
            "imu2": imu2
        }
        
        for key, is_running in status_values.items():
            self.status_labels[key].configure(
                text="RUNNING" if is_running else "NONE",
                text_color=self.config.BUTTON_COLOR if is_running else "red"
            )
            
    def clear_values(self):
        """Clear all status indicators"""
        self.update_status(False, False, False)
        
        # Stop logging if active
        if self.log_manager.get_imu1_logger().is_logging:
            self._stop_logging()
        
        self.log_button.configure(
            text="Log IMU",
            fg_color=self.config.BUTTON_COLOR,
            hover_color=self.config.BUTTON_HOVER_COLOR
        )
        self.set_button_states(False)

    def _create_log_button(self, parent):
        """Create the log button"""
        self.log_button = ButtonComponent(
            parent,
            "Log IMU",
            command=self._on_log
        )
        self.log_button.grid(row=0, column=6, columnspan=2, padx=3 ,sticky="e")
        self.log_button.configure(state="disabled")

    def show_log_button(self, show: bool):
        """Show or hide the log button"""
        if show:
            self.log_button.grid()
        else:
            self.log_button.grid_remove()

    def set_imu_presenters(self, imu1_presenter, imu2_presenter):
        """Set IMU presenters for logging"""
        self.imu1_presenter = imu1_presenter
        self.imu2_presenter = imu2_presenter

    def _on_log(self):
        """Handle log button click"""
        if not self.imu1_presenter or not self.imu2_presenter:
            return

        # If currently logging, stop logging
        if self.log_manager.get_imu1_logger().is_logging:
            self._stop_logging()
            return

        # Start logging using path from LogManager
        folder = self.log_manager.get_selected_folder()
        self.selected_folder = folder
        self._start_logging()
            
    def destroy(self):
        """Clean up resources before destroying widget"""
        # Remove folder change callback
        if hasattr(self, 'log_manager'):
            self.log_manager.remove_folder_change_callback(self._on_folder_change)
            
        # Stop logging if active
        if self.log_manager.get_imu1_logger().is_logging:
            self._stop_logging()
            
        super().destroy()
            
    def _on_folder_change(self, folder):
        """Handle folder selection changes from LogManager"""
        self.selected_folder = folder
        if folder:
            self.log_button.configure(text="Start Log IMU")
        else:
            self.log_button.configure(text="Log IMU")

    def _start_logging(self):
        """Start logging IMU and Sensor data"""
        try:
            # Set loggers in presenters
            self.imu1_presenter.set_logger(self.log_manager.get_imu1_logger())
            self.imu2_presenter.set_logger(self.log_manager.get_imu2_logger())
            
            # Start all logging
            if self.log_manager.start_all_logging():
                # Update button
                self.log_button.configure(text="Stop Log IMU", fg_color="darkred", hover_color="#8B0000")
            else:
                # Reset presenters if logging fails
                self.imu1_presenter.set_logger(None)
                self.imu2_presenter.set_logger(None)
                
        except Exception as e:
            print(f"Error starting logging: {e}")
            self._stop_logging()

    def _stop_logging(self):
        """Stop logging IMU and Sensor data"""
        try:
            self.log_manager.stop_all_logging()
            self.imu1_presenter.set_logger(None)
            self.imu2_presenter.set_logger(None)
            
            # Reset button
            self.selected_folder = None
            self.log_button.configure(text="Log", fg_color=self.config.BUTTON_COLOR, hover_color=self.config.BUTTON_HOVER_COLOR)
        except Exception as e:
            print(f"Error stopping logging: {e}")

    def set_button_states(self, enabled):
        """Enable/disable buttons"""
        state = "normal" if enabled else "disabled"
        self.log_button.configure(state=state)
