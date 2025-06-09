import pyautogui
import time

class Controller:
    hand_Landmarks = None
    screen_width, screen_height = pyautogui.size()
    last_index_state = None
    last_middle_state = None
    last_index_down_time = 0
    last_index_up_time = 0
    last_middle_down_time = 0
    last_click_time = 0
    double_clicked = False
    left_clicked = False
    right_clicked = False
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
        Controller.thumb_extended = abs(lm[4].x - lm[2].x) > 0.13
        # Move mode: index and middle up, rest closed, thumb not extended
        Controller.move_mode = Controller.index_up and Controller.middle_up and not Controller.ring_up and not Controller.little_up and not Controller.thumb_extended
        # Left click gesture: index down, thumb extended, middle up, rest closed
        Controller.left_click_gesture = (not Controller.index_up) and Controller.middle_up and not Controller.ring_up and not Controller.little_up and Controller.thumb_extended
        # Drag ready: after left click gesture, thumb closes (not extended), only middle up
        Controller.drag_ready_gesture = Controller.middle_up and not Controller.index_up and not Controller.ring_up and not Controller.little_up and not Controller.thumb_extended
        # Drag stop: thumb extended again, only middle up
        Controller.drag_stop_gesture = Controller.middle_up and not Controller.index_up and not Controller.ring_up and not Controller.little_up and Controller.thumb_extended
        # Right click gesture: middle down event with thumb extended
        Controller.right_click_gesture = (not Controller.middle_up) and Controller.thumb_extended

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
        # Freeze mouse if thumb is extended
        if Controller.thumb_extended:
            return
        # Move cursor only if move_mode is True
        if Controller.move_mode:
            point = 8  # index tip
            current_x, current_y = Controller.hand_Landmarks.landmark[point].x, Controller.hand_Landmarks.landmark[point].y
            x, y = Controller.get_position(current_x, current_y)
            pyautogui.moveTo(x, y, duration=0)
            Controller.prev_cursor_pos = (x, y)
        elif Controller.dragging:
            # During drag, move cursor even if thumb is not extended and only middle is up
            point = 8
            current_x, current_y = Controller.hand_Landmarks.landmark[point].x, Controller.hand_Landmarks.landmark[point].y
            x, y = Controller.get_position(current_x, current_y)
            pyautogui.moveTo(x, y, duration=0)
            Controller.prev_cursor_pos = (x, y)

    @staticmethod
    def detect_clicking():
        now = time.time()
        index_state = Controller.index_up
        middle_state = Controller.middle_up
        # --- Left Click & Double Click ---
        if Controller.last_index_state is None:
            Controller.last_index_state = index_state
        if Controller.left_click_gesture and not Controller.last_index_state:
            # Left click gesture detected (index just went down)
            if now - Controller.last_click_time < 0.5:
                pyautogui.doubleClick()
                print("Double Click")
                Controller.last_click_time = 0
                Controller.double_clicked = True
            else:
                pyautogui.click()
                print("Left Click")
                Controller.last_click_time = now
                Controller.left_clicked = True
            Controller.drag_ready = True  # Prepare for possible drag
        # --- Drag Start/Stop ---
        if Controller.drag_ready and Controller.drag_ready_gesture and not Controller.dragging:
            pyautogui.mouseDown(button="left")
            Controller.dragging = True
            print("Dragging Start")
        if Controller.dragging and Controller.drag_stop_gesture:
            pyautogui.mouseUp(button="left")
            Controller.dragging = False
            Controller.drag_ready = False
            print("Dragging End")
        # --- Right Click ---
        if Controller.last_middle_state is None:
            Controller.last_middle_state = middle_state
        if Controller.right_click_gesture and Controller.last_middle_state:
            pyautogui.rightClick()
            print("Right Click")
            Controller.right_clicked = True
        else:
            Controller.right_clicked = False
        Controller.last_index_state = index_state
        Controller.last_middle_state = middle_state