# Air Gesture Desktop Control

A Python desktop app that lets you control your mouse and perform actions using hand gestures, with a live camera feed shown in a separate window and controls in a web UI.

## Features
- **Separate Camera Feed**: The live camera feed is displayed in a dedicated OpenCV window for better performance.
- **Remi-based Web UI**: A web interface provides controls for calibration, showing gestures, and starting the app.
- **Calibration**: Calibrate your hand position to your screen with a step-by-step wizard.
- **Gesture Legend**: See a legend of all predefined gestures and their actions in the UI.
- **Test Mode**: Use predefined gestures to control your desktop in real time.

## Predefined Gestures
- **Left Click**: Pinch index finger and thumb
- **Double Click**: Two quick pinches
- **Right Click**: Index and middle fingers up, others down, thumb out
- **Scroll Up**: All fingers except thumb up
- **Scroll Down**: All fingers except thumb down
- **Speech-to-Text**: Only pinky up

## Installation

1. **Clone the repo:**
   ```sh
   git clone <repo-url>
   cd <repo-folder>
   ```
2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
3. **Run the app:**
   ```sh
   python main.py
   ```
4. **Open the UI:**
   - Go to [http://localhost:8081](http://localhost:8081) in your browser.

## Usage
- **Camera Feed**: An OpenCV window will open showing your camera feed. Keep this window open.
- **Calibrate**: Click 'Calibrate' in the UI and follow the on-screen instructions to map your hand to your screen.
- **Show Gestures**: Click 'Show Gestures' in the UI to see a legend of all available gestures.
- **Test**: Click 'Test' in the UI to start live gesture control. Use the gestures to control your desktop.

## Architecture
- **Python** backend with modular structure
- **MediaPipe** for hand tracking
- **OpenCV** for image processing and camera feed display
- **PyAutoGUI** for OS interaction
- **Remi** for the web-based UI

## Deployment
- Local only (for now). To run on another machine, change the address in `main.py`.

## Notes
- No secrets or credentials are required.
- The camera feed is displayed in a separate OpenCV window.
- UI elements in the browser are for control and feedback only, not camera display.

## Links
- [GitHub Repo](<repo-url>)
- (Add live demo link if available)

## Task Management

Project tasks are managed using markdown files located in the `AI Assistant Reference/Tasks/` directory, categorized into 