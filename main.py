# main.py
import cv2
import threading
import time
import numpy as np
from remi import start
from src.hand_tracking import HandTracker
from src.os_interaction import OSInteractor
from src.calibration import CalibrationManager
from src.visual_feedback import VisualFeedbackManager
from src.hand_stability import HandStabilityManager
from src.gesture_recognition import GestureRecognizer
from src.ui import GestureApp # Import the new UI

# DEBUG flag for controlling debug output
DEBUG = True

class ApplicationManager:
    def __init__(self):
        self.running = False
        self.hand_tracker = HandTracker()
        self.os_interactor = OSInteractor()
        self.calibration_manager = CalibrationManager(self.os_interactor.screen_width, self.os_interactor.screen_height)
        self.visual_feedback_manager = VisualFeedbackManager()
        self.hand_stability_manager = HandStabilityManager()
        self.gesture_recognizer = GestureRecognizer(
            self.os_interactor,
            self.calibration_manager,
            None, # custom_gesture_manager (for MVP)
            self.visual_feedback_manager,
            self.hand_stability_manager
        )
        self.app = None # Reference to the Remi UI app

        self.mode = 'idle' # 'idle', 'calibrate', 'test'
        self.calibration_step = 0
        self.calibration_points = ['top-left', 'top-right', 'bottom-left', 'bottom-right']
        self.calibration_prompt = ''
        self.calibration_done = False
        self.hand_is_stable = False
        self.gesture_feedback = ''
        self.stability_feedback = ''

    def set_app(self, app_instance):
        self.app = app_instance

    def camera_loop(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            if DEBUG:
                print("[Camera] Failed to open camera!")
            # Optionally, communicate camera error to UI
            return

        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                if DEBUG:
                    print("[Camera] Failed to read frame.")
                break

            frame = cv2.flip(frame, 1) # Mirror the frame

            if self.mode == 'calibrate':
                frame = self.calibration_manager.display_calibration_status(frame, frame.shape[1], frame.shape[0])
            elif self.mode == 'test':
                self.visual_feedback_manager.display_mode(frame, frame.shape[0], False, False) # No custom or debugging mode
                frame = self.visual_feedback_manager.display_gesture_action_feedback(frame, frame.shape[1])
                frame = self.calibration_manager.display_calibration_status(frame, frame.shape[1], frame.shape[0])

            # Process hand landmarks
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results, _ = self.hand_tracker.process_frame(image_rgb)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    if self.mode == 'calibrate':
                        index_finger_tip = hand_landmarks.landmark[8]
                        hand_x = int((1 - index_finger_tip.x) * frame.shape[1])
                        hand_y = int(index_finger_tip.y * frame.shape[0])
                        cv2.circle(frame, (hand_x, hand_y), 10, (0, 255, 255), 2)
                    elif self.mode == 'test':
                        self.hand_is_stable = self.hand_stability_manager.is_hand_stable(hand_landmarks)
                        if not self.calibration_manager.calibration_mode:
                            index_finger_tip = hand_landmarks.landmark[8]
                            hand_x = int((1 - index_finger_tip.x) * frame.shape[1])
                            hand_y = int(index_finger_tip.y * frame.shape[0])
                            mouse_x, mouse_y = self.calibration_manager.get_screen_coordinates(hand_x, hand_y, frame.shape[1], frame.shape[0])
                            self.os_interactor.move_to(mouse_x, mouse_y)
                            self.gesture_recognizer.recognize_gestures_and_perform_actions(hand_landmarks, frame.shape[1], frame.shape[0], self.hand_is_stable)
                            
                        if self.hand_is_stable:
                            self.stability_feedback = 'Stable'
                        else:
                            self.stability_feedback = ''
                        
                    self.hand_tracker.draw_landmarks(frame, results.multi_hand_landmarks)

            # Display stability feedback in OpenCV window
            if self.stability_feedback and self.mode == 'test':
                cv2.putText(frame, self.stability_feedback, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)

            cv2.imshow('Air Gesture Camera Feed', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.running = False
                break
        
        self.cap.release()
        cv2.destroyAllWindows()

    def start_calibration(self):
        self.mode = 'calibrate'
        self.calibration_step = 0
        self.calibration_manager.start_calibration()
        self.calibration_prompt = 'Calibration started. Place your finger at the prompted corner and press the button below.'
        self.calibration_manager.calibration_status_time = time.time()
        self.app.update_calibration_ui(self.calibration_prompt)

    def capture_calibration_point(self):
        ret, image = self.cap.read()
        if not ret:
            self.app.set_feedback('Camera error. Try again.')
            return
        image = cv2.flip(image, 1)
        results = self.hand_tracker.process_frame(image)
        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            index_finger_tip = hand_landmarks.landmark[8]
            point_x = index_finger_tip.x
            point_y = index_finger_tip.y

            point_key = self.calibration_points[self.calibration_step]
            self.calibration_manager.capture_point(point_key, point_x, point_y)

            self.calibration_step += 1
            if self.calibration_step >= len(self.calibration_points):
                self.calibration_manager.end_calibration()
                self.calibration_done = True
                self.calibration_prompt = 'Calibration complete!'
                self.mode = 'idle'
                self.app.update_calibration_ui(self.calibration_prompt, calibration_finished=True)
            else:
                self.calibration_prompt = f'Captured {point_key}. Move to the next point.'
                self.app.update_calibration_ui(self.calibration_prompt)
        else:
            self.app.set_feedback('No hand detected. Try again.')

    def show_gestures(self):
        self.mode = 'idle' # Exit any other modes
        self.app.show_gesture_legend()

    def start_test_mode(self):
        if self.calibration_done:
            self.mode = 'test'
            self.app.set_feedback('Test mode active. Control cursor with hand gestures.')
        else:
            self.app.set_feedback('Please calibrate first!')

def main():
    app_manager = ApplicationManager()
    
    # Start Remi UI in a separate thread
    remi_thread = threading.Thread(target=start, args=(GestureApp,), kwargs={'host': '0.0.0.0', 'port': 8081, 'debug': True, 'update_interval': 0.5})
    remi_thread.daemon = True
    remi_thread.start()

    # Wait for Remi to start and set the app instance
    # A more robust solution would be to use a Queue or Event
    # For now, loop and wait for app_instance to be set
    max_wait_time = 10 # seconds
    start_time = time.time()
    while GestureApp.app_instance is None and (time.time() - start_time) < max_wait_time:
        time.sleep(0.1) # Wait for a short period before rechecking

    if GestureApp.app_instance is None:
        print("[ERROR] Remi UI app instance not initialized after waiting.")
        return # Exit if UI app didn't start properly
    
    app_manager.set_app(GestureApp.app_instance) # Access the instance once it's set in ui.py

    # Pass the app_manager's methods to the UI for callbacks
    GestureApp.app_instance.set_callbacks(
        start_calibration_callback=app_manager.start_calibration,
        capture_calibration_point_callback=app_manager.capture_calibration_point,
        show_gestures_callback=app_manager.show_gestures,
        start_test_mode_callback=app_manager.start_test_mode
    )

    app_manager.running = True
    app_manager.camera_loop() # Start the OpenCV camera loop in the main thread

if __name__ == '__main__':
    main() 