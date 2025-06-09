# Module for visual feedback display

import cv2
import time

class VisualFeedbackManager:
    def __init__(self):
        # State variables for gesture/action feedback display
        # These are now managed here
        self.last_action_display_time = 0
        self.action_display_duration = 2 # Display action text for 2 seconds
        self.recognized_gesture_text = ""
        self.recognized_action_text = ""

    def update_action_feedback(self, gesture_text, action_text):
        """Updates the recognized gesture and action text for display."""
        self.recognized_gesture_text = gesture_text
        self.recognized_action_text = action_text
        self.last_action_display_time = time.time()

    def display_mode(self, image, img_height, is_calibration_mode, is_recording_gesture):
        """Displays the current operating mode on the image frame."""
        mode_text = "Mode: Normal"
        if is_calibration_mode:
            mode_text = "Mode: Calibration"
        elif is_recording_gesture:
            mode_text = "Mode: Recording Gesture"

        # Position mode text at the bottom left
        mode_text_pos = (10, img_height - 10)
        cv2.rectangle(image, (mode_text_pos[0], mode_text_pos[1] - 25), (mode_text_pos[0] + len(mode_text) * 15, mode_text_pos[1] + 5), (0, 0, 0), -1) # Black background
        cv2.putText(image, mode_text, mode_text_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)

    def display_gesture_action_feedback(self, image, img_width):
        """Displays the recognized gesture and action feedback on the image frame."""
        current_time_display = time.time()
        if current_time_display - self.last_action_display_time < self.action_display_duration:
            # Position gesture/action feedback near the top center
            feedback_pos_x = int(img_width / 2 - max(len(self.recognized_gesture_text), len(self.recognized_action_text)) * 15 / 2) # Estimate center based on longest text
            feedback_pos_y_gesture = 50
            feedback_pos_y_action = 80 # Position action text below gesture text

            if self.recognized_gesture_text:
                cv2.rectangle(image, (feedback_pos_x, feedback_pos_y_gesture - 25), (feedback_pos_x + len(self.recognized_gesture_text) * 20, feedback_pos_y_gesture + 5), (0, 0, 0), -1) # Black background
                cv2.putText(image, self.recognized_gesture_text, (feedback_pos_x, feedback_pos_y_gesture), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            if self.recognized_action_text:
                cv2.rectangle(image, (feedback_pos_x, feedback_pos_y_action - 25), (feedback_pos_x + len(self.recognized_action_text) * 20, feedback_pos_y_action + 5), (0, 0, 0), -1) # Black background
                cv2.putText(image, self.recognized_action_text, (feedback_pos_x, feedback_pos_y_action), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_AA)

        return image # Return the modified image frame

    # Additional methods for displaying other feedback (e.g., stability) can be added here 