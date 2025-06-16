import customtkinter as ctk
from customtkinter import filedialog
from PIL import Image

from src.config.app_config import AppConfig
from src.util.log_manager import LogManager
from src.view.view_component import ButtonComponent, CoordinateEntry


class LogView(ctk.CTkFrame):
    """View component that displays log information"""

    # region Initialization
    def __init__(self, parent: ctk.CTkFrame, **kwargs):
        super().__init__(parent, **kwargs)
        self.config = AppConfig()
        self.configure(
            fg_color=self.config.PANEL_COLOR,
            corner_radius=self.config.CORNER_RADIUS,
            height=self.config.INFO_PANEL_HEIGHT,
        )
        self.pack_propagate(False)
        self.log_manager = LogManager.instance()

        # UI Components
        self.path_entry = None
        self.log_button = None
        self.selected_folder = None
        self.presenter = None
        # self.set_button_states(True)
        # Initialize UI
        self._create_layout()
        self._setup_callbacks()

    # endregion

    # region UI Layout
    def _create_layout(self):
        """Create the main layout of the view"""
        # Create header section
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=12, pady=7)

        title = ctk.CTkLabel(
            header,
            text="LOG MANAGER",
            font=self.config.HEADER_FONT,
            text_color=self.config.TEXT_COLOR,
        )
        title.pack(anchor="w")

        # Create path selection section
        self._create_path_section()

    def _create_path_section(self):
        """Create path selection section"""
        path_container = ctk.CTkFrame(self, fg_color="transparent")
        path_container.pack(fill="x", padx=12, pady=(0, 10))

        # Configure grid for path entry and icon
        path_container.grid_columnconfigure(0, weight=1)  # Entry expands
        path_container.grid_columnconfigure(1, weight=0)  # Icon stays fixed
        
        # Path container top row
        path_frame = ctk.CTkFrame(path_container, fg_color="transparent")
        path_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        path_frame.grid_columnconfigure(0, weight=1)
        path_frame.grid_columnconfigure(1, weight=0)

        # Create path entry
        self.path_entry = CoordinateEntry(path_frame, "", entry_width=260)
        self.path_entry.grid(row=0, column=0, sticky="ew")

        # Set initial path
        self.path_entry.entry.delete(0, "end")
        self.path_entry.entry.insert(0, self.log_manager.get_selected_folder())
        self.path_entry.entry.configure(state="readonly", cursor="arrow")

        # Create folder icon
        icon = Image.open("assets/folder.png")
        folder_image = ctk.CTkImage(light_image=icon, dark_image=icon, size=(20, 20))
        folder_label = ctk.CTkLabel(
            path_frame, text="", image=folder_image, cursor="hand2"
        )
        folder_label.grid(row=0, column=1, padx=(0, 10), sticky="e")
        folder_label.bind("<Button-1>", lambda e: self._on_choose_folder())
        
        # Create log button in its own row
        button_frame = ctk.CTkFrame(path_container, fg_color="transparent")
        button_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10,0))
        button_frame.grid_columnconfigure(0, weight=1)  # Push button to right

        self.log_button = ButtonComponent(button_frame, "Start Log", command=self._on_log)
        self.log_button.grid(row=0, column=0, sticky="e")
        self.log_button.configure(state="disabled")


    # endregion

    # region Path Selection
    def _on_choose_folder(self):
        """Handle folder selection"""
        if not self._is_any_logger_active():
            self.path_entry.entry.configure(state="normal")

            folder = filedialog.askdirectory(
                initialdir=self.log_manager.get_selected_folder()
            )
            if folder:
                self.path_entry.entry.delete(0, "end")
                self.path_entry.entry.insert(0, folder)
                self.log_manager.setup_logging_folder(folder)

            self.path_entry.entry.configure(state="readonly", cursor="arrow")

    def _is_any_logger_active(self):
        """Check if any logger is currently active"""
        return (
            self.log_manager.get_imu1_logger().is_logging
            or self.log_manager.get_imu2_logger().is_logging
            or self.log_manager.get_sensor_logger().is_logging
        )

    def _setup_callbacks(self) -> None:
        """Set up callback functions"""
        self.log_manager.add_folder_change_callback(self._on_folder_change)

    def set_path_entry_state(self, state):
        """Set path entry state"""
        self.path_entry.entry.configure(state=state)

    def destroy(self) -> None:
        """Clean up resources before destruction"""
        if hasattr(self, "log_manager"):
            self.log_manager.remove_folder_change_callback(self._on_folder_change)
            if self.log_manager.get_imu1_logger().is_logging:
                self._stop_logging()
        super().destroy()

    # endregion

    # region Logging Control
    def _handle_logging_state(self, start: bool) -> None:
       """Handle logging state changes"""
       try:
           if start:
               if self.presenter.start_all_logging():
                   self._update_button_for_logging()
           else:
               self.presenter.stop_all_logging()
               self._update_button_for_stopped()
       except Exception as e:
           print(f"Error {'starting' if start else 'stopping'} logging: {e}")
           if start:
               self._stop_logging()

    def _update_button_for_logging(self) -> None:
       """Update button appearance for logging state"""
       self.log_button.configure(
           text="Stop Log", fg_color="darkred", hover_color="#8B0000"
       )

    def _update_button_for_stopped(self) -> None:
       """Update button appearance for stopped state"""
       self.selected_folder = None
       self.log_button.configure(
           text="Start Log",
           fg_color=self.config.BUTTON_COLOR,
           hover_color=self.config.BUTTON_HOVER_COLOR,
       )

    def _on_log(self) -> None:
       """Handle log button clicks"""
       if not self.presenter:
           return

       if self.log_manager.get_imu1_logger().is_logging:
           self._stop_logging()
       else:
           self.selected_folder = self.log_manager.get_selected_folder()
           self._start_logging()

    def _start_logging(self) -> None:
       """Start the logging process"""
       self._handle_logging_state(True)

    def _stop_logging(self) -> None:
       """Stop the logging process"""
       self._handle_logging_state(False)

    def set_presenter(self, presenter) -> None:
       """Set the presenter reference"""
       self.presenter = presenter

    def clear_values(self) -> None:
       """Reset logging state"""
       if self.log_manager.get_imu1_logger().is_logging:
           self._stop_logging()
       self._update_button_for_stopped()
       self.set_button_states(False)

    def set_button_states(self, enabled: bool) -> None:
       """Enable or disable interactive elements"""
       self.log_button.configure(state="normal" if enabled else "disabled")

    def show_log_button(self, show: bool) -> None:
       """Show or hide the log button"""
       if show:
           self.log_button.pack()
       else:
           self.log_button.pack_forget()

    def _on_folder_change(self, folder: str) -> None:
       """Handle folder selection changes"""
       self.selected_folder = folder
       self.log_button.configure(text="Start Log")
    # endregion