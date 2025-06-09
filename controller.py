import pyautogui
import time

class Controller:
    hand_Landmarks = None
    screen_width, screen_height = pyautogui.size()
    last_index_state = None
    last_middle_state = None
    last_ring_state = None
    last_index_down_time = 0
    last_index_up_time = 0
    last_click_time = 0
    left_click_pending = False
    dragging = False
    drag_ready = False
    prev_cursor_pos = None
    # Calibration: region of interest in camera frame (percentages)
    roi_left = 0.1
    roi_right = 0.9
    roi_top = 0.1
    roi_bottom = 0.9

    @staticmethod
    def update_fingers_status():
        lm = Controller.hand_Landmarks.landmark
        Controller.index_up = lm[8].y < lm[6].y
        Controller.middle_up = lm[12].y < lm[10].y
        Controller.ring_up = lm[16].y < lm[14].y
        Controller.little_up = lm[20].y < lm[18].y
        Controller.thumb_extended = abs(lm[4].x - lm[2].x) > 0.05
        # Move mode: index and middle up, ring down
        Controller.move_mode = Controller.index_up and Controller.middle_up and not Controller.ring_up
        # Freeze: index, middle, ring up
        Controller.freeze_mode = Controller.index_up and Controller.middle_up and Controller.ring_up
        # Left click gesture: index down, middle up, ring up
        Controller.left_click_gesture = (not Controller.index_up) and Controller.middle_up and Controller.ring_up
        # Drag ready: index down >1s, middle up, ring up
        Controller.drag_ready_gesture = (not Controller.index_up) and Controller.middle_up and Controller.ring_up
        # Drag start: index down, middle up, ring down
        Controller.drag_start_gesture = (not Controller.index_up) and Controller.middle_up and not Controller.ring_up
        # Drag stop: index up, middle up, ring up
        Controller.drag_stop_gesture = Controller.index_up and Controller.middle_up and Controller.ring_up
        # Right click: all up, thumb extended
        Controller.right_click_gesture = Controller.index_up and Controller.middle_up and Controller.ring_up and Controller.thumb_extended

    @staticmethod
    def map_to_screen(x, y):
        x = (x - Controller.roi_left) / (Controller.roi_right - Controller.roi_left)
        y = (y - Controller.roi_top) / (Controller.roi_bottom - Controller.roi_top)
        x = min(max(x, 0), 1)
        y = min(max(y, 0), 1)
        return int(x * Controller.screen_width), int(y * Controller.screen_height)

    @staticmethod
    def get_position(hand_x_position, hand_y_position):
        return Controller.map_to_screen(hand_x_position, hand_y_position)

    @staticmethod
    def cursor_moving():
        # Freeze mouse if freeze_mode or drag is active
        if Controller.freeze_mode or Controller.dragging:
            return
        # Move cursor only if move_mode is True
        if Controller.move_mode:
            point = 8  # index tip
            current_x, current_y = Controller.hand_Landmarks.landmark[point].x, Controller.hand_Landmarks.landmark[point].y
            x, y = Controller.get_position(current_x, current_y)
            pyautogui.moveTo(x, y, duration=0)
            Controller.prev_cursor_pos = (x, y)

    @staticmethod
    def detect_clicking():
        now = time.time()
        index_state = Controller.index_up
        middle_state = Controller.middle_up
        ring_state = Controller.ring_up
        # --- Left Click (tap) ---
        if Controller.last_index_state is None:
            Controller.last_index_state = index_state
        if Controller.left_click_gesture and not Controller.last_index_state:
            Controller.last_index_down_time = now
            Controller.left_click_pending = True
        if Controller.left_click_pending and index_state and not Controller.last_index_state:
            # Index released after tap
            duration = now - Controller.last_index_down_time
            if duration < 1.0:
                pyautogui.click()
                print("Left Click")
            Controller.left_click_pending = False
        # --- Drag Ready (index down >1s, ring up) ---
        if Controller.drag_ready_gesture and not index_state:
            if Controller.last_index_down_time and (now - Controller.last_index_down_time) > 1.0:
                Controller.drag_ready = True
        # --- Drag Start (index down, ring goes down) ---
        if Controller.drag_ready and Controller.drag_start_gesture and (Controller.last_ring_state is not None) and Controller.last_ring_state:
            pyautogui.mouseDown(button="left")
            Controller.dragging = True
            Controller.drag_ready = False
            print("Dragging Start")
        # --- Drag Stop (all up) ---
        if Controller.dragging and Controller.drag_stop_gesture:
            pyautogui.mouseUp(button="left")
            Controller.dragging = False
            print("Dragging End")
        # --- Right Click ---
        if Controller.right_click_gesture:
            pyautogui.rightClick()
            print("Right Click")
        Controller.last_index_state = index_state
        Controller.last_middle_state = middle_state
        Controller.last_ring_state = ring_state