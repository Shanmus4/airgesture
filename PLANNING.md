# Project Planning for Air Gesture Control

## Overall Architecture
The project is a Python desktop application designed to control the mouse cursor using hand gestures. It leverages computer vision libraries to detect hand landmarks and translates these detections into mouse actions.

- **Input Layer:** Webcam captures live video feed.
- **Hand Landmark Detection:** MediaPipe library processes video frames to detect and track hand landmarks.
- **Gesture Recognition & Control Logic:** A `Controller` class (in `controller.py`) interprets hand landmark data to recognize specific gestures and translate them into mouse and keyboard actions.
- **Output Layer:** PyAutoGUI library performs mouse movements, clicks, scrolls, and other interactions on the operating system level.

## Workflows
1.  **Application Start:** `app.py` initializes the webcam and MediaPipe hand detection.
2.  **Frame Processing Loop:** Continuously captures frames from the webcam.
3.  **Hand Detection:** MediaPipe processes each frame to identify hand landmarks.
4.  **Gesture Interpretation:** If hand landmarks are detected, `controller.py`'s `Controller` class updates the status of fingers and calls functions to detect various gestures.
5.  **Mouse Control:** Based on the detected gestures, PyAutoGUI functions are called to control the mouse cursor (move, left/right click, left/right drag, freeze).
6.  **Display:** The processed video feed with hand landmarks is displayed to the user.

## Gesture Mapping (Updated)
- **Move cursor:** Index and middle fingers up, ring finger down.
- **Freeze cursor:** Index, middle, and ring fingers all up.
- **Left click:** Index down (tap), middle and ring up. (If index is held down for more than ~1s, drag will start instead.)
- **Left drag:** Hold index down for more than ~1.3s (with middle and ring up), then move your hand. Drag stops when all three (index, middle, ring) are up.
- **Right click:** Quick tap of little finger up (all other fingers up), or all up + thumb extended.
- **Right drag:** Hold little finger up for more than ~1.2s (all other fingers up), then move your hand. Drag stops when all fingers are up.

## Goals
-   Provide a fully functioning MVP for hand gesture-based mouse control using the new gesture set.
-   Implement a modular and clean code structure.
-   Ensure all required dependencies are clearly documented with their latest stable versions.
-   Maintain comprehensive and up-to-date documentation (`README.md` and `PLANNING.md`).
-   Allow for future expansion with additional gestures and UI elements (e.g., calibration, hand position visualization).

## Tech Stack
-   **Python 3.x**
-   **OpenCV:** For webcam interaction and image processing.
-   **MediaPipe:** For real-time hand landmark detection.
-   **PyAutoGUI:** For programmatic control of mouse and keyboard.

## Naming Conventions
-   **Files:** `snake_case.py` (e.g., `app.py`, `controller.py`).
-   **Classes:** `CamelCase` (e.g., `Controller`).
-   **Functions/Methods:** `snake_case` (e.g., `cursor_moving`, `detect_clicking`).
-   **Variables:** `snake_case`.

## Task Management Structure
This project will follow the task management structure under `AI Assistant Reference/`:
-   `AI Assistant Reference/Tasks/planning/`
-   `AI Assistant Reference/Tasks/ongoing/`
-   `AI Assistant Reference/Tasks/completed/`

Each task will be a single file with a timestamp in its filename. Tasks will be moved between folders as progress happens. New features or changes will update both the appropriate task file and `PLANNING.md`. This folder will be `.gitignored`. 