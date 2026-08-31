"""
NIMMO - Step 4: Cursor Control
==============================
This module controls the mouse cursor based on hand gestures.

Features:
1. Move cursor: Move index finger to move cursor
2. Click: Bring thumb and index finger together to click
3. Drag: Thumb and index together while moving

What happens here:
1. Detects hand landmarks
2. Uses index fingertip position for cursor movement
3. Detects thumb-index proximity for clicking
4. Moves system cursor using PyAutoGUI
"""

import cv2
import mediapipe as mp
import pyautogui
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

# Disable PyAutoGUI failsafe (moving mouse to corner won't stop)
pyautogui.FAILSAFE = False


class CursorController:
    """
    Class to control mouse cursor using hand gestures.
    """
    
    def __init__(self, frame_width=640, frame_height=480, screen_width=1920, screen_height=1080):
        """
        Initialize cursor controller.
        
        Args:
            frame_width: Video frame width
            frame_height: Video frame height
            screen_width: Screen width
            screen_height: Screen height
        """
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Smoothing for cursor movement
        self.prev_x = 0
        self.prev_y = 0
        self.smoothing_factor = 0.7
        
        # Click detection
        self.clicking = False
        self.click_cooldown = 0
    
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
    
    def move_cursor(self, index_finger_pos):
        """
        Move cursor based on index finger position.
        
        Args:
            index_finger_pos: (x, y) position of index finger tip
        """
        # Convert frame coordinates to screen coordinates
        frame_x, frame_y = index_finger_pos
        
        # Map frame coordinates to screen coordinates
        # Frame is mirrored, so we need to flip x
        screen_x = int((1 - frame_x / self.frame_width) * self.screen_width)
        screen_y = int((frame_y / self.frame_height) * self.screen_height)
        
        # Apply smoothing
        smooth_x = int(self.prev_x * self.smoothing_factor + screen_x * (1 - self.smoothing_factor))
        smooth_y = int(self.prev_y * self.smoothing_factor + screen_y * (1 - self.smoothing_factor))
        
        self.prev_x = smooth_x
        self.prev_y = smooth_y
        
        # Move cursor
        pyautogui.moveTo(smooth_x, smooth_y)
    
    def click(self):
        """
        Perform mouse click.
        """
        if not self.clicking and self.click_cooldown <= 0:
            pyautogui.click()
            self.clicking = True
            self.click_cooldown = 10  # Cooldown to prevent multiple clicks
    
    def release_click(self):
        """
        Release click state.
        """
        self.clicking = False
        if self.click_cooldown > 0:
            self.click_cooldown -= 1
    
    def control_cursor(self, hand_landmarks, frame_shape):
        """
        Control cursor based on hand landmarks.
        
        Returns:
            action_performed (string)
        """
        landmarks_dict = self.get_landmark_coordinates(hand_landmarks, frame_shape)
        
        # Get positions
        index_tip = landmarks_dict[8]      # Index finger tip
        thumb_tip = landmarks_dict[4]      # Thumb tip
        
        # Move cursor to index finger position
        self.move_cursor(index_tip)
        
        # Calculate distance between thumb and index
        thumb_index_distance = self.distance(thumb_tip, index_tip)
        
        # If distance is small, perform click
        if thumb_index_distance < 50:
            self.click()
            return "CLICK"
        else:
            self.release_click()
            return "MOVING"


def main():
    """
    Main function for cursor control.
    """
    # Get screen size
    screen_width, screen_height = pyautogui.size()
    print(f"Screen size: {screen_width} x {screen_height}")
    
    # Open webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("ERROR: Could not open webcam.")
        return
    
    # Get frame size
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Frame size: {frame_width} x {frame_height}")
    
    # Initialize MediaPipe Hand Landmarker
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        model_complexity=1,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.6,
    )
    
    # Initialize cursor controller
    cursor_controller = CursorController(frame_width, frame_height, screen_width, screen_height)
    
    print("Cursor Control started. Press 'q' to quit.")
    print("\nControls:")
    print("- Move index finger to move cursor")
    print("- Bring thumb and index together to click")
    print("- Press 'q' to quit")
    
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
                
                # Control cursor
                action = cursor_controller.control_cursor(hand_landmarks, frame.shape)
        
        # Add text on frame
        cv2.putText(frame, "NIMMO - Step 4: Cursor Control", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # Display action
        if action == "CLICK":
            cv2.putText(frame, "ACTION: CLICK", (10, 65),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        elif action == "MOVING":
            cv2.putText(frame, "ACTION: MOVING CURSOR", (10, 65),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 0), 2)
        else:
            cv2.putText(frame, action, (10, 65),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        cv2.putText(frame, "Press 'q' to quit", (10, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # Display frame
        cv2.imshow("NIMMO - Cursor Control", frame)
        
        # Exit if 'q' is pressed
        if (cv2.waitKey(1) & 0xFF) == ord("q"):
            break
    
    # Cleanup
    hands.close()
    cap.release()
    cv2.destroyAllWindows()
    print("Cursor Control stopped.")


if __name__ == "__main__":
    main()
