import remi.gui as gui
from remi import start, App

class GestureManagerApp(App):
    def __init__(self, *args):
        super(GestureManagerApp, self).__init__(*args)
        # Do not set self.custom_gesture_manager here; set it in main()

    # Modify main to accept arbitrary arguments to handle Remi's call signature
    def main(self, *args):
        # Ensure custom_gesture_manager is set from server.userdata
        if not hasattr(self, 'custom_gesture_manager'):
            self.custom_gesture_manager = self.server.userdata[0] if self.server.userdata else None
        # Main container
        main_container = gui.VBox(width='100%', height='100%')
        main_container.style['justify-content'] = 'flex-start'
        main_container.style['align-items'] = 'center'

        # Title
        title = gui.Label('Custom Gesture Management', style={'font-size': '20px', 'margin-bottom': '20px'})
        main_container.append(title)

        # Placeholder for gesture list (will be populated later)
        self.gesture_list_container = gui.VBox()
        self.gesture_list_container.style['width'] = '80%'
        self.gesture_list_container.style['margin-bottom'] = '20px'
        self.gesture_list_container.style['border'] = '1px solid black'
        self.gesture_list_container.style['padding'] = '10px'
        main_container.append(self.gesture_list_container)

        # Load and display existing gestures
        self.load_and_display_gestures()

        # Section for adding a new gesture
        add_gesture_container = gui.VBox()
        add_gesture_container.style['width'] = '80%'
        add_gesture_container.style['margin-top'] = '20px'
        add_gesture_container.style['border'] = '1px solid black'
        add_gesture_container.style['padding'] = '10px'
        add_gesture_container.style['align-items'] = 'flex-start' # Align items to the start

        add_gesture_title = gui.Label('Add New Gesture', style={'font-size': '18px', 'margin-bottom': '10px', 'font-weight': 'bold'})
        add_gesture_container.append(add_gesture_title)

        # Input for Gesture Name
        gesture_name_label = gui.Label('Gesture Name:', style={'margin-bottom': '5px'})
        add_gesture_container.append(gesture_name_label)
        self.gesture_name_input = gui.TextInput(width='100%', style={'margin-bottom': '10px'})
        add_gesture_container.append(self.gesture_name_input)

        # Input for Associated Action
        gesture_action_label = gui.Label("Associated Action:", style={'margin-bottom': '5px'})
        add_gesture_container.append(gesture_action_label)
        
        self.action_options = [
            ("left_click", "Left Click"),
            ("double_click", "Double Click"),
            ("right_click", "Right Click"),
            ("scroll_up", "Scroll Up"),
            ("scroll_down", "Scroll Down"),
            ("win+h", "Speech-to-Text (Win+H)"),
            ("hotkey", "Other (Keyboard Shortcut)") # Option for custom hotkey
        ]
        self.gesture_action_dropdown = gui.DropDown(width='100%', style={'margin-bottom': '10px'})
        for value, text in self.action_options:
            self.gesture_action_dropdown.append(gui.DropDownItem(text, value=value))
        self.gesture_action_dropdown.onchange.do(self.on_action_dropdown_change)
        add_gesture_container.append(self.gesture_action_dropdown)

        # Text input for custom hotkey (initially hidden)
        self.hotkey_input_container = gui.HBox(width='100%', style={'margin-bottom': '10px', 'display': 'none'}) # Hidden by default
        hotkey_label = gui.Label('Hotkey (e.g., "ctrl+c", "alt+f4"): ')
        self.hotkey_input = gui.TextInput(width='70%')
        self.hotkey_input_container.append(hotkey_label)
        self.hotkey_input_container.append(self.hotkey_input)
        add_gesture_container.append(self.hotkey_input_container)

        # Buttons for recording
        button_container = gui.HBox()
        button_container.style['justify-content'] = 'space-around'
        button_container.style['width'] = '100%'

        self.start_record_button = gui.Button('Start Recording')
        self.start_record_button.onclick.do(self.start_recording)
        button_container.append(self.start_record_button)

        self.stop_record_button = gui.Button('Stop Recording and Save')
        self.stop_record_button.set_enabled(False) # Initially disabled
        self.stop_record_button.onclick.do(self.stop_recording_and_save)
        button_container.append(self.stop_record_button)

        add_gesture_container.append(button_container)

        main_container.append(add_gesture_container)

        # Status message label
        self.status_label = gui.Label('', style={'margin-top': '10px', 'color': 'red'})
        main_container.append(self.status_label)

        return main_container

    # New method to load and display gestures
    def load_and_display_gestures(self):
        # Clear the current list display
        self.gesture_list_container.empty()

        # Access gestures via gesture_recognizer
        gestures = None
        if self.custom_gesture_manager and self.custom_gesture_manager.gesture_recognizer:
            gestures = self.custom_gesture_manager.gesture_recognizer.custom_gestures

        if gestures and len(gestures) > 0:
            title = gui.Label('Existing Gestures:', style={'font-weight': 'bold', 'margin-bottom': '10px'})
            self.gesture_list_container.append(title)

            for gesture_name, gesture_data in gestures.items():
                gesture_info = gui.Label(f"{gesture_name}: {gesture_data['action']}")
                self.gesture_list_container.append(gesture_info)
        else:
            no_gestures_label = gui.Label('No custom gestures recorded yet.')
            self.gesture_list_container.append(no_gestures_label)

    # New method to handle dropdown change
    def on_action_dropdown_change(self, widget, value):
        if value == 'hotkey':
            self.hotkey_input_container.style['display'] = 'flex' # Show hotkey input
        else:
            self.hotkey_input_container.style['display'] = 'none' # Hide hotkey input
            self.hotkey_input.set_value('') # Clear hotkey input when not in use

    # New method to get the selected action (either from dropdown or hotkey input)
    def get_selected_action(self):
        selected_option = self.gesture_action_dropdown.get_value()
        if selected_option == 'hotkey':
            return self.hotkey_input.get_value().strip()
        else:
            return selected_option

    def start_recording(self, widget):
        gesture_name = self.gesture_name_input.get_value().strip()
        gesture_action = self.get_selected_action() # Use the new method to get the action
        self.status_label.set_text('') # Clear previous status message

        if gesture_name and gesture_action and self.custom_gesture_manager:
            # Disable start and enable stop button
            self.start_record_button.set_enabled(False)
            self.stop_record_button.set_enabled(True)
            # Trigger the start of recording in the CustomGestureManager
            self.custom_gesture_manager.start_recording_gesture(gesture_name, gesture_action)
            self.status_label.set_text(f"Started recording for '{gesture_name}'. Perform gesture in camera.")
            print(f"Started recording for gesture: {gesture_name} with action: {gesture_action}")
        else:
            self.status_label.set_text("Please enter both Gesture Name and Associated Action.")
            print("Please enter both Gesture Name and Associated Action.") # Add visual feedback for this later

    def stop_recording_and_save(self, widget):
        if self.custom_gesture_manager:
            # Enable start and disable stop button
            self.start_record_button.set_enabled(True)
            self.stop_record_button.set_enabled(False)
            # Trigger the stop and save process in the CustomGestureManager
            self.custom_gesture_manager.stop_recording_gesture()
            # Refresh the displayed list of gestures
            self.load_and_display_gestures()
            self.status_label.set_text("Gesture recorded and saved.") # Update status label on successful save
            # Clear input fields after successful save
            self.gesture_name_input.set_value('')
            self.gesture_action_dropdown.set_value('left_click') # Reset dropdown to default
            self.hotkey_input.set_value('') # Clear hotkey input
            self.hotkey_input_container.style['display'] = 'none' # Hide hotkey input
            print("Stopped recording and saved gesture.")

# This is where we'd typically start the app, but we'll integrate it
# into the main application's lifecycle later.
# if __name__ == '__main__':
#     start(GestureManagerApp, port=8081, debug=True) 