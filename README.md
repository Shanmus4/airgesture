# Air Gesture Control

## Project Overview

Air Gesture Control is a free and open-source application that allows you to control your computer's cursor and perform various actions using hand gestures detected via your webcam. This project utilizes hand tracking to interpret your hand movements and shapes, providing an alternative way to interact with your computer.

## Features

- Real-time cursor movement controlled by your index finger.
- Predefined gestures for common actions: Left Click, Double Click, Right Click, Scroll Up, Scroll Down, and triggering the Speech-to-Text shortcut (Win+H on Windows).
- Calibration mode to improve the accuracy of hand-to-screen mapping.
- Ability to create and assign custom hand gestures to keyboard shortcuts.

## GitHub Repository

The source code for this project is available on GitHub:
[https://github.com/Shanmus4/airgesture.git](https://github.com/Shanmus4/airgesture.git)

## Installation Guide

To set up and run the project locally, follow these steps:

1.  **Ensure you have Python 3.10 or 3.11 installed.**

2.  **Clone the repository:**
    ```bash
    git clone https://github.com/Shanmus4/airgesture.git
    ```

3.  **Navigate to the project directory:**
    ```bash
    cd airgesture
    ```

4.  **Create and activate a Python virtual environment named `myenv`:**
    Using your compatible Python executable (e.g., `python3.10` or the full path like `C:\Users\s4sha\AppData\Local\Programs\Python\Python310\python.exe`):
    ```bash
    <path_to_python_executable> -m venv myenv
    ```
    Activate the virtual environment:
    On Windows PowerShell:
    ```bash
    .\myenv\Scripts\activate
    ```
    On Git Bash or similar on Windows:
    ```bash
    source myenv/Scripts/activate
    ```
    On macOS and Linux:
    ```bash
    source myenv/bin/activate
    ```

5.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *Note: I will create the `requirements.txt` file in a later step.*

## How to Run

1.  Ensure your virtual environment is activated.
2.  Run the main script:
    ```bash
    python main.py
    ```
3.  A window showing your webcam feed will appear. You can now use hand gestures to control the cursor.

## Usage

-   **Cursor Movement:** Move your index finger to move the cursor.
-   **Calibration:** Press the 'c' key to enter/exit calibration mode. Follow the on-screen instructions (currently basic - will be improved).
-   **Custom Gesture Recording:** Press the 'r' key to enter/exit recording mode. (Currently basic - will be improved with prompts).
-   **Quit:** Press the 'q' key to exit the application.

## Technical Details (Brief)

The project uses the MediaPipe library for hand tracking to detect 21 key landmarks on the hand. OpenCV is used for handling camera input and displaying the video feed. PyAutoGUI is used to control the mouse cursor and simulate keyboard shortcuts based on recognized hand gestures. Custom gestures are captured as landmark data and stored in a JSON file.

## Deployment

This is a desktop application and does not require deployment to a server. Users can run it locally on their machines after following the installation steps.

## Task Management

Project tasks are managed using markdown files located in the `AI Assistant Reference/Tasks/` directory, categorized into `planning`, `ongoing`, and `completed`. The `PLANNING.md` file contains the overall project plan and architecture.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. *Note: I will create the LICENSE file in a later step.* 