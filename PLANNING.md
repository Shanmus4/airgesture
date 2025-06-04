# Air Gesture Control Project Planning

## Project Overview

This project aims to create a free and open-source application that allows users to control their computer cursor and perform various actions using hand gestures detected via a webcam.

**Goals:**
- Provide intuitive cursor control based on hand movement.
- Implement predefined hand gestures for common actions (clicks, scrolling, speech-to-text).
- Develop a calibration mode for improved accuracy.
- Enable users to create and assign custom hand gestures to specific actions or keyboard shortcuts.
- Ensure the project is entirely free and open-source, using only permissive licenses.

## Architecture and Modules

The project will be structured into several key modules:

1.  **Hand Tracking Module:** Utilizes a library like MediaPipe to detect hands and provide landmark coordinates in real-time.
2.  **Image Processing Module:** Handles camera input, image manipulation (like flipping and color conversion), and drawing annotations.
3.  **Gesture Recognition Module:** Analyzes hand landmark data to identify predefined and custom gestures.
4.  **Operating System Interaction Module:** Uses a library like PyAutoGUI to control the mouse cursor, simulate clicks, scrolling, and execute keyboard shortcuts.
5.  **Calibration Module:** Implements a process to map hand positions in the camera feed to screen coordinates accurately.
6.  **Custom Gesture Management Module:** Manages the recording, storing, loading, and recognition of custom user-defined gestures.
7.  **User Interface (Implicit):** While not a separate graphical UI module initially, visual feedback on the camera feed and potentially terminal prompts will serve as the user interface for calibration and custom gesture recording.

## Tech Stack

-   **Primary Language:** Python
-   **Hand Tracking:** MediaPipe
-   **Image Processing:** OpenCV (`opencv-python`)
-   **OS Interaction:** PyAutoGUI (`pyautogui`)
-   **Gesture Storage:** JSON file (`custom_gestures.json`)
-   **Virtual Environment:** `venv`

## Naming Conventions and Patterns

-   Use `snake_case` for variable and function names in Python.
-   Use clear and descriptive names for files and directories.
-   Organize code logically into functions and potentially separate files as the project grows, grouped by functionality.
-   Avoid hardcoding secrets (though none are anticipated for this project).

## Workflow

1.  Initialize hand tracking and camera feed.
2.  Continuously read frames from the camera.
3.  Process frames to detect hands and landmarks.
4.  In Calibration Mode, capture hand positions for mapping.
5.  In Custom Gesture Recording Mode, capture landmark data for a gesture.
6.  In Normal Operation, use hand position (and calibration mapping) to move the cursor.
7.  Analyze hand landmarks to recognize predefined or custom gestures.
8.  If a gesture is recognized, trigger the corresponding OS action.
9.  Display the camera feed with annotations.
10. Handle user input (key presses) for mode switching (calibrate, record, quit).

## Current Status (as of YYYY-MM-DD)

-   **Environment Setup:** Successfully set up a Python virtual environment (`myenv`) using Python 3.10 and installed required dependencies (`mediapipe`, `opencv-python`, `pyautogui`) via `requirements.txt`.
-   Initial `main.py` created with:
    -   Hand tracking and real-time cursor movement based on index finger tip.
    -   Basic gesture recognition logic for Left Click, Double Click, Right Click, Scroll Up, Scroll Down, and Speech-to-Text (Win+H).
    -   Improved calibration mode with guided point capture, perspective transformation, visual feedback, and reset functionality.
    -   Toggle for custom gesture recording mode and basic capture/saving/loading.
    -   Enhanced custom gesture recognition using feature extraction.
    -   Added temporary visual feedback for modes, gestures, and actions.

## Future Tasks and Enhancements

-   Refine Calibration Mode for a more user-guided process.
-   Implement the `recognize_custom_gesture` function using a suitable distance metric.
-   Implement execution of actions associated with recognized custom gestures (using `pyautogui`).
-   Improve gesture recognition accuracy and robustness.
-   Add visual feedback on the camera feed for recognized gestures and modes.
-   Consider handling multiple hands.
-   Develop a more robust method for associating recorded gestures with actions (e.g., a simple configuration interface or prompts that don't block the video feed).
-   Create a `requirements.txt` file for dependencies.
-   Write a comprehensive `README.md`.
-   Set up the task management structure under `AI Assistant Reference/Tasks/`.

This plan will be updated as the project progresses. 