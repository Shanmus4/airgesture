# Module for calibration

import cv2
import numpy as np
import time
import mediapipe as mp

class CalibrationManager:
    def __init__(self, screen_width, screen_height):
        self.calibration_mode = False
        self.calibration_points = {}
        self.CALIBRATION_POINTS_ORDER = ['top-left', 'top-right', 'bottom-left', 'bottom-right']
        self.CALIBRATION_POINTS_COUNT = len(self.CALIBRATION_POINTS_ORDER)
        self.current_calibration_point_index = 0
        self.calibration_status_text = ""
        self.calibration_status_time = 0
        self.mapping_matrix = None # Use a different name to avoid conflict with module var M
        self.screen_width = screen_width
        self.screen_height = screen_height

    def get_screen_coordinates(self, hand_x, hand_y, img_width, img_height):
        """Maps hand coordinates to screen coordinates using calibration matrix if available."""
        if self.mapping_matrix is not None:
            transformed_point = np.array([[hand_x, hand_y]], dtype='float32').reshape(-1, 1, 2)
            screen_point = cv2.perspectiveTransform(transformed_point, self.mapping_matrix)
            mouse_x = int(screen_point[0][0][0])
            mouse_y = int(screen_point[0][0][1])
        else:
            # Use basic mapping if not calibrated
            mouse_x = int((hand_x / img_width) * self.screen_width)
            mouse_y = int((hand_y / img_height) * self.screen_height)
        # Clamp mouse coordinates to screen boundaries
        mouse_x = max(0, min(mouse_x, self.screen_width - 1))
        mouse_y = max(0, min(mouse_y, self.screen_height - 1))
        return mouse_x, mouse_y

    def start_calibration(self):
        """Initializes the calibration process."""
        self.calibration_mode = True
        self.calibration_points = {}
        self.current_calibration_point_index = 0
        self.mapping_matrix = None
        self.calibration_status_text = "Calibration Started. Move to top-left corner."
        self.calibration_status_time = time.time()
        if DEBUG:
            print("[Calibration] Calibration process started.")

    def capture_point(self, point_key, hand_x, hand_y):
        """Captures a calibration point from hand coordinates."""
        if not self.calibration_mode:
            if DEBUG:
                print("[Calibration] Not in calibration mode. Cannot capture point.")
            return

        if self.current_calibration_point_index < self.CALIBRATION_POINTS_COUNT:
            self.calibration_points[point_key] = (hand_x, hand_y)
            self.calibration_status_text = f'Captured {point_key}.'
            self.calibration_status_time = time.time()
            self.current_calibration_point_index += 1
            if DEBUG:
                print(f'[Calibration] Captured {point_key}: ({hand_x}, {hand_y}). Index: {self.current_calibration_point_index}')

            if self.current_calibration_point_index == self.CALIBRATION_POINTS_COUNT:
                self.end_calibration()
        else:
            if DEBUG:
                print("[Calibration] All points already captured.")

    def end_calibration(self):
        """Finalizes the calibration process by calculating the mapping matrix."""
        if len(self.calibration_points) == self.CALIBRATION_POINTS_COUNT:
            src_points = np.float32([
                self.calibration_points['top-left'],
                self.calibration_points['top-right'],
                self.calibration_points['bottom-left'],
                self.calibration_points['bottom-right']
            ])

            dst_points = np.float32([
                [0, 0],
                [self.screen_width, 0],
                [0, self.screen_height],
                [self.screen_width, self.screen_height]
            ])

            self.mapping_matrix = cv2.getPerspectiveTransform(src_points, dst_points)
            self.calibration_mode = False
            self.calibration_status_text = "Calibration Complete!"
            self.calibration_status_time = time.time()
            if DEBUG:
                print("Calibration complete. Mapping matrix calculated.")
        else:
            self.calibration_status_text = "Calibration Failed: Not enough points captured."
            self.calibration_status_time = time.time()
            if DEBUG:
                print("[Calibration] Calibration failed: Not enough points captured.")

    def process_key_press(self, key, results, image_shape, is_recording):
        """Processes key presses related to calibration mode.

        Args:
            key: The integer key code pressed.
            results: The mediapipe hands results object.
            image_shape: The shape of the current image frame (height, width, channels).
            is_recording: Boolean indicating if gesture recording is active.
        """
        img_height, img_width, _ = image_shape

        # --- Handle Calibration Mode Toggle (from keyboard, kept for debugging/alternative) ---
        if key == ord('c'): # Press 'c' to toggle calibration mode
            # Toggle calibration mode only if not currently recording
            if not is_recording:
                if not self.calibration_mode: # If currently not in calibration, start it
                    self.start_calibration()
                else: # If currently in calibration, exit it (without saving if not all points are captured)
                    self.calibration_mode = False
                    self.calibration_status_text = "Exiting Calibration Mode"
                    self.calibration_status_time = time.time()
                    print("Exiting calibration mode.")
            else:
                 print("Cannot enter calibration mode while recording.")
                 self.calibration_status_text = "Cannot Calibrate Now"
                 self.calibration_status_time = time.time()

        # --- Handle Capture Calibration Point (from keyboard, kept for debugging/alternative) ---
        elif self.calibration_mode and key == ord('s'): # Press 's' to capture calibration point
            if results.multi_hand_landmarks:
                hand_landmarks = results.multi_hand_landmarks[0]
                index_finger_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP]
                hand_x = int((1 - index_finger_tip.x) * img_width)
                hand_y = int(index_finger_tip.y * img_height)

                point_key = self.CALIBRATION_POINTS_ORDER[self.current_calibration_point_index]
                self.capture_point(point_key, hand_x, hand_y)
            else:
                self.calibration_status_text = "No hand detected. Try again."
                self.calibration_status_time = time.time()

        # --- Handle Reset Calibration ---
        elif key == ord('R'): # Press 'R' to reset calibration
             # Reset calibration regardless of other modes
            print("Resetting calibration.")
            self.mapping_matrix = None
            self.calibration_points = {}
            self.current_calibration_point_index = 0
            self.calibration_mode = False # Ensure calibration mode is off after reset
            self.calibration_status_text = "Calibration Reset!"
            self.calibration_status_time = time.time()

    # Methods for displaying calibration status/visuals will be added next

    def display_calibration_status(self, image, img_width, img_height):
        """Displays calibration prompts, status, and visual guides on the image frame."""
        current_time_display = time.time()

        # --- Handle Calibration Mode Display ---
        if self.calibration_mode:
            if self.current_calibration_point_index < self.CALIBRATION_POINTS_COUNT:
                point_name = self.CALIBRATION_POINTS_ORDER[self.current_calibration_point_index]
                # Position calibration prompt at the top left
                calibration_prompt_pos = (10, 30)
                cv2.rectangle(image, (calibration_prompt_pos[0], calibration_prompt_pos[1] - 25), (calibration_prompt_pos[0] + len(f'Calibrate: Place index finger at {point_name} and press \'s\'') * 15, calibration_prompt_pos[1] + 5), (0, 0, 0), -1) # Black background
                cv2.putText(image, f'Calibrate: Place index finger at {point_name} and press \'s\'', calibration_prompt_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2, cv2.LINE_AA)

            # Display calibration status messages for a short duration
            # Position calibration status below the prompt
            calibration_status_pos = (10, 70)
            if current_time_display - self.calibration_status_time < 2: # Display message for 2 seconds
                 cv2.rectangle(image, (calibration_status_pos[0], calibration_status_pos[1] - 25), (calibration_status_pos[0] + len(self.calibration_status_text) * 15, calibration_status_pos[1] + 5), (0, 0, 0), -1) # Black background
                 cv2.putText(image, self.calibration_status_text, calibration_status_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2, cv2.LINE_AA)


            # Draw circles for target calibration points for visual guidance
            padding = 50 # Padding from the edge for visual guidance
            target_points_visual = {
                'top-left': (padding, padding),
                'top-right': (img_width - padding, padding),
                'bottom-left': (padding, img_height - padding),
                'bottom-right': (img_width - padding, img_height - padding)
            }

            for i, point_name in enumerate(self.CALIBRATION_POINTS_ORDER):
                color = (0, 255, 0) if i == self.current_calibration_point_index else (0, 100, 0) # Highlight current point
                # Draw the circle on the image frame
                cv2.circle(image, target_points_visual[point_name], 10, color, -1);
                # Add text label near the target point
                cv2.putText(image, point_name.replace('-', ' ').title(), (target_points_visual[point_name][0] + 15, target_points_visual[point_name][1] + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)


            # Draw captured points
            for i, point_name in enumerate(self.CALIBRATION_POINTS_ORDER):
                if point_name in self.calibration_points:
                    cv2.circle(image, self.calibration_points[point_name], 8, (0, 0, 255), -1) # Red circle for captured points

            # Draw lines connecting captured points if there are enough points
            if len(self.calibration_points) >= 2:
                points = []
                # Get points in order to draw lines correctly
                for point_name in self.CALIBRATION_POINTS_ORDER:
                     if point_name in self.calibration_points:
                         points.append(self.calibration_points[point_name])

                # Draw lines between consecutive captured points
                for i in range(len(points) - 1):
                     cv2.line(image, points[i], points[i+1], (0, 255, 255), 2) # Yellow lines

                # Draw closing line if all 4 points are captured
                if len(points) == 4:
                     cv2.line(image, points[3], points[0], (0, 255, 255), 2) # Yellow closing line

        return image # Return the modified image frame 