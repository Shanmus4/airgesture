# Module for operating system interaction 

import pyautogui

class OSInteractor:
    def __init__(self):
        self.screen_width, self.screen_height = pyautogui.size()

    def move_to(self, x, y):
        """Moves the mouse cursor to the specified screen coordinates."""
        pyautogui.moveTo(x, y)

    def left_click(self):
        """Performs a left mouse click."""
        pyautogui.click()

    def double_click(self):
        """Performs a double left mouse click."""
        pyautogui.doubleClick()

    def right_click(self):
        """Performs a right mouse click."""
        pyautogui.rightClick()

    def scroll_up(self, amount=10):
        """Scrolls up by the specified amount."""
        pyautogui.scroll(amount)

    def scroll_down(self, amount=10):
        """Scrolls down by the specified amount."""
        pyautogui.scroll(-amount)

    def press_hotkey(self, *keys):
        """Presses a combination of keys (hotkey)."""
        pyautogui.hotkey(*keys)

    # Add methods for OS interactions here 