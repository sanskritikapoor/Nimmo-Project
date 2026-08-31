"""
NIMMO - Step 6: Presentation Control
====================================
This module allows you to control presentations/slideshows using hand gestures.

Features:
1. Next Slide: Peace sign (index + middle fingers up)
2. Previous Slide: Thumbs down
3. Go to First Slide: Open hand (all fingers up)
4. Go to Last Slide: Closed fist (all fingers down)
5. Pause/Resume: OK sign (thumb + index touching)
6. Fullscreen Toggle: Pointing gesture (index only)

What happens here:
1. Detects hand landmarks
2. Recognizes gestures for presentation control
3. Sends keyboard commands to control presentation
4. Works with PowerPoint, Google Slides, Keynote, etc.

Keyboard Commands Used:
- Next Slide: Right Arrow Key
- Previous Slide: Left Arrow Key
- First Slide: Home Key
- Last Slide: End Key
- Fullscreen: F5 (PowerPoint)
- Escape: Esc Key
"""

import cv2
import mediapipe as mp
import pyautogui
import math
import time

# Import MediaPipe hand detection modules
try:
    mp_hands = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils
    mp_styles = mp.solutions.drawing_styles
except AttributeError:
    from mediapipe.python.solutions import hands as mp_hands
    from mediapipe.python.solutions import drawing_utils as mp_draw
    from mediapipe.python.solutions import drawing_styles as mp_styles


class PresentationController:
    """
    Class to control presentations using hand gestures.
    """
    
    def __init__(self):
        """Initialize presentation controller."""
        self.last_gesture_time = 0
        self.gesture_cooldown = 1.0  # 1 second cooldown between gestures
        self.current_slide = 1
        self.total_slides = 0
    
    def get_landmark_coordinates(self, hand_landmarks, frame_shape):
        """
        Extract coordinates of all hand landmarks.
        """
        h, w, c = frame_shape
        landmarks_dict = {}
        
        for idx, lm in enumerate(hand_landmarks.landmark):
            x = int(lm.x * w)
            y = int(lm.y * h)
            landmarks_dict[idx] = (x, y)
        
        return landmarks_dict
    
    def distance(self, point1, point2):
        """
        Calculate Euclidean distance between two points.
        """
        return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    def is_finger_up(self, landmarks_dict, tip_idx, pip_idx):
        """
        Check if a finger is up (tip is above PIP joint).
        """
        tip_y = landmarks_dict[tip_idx][1]
        pip_y = landmarks_dict[pip_idx][1]
        return tip_y < pip_y
    
    def can_perform_gesture(self):
        """
        Check if enough time has passed since last gesture.
        Prevents accidental double gestures.
        """
        current_time = time.time()
        if current_time - self.last_gesture_time > self.gesture_cooldown:
            self.last_gesture_time = current_time
            return True
        return False
    
    def recognize_presentation_gesture(self, hand_landmarks, frame_shape):
        """
        Recognize gestures for presentation control.
        
        Returns:
            Tuple: (gesture_name, action_performed)
        """
        landmarks_dict = self.get_landmark_coordinates(hand_landmarks, frame_shape)
        
        # Get finger positions
        thumb_up = self.is_finger_up(landmarks_dict, 4, 3)
        index_up = self.is_finger_up(landmarks_dict, 8, 6)
        middle_up = self.is_finger_up(landmarks_dict, 12, 10)
        ring_up = self.is_finger_up(landmarks_dict, 16, 14)
        pinky_up = self.is_finger_up(landmarks_dict, 20, 18)
        
        # Get thumb and index positions
        thumb_tip = landmarks_dict[4]
        index_tip = landmarks_dict[8]
        thumb_index_distance = self.distance(thumb_tip, index_tip)
        
        # Get wrist and hand positions for thumbs down detection
        wrist = landmarks_dict[0]
        thumb_base = landmarks_dict[2]
        
        # Gesture Recognition
        
        # 1. Peace Sign = Next Slide
        if index_up and middle_up and not thumb_up and not ring_up and not pinky_up:
            if self.can_perform_gesture():
                pyautogui.press('right')
                self.current_slide += 1
                return ("PEACE SIGN", "NEXT SLIDE")
            return ("PEACE SIGN", "COOLDOWN")
        
        # 2. Thumbs Down = Previous Slide (thumb down relative to wrist)
        if not index_up and not middle_up and not ring_up and not pinky_up and thumb_up:
            # Check if thumb is pointing down (thumb_tip below wrist)
            if thumb_tip[1] > wrist[1] + 50:  # Thumb significantly below wrist
                if self.can_perform_gesture():
                    pyautogui.press('left')
                    self.current_slide -= 1
                    return ("THUMBS DOWN", "PREVIOUS SLIDE")
                return ("THUMBS DOWN", "COOLDOWN")
        
        # 3. Open Hand = First Slide
        if thumb_up and index_up and middle_up and ring_up and pinky_up:
            if self.can_perform_gesture():
                pyautogui.press('home')
                self.current_slide = 1
                return ("OPEN HAND", "FIRST SLIDE")
            return ("OPEN HAND", "COOLDOWN")
        
        # 4. Closed Fist = Last Slide
        if not thumb_up and not index_up and not middle_up and not ring_up and not pinky_up:
            if self.can_perform_gesture():
                pyautogui.press('end')
                self.current_slide = self.total_slides
                return ("CLOSED FIST", "LAST SLIDE")
            return ("CLOSED FIST", "COOLDOWN")
        
        # 5. OK Sign = Pause/Resume (toggle)
        if thumb_index_distance < 50 and middle_up and ring_up and pinky_up:
            if self.can_perform_gesture():
                pyautogui.press('space')
                return ("OK SIGN", "PAUSE/RESUME")
            return ("OK SIGN", "COOLDOWN")
        
        # 6. Pointing = Fullscreen Toggle
        if index_up and not middle_up and not ring_up and not pinky_up and not thumb_up:
            if self.can_perform_gesture():
                pyautogui.press('f5')
                return ("POINTING", "FULLSCREEN")
            return ("POINTING", "COOLDOWN")
        
        # 7. Three Fingers = Escape (exit presentation)
        if index_up and middle_up and ring_up and not pinky_up:
            if self.can_perform_gesture():
                pyautogui.press('esc')
                return ("THREE FINGERS", "EXIT PRESENTATION")
            return ("THREE FINGERS", "COOLDOWN")
        
        return ("UNKNOWN", "READY")
    
    def get_gesture_description(self, gesture):
        """
        Get human-readable description of gesture.
        """
        descriptions = {
            "PEACE SIGN": "Next Slide →",
            "THUMBS DOWN": "Previous Slide ←",
            "OPEN HAND": "First Slide (Home)",
            "CLOSED FIST": "Last Slide (End)",
            "OK SIGN": "Pause/Resume (Space)",
            "POINTING": "Fullscreen (F5)",
            "THREE FINGERS": "Exit (Esc)",
            "UNKNOWN": "Unknown Gesture"
        }
        return descriptions.get(gesture, "Unknown")


def main():
    """
    Main function for presentation control.
    """
    # Open webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("ERROR: Could not open webcam.")
        return
    
    # Get frame size
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Initialize MediaPipe Hand Landmarker
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        model_complexity=1,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.6,
    )
    
    # Initialize presentation controller
    presenter = PresentationController()
    
    print("=" * 70)
    print("NIMMO - Presentation Control Started")
    print("=" * 70)
    print("\nGesture Controls:")
    print("1. PEACE SIGN (✌️)           → Next Slide (Right Arrow)")
    print("2. THUMBS DOWN (👎)          → Previous Slide (Left Arrow)")
    print("3. OPEN HAND (✋)             → First Slide (Home)")
    print("4. CLOSED FIST (✊)           → Last Slide (End)")
    print("5. OK SIGN (👌)              → Pause/Resume (Space)")
    print("6. POINTING (☝️)             → Fullscreen (F5)")
    print("7. THREE FINGERS (✌️+👊)    → Exit Presentation (Esc)")
    print("\nPress 'q' in window to quit")
    print("Make sure PowerPoint/Google Slides is running!")
    print("=" * 70 + "\n")
    
    gesture_history = []
    
    while True:
        ok, frame = cap.read()
        
        if not ok:
            break
        
        # Flip frame for selfie view
        frame = cv2.flip(frame, 1)
        
        # Convert to RGB
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process frame
        result = hands.process(rgb)
        
        gesture_name = "No hand detected"
        action = "Waiting for hand"
        
        # If hands are detected
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                # Draw landmarks
                mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_styles.get_default_hand_landmarks_style(),
                    mp_styles.get_default_hand_connections_style(),
                )
                
                # Recognize presentation gesture
                gesture_name, action = presenter.recognize_presentation_gesture(
                    hand_landmarks, frame.shape
                )
                
                # Add to history
                if action != "COOLDOWN":
                    gesture_history.append(gesture_name)
                    if len(gesture_history) > 5:
                        gesture_history.pop(0)
        
        # Add background for better text visibility
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (frame_width, 250), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
        
        # Add text on frame
        cv2.putText(frame, "NIMMO - Presentation Control", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
        
        # Display current gesture
        if gesture_name == "No hand detected":
            cv2.putText(frame, "No hand detected - Show your hand!", (10, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            color = (0, 0, 255)
        else:
            color = (0, 255, 0)
            if "COOLDOWN" in action:
                color = (0, 165, 255)  # Orange
        
        # Show gesture and action
        cv2.putText(frame, f"Gesture: {gesture_name}", (10, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        cv2.putText(frame, f"Action: {action}", (10, 160),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
        # Show slide number if available
        if presenter.current_slide > 0:
            cv2.putText(frame, f"Slide: {presenter.current_slide}", (10, 200),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
        
        cv2.putText(frame, "Press 'q' to quit", (frame_width - 300, frame_height - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # Display frame
        cv2.imshow("NIMMO - Presentation Control", frame)
        
        # Exit if 'q' is pressed
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
    
    # Cleanup
    hands.close()
    cap.release()
    cv2.destroyAllWindows()
    print("\nPresentation Control stopped.")
    print(f"Total gestures detected: {len(gesture_history)}")


if __name__ == "__main__":
    main()
