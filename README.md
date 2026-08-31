# 🎯 NIMMO - Touchless AI Interaction Platform

**Write in the air. Control your computer with hand gestures. No keyboard. No mouse. Just your hand.**

![NIMMO](https://img.shields.io/badge/NIMMO-Touchless%20AI-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Hand%20Detection-orange)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-red)

---

## 📋 Table of Contents

1. [What is NIMMO?](#what-is-nimmo)
2. [Features](#features)
3. [Technologies Used](#technologies-used)
4. [Project Structure](#project-structure)
5. [Installation & Setup](#installation--setup)
6. [How to Run](#how-to-run)
7. [Step-by-Step Guide](#step-by-step-guide)
8. [Gesture Controls](#gesture-controls)
9. [Architecture](#architecture)
10. [Troubleshooting](#troubleshooting)
11. [Future Enhancements](#future-enhancements)

---

## 🎬 What is NIMMO?

**NIMMO** is a touchless AI interaction platform that allows you to control your computer using **hand gestures** and **finger movements** instead of physical devices like mice and keyboards.

### Key Concept
Your webcam captures your hand in real-time, MediaPipe detects 21 hand landmarks, Python interprets the finger positions, and your computer executes commands.

### Real-World Applications
- 📊 **Presentations**: Navigate slides without touching a remote
- 🏥 **Healthcare**: Touch-free interfaces for hygiene
- 🎓 **Smart Classrooms**: Interactive digital whiteboards
- 🎮 **Gaming**: Gesture-based control
- ♿ **Accessibility**: For users with mobility limitations
- 🛍️ **Public Kiosks**: Touch-free information terminals

---

## ✨ Features

### 1. **Hand Detection**
   - Detects presence of hand in real-time
   - Identifies 21 hand landmarks (joints, fingertips, palm)
   - Works with different hand sizes and positions

### 2. **Gesture Recognition**
   - **Open Hand**: All fingers extended
   - **Closed Fist**: All fingers folded
   - **Peace Sign**: Index + Middle fingers up
   - **Thumbs Up**: Thumb pointing up
   - **Pointing**: Index finger up
   - **OK Sign**: Thumb + Index touching
   - **Three Fingers**: Index + Middle + Ring up

### 3. **Cursor Control**
   - Move cursor by moving index finger
   - Click by bringing thumb and index together
   - Smooth cursor movement with acceleration
   - No lag, real-time response

### 4. **Air Writing** (Main Feature)
   - Draw/write in the air using index finger
   - Multiple color options
   - Clear canvas gesture
   - Save drawings to file

---

## 🛠️ Technologies Used

| Technology | Purpose |
|-----------|---------|
| **Python** | Main programming language |
| **OpenCV** | Webcam access & video frame processing |
| **MediaPipe** | AI-based hand detection & landmark tracking |
| **PyAutoGUI** | Mouse & keyboard control |
| **NumPy** | Numerical computations |
| **Pillow** | Image processing |

---

## 📁 Project Structure

```
Nimmo-Project/
├── requirements.txt              # Project dependencies
├── step1_hand_detection.py       # Basic hand detection
├── step2_hand_landmarks.py       # Landmark analysis
├── step3_gesture_recognition.py  # Gesture recognition
├── step4_cursor_control.py       # Mouse cursor control
├── step5_air_writing.py          # Air writing (main feature)
├── drawings/                     # Folder for saved drawings
└── README.md                     # This file
```

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Webcam connected to your computer
- Windows/Mac/Linux

### Step 1: Clone the Repository
```bash
git clone https://github.com/sanskritikapoor/Nimmo-Project.git
cd Nimmo-Project
```

### Step 2: Create Virtual Environment (Optional but Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Verify Installation
```bash
python -c "import cv2; import mediapipe as mp; print('Installation successful!')"
```

---

## 🎮 How to Run

### Run Step 1: Hand Detection
```bash
python step1_hand_detection.py
```
**What it does**: Shows if your webcam can detect hands
- Shows hand landmarks in real-time
- Press 'q' to quit

### Run Step 2: Hand Landmarks Analysis
```bash
python step2_hand_landmarks.py
```
**What it does**: Displays all 21 hand landmark coordinates
- Shows coordinates in console
- Updates every 30 frames
- Helpful for understanding hand positioning

### Run Step 3: Gesture Recognition
```bash
python step3_gesture_recognition.py
```
**What it does**: Recognizes different hand gestures
- Shows detected gesture on screen
- Practice different gestures
- Used as foundation for other steps

### Run Step 4: Cursor Control
```bash
python step4_cursor_control.py
```
**What it does**: Control your mouse cursor with hand
- Move index finger to move cursor
- Thumb + Index together = Click
- **Be careful**: This actually moves your cursor!

### Run Step 5: Air Writing (Main Feature)
```bash
python step5_air_writing.py
```
**What it does**: Write/draw in the air!
- Index finger up = Draw
- Multiple colors available
- Press 's' to save drawing
- Press 'q' to quit

---

## 📊 Step-by-Step Guide

### Understanding the Pipeline

```
Webcam Input
     ↓
OpenCV reads frame
     ↓
Convert BGR → RGB
     ↓
MediaPipe detects landmarks
     ↓
Python analyzes landmarks
     ↓
Recognize gesture/position
     ↓
Execute action (move cursor, click, draw, etc.)
     ↓
Display on screen
```

### The 21 Hand Landmarks

MediaPipe detects these points on your hand:

```
0  - Wrist
1  - Thumb CMC (base)
2  - Thumb MCP
3  - Thumb IP
4  - Thumb Tip
5  - Index MCP
6  - Index PIP
7  - Index DIP
8  - Index Tip
9  - Middle MCP
10 - Middle PIP
11 - Middle DIP
12 - Middle Tip
13 - Ring MCP
14 - Ring PIP
15 - Ring DIP
16 - Ring Tip
17 - Pinky MCP
18 - Pinky PIP
19 - Pinky DIP
20 - Pinky Tip
```

**Key Points to Remember**:
- **Tip indices**: 4, 8, 12, 16, 20 (finger tips)
- **PIP indices**: 3, 6, 10, 14, 18 (middle joints)
- Compare tip Y-coordinate with PIP Y-coordinate to determine if finger is up or down

---

## 👆 Gesture Controls

### Step 3: Gesture Recognition
| Gesture | Description | Recognition |
|---------|-------------|------------|
| Open Hand | All fingers extended | All fingers up |
| Closed Fist | All fingers folded | All fingers down |
| Peace Sign | Index + Middle up | 2 fingers up, others down |
| Thumbs Up | Thumb pointing up | Only thumb up |
| Pointing | Index finger up | Only index up |
| OK Sign | Thumb + Index close | Fingers touching, others up |

### Step 4: Cursor Control
| Action | Gesture | Result |
|--------|---------|--------|
| Move Cursor | Move index finger | Cursor follows |
| Click | Thumb + Index close | Mouse click |
| Release | Separate fingers | Stop clicking |

### Step 5: Air Writing
| Action | Gesture | Result |
|--------|---------|--------|
| Draw | Index finger up | Draws line |
| Red Color | Index only | Changes to red |
| Green Color | Index + Middle | Changes to green |
| Blue Color | Index + Middle + Ring | Changes to blue |
| Clear Canvas | Close fist | Clears drawing |
| Save | Press 's' key | Saves as PNG |

---

## 🏗️ Architecture

### Class: GestureRecognizer (Step 3)
```python
class GestureRecognizer:
    - get_landmark_coordinates()      # Extract hand positions
    - is_finger_up()                  # Check if finger extended
    - distance()                      # Calculate distances
    - recognize_gesture()             # Identify gesture
```

### Class: CursorController (Step 4)
```python
class CursorController:
    - get_landmark_coordinates()      # Extract positions
    - distance()                      # Calculate distances
    - move_cursor()                   # Move mouse cursor
    - click()                         # Perform click
    - control_cursor()                # Main control logic
```

### Class: AirWriter (Step 5)
```python
class AirWriter:
    - get_landmark_coordinates()      # Extract positions
    - is_finger_up()                  # Check finger state
    - detect_color_gesture()          # Identify color gesture
    - map_to_canvas()                 # Convert to canvas coords
    - draw_on_canvas()                # Draw line
    - process_hand()                  # Main logic
    - save_drawing()                  # Save to file
```

---

## ⚙️ Troubleshooting

### Webcam not detected
```python
# Check if webcam works:
python -c "import cv2; cap = cv2.VideoCapture(0); print(cap.isOpened())"
# Should print: True
```

### Hand not detected
- Ensure good lighting
- Position hand fully in frame
- Try different distances from camera
- Check if MediaPipe is installed: `pip install mediapipe`

### Cursor control not working
- Make sure PyAutoGUI is installed: `pip install pyautogui`
- Check if screen resolution is detected: Look at console output
- Try pressing 'q' and running again

### Drawing not appearing
- Ensure index finger is clearly visible
- Check if index finger is actually pointing up
- Try adjusting lighting

### Import errors
```bash
# Reinstall all dependencies
pip install -r requirements.txt --force-reinstall
```

---

## 🔮 Future Enhancements

### Planned Features
1. **Hand Tracking Optimization**
   - Reduce latency further
   - Better performance on low-end devices

2. **Advanced Gestures**
   - Pinch to zoom
   - Swipe gestures
   - Double-tap

3. **AI Handwriting Recognition**
   - Recognize handwritten letters
   - Convert air writing to text
   - Support multiple languages

4. **Customizable Controls**
   - Map any gesture to any action
   - Custom hotkeys
   - Settings file

5. **Multi-hand Support**
   - Detect both hands
   - Simultaneous gestures
   - Advanced interactions

6. **Performance**
   - GPU acceleration
   - Lower latency
   - Reduced CPU usage

7. **Machine Learning**
   - Train custom gesture models
   - Personalized gesture recognition
   - Adaptive learning

---

## 📚 Code Explanation

### Opening Webcam (All steps)
```python
cap = cv2.VideoCapture(0)  # 0 = default webcam
if not cap.isOpened():
    print("ERROR: Could not open webcam.")
    return
```

### Initializing MediaPipe
```python
hands = mp_hands.Hands(
    static_image_mode=False,        # Video mode
    max_num_hands=1,                # Detect 1 hand
    model_complexity=1,             # Full model
    min_detection_confidence=0.6,   # Confidence threshold
    min_tracking_confidence=0.6     # Tracking threshold
)
```

### Processing Frame
```python
# Read frame from webcam
ok, frame = cap.read()

# Flip for mirror effect
frame = cv2.flip(frame, 1)

# Convert BGR to RGB
rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

# Detect hand landmarks
result = hands.process(rgb)

# If hand detected
if result.multi_hand_landmarks:
    for hand_landmarks in result.multi_hand_landmarks:
        # Process landmarks
        mp_draw.draw_landmarks(frame, hand_landmarks, ...)
```

### Checking if Finger is Up
```python
def is_finger_up(landmarks_dict, tip_idx, pip_idx):
    """Compare Y-coordinates: if tip_y < pip_y, finger is up"""
    return landmarks_dict[tip_idx][1] < landmarks_dict[pip_idx][1]

# Example: Check if index finger is up
index_up = is_finger_up(landmarks_dict, 8, 6)
```

### Drawing on Canvas
```python
# Draw line from last point to current point
cv2.line(canvas, last_point, current_point, color, thickness)

# Save canvas
cv2.imwrite('drawing.png', canvas)
```

---

## 📝 Viva Questions & Answers

### Q1: What is NIMMO?
**A**: NIMMO is a touchless AI interaction platform that allows users to control a computer using hand gestures. The webcam captures hand movements, MediaPipe detects 21 landmarks, and Python interprets finger positions to execute commands like cursor movement, clicking, and air writing.

### Q2: How many hand landmarks does MediaPipe detect?
**A**: MediaPipe detects 21 hand landmarks, including wrist, finger joints (CMC, MCP, PIP, DIP), and finger tips.

### Q3: What algorithm does MediaPipe use?
**A**: MediaPipe uses a trained deep learning model based on convolutional neural networks (CNN) for hand detection and BlazePose-based architecture for landmark estimation.

### Q4: How do you detect if a finger is up or down?
**A**: By comparing the Y-coordinate of the finger tip with the Y-coordinate of the PIP (Proximal Interphalangeal) joint. If tip_Y < PIP_Y, the finger is up.

### Q5: What is the difference between Steps 3 and 4?
**A**: Step 3 (Gesture Recognition) identifies static gestures (like thumbs up, peace sign). Step 4 (Cursor Control) uses continuous finger position and proximity detection for dynamic cursor movement and clicking.

### Q6: Why is smoothing applied to cursor movement?
**A**: Smoothing reduces jitter and makes cursor movement more stable and natural. It uses a weighted average of previous and current positions.

### Q7: How is air writing implemented?
**A**: When the index finger is up, the program tracks its position on a virtual canvas and draws a line from the last point to the current point, creating a continuous drawing.

### Q8: What challenges do you face?
**A**: Lighting conditions, background clutter, fast hand movements, device performance, and user arm fatigue during prolonged use.

---

## 📞 Support & Contact

If you face any issues:
1. Check the **Troubleshooting** section above
2. Verify all dependencies are installed
3. Ensure your webcam is working
4. Try running Step 1 first to test webcam

---

## 📄 License

This project is open source and available for educational purposes.

---

## 🎓 Project Information

**Project Name**: NIMMO - Touchless AI Interaction Platform  
**Type**: Computer Vision + AI Project  
**Language**: Python  
**Technologies**: OpenCV, MediaPipe, PyAutoGUI  
**Suitable For**: BCA Data Science, AI/ML Projects  

---

## 🙌 Acknowledgments

- **MediaPipe**: For the amazing hand detection model
- **OpenCV**: For computer vision utilities
- **PyAutoGUI**: For system automation

---

**Happy Coding! ✨**

*Write in the air. Control with gestures. Experience the future of interaction.*
