import pyautogui
import time

class Controller:
    hand_Landmarks = None
    screen_width, screen_height = pyautogui.size()
    last_index_state = None
    last_index_down_time = 0
    last_index_up_time = 0
    last_click_time = 0
    click_count = 0
    dragging = False
    drag_start_time = 0
    drag_min_duration = 0.5  # seconds to start drag
    left_clicked = False
    right_clicked = False
    double_clicked = False
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
        Controller.thumb_up = lm[4].x < lm[3].x if lm[4].x < lm[2].x else lm[4].x > lm[3].x  # crude, not used for gestures
        # Only index up (all others down)
        Controller.only_index_up = Controller.index_up and not Controller.middle_up and not Controller.ring_up and not Controller.little_up
        # Both index and middle up, others down
        Controller.index_and_middle_up = Controller.index_up and Controller.middle_up and not Controller.ring_up and not Controller.little_up
        # All fingers closed (down)
        Controller.all_fingers_down = not Controller.index_up and not Controller.middle_up and not Controller.ring_up and not Controller.little_up

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
        # Move cursor only if only index finger is up and not dragging
        if Controller.only_index_up and not Controller.dragging:
            point = 8
            current_x, current_y = Controller.hand_Landmarks.landmark[point].x, Controller.hand_Landmarks.landmark[point].y
            x, y = Controller.get_position(current_x, current_y)
            pyautogui.moveTo(x, y, duration=0)
            Controller.prev_cursor_pos = (x, y)
        elif Controller.dragging:
            # During drag, move cursor even if all fingers are down
            point = 8
            current_x, current_y = Controller.hand_Landmarks.landmark[point].x, Controller.hand_Landmarks.landmark[point].y
            x, y = Controller.get_position(current_x, current_y)
            pyautogui.moveTo(x, y, duration=0)
            Controller.prev_cursor_pos = (x, y)

    @staticmethod
    def detect_clicking():
        now = time.time()
        # Detect index finger down/up transitions
        index_state = Controller.index_up
        if Controller.last_index_state is None:
            Controller.last_index_state = index_state
        # Index finger down event
        if not index_state and Controller.last_index_state:
            Controller.last_index_down_time = now
        # Index finger up event
        if index_state and not Controller.last_index_state:
            Controller.last_index_up_time = now
            # If not dragging, check for click/double click
            if not Controller.dragging:
                down_duration = Controller.last_index_up_time - Controller.last_index_down_time
                if down_duration < 0.4:
                    # Check for double click
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
        Controller.last_index_state = index_state

        # Right click: both index and middle up, others down
        if Controller.index_and_middle_up and not Controller.right_clicked:
            pyautogui.rightClick()
            print("Right Click")
            Controller.right_clicked = True
        elif not Controller.index_and_middle_up:
            Controller.right_clicked = False

    @staticmethod
    def detect_dragging():
        now = time.time()
        # Drag: all fingers closed (index down), hold for >drag_min_duration
        if Controller.all_fingers_down and not Controller.dragging:
            if Controller.last_index_down_time > 0 and (now - Controller.last_index_down_time) > Controller.drag_min_duration:
                pyautogui.mouseDown(button="left")
                Controller.dragging = True
                print("Dragging Start")
        elif not Controller.all_fingers_down and Controller.dragging:
            pyautogui.mouseUp(button="left")
            Controller.dragging = False
            print("Dragging End")