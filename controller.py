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

        thumb_x = lm[4].x
        thumb_y = lm[4].y
        index_mcp_x = lm[2].x
        index_mcp_y = lm[2].y

        # Improved thumb detection (simplified to x-difference)
        thumb_threshold = 0.03
        Controller.thumb_extended = abs(thumb_x - index_mcp_x) > thumb_threshold

        Controller.move_mode = Controller.index_up and Controller.middle_up and not Controller.ring_up
        Controller.freeze_mode = Controller.index_up and Controller.middle_up and Controller.ring_up
        Controller.left_click_gesture = (not Controller.index_up) and Controller.middle_up and Controller.ring_up
        Controller.drag_unlock_gesture = (not Controller.index_up) and Controller.middle_up and Controller.ring_up
        Controller.drag_stop_gesture = Controller.index_up and Controller.middle_up and Controller.ring_up
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
        if Controller.freeze_mode and not Controller.dragging:
            return
        if Controller.move_mode or Controller.dragging:
            point = 12  # middle finger tip
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

        # Track when index is freshly pressed
        if not index_state and Controller.last_index_state:
            Controller.last_index_down_time = now

        # --- Left Click ---
        if Controller.left_click_gesture and not Controller.last_index_state:
            Controller.left_click_pending = True

        if Controller.left_click_pending and index_state and not Controller.last_index_state:
            duration = now - Controller.last_index_down_time
            if duration < 1.0 and not Controller.dragging:
                pyautogui.click()
                print("Left Click")
            Controller.left_click_pending = False

        # --- Drag unlock: index held > 2 sec ---
        if Controller.drag_unlock_gesture and not index_state:
            if (now - Controller.last_index_down_time) > 2.0 and not Controller.dragging:
                pyautogui.mouseDown(button="left")
                Controller.dragging = True
                print("Dragging Start")

        # --- Drag stop ---
        if Controller.dragging and Controller.drag_stop_gesture:
            pyautogui.mouseUp(button="left")
            Controller.dragging = False
            print("Dragging End")

        # --- Right Click with cooldown ---
        if Controller.right_click_gesture and (now - Controller.last_click_time) > 1.0:
            pyautogui.rightClick()
            Controller.last_click_time = now
            print("Right Click")

        Controller.last_index_state = index_state
        Controller.last_middle_state = middle_state
        Controller.last_ring_state = ring_state
