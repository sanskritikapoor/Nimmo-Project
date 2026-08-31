"""
NIMMO - Step 3: Gesture Recognition
====================================
This module recognizes basic hand gestures from landmark positions.

Gestures recognized:
1. Open Hand: All fingers extended
2. Closed Fist: All fingers folded
3. Peace Sign: Index and middle fingers up, others down
4. Thumbs Up: Thumb pointing up, others folded
5. Pointing: Index finger up, others folded
6. OK Sign: Index and thumb touching, others extended

What happens here:
1. Detects landmarks
2. Calculates finger positions (up/down)
3. Recognizes gestures based on finger positions
4. Displays gesture name on screen
"""

import cv2
import mediapipe as mp
import math

# Import MediaPipe hand detection modules
try:
    mp_hands = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils
    mp_styles = mp.solutions.drawing_styles
except AttributeError:
    from mediapipe.python.solutions import hands as mp_hands
    from mediapipe.python.solutions import drawing_utils as mp_draw
    from mediapipe.python.solutions import drawing_styles as mp_styles


class GestureRecognizer:
    """
    Class to recognize hand gestures based on landmark positions.
    """
    
    def __init__(self):
        """Initialize gesture recognizer."""
        pass
    
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
    
    def is_finger_up(self, landmarks_dict, tip_idx, pip_idx):
        """
        Check if a finger is up (tip is above PIP joint).
        
        Args:
            landmarks_dict: Dictionary of landmark positions
            tip_idx: Index of finger tip
            pip_idx: Index of PIP joint
        
        Returns:
            True if finger is up, False otherwise
        """
        tip_y = landmarks_dict[tip_idx][1]
        pip_y = landmarks_dict[pip_idx][1]
        return tip_y < pip_y
    
    def distance(self, point1, point2):
        """
        Calculate Euclidean distance between two points.
        """
        return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    def recognize_gesture(self, hand_landmarks, frame_shape):
        """
        Recognize gesture from hand landmarks.
        
        Returns:
            String with gesture name
        """
        landmarks_dict = self.get_landmark_coordinates(hand_landmarks, frame_shape)
        
        # Finger tip indices: 4(thumb), 8(index), 12(middle), 16(ring), 20(pinky)
        # PIP joint indices: 3(thumb), 6(index), 10(middle), 14(ring), 18(pinky)
        
        thumb_up = self.is_finger_up(landmarks_dict, 4, 3)
        index_up = self.is_finger_up(landmarks_dict, 8, 6)
        middle_up = self.is_finger_up(landmarks_dict, 12, 10)
        ring_up = self.is_finger_up(landmarks_dict, 16, 14)
        pinky_up = self.is_finger_up(landmarks_dict, 20, 18)
        
        # Check if fingers are close (touching)
        thumb_index_distance = self.distance(landmarks_dict[4], landmarks_dict[8])
        
        # Gesture recognition logic
        
        # Open Hand: All fingers up
        if thumb_up and index_up and middle_up and ring_up and pinky_up:
            return "OPEN HAND"
        
        # Closed Fist: All fingers down
        if not thumb_up and not index_up and not middle_up and not ring_up and not pinky_up:
            return "CLOSED FIST"
        
        # Peace Sign: Index and middle up, others down
        if index_up and middle_up and not thumb_up and not ring_up and not pinky_up:
            return "PEACE SIGN"
        
        # Thumbs Up: Thumb up, others down
        if thumb_up and not index_up and not middle_up and not ring_up and not pinky_up:
            return "THUMBS UP"
        
        # Pointing: Index up, others down
        if index_up and not middle_up and not ring_up and not pinky_up and not thumb_up:
            return "POINTING"
        
        # OK Sign: Thumb and index close, others up
        if thumb_index_distance < 50 and middle_up and ring_up and pinky_up:
            return "OK SIGN"
        
        # Three Fingers: Index, middle, ring up
        if index_up and middle_up and ring_up and not pinky_up:
            return "THREE FINGERS"
        
        return "UNKNOWN"


def main():
    """
    Main function for gesture recognition.
    """
    # Open webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("ERROR: Could not open webcam.")
        return
    
    # Initialize MediaPipe Hand Landmarker
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        model_complexity=1,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.6,
    )
    
    # Initialize gesture recognizer
    gesture_recognizer = GestureRecognizer()
    
    print("Gesture Recognition started. Press 'q' to quit.")
    print("\nAvailable gestures:")
    print("- Open Hand")
    print("- Closed Fist")
    print("- Peace Sign")
    print("- Thumbs Up")
    print("- Pointing")
    print("- OK Sign")
    print("- Three Fingers")
    
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
                
                # Recognize gesture
                gesture_name = gesture_recognizer.recognize_gesture(hand_landmarks, frame.shape)
        
        # Add text on frame
        cv2.putText(frame, "NIMMO - Step 3: Gesture Recognition", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # Display recognized gesture
        if gesture_name == "No hand detected":
            cv2.putText(frame, gesture_name, (10, 65),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        else:
            cv2.putText(frame, f"Gesture: {gesture_name}", (10, 65),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        cv2.putText(frame, "Press 'q' to quit", (10, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # Display frame
        cv2.imshow("NIMMO - Gesture Recognition", frame)
        
        # Exit if 'q' is pressed
        if (cv2.waitKey(1) & 0xFF) == ord("q"):
            break
    
    # Cleanup
    hands.close()
    cap.release()
    cv2.destroyAllWindows()
    print("Gesture Recognition stopped.")


if __name__ == "__main__":
    main()
