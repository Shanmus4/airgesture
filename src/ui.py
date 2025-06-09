# ui.py
import remi.gui as gui
from remi import App

# DEBUG flag for controlling debug output
DEBUG = True

class GestureApp(App):
    app_instance = None # Class variable to hold the single app instance

    def __init__(self, *args):
        if GestureApp.app_instance is not None:
            raise Exception("Only one instance of GestureApp can be created.")
        super(GestureApp, self).__init__(*args)
        GestureApp.app_instance = self

        self.calibrate_callback = None
        self.capture_point_callback = None
        self.show_gestures_callback = None
        self.test_mode_callback = None

        # UI elements
        self.feedback_label = None
        self.legend_box = None
        self.next_point_btn = None

    def set_callbacks(self, start_calibration_callback, capture_calibration_point_callback, show_gestures_callback, start_test_mode_callback):
        self.calibrate_callback = start_calibration_callback
        self.capture_point_callback = capture_calibration_point_callback
        self.show_gestures_callback = show_gestures_callback
        self.test_mode_callback = start_test_mode_callback

    def main(self):
        main_container = gui.VBox(width='100%', height='100%')
        main_container.style['align-items'] = 'center'
        main_container.style['justify-content'] = 'flex-start'

        # Feedback label
        self.feedback_label = gui.Label('', width='100%', style={'color': 'blue', 'font-size': '16px', 'margin-bottom': '10px'})
        main_container.append(self.feedback_label)

        # Buttons
        button_box = gui.HBox(width='100%', style={'justify-content': 'space-around', 'margin-bottom': '10px'})
        
        self.calibrate_btn = gui.Button('Calibrate', width=120, height=40)
        self.calibrate_btn.onclick.do(self.on_calibrate_clicked)
        button_box.append(self.calibrate_btn)
        
        self.gesture_legend_btn = gui.Button('Show Gestures', width=120, height=40)
        self.gesture_legend_btn.onclick.do(self.on_show_gestures_clicked)
        button_box.append(self.gesture_legend_btn)
        
        self.test_btn = gui.Button('Test', width=120, height=40)
        self.test_btn.onclick.do(self.on_test_clicked)
        button_box.append(self.test_btn)
        
        main_container.append(button_box)

        # Legend/Calibration prompt box
        self.legend_box = gui.VBox(width='80%', style={'margin-top': '10px', 'margin-bottom': '10px', 'border': '1px solid #ccc', 'padding': '10px'})
        main_container.append(self.legend_box)

        return main_container

    # --- UI Callbacks (triggered by button clicks) ---
    def on_calibrate_clicked(self, widget):
        if DEBUG: print("[UI] Calibrate button clicked.")
        if self.calibrate_callback:
            self.calibrate_callback()

    def on_show_gestures_clicked(self, widget):
        if DEBUG: print("[UI] Show Gestures button clicked.")
        if self.show_gestures_callback:
            self.show_gestures_callback()

    def on_test_clicked(self, widget):
        if DEBUG: print("[UI] Test button clicked.")
        if self.test_mode_callback:
            self.test_mode_callback()

    def on_capture_point_clicked(self, widget):
        if DEBUG: print("[UI] Capture Point button clicked.")
        if self.capture_point_callback:
            self.capture_point_callback()

    # --- Methods for main.py to update UI ---
    def set_feedback(self, message):
        if self.feedback_label:
            self.feedback_label.set_text(message)

    def update_calibration_ui(self, prompt, calibration_finished=False):
        if self.legend_box:
            self.legend_box.empty()
            self.legend_box.append(gui.Label(prompt))
            if not calibration_finished:
                # Re-create the next_point_btn if it's not already there or needs update
                if not hasattr(self, 'next_point_btn') or self.next_point_btn not in self.legend_box.children:
                    self.next_point_btn = gui.Button('Capture Point', width=180, height=40)
                    self.next_point_btn.onclick.do(self.on_capture_point_clicked)
                
                self.legend_box.append(self.next_point_btn)
            else:
                # Remove the button if calibration is finished
                if hasattr(self, 'next_point_btn') and self.next_point_btn in self.legend_box.children:
                    self.legend_box.remove_child(self.next_point_btn)
        self.set_feedback(prompt)

    def show_gesture_legend(self):
        if self.legend_box:
            self.legend_box.empty()
            legend = gui.VBox(width='100%')
            legend.append(gui.Label('Predefined Gestures:', style={'font-weight': 'bold', 'font-size': '18px'}))
            legend.append(gui.Label('Left Click: Pinch index finger and thumb'))
            legend.append(gui.Label('Double Click: Two quick pinches'))
            legend.append(gui.Label('Right Click: Index and middle fingers up, others down, thumb out'))
            legend.append(gui.Label('Scroll Up: All fingers except thumb up'))
            legend.append(gui.Label('Scroll Down: All fingers except thumb down'))
            legend.append(gui.Label('Speech-to-Text: Only pinky up'))
            self.legend_box.append(legend)
        self.set_feedback('') 