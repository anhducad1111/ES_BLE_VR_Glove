from src.model.gamepad import JoystickData, ButtonsData

class GamepadPresenter:
    """Presenter for handling gamepad data"""
    
    def __init__(self, view, ble_service):
        """Initialize gamepad presenter
        
        Args:
            view: Reference to the gamepad view
            ble_service: Reference to the BLE service
        """
        self.view = view
        self.service = ble_service
        self._current_joystick_data = None
        self._current_buttons_data = None
        
        # Initially disable buttons until connection is established
        self.view.set_button_states(False)

    async def start_notifications(self):
        """Start gamepad notifications"""
        if self.service:
            joystick_success = await self.service.start_joystick_notify(self._handle_joystick_update)
            buttons_success = await self.service.start_buttons_notify(self._handle_buttons_update)
            if joystick_success and buttons_success:
                self.view.set_button_states(True)
                return True
            return False
        return False

    async def stop_notifications(self):
        """Stop gamepad notifications"""
        if self.service:
            await self.service.stop_joystick_notify()
            await self.service.stop_buttons_notify()
            self.view.set_button_states(False)

    async def _handle_joystick_update(self, sender, joystick_data):
        """Handle joystick data updates
        
        Args:
            sender: The characteristic that sent the notification
            joystick_data: JoystickData object containing joystick data
        """
        if joystick_data and isinstance(joystick_data, JoystickData):
            self._current_joystick_data = joystick_data
            # Update view with new values
            self.view.update_xy_values(joystick_data.x, joystick_data.y)

    async def _handle_buttons_update(self, sender, buttons_data):
        """Handle buttons data updates
        
        Args:
            sender: The characteristic that sent the notification
            buttons_data: ButtonsData object containing buttons data
        """
        if buttons_data and isinstance(buttons_data, ButtonsData):
            self._current_buttons_data = buttons_data
            # Update view with new button states
            for i, state in enumerate(buttons_data.states):
                self.view.update_button_state(i, bool(state))

    def clear_values(self):
        """Clear current gamepad values"""
        self._current_joystick_data = None
        self._current_buttons_data = None
        
        # Reset joystick position
        self.view.update_xy_values(0, 0)
        
        # Reset button states
        for i in range(4):
            self.view.update_button_state(i, False)
