import asyncio
import customtkinter as ctk
from src.config.app_config import AppConfig
from src.view.main_view import MainView
from src.model.esp32_service import ESP32BLEService
from src.model.device_manager import DeviceManager
from src.presenter import (
    ConnectionPresenter,
    GamepadPresenter,
    IMUPresenter,
    OverallStatusPresenter,
    ProfilePresenter,
    SensorPresenter,
    TimestampPresenter,
    LogPresenter
)

class App:
    """Main application class handling BLE device monitoring and IMU data visualization"""
    
    def __init__(self):
        """Initialize the application with BLE service, views, and presenters"""
        # Initialize base components
        self.loop = self._setup_event_loop()
        self.ble_service = ESP32BLEService()  # Will return singleton instance
        self.window = self._setup_window()
        
        # Setup views and presenters
        self.main_view = MainView(self.window)
        self.presenters = self._setup_presenters()
        
        # Setup device manager with singleton instance
        self.device_manager = DeviceManager(self.ble_service, self.presenters)  # Will return singleton instance
        
        # Setup event handlers
        self._init_event_handlers()

    def _setup_event_loop(self):
        """Setup asyncio event loop"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop
    
    def _setup_window(self):
        """Setup main window"""
        config = AppConfig()
        ctk.set_appearance_mode(config.APPEARANCE_MODE)
        window = ctk.CTk()
        
        # Set window title and icon
        window.title(config.WINDOW_TITLE)
        window.iconbitmap(config.WINDOW_ICON)
        
        # Get screen dimensions
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        
        # Set window size to screen size
        window.geometry(f"{screen_width}x{screen_height}+0+0")
        window.after(0, lambda: window.state('zoomed'))
        # window.attributes('-fullscreen', True)
        return window

    def _setup_presenters(self):
        """Initialize all presenters"""
        presenters = {
            'profile': ProfilePresenter(
                self.main_view.device_monitor,
                self.ble_service
            ),
            'timestamp': TimestampPresenter(
                self.main_view.footer,
                self.ble_service,
                self.ble_service.TIMESTAMP_CHAR_UUID
            ),
            'connection': ConnectionPresenter(
                self.main_view.device_monitor,
                self.ble_service,
                self.loop
            ),
            'imu1': IMUPresenter(
                self.main_view.imu1_view,
                self.ble_service,
                self.ble_service.IMU1_CHAR_UUID,
                self.loop
            ),
            'imu2': IMUPresenter(
                self.main_view.imu2_view,
                self.ble_service,
                self.ble_service.IMU2_CHAR_UUID,
                self.loop
            ),
            'sensor': SensorPresenter(
                self.main_view.sensor_view,
                self.ble_service,
                self.loop
            ),
            'gamepad': GamepadPresenter(
                self.main_view.gamepad_view,
                self.ble_service,
                self.loop
            ),
            'overall_status': OverallStatusPresenter(
                self.main_view.overall_status_view,
                self.ble_service,
            )
        }
        
        # Create overall status presenter after other presenters
        presenters['log'] = LogPresenter(
            self.main_view.log_view,
            self.ble_service,
            self.loop,
            presenters['imu1'],
            presenters['imu2'],
            presenters['sensor']
        )
        
        # Setup footer and timestamp
        self.main_view.footer.loop = self.loop
        self.main_view.footer.on_timestamp_click = lambda: self.loop.create_task(
            self._handle_timestamp_sync()
        )
        
        return presenters
    
    def _init_event_handlers(self):
        """Initialize event handlers"""
        # Setup device monitor handlers
        self.main_view.device_monitor.loop = self.loop
        self.main_view.device_monitor.set_handlers(
            connect_command=self._handle_connection,
            disconnect_command=self._handle_disconnect
        )
        
        # Setup asyncio integration
        self._setup_asyncio_integration()
        
        # Setup window close handler
        self.window.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _setup_asyncio_integration(self):
        """Setup asyncio integration with Tkinter event loop"""
        def handle_asyncio():
            self.loop.stop()
            self.loop.run_forever()
            self.window.after(10, handle_asyncio)
        self.window.after(10, handle_asyncio)
    
    def _handle_connection(self, device_info):
        """Handle device connection request"""
        self.loop.create_task(self.device_manager.connect(device_info))
    
    def _handle_disconnect(self):
        """Handle device disconnection request"""
        self.loop.create_task(self.device_manager.disconnect())
    
    async def _handle_timestamp_sync(self):
        """Handle timestamp sync request"""
        if await self.presenters['timestamp'].write_current_time():
            self.main_view.footer.sync_with_pc_time()
    
    def _on_closing(self):
        """Handle application shutdown"""
        from src.view.view_dialog.exit_confirmation_dialog import ExitConfirmationDialog
        dialog = ExitConfirmationDialog(self.window)
        
        async def handle_exit():
            """Handle exit confirmation"""
            try:
                if self.ble_service.is_connected():
                    # Show disconnecting status
                    dialog.yes_btn.configure(state="disabled", text="Disconnecting...")
                    
                    # Run cleanup and disconnect
                    await self.device_manager.disconnect()
                else:
                    # No device connected, just quit
                    dialog.yes_btn.configure(state="disabled")
                
                # Stop event loop and quit
                self.loop.stop()
                self.window.quit()
            except Exception as e:
                print(f"Error during application shutdown: {e}")
                self.window.quit()
                
        dialog.set_on_yes_callback(lambda: self.loop.create_task(handle_exit()))

    def run(self):
        """Start the application"""
        self.window.mainloop()

if __name__ == "__main__":
    app = App()
    app.run()
