# Module for gesture recognition

import math
import numpy as np
import mediapipe as mp
import time
import json
import os # Import os for file path handling

# Helper class for processing captured gesture data (Keep outside the class for now)
class MockHandLandmarks:
    def __init__(self, landmarks_data):
        self.landmark = []
        for l in landmarks_data:
            # Create a mock landmark object with x, y, z attributes
            class MockLandmark:
                def __init__(self, x, y, z):
                    self.x = x
                    self.y = y
                    self.z = z
            self.landmark.append(MockLandmark(l['x'], l['y'], l['z']))

class GestureRecognizer:
    def __init__(self):
        # Constants for gesture recognition
        self.CLICK_DISTANCE_THRESHOLD = 30 # Adjust based on hand size and camera distance
        self.SCROLL_THRESHOLD = 50 # Adjust sensitivity for scrolling
        # Angle thresholds for finger bending (adjust as needed)
        self.FINGER_BENT_THRESHOLD = 160 # Angle in degrees below which a finger is considered bent
        self.THUMB_BENT_THRESHOLD = 140 # Angle in degrees for thumb bending

        # State variables for double click
        self.last_click_time = 0
        self.DOUBLE_CLICK_INTERVAL = 0.5 # Maximum time between two clicks for a double click

        # Custom Gesture variables
        self.custom_gestures = {} # Dictionary to store custom gestures {gesture_name: {features: [...], action: "..."}}
        self.CUSTOM_GESTURES_FILE = "custom_gestures.json"
        self.CUSTOM_GESTURE_SIMILARITY_THRESHOLD = 0.1 # Adjust this threshold for custom gesture recognition (higher for features)

        # State variable to prevent repeated custom gesture action
        self.last_custom_action_time = 0
        self.CUSTOM_ACTION_COOLDOWN = 1.0 # Cooldown period in seconds after executing a custom action

        # Gesture stability variables
        self.last_gesture_landmarks = None
        self.GESTURE_STABILITY_THRESHOLD = 0.01 # Maximum average landmark movement for stability (normalized coordinates)
        self.STABILITY_FRAME_COUNT = 5 # Number of frames to check for stability
        self.stability_buffer = []

        # State variable for custom action feedback display
        self.last_action_display_time = 0
        self.action_display_duration = 2 # Display action text for 2 seconds
        self.recognized_gesture_text = ""
        self.recognized_action_text = ""

        # Load custom gestures on startup
        # self.custom_gestures = self.load_custom_gestures(self.CUSTOM_GESTURES_FILE) # This will be added in a later step

    # Function to load custom gestures from file
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

    # Function to save custom gestures to file
    def save_custom_gestures(self, gestures, filename):
        try:
            with open(filename, 'w') as f:
                json.dump(gestures, f, indent=4)
        except IOError as e:
            print(f"Error saving custom gestures: {e}")

    # Function to calculate distance between two landmarks
    def calculate_distance(self, landmark1, landmark2, img_width=None, img_height=None):
        # Use normalized coordinates if img_width/height are not provided
        x1 = landmark1.x
        y1 = landmark1.y
        x2 = landmark2.x
        y2 = landmark2.y

        if img_width is not None and img_height is not None:
            x1 *= img_width
            y1 *= img_height
            x2 *= img_width
            y2 *= img_height

        return math.hypot(x2 - x1, y2 - y1)

    # Function to calculate angle between three landmarks
    def calculate_angle(self, landmark1, landmark2, landmark3):
        # Calculate the angle between three landmarks (e.g., PIP-MCP-Wrist for finger bending)
        # Using normalized coordinates
        vec1 = np.array([landmark1.x - landmark2.x, landmark1.y - landmark2.y])
        vec2 = np.array([landmark3.x - landmark2.x, landmark3.y - landmark3.y]) # Corrected landmark3 y-coordinate

        dot_product = np.dot(vec1, vec2)
        norm_vec1 = np.linalg.norm(vec1)
        norm_vec2 = np.linalg.norm(vec2)

        if norm_vec1 == 0 or norm_vec2 == 0:
            return 180.0 # Return 180 degrees if vectors are zero length

        cosine_angle = dot_product / (norm_vec1 * norm_vec2)
        # Clamp the cosine value to the range [-1, 1] to avoid issues with floating point inaccuracies
        cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
        angle_in_radians = math.acos(cosine_angle)
        angle_in_degrees = math.degrees(angle_in_radians)

        return angle_in_degrees

    # Function to check if finger is up by angle
    def is_finger_up_by_angle(self, finger_tip, finger_pip, finger_mcp):
        # Check if the angle at the PIP joint indicates the finger is relatively straight (up)
        # Use MCP as the third point for angle calculation
        angle = self.calculate_angle(finger_tip, finger_pip, finger_mcp)
        return angle > self.FINGER_BENT_THRESHOLD

    # Function to check if thumb is up by angle
    def is_thumb_up_by_angle(self, thumb_tip, thumb_ip, thumb_cmc):
         # Check if the angle at the IP joint indicates the thumb is relatively straight (up)
        angle = self.calculate_angle(thumb_tip, thumb_ip, thumb_cmc)
        return angle > self.THUMB_BENT_THRESHOLD

    # Function to extract gesture features
    def extract_gesture_features(self, hand_landmarks):
        """Extracts a feature vector from hand landmarks for gesture recognition.

        Features include distances between key landmarks and key angles.
        Uses normalized coordinates for scale invariance.
        """
        features = []

        # Example Feature: Distances from Wrist (0) to all finger tips (4, 8, 12, 16, 20)
        wrist = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.WRIST]
        for finger_tip_id in [mp.solutions.hands.HandLandmark.THUMB_TIP, mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP,
                              mp.solutions.hands.HandLandmark.MIDDLE_FINGER_TIP, mp.solutions.hands.HandLandmark.RING_FINGER_TIP,
                              mp.solutions.hands.HandLandmark.PINKY_TIP]:
            features.append(self.calculate_distance(wrist, hand_landmarks.landmark[finger_tip_id]))

        # Example Feature: Distances between consecutive finger tips
        finger_tips_ids = [mp.solutions.hands.HandLandmark.THUMB_TIP, mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP,
                           mp.solutions.hands.HandLandmark.MIDDLE_FINGER_TIP, mp.solutions.hands.HandLandmark.RING_FINGER_TIP,
                           mp.solutions.hands.HandLandmark.PINKY_TIP]
        for i in range(len(finger_tips_ids) - 1):
            features.append(self.calculate_distance(hand_landmarks.landmark[finger_tips_ids[i]],
                                               hand_landmarks.landmark[finger_tips_ids[i+1]]))

        # Example Feature: Angles at PIP joints for fingers (excluding thumb)
        pip_mcp_ids = [(mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP, mp.solutions.hands.HandLandmark.INDEX_FINGER_PIP, mp.solutions.hands.HandLandmark.INDEX_FINGER_MCP),
                       (mp.solutions.hands.HandLandmark.MIDDLE_FINGER_TIP, mp.solutions.hands.HandLandmark.MIDDLE_FINGER_PIP, mp.solutions.hands.HandLandmark.MIDDLE_FINGER_MCP),
                       (mp.solutions.hands.HandLandmark.RING_FINGER_TIP, mp.solutions.hands.HandLandmark.RING_FINGER_PIP, mp.solutions.hands.HandLandmark.RING_FINGER_MCP),
                       (mp.solutions.hands.HandLandmark.PINKY_TIP, mp.solutions.hands.HandLandmark.PINKY_PIP, mp.solutions.hands.HandLandmark.PINKY_MCP)]

        for tip_id, pip_id, mcp_id in pip_mcp_ids:
             features.append(self.calculate_angle(hand_landmarks.landmark[tip_id],
                                             hand_landmarks.landmark[pip_id],
                                             hand_landmarks.landmark[mcp_id]))

        # Add more features as needed for better discrimination
        # e.g., angles at MCP joints, distances between other key points

        return np.array(features)

    # Function to check if hand is stable
    def is_hand_stable(self, current_landmarks):
        if len(self.stability_buffer) < self.STABILITY_FRAME_COUNT:
            # Add current landmarks to buffer
            # Convert landmark objects to list of tuples for easier handling
            self.stability_buffer.append([(l.x, l.y, l.z) for l in current_landmarks.landmark])
            return False # Not enough frames to check stability

        # Compare current landmarks to the average of the buffer
        avg_buffer_landmarks = np.mean(np.array(self.stability_buffer), axis=0).flatten().tolist()
        current_landmarks_flat = np.array([(l.x, l.y, l.z) for l in current_landmarks.landmark]).flatten().tolist()

        distance = np.linalg.norm(np.array(current_landmarks_flat) - np.array(avg_buffer_landmarks))

        # print(f"Stability distance: {distance:.4f}")

        # Remove the oldest frame from the buffer and add the current one
        self.stability_buffer.pop(0)
        self.stability_buffer.append([(l.x, l.y, l.z) for l in current_landmarks.landmark])

        return distance < self.GESTURE_STABILITY_THRESHOLD

    # Function to process captured gesture landmarks
    def process_captured_gesture(self, landmarks_list):
        """Processes captured raw landmark data to extract a representative feature vector.

        Args:
            landmarks_list: A list of hand landmarks captured over several frames.

        Returns:
            A flattened numpy array of gesture features, or None if no data.
        """
        if not landmarks_list:
            return None

        # Average the raw landmark positions across the captured frames first
        # This helps to smooth out minor fluctuations during recording
        avg_raw_landmarks = []
        # Assuming all frames have the same number of landmarks, get from the first frame
        num_landmarks = len(landmarks_list[0])
        for i in range(num_landmarks):
            avg_raw_landmarks.append({'x': np.mean([frame[i][0] for frame in landmarks_list]),
                                      'y': np.mean([frame[i][1] for frame in landmarks_list]),
                                      'z': np.mean([frame[i][2] for frame in landmarks_list])})

        # Convert the averaged raw landmarks back to a format suitable for feature extraction
        avg_hand_landmarks = MockHandLandmarks(avg_raw_landmarks)

        # Extract features from the averaged hand landmarks
        gesture_features = self.extract_gesture_features(avg_hand_landmarks)

        # Flatten the feature vector for storage/comparison
        return gesture_features.flatten().tolist()

    # Implement a function to recognize custom gestures
    def recognize_custom_gesture(self, current_hand_landmarks):
        """Compares current hand features to stored custom gestures features.

        Args:
            current_hand_landmarks: The current hand landmark object.

        Returns:
            The action string associated with the recognized gesture, or None if no match.
        """
        min_distance = float('inf')
        best_match_action = None

        # Extract features from the current hand landmarks
        current_features = self.extract_gesture_features(current_hand_landmarks)

        for gesture_name, gesture_data in self.custom_gestures.items():
            stored_features = np.array(gesture_data['features'])

            # Calculate Euclidean distance between current and stored feature vectors
            distance = np.linalg.norm(current_features - stored_features)

            if distance < min_distance:
                 min_distance = distance
                 best_match_action = gesture_data['action']
                 # print(f"Potential match: {gesture_name} with feature distance {distance:.4f}")

        if min_distance < self.CUSTOM_GESTURE_SIMILARITY_THRESHOLD:
            # print(f"Matched gesture with feature distance {min_distance:.4f}")
            # Update state for displaying recognized action
            self.recognized_gesture_text = f"Recognized: {gesture_name}"
            self.recognized_action_text = f"Action: {best_match_action}"
            self.last_action_display_time = time.time()

            return best_match_action

        return None

    # Method to check for predefined gestures
    def recognize_predefined_gesture(self, hand_landmarks, hand_handedness, img_width, img_height):
        recognized_gesture = None
        action_to_perform = None

        current_time = time.time()

        # Get landmark coordinates
        index_finger_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP]
        thumb_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_TIP]
        middle_finger_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_TIP]
        ring_finger_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.RING_FINGER_TIP]
        pinky_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_TIP]

        index_finger_pip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_PIP]
        middle_finger_pip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_PIP]
        ring_finger_pip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.RING_FINGER_PIP]
        pinky_pip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_PIP]

        thumb_ip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_IP]
        thumb_cmc = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_CMC]


        # Convert to pixel coordinates for distance calculations where necessary
        index_tip_x, index_tip_y = int(index_finger_tip.x * img_width), int(index_finger_tip.y * img_height)
        thumb_tip_x, thumb_tip_y = int(thumb_tip.x * img_width), int(thumb_tip.y * img_height)

        # Check for predefined gestures

        # Left Click: Index finger and thumb tips are close
        click_distance = self.calculate_distance(index_finger_tip, thumb_tip, img_width, img_height)
        if click_distance < self.CLICK_DISTANCE_THRESHOLD:
            # Check for double click
            if current_time - self.last_click_time < self.DOUBLE_CLICK_INTERVAL:
                recognized_gesture = "Double Click"
                action_to_perform = "double_click"
                self.last_click_time = 0 # Reset last click time after a double click
                print("Double Click")
            else:
                recognized_gesture = "Left Click"
                action_to_perform = "left_click"
                self.last_click_time = current_time
                print("Left Click")

        # Scroll Up: All fingers except thumb are up and hand moves up (Y coordinate decreases significantly between frames)
        # Need to track hand movement for scrolling - this requires state/history, maybe in the main loop or passed in
        # For now, let's implement a static scroll gesture: all fingers straight up, thumb out.
        elif (self.is_finger_up_by_angle(index_finger_tip, index_finger_pip, hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_MCP]) and
              self.is_finger_up_by_angle(middle_finger_tip, middle_finger_pip, hand_landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_MCP]) and
              self.is_finger_up_by_angle(ring_finger_tip, ring_finger_pip, hand_landmarks.landmark[mp.solutions.hands.HandLandmark.RING_FINGER_MCP]) and
              self.is_finger_up_by_angle(pinky_tip, pinky_pip, hand_landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_MCP]) and
              not self.is_thumb_up_by_angle(thumb_tip, thumb_ip, thumb_cmc)):
             recognized_gesture = "Scroll Up"
             action_to_perform = "scroll_up"
             print("Scroll Up")


        # Scroll Down: All fingers except thumb are down.
        # Implement a static scroll down gesture: all fingers bent, thumb out.
        elif (not self.is_finger_up_by_angle(index_finger_tip, index_finger_pip, hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_MCP]) and
              not self.is_finger_up_by_angle(middle_finger_tip, middle_finger_pip, hand_landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_MCP]) and
              not self.is_finger_up_by_angle(ring_finger_tip, ring_finger_pip, hand_landmarks.landmark[mp.solutions.hands.HandLandmark.RING_FINGER_MCP]) and
              not self.is_finger_up_by_angle(pinky_tip, pinky_pip, hand_landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_MCP]) and
              not self.is_thumb_up_by_angle(thumb_tip, thumb_ip, thumb_cmc)):
             recognized_gesture = "Scroll Down"
             action_to_perform = "scroll_down"
             print("Scroll Down")

        # Right Click: Index, Middle, Ring, Pinky fingers up, Thumb out. (Open Hand)
        # This is currently similar to Scroll Up. Need a better distinction.
        # Let's redefine Right Click as: Index and Middle fingers up, others down, thumb out.
        elif (self.is_finger_up_by_angle(index_finger_tip, index_finger_pip, hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_MCP]) and
              self.is_finger_up_by_angle(middle_finger_tip, middle_finger_pip, hand_landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_MCP]) and
              not self.is_finger_up_by_angle(ring_finger_tip, ring_finger_pip, hand_landmarks.landmark[mp.solutions.hands.HandLandmark.RING_FINGER_MCP]) and
              not self.is_finger_up_by_angle(pinky_tip, pinky_pip, hand_landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_MCP]) and
              not self.is_thumb_up_by_angle(thumb_tip, thumb_ip, thumb_cmc)):
             recognized_gesture = "Right Click"
             action_to_perform = "right_click"
             print("Right Click")

        # Speech-to-Text (Win+H): Pinky finger up, others down, thumb out.
        elif (not self.is_finger_up_by_angle(index_finger_tip, index_finger_pip, hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_MCP]) and
              not self.is_finger_up_by_angle(middle_finger_tip, middle_finger_pip, hand_landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_MCP]) and
              not self.is_finger_up_by_angle(ring_finger_tip, ring_finger_pip, hand_landmarks.landmark[mp.solutions.hands.HandLandmark.RING_FINGER_MCP]) and
              self.is_finger_up_by_angle(pinky_tip, pinky_pip, hand_landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_MCP]) and
              not self.is_thumb_up_by_angle(thumb_tip, thumb_ip, thumb_cmc)):
             recognized_gesture = "Speech-to-Text"
             action_to_perform = "speech_to_text"
             print("Speech-to-Text")

        # Update state for displaying recognized gesture (predefined)
        if recognized_gesture:
            self.recognized_gesture_text = f"Recognized: {recognized_gesture}"
            # For predefined gestures, the action is directly related
            self.recognized_action_text = f"Action: {action_to_perform}"
            self.last_action_display_time = time.time()

        return recognized_gesture, action_to_perform