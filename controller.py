import pyautogui
import time

class Controller:
    hand_Landmarks = None
    screen_width, screen_height = pyautogui.size()

    last_index_state = None
    last_middle_state = None
    last_ring_state = None
    last_little_state = None

    last_index_down_time = 0
    last_index_up_time = 0
    last_little_up_time = 0
    right_drag_started = False

    left_click_pending = False
    dragging = False
    right_dragging = False

    prev_cursor_pos = None
    prev_finger_pos = None

    relative_mode = True  # Set True to use relative movement

    roi_left = 0.1
    roi_right = 0.9
    roi_top = 0.1
    roi_bottom = 0.9

    smoothing_buffer = []
    smoothing_window = 3  # last 3 movements
    speed_scale = 0.85  # Reduce speed by 15%

    @staticmethod
    def update_fingers_status():
        lm = Controller.hand_Landmarks.landmark
        Controller.index_up = lm[8].y < lm[6].y
        Controller.middle_up = lm[12].y < lm[10].y
        Controller.ring_up = lm[16].y < lm[14].y
        Controller.little_up = lm[20].y < lm[18].y

        thumb_x = lm[4].x
        index_mcp_x = lm[2].x
        Controller.thumb_extended = abs(thumb_x - index_mcp_x) > 0.03

        Controller.move_mode = Controller.index_up and Controller.middle_up and not Controller.ring_up
        Controller.freeze_mode = Controller.index_up and Controller.middle_up and Controller.ring_up
        Controller.left_click_gesture = (not Controller.index_up) and Controller.middle_up and Controller.ring_up
        Controller.drag_unlock_gesture = (not Controller.index_up) and Controller.middle_up and Controller.ring_up
        Controller.drag_stop_gesture = Controller.index_up and Controller.middle_up and Controller.ring_up

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
        if Controller.freeze_mode and not (Controller.dragging or Controller.right_dragging):
            Controller.prev_finger_pos = None
            Controller.smoothing_buffer = []  # Reset smoothing
            return

        if Controller.move_mode or Controller.dragging or Controller.right_dragging:
            point = 12  # middle finger tip
            current_x, current_y = Controller.hand_Landmarks.landmark[point].x, Controller.hand_Landmarks.landmark[point].y

            if Controller.relative_mode:
                if Controller.prev_finger_pos is not None:
                    dx = (current_x - Controller.prev_finger_pos[0]) * Controller.screen_width
                    dy = (current_y - Controller.prev_finger_pos[1]) * Controller.screen_height

                    dx *= Controller.speed_scale
                    dy *= Controller.speed_scale

                    # Add to smoothing buffer
                    Controller.smoothing_buffer.append((dx, dy))
                    if len(Controller.smoothing_buffer) > Controller.smoothing_window:
                        Controller.smoothing_buffer.pop(0)

                    avg_dx = sum(d[0] for d in Controller.smoothing_buffer) / len(Controller.smoothing_buffer)
                    avg_dy = sum(d[1] for d in Controller.smoothing_buffer) / len(Controller.smoothing_buffer)

                    if abs(avg_dx) > 1 or abs(avg_dy) > 1:  # Deadzone
                        pyautogui.moveRel(avg_dx, avg_dy, duration=0)

                Controller.prev_finger_pos = (current_x, current_y)

            else:
                x, y = Controller.get_position(current_x, current_y)
                pyautogui.moveTo(x, y, duration=0)
                Controller.prev_cursor_pos = (x, y)
                Controller.prev_finger_pos = (current_x, current_y)

    @staticmethod
    def detect_clicking():
        now = time.time()
        index_state = Controller.index_up
        middle_state = Controller.middle_up
        ring_state = Controller.ring_up
        little_state = Controller.little_up

        # ---- LEFT CLICK ----
        if not index_state and Controller.last_index_state:
            Controller.last_index_down_time = now

        if Controller.left_click_gesture and not Controller.last_index_state:
            Controller.left_click_pending = True

        if Controller.left_click_pending and index_state and not Controller.last_index_state:
            duration = now - Controller.last_index_down_time
            if duration < 1.0 and not Controller.dragging:
                pyautogui.click()
                print("Left Click")
            Controller.left_click_pending = False

        if Controller.drag_unlock_gesture and not index_state:
            if (now - Controller.last_index_down_time) > 1.3 and not Controller.dragging:
                pyautogui.mouseDown(button="left")
                Controller.dragging = True
                print("Dragging Start (Left)")

        if Controller.dragging and Controller.drag_stop_gesture:
            pyautogui.mouseUp(button="left")
            Controller.dragging = False
            print("Dragging End (Left)")

        # ---- RIGHT CLICK (SAFER) ----
        lm = Controller.hand_Landmarks.landmark
        pinky_tip = lm[20]
        pinky_mcp = lm[17]
        pinky_distance = abs(pinky_tip.y - pinky_mcp.y)

        pinky_is_confidently_up = little_state and pinky_distance > 0.05

        if pinky_is_confidently_up and not Controller.last_little_state:
            Controller.last_little_up_time = now
            Controller.right_drag_started = False

        if pinky_is_confidently_up and not Controller.right_dragging and not Controller.right_drag_started:
            if now - Controller.last_little_up_time > 1.2:
                pyautogui.mouseDown(button="right")
                Controller.right_dragging = True
                Controller.right_drag_started = True
                print("Dragging Start (Right)")

        if not pinky_is_confidently_up and Controller.last_little_state:
            held_duration = now - Controller.last_little_up_time
            if held_duration < 1.0:
                pyautogui.rightClick()
                print("Right Click")

        if Controller.right_dragging and Controller.index_up and Controller.middle_up and Controller.ring_up and not little_state:
            pyautogui.mouseUp(button="right")
            Controller.right_dragging = False
            Controller.right_drag_started = False
            print("Dragging End (Right)")

        # Update last states
        Controller.last_index_state = index_state
        Controller.last_middle_state = middle_state
        Controller.last_ring_state = ring_state
        Controller.last_little_state = little_state
