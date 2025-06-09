# Module for custom gesture management 

import cv2
import time
import json
import os
import numpy as np
# Import necessary functions from gesture_recognition for processing/saving gestures
# from .gesture_recognition import process_captured_gesture, save_custom_gestures, custom_gestures # Will handle passing/accessing these later

class CustomGestureManager:
    def __init__(self):
        # Custom Gesture recording variables
        self.recording_gesture = False
        self.captured_gesture_landmarks = [] # Store raw landmarks during recording
        # self.current_gesture_to_save = None # Store processed features before naming/action - No longer needed with GUI
        self.current_gesture_name = None # Store name and action for saving with GUI
        self.current_gesture_action = None

        # Non-blocking input variables for saving custom gestures - No longer needed with GUI input
        # self.awaiting_gesture_name = False
        # self.awaiting_gesture_action = False
        # self.input_text = ""

        # Reference to the gesture recognizer instance (will be passed from main)
        self.gesture_recognizer = None

        # Custom Gesture storage
        self.CUSTOM_GESTURES_FILE = "custom_gestures.json"
        # Load gestures on startup
        self.custom_gestures = self.load_custom_gestures(self.CUSTOM_GESTURES_FILE)

    def set_gesture_recognizer(self, recognizer):
        self.gesture_recognizer = recognizer
        # After setting the recognizer, ensure it has access to the custom_gestures from this manager
        # The recognizer's custom_gestures reference should point to this manager's custom_gestures
        if self.gesture_recognizer:
            self.gesture_recognizer.custom_gestures = self.custom_gestures # Ensure recognizer uses this dictionary

    # Methods for handling recording triggered by GUI
    def start_recording_gesture(self, gesture_name, gesture_action):
        """Starts recording a new custom gesture with the given name and action."""
        if not self.recording_gesture: # Only start if not already recording
            self.recording_gesture = True
            self.captured_gesture_landmarks = [] # Clear previous data
            self.current_gesture_name = gesture_name # Store name and action
            self.current_gesture_action = gesture_action
            print(f"GUI triggered: Starting custom gesture recording for '{gesture_name}'.")
        else:
            print("Already recording a gesture.")

    def stop_recording_gesture(self):
        """Stops recording and processes/saves the captured gesture."""
        if self.recording_gesture and self.gesture_recognizer:
            self.recording_gesture = False
            print("GUI triggered: Stopping custom gesture recording.")

            # Process captured gesture data
            processed_gesture_features = self.gesture_recognizer.process_captured_gesture(self.captured_gesture_landmarks)

            if processed_gesture_features is not None and self.current_gesture_name and self.current_gesture_action:
                # Save the gesture using THIS manager's custom_gestures dictionary and save method
                self.custom_gestures[self.current_gesture_name] = {'features': processed_gesture_features, 'action': self.current_gesture_action}
                self.save_custom_gestures(self.custom_gestures, self.CUSTOM_GESTURES_FILE) # Use this manager's save method
                print(f"Custom gesture '{self.current_gesture_name}' saved successfully.")
            elif processed_gesture_features is None:
                print("No valid gesture data captured for saving.")
            else:
                print("Gesture name or action was not set. Cannot save gesture.")

            # Reset variables
            self.captured_gesture_landmarks = []
            self.current_gesture_name = None
            self.current_gesture_action = None

    # The following methods are for key-press based interaction and are not needed for the GUI flow.
    # They are commented out or removed to avoid conflict and confusion.

    # def process_recording_key_press(self, key, results, is_calibration_mode, is_awaiting_name, is_awaiting_action):
    #     """Processes the 'r' key press to toggle custom gesture recording."""
    #     pass # Handled by GUI buttons now

    # def process_input_key_press(self, key):
    #     """Processes key presses when awaiting gesture name or action."""
    #     pass # Handled by GUI input fields and buttons now

    def capture_landmarks_if_recording(self, hand_landmarks):
        """Captures hand landmarks if recording is active."""
        if self.recording_gesture:
            # Store normalized coordinates (x, y, z)
            self.captured_gesture_landmarks.append([(l.x, l.y, l.z) for l in hand_landmarks.landmark])

    # def display_input_status(self, image, img_height, img_width):
    #     """Displays the input prompt and current input text on the image frame."""
    #     pass # Handled by GUI now, though visual feedback on main screen could be added later if needed

    # Load custom gestures from file
    def load_custom_gestures(self, filename):
        try:
            # Check if file exists before trying to open
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    return json.load(f)
            else:
                return {}
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading custom gestures: {e}")
            return {}

    # Save custom gestures to file
    def save_custom_gestures(self, gestures, filename):
        try:
            with open(filename, 'w') as f:
                json.dump(gestures, f, indent=4)
        except IOError as e:
            print(f"Error saving custom gestures: {e}") 