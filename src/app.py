# Main application class

import cv2
import mediapipe as mp
import time
import threading
import pyautogui

# Import all the modularized components
from .hand_tracking import HandTracker
from .os_interaction import OSInteractor
from .calibration import CalibrationManager
from .custom_gestures import CustomGestureManager
from .visual_feedback import VisualFeedbackManager
from .hand_stability import HandStabilityManager
from .gesture_recognition import GestureRecognizer
from .gesture_gui import GestureManagerApp
from remi import start as start_remi_app

class AirGestureApp:
    def __init__(self):
        # Initialize camera
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Could not open camera.")
            exit()

        # Get screen size for OS interactions
        # Initialize OSInteractor first to get screen size
        self.os_interactor = OSInteractor()

        # Initialize managers
        self.hand_tracker = HandTracker()
        self.calibration_manager = CalibrationManager(self.os_interactor.screen_width, self.os_interactor.screen_height)
        # Initialize VisualFeedbackManager first as GestureRecognizer depends on it
        self.visual_feedback_manager = VisualFeedbackManager()
        # Initialize CustomGestureManager first as GestureRecognizer depends on it and GestureManagerApp will need it
        self.custom_gesture_manager = CustomGestureManager()

        self.hand_stability_manager = HandStabilityManager()

        # Initialize GestureRecognizer, passing dependencies
        self.gesture_recognizer = GestureRecognizer(
            self.os_interactor,
            self.calibration_manager,
            # self.custom_gesture_manager, # Temporarily disable custom gestures
            self.visual_feedback_manager,
            self.hand_stability_manager
        )

        # Set gesture recognizer instance in custom gesture manager
        # self.custom_gesture_manager.set_gesture_recognizer(self.gesture_recognizer) # Temporarily disable custom gestures

        self.is_running = True
        self.current_mode = 'normal' # 'normal', 'calibration', 'recording'
        self.recording_gesture_name = None

        # Start the Remi web server in a separate thread
        # Pass the custom_gesture_manager instance to the GUI app
        # Correctly passing args and kwargs to start_remi_app
        # Pass custom_gesture_manager within the userdata tuple
        # self.remi_thread = threading.Thread(target=start_remi_app, # Temporarily disable custom gestures GUI
        #                                     args=(GestureManagerApp,),
        #                                     kwargs={
        #                                         'port': 8081,
        #                                         'address': '127.0.0.1',
        #                                         'debug': True,
        #                                         'userdata': (self.custom_gesture_manager,)
        #                                     })
        # self.remi_thread.daemon = True # Allow the main program to exit even if the thread is running
        # self.remi_thread.start() # Temporarily disable custom gestures GUI

    def start_gesture_manager_gui(self):
        # Start the Remi app. The start function blocks, so it needs a separate thread.
        # We set the address to 127.0.0.1 so it's only accessible locally.
        # This method is no longer used since we are starting the thread directly in __init__
        pass

    def run(self):
        try:
            while self.cap.isOpened() and self.is_running:
                success, image = self.cap.read()
                if not success:
                    print("Ignoring empty camera frame.")
                    continue

                # Flip the image horizontally for a later selfie-view display
                image = cv2.flip(image, 1)

                # Convert the image to RGB
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                # Process the image with MediaPipe Hands
                results, image_rgb = self.hand_tracker.process_frame(image_rgb)

                img_height, img_width, _ = image.shape

                # --- Display Current Mode ---
                # self.visual_feedback_manager.display_mode(image, img_height, self.calibration_manager.calibration_mode, self.custom_gesture_manager.recording_gesture)
                self.visual_feedback_manager.display_mode(image, img_height, self.calibration_manager.calibration_mode, False) # Pass False for recording_gesture

                # --- Handle Non-blocking Input Display ---
                # Assumes custom_gesture_manager handles drawing input text on image
                # This is now handled by the GUI, so we remove this call
                # self.custom_gesture_manager.display_input_status(image, img_height, img_width)

                # --- Display Gesture/Action Feedback (Temporary) ---
                image = self.visual_feedback_manager.display_gesture_action_feedback(image, img_width)

                # --- Handle Calibration Mode Display ---
                image = self.calibration_manager.display_calibration_status(image, img_width, img_height)

                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        # Get the index finger tip landmark (landmark 8)
                        index_finger_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP]

                        # Calculate the pixel coordinates of the index finger tip
                        # Need to invert the x-axis because the image is flipped
                        hand_x = int((1 - index_finger_tip.x) * img_width)
                        hand_y = int(index_finger_tip.y * img_height)

                        # Use custom_gesture_manager to capture landmarks if recording
                        # self.custom_gesture_manager.capture_landmarks_if_recording(hand_landmarks) # Temporarily disable custom gestures

                        # Check for hand stability (only if not in calibration/recording/input mode)
                        hand_is_stable = False
                        # if not self.calibration_manager.calibration_mode and not self.custom_gesture_manager.recording_gesture and not self.custom_gesture_manager.awaiting_gesture_name and not self.custom_gesture_manager.awaiting_gesture_action:
                        if not self.calibration_manager.calibration_mode:
                             hand_is_stable = self.hand_stability_manager.is_hand_stable(hand_landmarks)
                             if hand_is_stable:
                                 cv2.putText(image, 'Stable', (10, img_height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)


                        # --- Custom Gesture Recording Mode ---
                        # Only record if not in calibration or awaiting input
                        # if self.custom_gesture_manager.recording_gesture and not self.calibration_manager.calibration_mode and not self.custom_gesture_manager.awaiting_gesture_name and not self.custom_gesture_manager.awaiting_gesture_action:
                        #     cv2.putText(image, 'Recording Gesture...', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

                        # --- Normal Operation (Cursor Movement and Predefined/Custom Gestures) ---
                        # Only perform normal operations if not in calibration, recording, or awaiting input
                        # elif not self.calibration_manager.calibration_mode and not self.custom_gesture_manager.recording_gesture and not self.custom_gesture_manager.awaiting_gesture_name and not self.custom_gesture_manager.awaiting_gesture_action:
                        elif not self.calibration_manager.calibration_mode:
                            # --- Cursor Movement (using calibration if available) ---
                            mouse_x, mouse_y = self.calibration_manager.get_screen_coordinates(hand_x, hand_y, img_width, img_height)
                            self.os_interactor.move_to(mouse_x, mouse_y)

                            # Use GestureRecognizer to recognize gestures and perform actions
                            # Pass relevant state and managers
                            self.gesture_recognizer.recognize_gestures_and_perform_actions(hand_landmarks, img_width, img_height, hand_is_stable)


                    # Draw landmarks and connections
                    self.hand_tracker.draw_landmarks(image, results.multi_hand_landmarks)

                # Display the image
                cv2.imshow('Hand Tracking and Cursor Control', image)

                # Check for key presses
                key = cv2.waitKey(5) & 0xFF
                if key == ord('q'):
                    print("'q' key pressed. Attempting to exit.")
                    self.is_running = False # Set flag to stop the loop
                    break

                # --- Handle Calibration Mode Key Presses ---
                # Pass relevant state to calibration_manager, including custom gesture manager states
                # self.calibration_manager.process_key_press(key, results, image.shape, self.custom_gesture_manager.recording_gesture) # Temporarily disable custom gestures
                self.calibration_manager.process_key_press(key, results, image.shape, False) # Pass False for recording_gesture
                # Clear stability buffer when entering/exiting calibration mode
                if key == ord('c'):
                    self.hand_stability_manager.clear_buffer()

                # --- Handle Custom Gesture Recording and Input Key Presses ---
                # Process custom gesture recording key press and input key press using the manager
                # Pass the gesture_recognizer instance and custom_gestures dictionary to the process_recording_key_press method
                # The process_input_key_press method returns whether input is still awaited
                # These are now handled by the GUI, so we remove these calls
                # self.custom_gesture_manager.process_recording_key_press(key, results, self.calibration_manager.calibration_mode, self.custom_gesture_manager.awaiting_gesture_name, self.custom_gesture_manager.awaiting_gesture_action)
                # is_input_awaited = self.custom_gesture_manager.process_input_key_press(key) # This return value is not currently used in the loop, can remove if unnecessary
                # Clear stability buffer when toggling recording mode
                # if key == ord('r'): # Temporarily disable custom gestures
                #     self.hand_stability_manager.clear_buffer()

        except KeyboardInterrupt:
            print("\nKeyboardInterrupt received. Exiting application...")
            self.is_running = False # Ensure the loop terminates
        finally:
            print("Entering finally block: Releasing resources.")
            # Release the video capture object and close all OpenCV windows
            self.cap.release()
            cv2.destroyAllWindows()
            print("Application run loop finished.")

    def stop(self):
        self.is_running = False
        # We might need a way to stop the Remi thread gracefully here if it's not a daemon thread
        # For now, with daemon=True, it will exit when the main thread exits.

if __name__ == "__main__":
    app = AirGestureApp()
    app.run() 