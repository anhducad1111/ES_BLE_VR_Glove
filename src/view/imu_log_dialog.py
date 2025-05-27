import customtkinter as ctk
from customtkinter import filedialog
from src.config.app_config import AppConfig
from src.view.button_component import ButtonComponent
from src.view.coordinate_entry import CoordinateEntry
from PIL import Image

class IMULogDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self._destroyed = False
        
        # Store parent reference
        self.parent = parent
        
        # Set window attributes
        self._setup_window(parent)
        self._create_main_layout()
        
        # Initialize logger
        self.logger = None
        
        # Update window and show the dialog
        self.update_idletasks()
        # self._ensure_visibility()
        
    def _ensure_visibility(self):
        """Ensure dialog is visible and on top"""
        self.lift()
        self.focus_force()

    def _setup_window(self, parent):
        self.title("IMU Log")
        self.overrideredirect(False)  # Keep window decorations
        self.configure(fg_color="#1F1F1F")  # Dark background
        self.geometry("500x320")  # Adjust size as needed
        self.resizable(False, False)  # Fix window size
        self.protocol("WM_DELETE_WINDOW", self.destroy)  # Handle window close button
        self._center_window(parent)
        self._make_modal(parent)
        
        # Force as top-level window
        self.attributes('-topmost', True)

    def _center_window(self, parent):
        """Center the dialog on the main window"""
        root = parent.winfo_toplevel()
        
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        root_x = root.winfo_x()
        root_y = root.winfo_y()
        root_width = root.winfo_width()
        root_height = root.winfo_height()
        
        x = root_x + (root_width - 450) // 2
        y = root_y + (root_height - 280) // 2
        
        x = max(0, min(x, screen_width - 450))
        y = max(0, min(y, screen_height - 280))
        
        self.geometry(f"+{x}+{y}")

    def _make_modal(self, parent):
        self.transient(parent)
        self.grab_set()
        
        # Ensure dialog appears on top
        # self.lift()
        # self.focus_force()

    def _create_main_layout(self):
        # Main frame with border
        main_frame = ctk.CTkFrame(
            self,
            fg_color="#141414",
            border_color="#333333",
            border_width=1,
            corner_radius=12
        )
        main_frame.pack(fill="both", expand=True, padx=2, pady=2)

        # Content frame with padding
        content = ctk.CTkFrame(main_frame, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=(30, 0))

        # Title - large, bold, white
        header = ctk.CTkLabel(
            content,
            text="IMU log",
            font=("Inter Bold", 24),
            text_color="white"
        )
        header.pack(anchor="w", pady=(0, 30))

        # Path entry container
        path_container = ctk.CTkFrame(
            content,
            fg_color="#1F1F1F",  # Darker than main background
            corner_radius=12
        )
        path_container.pack(fill="x", pady=(0, 30))

        # Path content padding
        path_frame = ctk.CTkFrame(path_container, fg_color="transparent")
        path_frame.pack(padx=20, pady=20, fill="x")
        
        # Path label
        path_label = ctk.CTkLabel(
            path_frame,
            text="Path Location",
            font=("Inter Bold", 16),
            text_color="white"
        )
        path_label.pack(anchor="w", pady=(0, 10))

        # Create path entry container
        path_input_container = ctk.CTkFrame(path_frame, fg_color="transparent")
        path_input_container.pack(fill="x", pady=(0, 0))

        # Create folder icon and convert to white
        icon = Image.open("assets/folder.png")
        folder_image = ctk.CTkImage(
            light_image=icon,
            dark_image=icon,
            size=(20, 20)
        )
        
        # Create clickable icon label
        folder_label = ctk.CTkLabel(
            path_input_container,
            text="",
            image=folder_image,
            cursor="hand2"
        )
        folder_label.pack(side="left", padx=(0, 10))
        folder_label.bind("<Button-1>", lambda e: self._on_choose_folder())

        # Path entry field
        self.path_entry = CoordinateEntry(
            path_input_container,
            "",  
            entry_width=350
        )
        self.path_entry.pack(side="left", fill="x", expand=True)

        # Set initial path
        self.path_entry.entry.configure(state="normal")
        self.path_entry.entry.delete(0, "end")
        self.path_entry.entry.insert(0, "C:/ProjectIT/ES_iot/tutorial_python")


        # Button container
        button_container = ctk.CTkFrame(content, fg_color="transparent")
        button_container.pack(fill="x", pady=(0, 0))

        # Left side buttons
        left_buttons = ctk.CTkFrame(button_container, fg_color="transparent")
        left_buttons.pack(side="left")

        # Choose folder button
        self.choose_folder_button = ButtonComponent(
            left_buttons,
            "Choose Folder",
            command=self._on_choose_folder,
            fg_color="#333333",  # Light gray
            hover_color="#444444",
            text_color="white",
            width=120,
            height=38,
        )
        self.choose_folder_button.pack(side="left")

        # Right side buttons
        right_buttons = ctk.CTkFrame(button_container, fg_color="transparent")
        right_buttons.pack(side="right")

        # Cancel button
        self.cancel_button = ButtonComponent(
            right_buttons,
            "Cancel",
            fg_color="#666666",  # Medium gray
            hover_color="#777777",
            text_color="white",
            width=100,
            height=38
        )
        self.cancel_button.pack(side="left", padx=10)

        # Apply button
        self.apply_button = ButtonComponent(
            right_buttons,
            "Apply",
            fg_color="#0094FF",  # Blue
            hover_color="#0078CC",
            text_color="white",
            width=100,
            height=38
        )
        self.apply_button.pack(side="left")

    def get_path(self):
        """Get the selected path"""
        return self.path_entry.entry.get()

    def _on_choose_folder(self):
        """Handle choose folder button click"""
        folder = filedialog.askdirectory(parent=self, initialdir=r"C:\ProjectIT\ES_iot\tutorial_python")
        if folder:
            self.path_entry.entry.configure(state="normal")
            self.path_entry.entry.delete(0, "end")
            self.path_entry.entry.insert(0, folder)

    def get_path(self):
        """Get the selected path"""
        return self.path_entry.entry.get()

    def set_cancel_callback(self, callback):
        self.cancel_button.configure(command=callback)

    def set_apply_callback(self, callback):
        self.apply_button.configure(command=callback)
