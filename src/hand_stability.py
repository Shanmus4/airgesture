# Module for hand stability checking

import numpy as np
import mediapipe as mp

class HandStabilityManager:
    def __init__(self):
        # Gesture stability variables
        self.stability_buffer = []
        self.GESTURE_STABILITY_THRESHOLD = 0.01 # Maximum average landmark movement for stability (normalized coordinates)
        self.STABILITY_FRAME_COUNT = 5 # Number of frames to check for stability

    def is_hand_stable(self, current_landmarks):
        """Checks if the hand has been stable over the last few frames."""
        # Add current landmarks to buffer
        # Convert landmark objects to list of tuples for easier handling
        self.stability_buffer.append([(l.x, l.y, l.z) for l in current_landmarks.landmark])
        # Keep buffer size limited
        if len(self.stability_buffer) > self.STABILITY_FRAME_COUNT:
            self.stability_buffer.pop(0)

        if len(self.stability_buffer) < self.STABILITY_FRAME_COUNT:
            return False # Not enough frames to check stability

        # Compare current landmarks to the average of the buffer
        avg_buffer_landmarks = np.mean(np.array(self.stability_buffer), axis=0).flatten().tolist()
        current_landmarks_flat = np.array([(l.x, l.y, l.z) for l in current_landmarks.landmark]).flatten().tolist()

        distance = np.linalg.norm(np.array(current_landmarks_flat) - np.array(avg_buffer_landmarks))

        # print(f"Stability distance: {distance:.4f}")

        return distance < self.GESTURE_STABILITY_THRESHOLD

    # Method to clear the stability buffer, e.g., when changing modes
    def clear_buffer(self):
        self.stability_buffer = [] 