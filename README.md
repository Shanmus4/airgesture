# Air Gesture Desktop Control

A Python desktop app that lets you control your mouse and perform actions using hand gestures, with a live camera feed and controls in a modern web UI.

## Features
- **Remi-based Web UI**: All controls and camera feed are in a single web interface (no separate OpenCV window).
- **Calibration**: Calibrate your hand position to your screen with a step-by-step wizard.
- **Gesture Legend**: See a live legend of all predefined gestures and their actions.
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
   python src/app.py
   ```
4. **Open the UI:**
   - Go to [http://localhost:8081](http://localhost:8081) in your browser.

## Usage
- **Calibrate**: Click 'Calibrate' and follow the on-screen instructions to map your hand to your screen.
- **Show Gestures**: Click to see a legend of all available gestures.
- **Test**: Click 'Test' to start live gesture control. Use the gestures to control your desktop.

## Architecture
- **Python** backend with modular structure
- **MediaPipe** for hand tracking
- **OpenCV** for image processing
- **PyAutoGUI** for OS interaction
- **Remi** for the web-based UI

## Deployment
- Local only (for now). To run on another machine, change the address in `src/app.py`.

## Notes
- No secrets or credentials are required.
- All camera and gesture overlays are shown in the web UI.
- No OpenCV window is used.

## Links
- [GitHub Repo](<repo-url>)
- (Add live demo link if available)

## Task Management

Project tasks are managed using markdown files located in the `AI Assistant Reference/Tasks/` directory, categorized into `