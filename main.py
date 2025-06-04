import cv2
import mediapipe as mp
import pyautogui
import math
import time
import numpy as np
import json
import os

# Import HandTracker from the new module
from src.hand_tracking import HandTracker
# Import gesture recognition components from the new module
from src.gesture_recognition import (
    CLICK_DISTANCE_THRESHOLD,
    SCROLL_THRESHOLD,
    FINGER_BENT_THRESHOLD,
    THUMB_BENT_THRESHOLD,
    last_click_time, # Need to manage state in main or pass it
    DOUBLE_CLICK_INTERVAL,
    custom_gestures, # Need to manage state in main or pass it
    CUSTOM_GESTURES_FILE,
    CUSTOM_GESTURE_SIMILARITY_THRESHOLD,
    last_custom_action_time, # Need to manage state in main or pass it
    CUSTOM_ACTION_COOLDOWN,
    awaiting_gesture_name, # Need to manage state in main or pass it
    awaiting_gesture_action, # Need to manage state in main or pass it
    input_text, # Need to manage state in main or pass it
    current_gesture_to_save, # Need to manage state in main or pass it
    last_gesture_landmarks, # Need to manage state in main or pass it
    GESTURE_STABILITY_THRESHOLD,
    STABILITY_FRAME_COUNT,
    stability_buffer, # Need to manage state in main or pass it
    last_action_display_time, # Need to manage state in main or pass it
    action_display_duration,
    recognized_gesture_text, # Need to manage state in main or pass it
    recognized_action_text, # Need to manage state in main or pass it
    load_custom_gestures,
    save_custom_gestures,
    calculate_distance,
    calculate_angle,
    is_finger_up_by_angle,
    is_thumb_up_by_angle,
    extract_gesture_features,
    is_hand_stable,
    process_captured_gesture,
    recognize_custom_gesture
)

# Initialize MediaPipe Hands and Drawing Utils
# Moved to HandTracker class
# mp_hands = mp.solutions.hands
# hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
# mp_drawing = mp.solutions.drawing_utils

# Initialize HandTracker
hand_tracker = HandTracker()

# Get screen size
screen_width, screen_height = pyautogui.size()

# Initialize video capture
cap = cv2.VideoCapture(0) # Use camera 0

# Variables for gesture recognition
# Moved to src/gesture_recognition.py
# CLICK_DISTANCE_THRESHOLD = 30 # Adjust based on hand size and camera distance
# SCROLL_THRESHOLD = 50 # Adjust sensitivity for scrolling
# # Angle thresholds for finger bending (adjust as needed)
# FINGER_BENT_THRESHOLD = 160 # Angle in degrees below which a finger is considered bent
# THUMB_BENT_THRESHOLD = 140 # Angle in degrees for thumb bending

# State variables for double click
# Moved to src/gesture_recognition.py
# last_click_time = 0
# DOUBLE_CLICK_INTERVAL = 0.5 # Maximum time between two clicks for a double click

# Calibration variables
calibration_mode = False
calibration_points = {}
CALIBRATION_POINTS_ORDER = ['top-left', 'top-right', 'bottom-left', 'bottom-right']
CALIBRATION_POINTS_COUNT = len(CALIBRATION_POINTS_ORDER)
current_calibration_point_index = 0
calibration_status_text = ""
calibration_status_time = 0

# Mapping transformation matrix (initialized as None)
M = None

# Custom Gesture variables
# Moved to src/gesture_recognition.py
# recording_gesture = False
# captured_gesture_landmarks = [] # Store raw landmarks during recording
# custom_gestures = {} # Dictionary to store custom gestures {gesture_name: {features: [...], action: "..."}}
# CUSTOM_GESTURES_FILE = "custom_gestures.json"
# CUSTOM_GESTURE_SIMILARITY_THRESHOLD = 0.1 # Adjust this threshold for custom gesture recognition (higher for features)

# State variable to prevent repeated custom gesture action
# Moved to src/gesture_recognition.py
# last_custom_action_time = 0
# CUSTOM_ACTION_COOLDOWN = 1.0 # Cooldown period in seconds after executing a custom action

# Non-blocking input variables
awaiting_gesture_name = False
awaiting_gesture_action = False
input_text = ""
current_gesture_to_save = None # Store processed features

# Gesture stability variables
# Moved to src/gesture_recognition.py
# last_gesture_landmarks = None
# GESTURE_STABILITY_THRESHOLD = 0.01 # Maximum average landmark movement for stability (normalized coordinates)
# STABILITY_FRAME_COUNT = 5 # Number of frames to check for stability
# stability_buffer = []

# State variable for custom action feedback display
# Moved to src/gesture_recognition.py
# last_action_display_time = 0
# action_display_duration = 2 # Display action text for 2 seconds
# recognized_gesture_text = ""
# recognized_action_text = ""

# Function to load custom gestures from file
# Moved to src/gesture_recognition.py
# def load_custom_gestures(filename):
#     try:
#         with open(filename, 'r') as f:
#             return json.load(f)
#     except FileNotFoundError:
#         return {}

# Function to save custom gestures to file
# Moved to src/gesture_recognition.py
# def save_custom_gestures(gestures, filename):
#     with open(filename, 'w') as f:
#         json.dump(gestures, f, indent=4)

# Load custom gestures on startup
# custom_gestures = load_custom_gestures(CUSTOM_GESTURES_FILE)

# Function to calculate distance between two landmarks
# Moved to src/gesture_recognition.py
# def calculate_distance(landmark1, landmark2, img_width=None, img_height=None):
#     # Use normalized coordinates if img_width/height are not provided
#     x1 = landmark1.x
#     y1 = landmark1.y
#     x2 = landmark2.x
#     y2 = landmark2.y

# def calculate_angle(landmark1, landmark2, landmark3):
#     # Calculate the angle between three landmarks (e.g., PIP-MCP-Wrist for finger bending)
#     # Using normalized coordinates
#     vec1 = np.array([landmark1.x - landmark2.x, landmark1.y - landmark2.y])
#     vec2 = np.array([landmark3.x - landmark2.x, landmark3.y - landmark2.y])

# def is_finger_up_by_angle(finger_tip, finger_pip, finger_mcp):
#     # Check if the angle at the PIP joint indicates the finger is relatively straight (up)
#     # Use MCP as the third point for angle calculation
#     angle = calculate_angle(finger_tip, finger_pip, finger_mcp)
#     return angle > FINGER_BENT_THRESHOLD

# def is_thumb_up_by_angle(thumb_tip, thumb_ip, thumb_cmc):
#      # Check if the angle at the IP joint indicates the thumb is relatively straight (up)
#     angle = calculate_angle(thumb_tip, thumb_ip, thumb_cmc)
#     return angle > THUMB_BENT_THRESHOLD

# def extract_gesture_features(hand_landmarks):
#     """Extracts a feature vector from hand landmarks for gesture recognition.

#     Features include distances between key landmarks and key angles.
#     Uses normalized coordinates for scale invariance.
#     """
#     features = []

# def calculate_distance(landmark1, landmark2, img_width=None, img_height=None):
#     # Use normalized coordinates if img_width/height are not provided
#     x1 = landmark1.x
#     y1 = landmark1.y
#     x2 = landmark2.x
#     y2 = landmark2.y

def calculate_distance(landmark1, landmark2, img_width=None, img_height=None):
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

def calculate_angle(landmark1, landmark2, landmark3):
    # Calculate the angle between three landmarks (e.g., PIP-MCP-Wrist for finger bending)
    # Using normalized coordinates
    vec1 = np.array([landmark1.x - landmark2.x, landmark1.y - landmark2.y])
    vec2 = np.array([landmark3.x - landmark2.x, landmark3.y - landmark2.y])

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

def is_finger_up_by_angle(finger_tip, finger_pip, finger_mcp):
    # Check if the angle at the PIP joint indicates the finger is relatively straight (up)
    # Use MCP as the third point for angle calculation
    angle = calculate_angle(finger_tip, finger_pip, finger_mcp)
    return angle > FINGER_BENT_THRESHOLD

def is_thumb_up_by_angle(thumb_tip, thumb_ip, thumb_cmc):
     # Check if the angle at the IP joint indicates the thumb is relatively straight (up)
    angle = calculate_angle(thumb_tip, thumb_ip, thumb_cmc)
    return angle > THUMB_BENT_THRESHOLD

def extract_gesture_features(hand_landmarks):
    """Extracts a feature vector from hand landmarks for gesture recognition.

    Features include distances between key landmarks and key angles.
    Uses normalized coordinates for scale invariance.
    """
    features = []

    # Example Feature: Distances from Wrist (0) to all finger tips (4, 8, 12, 16, 20)
    wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
    for finger_tip_id in [mp_hands.HandLandmark.THUMB_TIP, mp_hands.HandLandmark.INDEX_FINGER_TIP,
                          mp_hands.HandLandmark.MIDDLE_FINGER_TIP, mp_hands.HandLandmark.RING_FINGER_TIP,
                          mp_hands.HandLandmark.PINKY_TIP]:
        features.append(calculate_distance(wrist, hand_landmarks.landmark[finger_tip_id]))

    # Example Feature: Distances between consecutive finger tips
    finger_tips_ids = [mp_hands.HandLandmark.THUMB_TIP, mp_hands.HandLandmark.INDEX_FINGER_TIP,
                       mp_hands.HandLandmark.MIDDLE_FINGER_TIP, mp_hands.HandLandmark.RING_FINGER_TIP,
                       mp_hands.HandLandmark.PINKY_TIP]
    for i in range(len(finger_tips_ids) - 1):
        features.append(calculate_distance(hand_landmarks.landmark[finger_tips_ids[i]],
                                           hand_landmarks.landmark[finger_tips_ids[i+1]]))

    # Example Feature: Angles at PIP joints for fingers (excluding thumb)
    pip_mcp_ids = [(mp_hands.HandLandmark.INDEX_FINGER_TIP, mp_hands.HandLandmark.INDEX_FINGER_PIP, mp_hands.HandLandmark.INDEX_FINGER_MCP),
                   (mp_hands.HandLandmark.MIDDLE_FINGER_TIP, mp_hands.HandLandmark.MIDDLE_FINGER_PIP, mp_hands.HandLandmark.MIDDLE_FINGER_MCP),
                   (mp_hands.HandLandmark.RING_FINGER_TIP, mp_hands.HandLandmark.RING_FINGER_PIP, mp_hands.HandLandmark.RING_FINGER_MCP),
                   (mp_hands.HandLandmark.PINKY_TIP, mp_hands.HandLandmark.PINKY_PIP, mp_hands.HandLandmark.PINKY_MCP)]

    for tip_id, pip_id, mcp_id in pip_mcp_ids:
         features.append(calculate_angle(hand_landmarks.landmark[tip_id],
                                         hand_landmarks.landmark[pip_id],
                                         hand_landmarks.landmark[mcp_id]))

    # Add more features as needed for better discrimination
    # e.g., angles at MCP joints, distances between other key points

    return np.array(features)


def is_hand_stable(current_landmarks, stability_buffer, threshold):
    if len(stability_buffer) < STABILITY_FRAME_COUNT:
        return False # Not enough frames to check stability

    # Compare current landmarks to the average of the buffer
    avg_buffer_landmarks = np.mean(np.array([[(l.x, l.y, l.z) for l in frame] for frame in stability_buffer]), axis=0).flatten().tolist()
    current_landmarks_flat = np.array([(l.x, l.y, l.z) for l in current_landmarks.landmark]).flatten().tolist()

    distance = np.linalg.norm(np.array(current_landmarks_flat) - np.array(avg_buffer_landmarks))

    # print(f"Stability distance: {distance:.4f}")

    return distance < threshold


def get_screen_coordinates(hand_x, hand_y, img_width, img_height, screen_width, screen_height, M):
    if M is not None:
        # Use the perspective transformation matrix if calibrated
        transformed_point = np.array([[hand_x, hand_y]], dtype='float32').reshape(-1, 1, 2)
        screen_point = cv2.perspectiveTransform(transformed_point, M)
        mouse_x = int(screen_point[0][0][0])
        mouse_y = int(screen_point[0][0][1])
    else:
        # Use basic mapping if not calibrated
        mouse_x = int((hand_x / img_width) * screen_width)
        mouse_y = int((hand_y / img_height) * screen_height)
    # Clamp mouse coordinates to screen boundaries
    mouse_x = max(0, min(mouse_x, screen_width - 1))
    mouse_y = max(0, min(mouse_y, screen_height - 1))
    return mouse_x, mouse_y

def process_captured_gesture(landmarks_list):
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
    num_landmarks = len(landmarks_list[0]) # Assuming all frames have the same number of landmarks
    for i in range(num_landmarks):
        avg_raw_landmarks.append({'x': np.mean([frame[i][0] for frame in landmarks_list]),
                                  'y': np.mean([frame[i][1] for frame in landmarks_list]),
                                  'z': np.mean([frame[i][2] for frame in landmarks_list])})

    # Convert the averaged raw landmarks back to a format suitable for feature extraction
    # Create a mock hand_landmarks object with the averaged data
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

    avg_hand_landmarks = MockHandLandmarks(avg_raw_landmarks)

    # Extract features from the averaged hand landmarks
    gesture_features = extract_gesture_features(avg_hand_landmarks)

    # Flatten the feature vector for storage/comparison
    return gesture_features.flatten().tolist()


# Implement a function to recognize custom gestures
def recognize_custom_gesture(current_hand_landmarks, custom_gestures, similarity_threshold=CUSTOM_GESTURE_SIMILARITY_THRESHOLD):
    """Compares current hand features to stored custom gestures features.

    Args:
        current_hand_landmarks: The current hand landmark object.
        custom_gestures: Dictionary of stored custom gestures {name: {features: [...], action: "..."}}.
        similarity_threshold: The maximum distance for a gesture to be considered a match.

    Returns:
        The action string associated with the recognized gesture, or None if no match.
    """
    min_distance = float('inf')
    best_match_action = None

    # Extract features from the current hand landmarks
    current_features = extract_gesture_features(current_hand_landmarks)

    for gesture_name, gesture_data in custom_gestures.items():
        stored_features = np.array(gesture_data['features'])

        # Calculate Euclidean distance between current and stored feature vectors
        distance = np.linalg.norm(current_features - stored_features)

        if distance < min_distance:
             min_distance = distance
             best_match_action = gesture_data['action']
             # print(f"Potential match: {gesture_name} with feature distance {distance:.4f}")

    if min_distance < similarity_threshold:
        print(f"Matched gesture with feature distance {min_distance:.4f}")
        return best_match_action

    return None


while cap.isOpened():
    success, image = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        continue

    # Flip the image horizontally for a later selfie-view display
    # Convert the BGR image to RGB. (Conversion moved to HandTracker)
    image = cv2.flip(image, 1)

    # Process the image and find hands
    image.flags.writeable = False # Set image to read-only before processing
    results, image_rgb = hand_tracker.process_frame(image) # Use HandTracker to process frame

    # Draw the hand annotations on the image.
    image.flags.writeable = True # Set image back to writeable for drawing
    image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR) # Convert back to BGR for display

    img_height, img_width, _ = image.shape

    # --- Display Current Mode ---
    mode_text = "Mode: Normal"
    if calibration_mode:
        mode_text = "Mode: Calibration"
    elif recording_gesture:
        mode_text = "Mode: Recording Gesture"
    # Add more mode checks here if needed in the future
    # Position mode text at the bottom left
    mode_text_pos = (10, img_height - 10)
    cv2.rectangle(image, (mode_text_pos[0], mode_text_pos[1] - 25), (mode_text_pos[0] + len(mode_text) * 15, mode_text_pos[1] + 5), (0, 0, 0), -1) # Black background
    cv2.putText(image, mode_text, mode_text_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)

    # --- Handle Non-blocking Input Display ---
    if awaiting_gesture_name or awaiting_gesture_action:
        prompt = "Enter Gesture Name: " if awaiting_gesture_name else "Enter Action (e.g., win+d): "
        # Position input text above mode text
        input_text_pos = (10, img_height - 30)
        cv2.rectangle(image, (input_text_pos[0], input_text_pos[1] - 25), (input_text_pos[0] + len(prompt + input_text) * 15, input_text_pos[1] + 5), (0, 0, 0), -1) # Black background
        cv2.putText(image, prompt + input_text, input_text_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)

    # --- Display Gesture/Action Feedback (Temporary) ---
    current_time_display = time.time()
    if current_time_display - last_action_display_time < action_display_duration:
        # Position gesture/action feedback near the top center
        feedback_pos_x = int(img_width / 2 - max(len(recognized_gesture_text), len(recognized_action_text)) * 15 / 2) # Estimate center based on longest text
        feedback_pos_y_gesture = 50
        feedback_pos_y_action = 80 # Position action text below gesture text

        if recognized_gesture_text:
            cv2.rectangle(image, (feedback_pos_x, feedback_pos_y_gesture - 25), (feedback_pos_x + len(recognized_gesture_text) * 20, feedback_pos_y_gesture + 5), (0, 0, 0), -1) # Black background
            cv2.putText(image, recognized_gesture_text, (feedback_pos_x, feedback_pos_y_gesture), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        if recognized_action_text:
            cv2.rectangle(image, (feedback_pos_x, feedback_pos_y_action - 25), (feedback_pos_x + len(recognized_action_text) * 20, feedback_pos_y_action + 5), (0, 0, 0), -1) # Black background
            cv2.putText(image, recognized_action_text, (feedback_pos_x, feedback_pos_y_action), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_AA)

    # --- Handle Calibration Mode Display ---
    if calibration_mode:
        if current_calibration_point_index < CALIBRATION_POINTS_COUNT:
            point_name = CALIBRATION_POINTS_ORDER[current_calibration_point_index]
            # Position calibration prompt at the top left
            calibration_prompt_pos = (10, 30)
            cv2.rectangle(image, (calibration_prompt_pos[0], calibration_prompt_pos[1] - 25), (calibration_prompt_pos[0] + len(f'Calibrate: Place index finger at {point_name} and press \'s\''), calibration_prompt_pos[1] + 5), (0, 0, 0), -1) # Black background
            cv2.putText(image, f'Calibrate: Place index finger at {point_name} and press \'s\'', calibration_prompt_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2, cv2.LINE_AA)

        # Display calibration status messages for a short duration
        # Position calibration status below the prompt
        calibration_status_pos = (10, 70)
        if time.time() - calibration_status_time < 2: # Display message for 2 seconds
             cv2.rectangle(image, (calibration_status_pos[0], calibration_status_pos[1] - 25), (calibration_status_pos[0] + len(calibration_status_text) * 15, calibration_status_pos[1] + 5), (0, 0, 0), -1) # Black background
             cv2.putText(image, calibration_status_text, calibration_status_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2, cv2.LINE_AA)


        # Draw circles for target calibration points for visual guidance
        padding = 50 # Padding from the edge for visual guidance
        target_points_visual = {
            'top-left': (padding, padding),
            'top-right': (img_width - padding, padding),
            'bottom-left': (padding, img_height - padding),
            'bottom-right': (img_width - padding, img_height - padding)
        }

        for i, point_name in enumerate(CALIBRATION_POINTS_ORDER):
            color = (0, 255, 0) if i == current_calibration_point_index else (0, 100, 0) # Highlight current point
            # Draw the circle on the image frame
            cv2.circle(image, target_points_visual[point_name], 10, color, -1);
            # Add text label near the target point
            cv2.putText(image, point_name.replace('-', ' ').title(), (target_points_visual[point_name][0] + 15, target_points_visual[point_name][1] + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)


        # Draw captured points
        for i, point_name in enumerate(CALIBRATION_POINTS_ORDER):
            if point_name in calibration_points:
                cv2.circle(image, calibration_points[point_name], 8, (0, 0, 255), -1) # Red circle for captured points

        # Draw lines connecting captured points if there are enough points
        if len(calibration_points) >= 2:
            points = []
            # Get points in order to draw lines correctly
            for point_name in CALIBRATION_POINTS_ORDER:
                 if point_name in calibration_points:
                     points.append(calibration_points[point_name])

            # Draw lines between consecutive captured points
            for i in range(len(points) - 1):
                 cv2.line(image, points[i], points[i+1], (0, 255, 255), 2) # Yellow lines

            # Draw closing line if all 4 points are captured
            if len(points) == 4:
                 cv2.line(image, points[3], points[0], (0, 255, 255), 2) # Yellow closing line


    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Get the index finger tip landmark (landmark 8)
            index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

            # Calculate the pixel coordinates of the index finger tip
            # Need to invert the x-axis because the image is flipped
            hand_x = int((1 - index_finger_tip.x) * img_width)
            hand_y = int(index_finger_tip.y * img_height)

            # Append current landmarks to stability buffer
            stability_buffer.append([(l.x, l.y, l.z) for l in hand_landmarks.landmark])
            # Keep buffer size limited
            if len(stability_buffer) > STABILITY_FRAME_COUNT:
                stability_buffer.pop(0)

            # Check for hand stability (only if enough frames are in the buffer and not in calibration/recording/input mode)
            hand_is_stable = False
            if len(stability_buffer) == STABILITY_FRAME_COUNT and not calibration_mode and not recording_gesture and not awaiting_gesture_name and not awaiting_gesture_action:
                 # Pass the first set of landmarks from the buffer to check stability against
                 hand_is_stable = is_hand_stable(hand_landmarks, stability_buffer, GESTURE_STABILITY_THRESHOLD)
                 if hand_is_stable:
                     cv2.putText(image, 'Stable', (10, img_height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)


            # --- Custom Gesture Recording Mode ---
            # Only record if not in calibration or awaiting input
            if recording_gesture and not calibration_mode and not awaiting_gesture_name and not awaiting_gesture_action:
                cv2.putText(image, 'Recording Gesture...', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
                # Capture landmark data for this frame
                # Store normalized coordinates (x, y, z)
                captured_gesture_landmarks.append([(l.x, l.y, l.z) for l in hand_landmarks.landmark])

            # --- Normal Operation (Cursor Movement and Predefined/Custom Gestures) ---
            # Only perform normal operations if not in calibration, recording, or awaiting input
            elif not calibration_mode and not recording_gesture and not awaiting_gesture_name and not awaiting_gesture_action:
                # --- Cursor Movement (using calibration if available) ---
                mouse_x, mouse_y = get_screen_coordinates(hand_x, hand_y, img_width, img_height, screen_width, screen_height, M)
                pyautogui.moveTo(mouse_x, mouse_y)

                # --- Gesture Recognition ---
                # Perform gesture recognition only if hand is stable
                if hand_is_stable:
                    # Get finger tip and PIP landmarks for checks
                    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                    thumb_ip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP]
                    thumb_cmc = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_CMC]

                    index_finger_tip_gesture = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                    index_finger_pip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP]
                    index_finger_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]

                    middle_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
                    middle_finger_pip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_PIP]
                    middle_finger_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]

                    ring_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
                    ring_finger_pip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_PIP]
                    ring_finger_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_MCP]

                    pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
                    pinky_pip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_PIP]
                    pinky_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP]

                    # Check if fingers are up using angle-based method
                    thumb_up = is_thumb_up_by_angle(thumb_tip, thumb_ip, thumb_cmc)
                    index_up = is_finger_up_by_angle(index_finger_tip_gesture, index_finger_pip, index_finger_mcp)
                    middle_up = is_finger_up_by_angle(middle_finger_tip, middle_finger_pip, middle_finger_mcp)
                    ring_up = is_finger_up_by_angle(ring_finger_tip, ring_finger_pip, ring_finger_mcp)
                    pinky_up = is_finger_up_by_angle(pinky_tip, pinky_pip, pinky_mcp)

                    # Left Click: Thumb and Index finger tips touching
                    # Ensure other fingers are not up to avoid accidental clicks during other gestures
                    # Refined condition: Thumb tip close to index finger tip AND only thumb and index are up (or mostly up)
                    if calculate_distance(thumb_tip, index_finger_tip_gesture, img_width, img_height) < CLICK_DISTANCE_THRESHOLD \
                       and thumb_up and index_up and not middle_up and not ring_up and not pinky_up:
                        current_time = time.time()
                        if current_time - last_click_time < DOUBLE_CLICK_INTERVAL:
                            print("Double Click Gesture Detected")
                            # Update recognized gesture text for display
                            recognized_gesture_text = 'Double Click!'
                            last_action_display_time = time.time() # Start timer for display
                            # pyautogui.doubleClick() # Uncomment to enable actual double clicking
                            last_click_time = 0 # Reset for double click
                        else:
                            print("Left Click Gesture Detected")
                            # Update recognized gesture text for display
                            recognized_gesture_text = 'Left Click!'
                            last_action_display_time = time.time() # Start timer for display
                            # pyautogui.click() # Uncomment to enable actual clicking
                            last_click_time = current_time
                    else:
                        last_click_time = 0 # Reset if click gesture is not held or other fingers are up

                    # Right Click: Index and Middle fingers are up, others down
                    # Refined condition: Index and middle fingers are up, others are down (or mostly down)
                    if index_up and middle_up and not ring_up and not pinky_up and not thumb_up:
                         print("Right Click Gesture Detected")
                         # Update recognized gesture text for display
                         recognized_gesture_text = 'Right Click!'
                         last_action_display_time = time.time() # Start timer for display
                         # pyautogui.rightClick() # Uncomment to enable actual right clicking

                    # Scroll Down: Pointer finger and middle finger together and up
                    # Refined condition: Index and middle fingers up and close together vertically, others down
                    if index_up and middle_up and not ring_up and not pinky_up and not thumb_up \
                       and abs(index_finger_tip_gesture.y - middle_finger_tip.y) * img_height < SCROLL_THRESHOLD:
                        print("Scroll Down Gesture Detected")
                        # Update recognized gesture text for display
                        recognized_gesture_text = 'Scroll Down'
                        last_action_display_time = time.time() # Start timer for display
                        # pyautogui.scroll(-10) # Uncomment to enable actual scrolling down

                    # Scroll Up: First 3 fingers together and up (Index, Middle, Ring tips close vertically)
                    # Refined condition: Index, middle, and ring fingers up and close together vertically, others down
                    if index_up and middle_up and ring_up and not pinky_up and not thumb_up \
                       and abs(index_finger_tip_gesture.y - middle_finger_tip.y) * img_height < SCROLL_THRESHOLD \
                       and abs(middle_finger_tip.y - ring_finger_tip.y) * img_height < SCROLL_THRESHOLD:
                         print("Scroll Up Gesture Detected")
                         # Update recognized gesture text for display
                         recognized_gesture_text = 'Scroll Up'
                         last_action_display_time = time.time() # Start timer for display
                         # pyautogui.scroll(10) # Uncomment to enable actual scrolling up

                    # Speech to Text: All 5 fingers up
                    # Condition remains: All 5 fingers are up
                    if thumb_up and index_up and middle_up and ring_up and pinky_up:
                        print("Speech to Text Gesture Detected (All 5 fingers up)")
                        # Update recognized gesture text for display
                        recognized_gesture_text = 'Speech to Text'
                        last_action_display_time = time.time() # Start timer for display
                        # pyautogui.hotkey('win', 'h') # Uncomment to enable actual shortcut

                    # Check for custom gestures
                    recognized_action = recognize_custom_gesture(hand_landmarks, custom_gestures)

                    # Execute custom action if recognized and cooldown is over
                    current_time = time.time()
                    if recognized_action and (current_time - last_custom_action_time > CUSTOM_ACTION_COOLDOWN):
                        print(f"Executing custom action: {recognized_action}")
                         # Update recognized action text for display
                        recognized_action_text = f'Action: {recognized_action}'
                        last_action_display_time = time.time() # Start timer for display
                        # Execute the action using pyautogui.hotkey
                        # Split the action string by '+' to handle multiple keys (e.g., 'win+h')
                        keys = recognized_action.split('+')
                        pyautogui.hotkey(*keys) # Uncommented to enable actual hotkey execution
                        last_custom_action_time = current_time # Update last action time


            # Draw landmarks and connections
            # Use HandTracker to draw landmarks
            hand_tracker.draw_landmarks(image, results.multi_hand_landmarks)

    # Display the image
    cv2.imshow('Hand Tracking and Cursor Control', image)

    # Check for key presses
    key = cv2.waitKey(5) & 0xFF
    if key == ord('q'):
        break

    # --- Handle Calibration Mode Key Presses ---
    elif key == ord('c'): # Press 'c' to toggle calibration mode
        calibration_mode = not calibration_mode
        if calibration_mode:
            print("Entering calibration mode. Press 's' to capture points.")
            calibration_points = {}
            current_calibration_point_index = 0
            M = None # Reset mapping on entering calibration
            calibration_status_text = "Entering Calibration Mode"
            calibration_status_time = time.time()
            # Ensure not in recording/input mode
            recording_gesture = False
            awaiting_gesture_name = False
            awaiting_gesture_action = False
            input_text = ""
            current_gesture_to_save = None
        else:
            print("Exiting calibration mode.")
            calibration_status_text = "Exiting Calibration Mode"
            calibration_status_time = time.time()

    elif calibration_mode and key == ord('s'): # Press 's' to capture calibration point
        if results.multi_hand_landmarks:
            # Assuming only one hand is present for calibration
            hand_landmarks = results.multi_hand_landmarks[0]
            index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            img_height, img_width, _ = image.shape
            hand_x = int((1 - index_finger_tip.x) * img_width)
            hand_y = int(index_finger_tip.y * img_height)

            if current_calibration_point_index < CALIBRATION_POINTS_COUNT:
                point_key = CALIBRATION_POINTS_ORDER[current_calibration_point_index]
                calibration_points[point_key] = (hand_x, hand_y)
                print(f'Captured {point_key}: ({hand_x}, {hand_y})')
                calibration_status_text = f'Captured {point_key}'
                calibration_status_time = time.time()
                current_calibration_point_index += 1

                if current_calibration_point_index == CALIBRATION_POINTS_COUNT:
                    # Once all points are captured, calculate the perspective transformation matrix
                    src_points = np.float32([
                        calibration_points['top-left'],
                        calibration_points['top-right'],
                        calibration_points['bottom-left'],
                        calibration_points['bottom-right']
                    ])

                    dst_points = np.float32([
                        [0, 0],                          # Top-left of screen
                        [screen_width, 0],               # Top-right of screen
                        [0, screen_height],              # Bottom-left of screen
                        [screen_width, screen_height]    # Bottom-right of screen
                    ])

                    M = cv2.getPerspectiveTransform(src_points, dst_points)
                    print("Calibration complete. Mapping matrix calculated.")
                    calibration_status_text = "Calibration Complete!"
                    calibration_status_time = time.time()
                    # calibration_mode = False # Keep calibration mode active until user exits
                    # calibration_points = {} # Keep calibration points for potential display/refinement
            else:
                 calibration_status_text = "Calibration already completed."
                 calibration_status_time = time.time()

    # --- Handle Reset Calibration ---
    elif key == ord('R'): # Press 'R' to reset calibration
        print("Resetting calibration.")
        M = None
        calibration_points = {}
        current_calibration_point_index = 0
        calibration_status_text = "Calibration Reset!"
        calibration_status_time = time.time()

    # --- Handle Custom Gesture Recording and Input Key Presses ---
    elif key == ord('r'): # Press 'r' to toggle custom gesture recording mode
        # Toggle recording mode only if not currently in calibration or awaiting input
        if not calibration_mode and not awaiting_gesture_name and not awaiting_gesture_action:
            recording_gesture = not recording_gesture
            if recording_gesture:
                print("Starting custom gesture recording.")
                captured_gesture_landmarks = [] # Clear previous data
            else:
                print("Stopping custom gesture recording.")
                # Process captured gesture data when recording stops
                processed_gesture = process_captured_gesture(captured_gesture_landmarks)
                if processed_gesture is not None:
                    current_gesture_to_save = processed_gesture
                    awaiting_gesture_name = True # Start awaiting gesture name input
                    input_text = ""
                    print("Recording stopped. Enter gesture name.")
                else:
                    print("No valid gesture data captured.")

    # Handle input while awaiting gesture name or action
    elif awaiting_gesture_name or awaiting_gesture_action:
        if key == 13: # Enter key
            if awaiting_gesture_name:
                gesture_name = input_text.strip()
                if gesture_name:
                    # Move to awaiting action
                    awaiting_gesture_name = False
                    awaiting_gesture_action = True
                    # Store the processed gesture temporarily, will add action later
                    # Assuming current_gesture_to_save holds the processed gesture data (now features)
                    custom_gestures[gesture_name] = {'features': current_gesture_to_save, 'action': ''} # Store gesture, await action
                    input_text = ""
                    print(f"Gesture name '{gesture_name}' captured. Enter action.")
                else:
                    print("Gesture name cannot be empty. Please enter a name.")
                    # Stay in awaiting_gesture_name mode

            elif awaiting_gesture_action:
                gesture_action = input_text.strip()
                if gesture_action:
                    # Save gesture and action
                    # Get the last added gesture name (since we added it in awaiting_gesture_name step)
                    custom_gesture_name = list(custom_gestures.keys())[-1]
                    custom_gestures[custom_gesture_name]['action'] = gesture_action
                    save_custom_gestures(custom_gestures, CUSTOM_GESTURES_FILE)

                    print(f"Custom gesture '{custom_gesture_name}' saved with action '{gesture_action}'.")
                    # Reset input state
                    awaiting_gesture_action = False
                    input_text = ""
                    current_gesture_to_save = None # Clear the saved gesture data
                else:
                     print("Gesture action cannot be empty. Please enter an action.")
                     # Stay in awaiting_gesture_action mode

        elif key == 8: # Backspace key
            input_text = input_text[:-1]
        elif key != 255: # Ignore empty key events
             # Convert key code to character (basic handling)
             if 32 <= key <= 126:
                input_text += chr(key)


# Release the video capture object and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()