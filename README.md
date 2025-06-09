# Air Gesture Control

## Project Overview
Air Gesture Control is a Python desktop application that enables users to control their computer's mouse cursor through intuitive hand gestures captured via a webcam. This project aims to provide an alternative and accessible method of computer interaction, particularly useful for various applications including presentations, accessibility, and hands-free computing.

## Purpose and Features
This application transforms real-time hand movements into precise mouse actions, offering a seamless and natural control experience. Key features include:
-   **Cursor Movement:** Control the mouse cursor by moving your hand.
-   **Click Actions:** Perform left, right, and double clicks with distinct hand gestures.
-   **Drag and Drop:** Initiate and control drag-and-drop operations.
-   **Scrolling:** Scroll up and down through documents and web pages.
-   **Zoom:** Zoom in and out using specific hand gestures.
-   **Gesture Freezing:** Pause cursor movement with a designated gesture.

## GitHub Repository
Access the project source code on GitHub: [https://github.com/Shanmus4/airgesture.git](https://github.com/Shanmus4/airgesture.git)

## Installation Guide
To set up and run the Air Gesture Control application locally, follow these steps:

### 1. Clone the Repository
```bash
git clone https://github.com/Shanmus4/airgesture.git
cd airgesture
```

### 2. Set Up a Virtual Environment (Recommended)
It's highly recommended to use a virtual environment to manage project dependencies.

```bash
python -m venv venv
```

### 3. Activate the Virtual Environment
-   **Windows:**
    ```bash
    .\venv\Scripts\activate
    ```
-   **macOS/Linux:**
    ```bash
    source venv/bin/activate
    ```

### 4. Install Dependencies
Install the required Python packages using `pip` and the provided `requirements.txt` file. This ensures you have the correct versions of all libraries.

```bash
pip install -r requirements.txt
```

### 5. Run the Application
Once the dependencies are installed, you can run the main application script:

```bash
python app.py
```

Ensure you have a webcam connected and properly configured. The application window will display the live video feed with hand landmark visualizations.

## How the Project Works Technically
The Air Gesture Control application is built on a robust computer vision pipeline:

-   **MediaPipe Integration:** Utilizes Google's MediaPipe Hands solution for real-time, accurate detection of 21 3D hand landmarks from a live video stream.
-   **OpenCV for Camera Interaction:** Employs OpenCV to access and manage the webcam feed, processing each frame for hand detection.
-   **PyAutoGUI for System Control:** Translates recognized hand gestures into system-level mouse and keyboard events using PyAutoGUI, allowing for cursor movement, clicks, drags, and more.
-   **Modular Design:** The core logic is separated into `app.py` (main application flow, video processing) and `controller.py` (gesture recognition and mouse/keyboard control), promoting modularity and maintainability.

## Deployment Instructions
(Currently, there are no specific deployment instructions as this is a desktop application. Future iterations may include packaging options.)

## How to Run
After installing the required libraries, run the `app.py` file in a Python environment with a webcam. The program will start capturing video from the webcam, and the mouse cursor can be controlled using the following hand gestures:

  - **Move cursor**: Only index finger pointed up.
  - **Freeze cursor**: Index finger pointed up and thumb extended.
  - **Left click**: Index and thumb finger touch.
  - **Double click**: Index and thumb finger touch twice quickly.
  - **Drag and drop**: Index finger and thumb touch and move.
  - **Right-click**: Middle finger and thumb touch.

## Demo
The repository includes some demo GIFs to help you understand how to use hand gestures to control the mouse. The GIFs show the different hand gestures and their corresponding mouse actions in action, making it easy to follow along and learn how to use the program. To view the demo GIFs, simply navigate to the `demo/` folder in the repository and open the GIFs using any image viewer.

Hopefully these demos make it easier for you to get started with the program and learn how to use it effectively. If you have any questions or feedback, feel free to reach out to us!

## How it Works
The program uses the Mediapipe library to detect hand landmarks from the video captured by the webcam. The `controller.py` file contains the logic for mapping the hand landmarks to specific mouse cursor actions, such as movement and clicking.

## Limitations
The program currently only supports controlling a single mouse cursor, and it may not work well in low-light conditions. It also doesn't support handling gestures of more than one hand, however this is easy to overcome, may be in comming commits of this project.

## License

This project is licensed under the Apache License 2.0. The Apache License 2.0 is a permissive license that allows you to freely use, modify, distribute, and sell the software.<br>

Feel free to use, modify and distribute the code as you see fit under the terms of the Apache License 2.0. For more information, please refer to the LICENSE file in the root of the project directory.
