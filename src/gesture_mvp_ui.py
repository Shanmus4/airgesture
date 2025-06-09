import remi.gui as gui
from remi import start, App
import cv2
import threading
import time
import numpy as np
import io
from PIL import Image

# Import the core modules
from hand_tracking import HandTracker
from os_interaction import OSInteractor
from calibration import CalibrationManager
from visual_feedback import VisualFeedbackManager
from hand_stability import HandStabilityManager
from gesture_recognition import GestureRecognizer

class GestureMVPApp(App):
    def __init__(self, *args):
        super(GestureMVPApp, self).__init__(*args)
        self.running = False
        self.calibrating = False
        self.show_gestures = False
        self.capture_thread = None
        self.frame = None  # Ensure frame is always initialized
        self.last_frame_time = 0
        self.mode = 'idle'  # 'idle', 'calibrate', 'test'
        self.calibration_step = 0
        self.calibration_points = ['top-left', 'top-right', 'bottom-left', 'bottom-right']
        self.calibration_prompt = ''
        self.calibration_done = False
        self.hand_is_stable = False
        self.gesture_feedback = ''
        self.action_feedback = ''
        self.stability_feedback = ''

        # Core modules
        self.cap = cv2.VideoCapture(0)
        self.os_interactor = OSInteractor()
        self.hand_tracker = HandTracker()
        self.calibration_manager = CalibrationManager(self.os_interactor.screen_width, self.os_interactor.screen_height)
        self.visual_feedback_manager = VisualFeedbackManager()
        self.hand_stability_manager = HandStabilityManager()
        self.gesture_recognizer = GestureRecognizer(
            self.os_interactor,
            self.calibration_manager,
            None,  # No custom gestures
            self.visual_feedback_manager,
            self.hand_stability_manager
        )

        # For thread safety
        self.lock = threading.Lock()

    def idle_loop(self):
        while self.running:
            if not hasattr(self, 'cap') or self.cap is None:
                print('[Camera] cap not initialized')
                time.sleep(0.03)
                continue
            if not self.cap.isOpened():
                print('[Camera] cap not opened!')
                self.camera_error = True
                time.sleep(0.5)
                continue
            ret, image = self.cap.read()
            if not ret:
                print('[Camera] Failed to read frame!')
                self.camera_error = True
                time.sleep(0.1)
                continue
            self.camera_error = False
            image = cv2.flip(image, 1)
            img_height, img_width, _ = image.shape
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results, image_rgb = self.hand_tracker.process_frame(image_rgb)

            # Calibration mode
            if self.mode == 'calibrate':
                image = self.calibration_manager.display_calibration_status(image, img_width, img_height)
                if results.multi_hand_landmarks:
                    hand_landmarks = results.multi_hand_landmarks[0]
                    if self.calibration_step < 4:
                        # Draw a circle at the index finger tip
                        index_finger_tip = hand_landmarks.landmark[8]
                        hand_x = int((1 - index_finger_tip.x) * img_width)
                        hand_y = int(index_finger_tip.y * img_height)
                        cv2.circle(image, (hand_x, hand_y), 10, (0, 255, 255), 2)
            elif self.mode == 'test':
                self.visual_feedback_manager.display_mode(image, img_height, False, False)
                image = self.visual_feedback_manager.display_gesture_action_feedback(image, img_width)
                image = self.calibration_manager.display_calibration_status(image, img_width, img_height)
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        index_finger_tip = hand_landmarks.landmark[8]
                        hand_x = int((1 - index_finger_tip.x) * img_width)
                        hand_y = int(index_finger_tip.y * img_height)
                        hand_is_stable = self.hand_stability_manager.is_hand_stable(hand_landmarks)
                        if not self.calibration_manager.calibration_mode:
                            mouse_x, mouse_y = self.calibration_manager.get_screen_coordinates(hand_x, hand_y, img_width, img_height)
                            self.os_interactor.move_to(mouse_x, mouse_y)
                            self.gesture_recognizer.recognize_gestures_and_perform_actions(hand_landmarks, img_width, img_height, hand_is_stable)
                        if hand_is_stable:
                            self.stability_feedback = 'Stable'
                        else:
                            self.stability_feedback = ''
                    self.hand_tracker.draw_landmarks(image, results.multi_hand_landmarks)
            else:
                # Idle mode, just show camera
                pass

            # Draw overlays for feedback
            if self.stability_feedback:
                cv2.putText(image, self.stability_feedback, (10, img_height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)

            # Save frame for UI
            with self.lock:
                self.frame = image.copy()
            time.sleep(0.03)

    def main(self):
        main_container = gui.VBox(width='100%', height='100%')
        main_container.style['align-items'] = 'center'
        main_container.style['justify-content'] = 'flex-start'

        # Camera feed
        self.img_widget = gui.Image('', width=640, height=480, style={'border': '2px solid #333', 'margin-bottom': '10px'})
        main_container.append(self.img_widget)

        # Buttons
        button_box = gui.HBox(width='100%')
        self.calibrate_btn = gui.Button('Calibrate', width=120, height=40)
        self.calibrate_btn.onclick.do(self.on_calibrate)
        button_box.append(self.calibrate_btn)
        self.gesture_legend_btn = gui.Button('Show Gestures', width=120, height=40)
        self.gesture_legend_btn.onclick.do(self.on_show_gestures)
        button_box.append(self.gesture_legend_btn)
        self.test_btn = gui.Button('Test', width=120, height=40)
        self.test_btn.onclick.do(self.on_test)
        button_box.append(self.test_btn)
        main_container.append(button_box)

        # Legend and feedback
        self.legend_box = gui.VBox(width='80%', style={'margin-top': '10px', 'margin-bottom': '10px'})
        main_container.append(self.legend_box)
        self.feedback_label = gui.Label('', width='100%', style={'color': 'red', 'font-size': '16px'})
        main_container.append(self.feedback_label)

        # Start camera thread
        self.running = True
        if not hasattr(self, 'cap'):
            self.cap = cv2.VideoCapture(0)
        self.capture_thread = threading.Thread(target=self.idle_loop)
        self.capture_thread.daemon = True
        self.capture_thread.start()

        # Start UI update timer (Remi: use idle() + update_interval, not schedule_interval)
        return main_container

    def update_ui(self):
        # Defensive: Ensure self.frame exists
        if not hasattr(self, 'frame'):
            self.frame = None
        # Update camera image
        if self.camera_error:
            print('[UI] Camera error detected, showing error image')
            # Show a red error image
            error_img = np.zeros((480, 640, 3), dtype=np.uint8)
            error_img[:, :, 2] = 255  # Red
            pil_img = Image.fromarray(error_img)
            img_bytes = io.BytesIO()
            pil_img.save(img_bytes, format='JPEG')
            img_bytes = img_bytes.getvalue()
            self.img_widget.set_image('data:image/jpeg;base64,' + gui.from_file(img_bytes, 'jpeg'))
            self.feedback_label.set_text('Camera Error!')
            return
        if self.frame is not None:
            img = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(img)
            img_bytes = io.BytesIO()
            pil_img.save(img_bytes, format='JPEG')
            img_bytes = img_bytes.getvalue()
            self.img_widget.set_image('data:image/jpeg;base64,' + gui.from_file(img_bytes, 'jpeg'))
        else:
            # Show a gray placeholder
            placeholder = np.full((480, 640, 3), 180, dtype=np.uint8)
            pil_img = Image.fromarray(placeholder)
            img_bytes = io.BytesIO()
            pil_img.save(img_bytes, format='JPEG')
            img_bytes = img_bytes.getvalue()
            self.img_widget.set_image('data:image/jpeg;base64,' + gui.from_file(img_bytes, 'jpeg'))
            self.feedback_label.set_text('Waiting for camera...')

    def on_calibrate(self, widget):
        self.mode = 'calibrate'
        self.calibration_manager.calibration_mode = True
        self.calibration_manager.calibration_points = {}
        self.calibration_manager.current_calibration_point_index = 0
        self.calibration_manager.mapping_matrix = None
        self.calibration_manager.calibration_status_text = 'Calibration started. Place your finger at the prompted corner and press the button below.'
        self.calibration_manager.calibration_status_time = time.time()
        self.legend_box.empty()
        self.feedback_label.set_text('')
        # Add a button for each calibration point
        self.legend_box.empty()
        self.next_point_btn = gui.Button('Capture Point', width=180, height=40)
        self.next_point_btn.onclick.do(self.on_capture_calibration_point)
        self.legend_box.append(gui.Label('Follow the on-screen prompt and click "Capture Point" for each corner.'))
        self.legend_box.append(self.next_point_btn)

    def on_capture_calibration_point(self, widget):
        # Capture the current hand position for calibration
        ret, image = self.cap.read()
        if not ret:
            self.feedback_label.set_text('Camera error. Try again.')
            return
        image = cv2.flip(image, 1)
        img_height, img_width, _ = image.shape
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results, _ = self.hand_tracker.process_frame(image_rgb)
        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            index_finger_tip = hand_landmarks.landmark[8]
            hand_x = int((1 - index_finger_tip.x) * img_width)
            hand_y = int(index_finger_tip.y * img_height)
            if self.calibration_manager.current_calibration_point_index < 4:
                point_key = self.calibration_points[self.calibration_manager.current_calibration_point_index]
                self.calibration_manager.calibration_points[point_key] = (hand_x, hand_y)
                self.calibration_manager.current_calibration_point_index += 1
                self.calibration_manager.calibration_status_text = f'Captured {point_key}'
                self.calibration_manager.calibration_status_time = time.time()
                if self.calibration_manager.current_calibration_point_index == 4:
                    # Compute mapping
                    src_points = np.float32([
                        self.calibration_manager.calibration_points['top-left'],
                        self.calibration_manager.calibration_points['top-right'],
                        self.calibration_manager.calibration_points['bottom-left'],
                        self.calibration_manager.calibration_points['bottom-right']
                    ])
                    dst_points = np.float32([
                        [0, 0],
                        [self.os_interactor.screen_width, 0],
                        [0, self.os_interactor.screen_height],
                        [self.os_interactor.screen_width, self.os_interactor.screen_height]
                    ])
                    self.calibration_manager.mapping_matrix = cv2.getPerspectiveTransform(src_points, dst_points)
                    self.calibration_manager.calibration_mode = False
                    self.mode = 'idle'
                    self.legend_box.empty()
                    self.feedback_label.set_text('Calibration complete!')
                else:
                    self.feedback_label.set_text(f'Captured {point_key}. Move to the next point.')
            else:
                self.feedback_label.set_text('Calibration already complete.')
        else:
            self.feedback_label.set_text('No hand detected. Try again.')

    def on_show_gestures(self, widget):
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
        self.feedback_label.set_text('')

    def on_test(self, widget):
        if self.calibration_manager.mapping_matrix is None:
            self.feedback_label.set_text('Please calibrate first!')
            return
        self.mode = 'test'
        self.legend_box.empty()
        self.feedback_label.set_text('Test mode: Use gestures to control your desktop!')

    def idle(self):
        # Defensive: Ensure self.lock exists
        if not hasattr(self, 'lock'):
            import threading
            self.lock = threading.Lock()
        # Called by Remi every update_interval seconds
        self.update_ui()
        # Defensive: Only try to release cap if it exists when shutting down
        if hasattr(self, 'cap') and self.cap and not self.running:
            self.cap.release()
            self.cap = None

if __name__ == '__main__':
    start(GestureMVPApp, address='0.0.0.0', port=8081, debug=True) 