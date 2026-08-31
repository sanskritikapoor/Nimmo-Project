"""
NIMMO - Step 5: Air Writing
===========================
This is the main feature! Write in the air with your finger.

Features:
1. Drawing Mode: Index finger acts as a pen
2. Color Selection: Different gestures for different colors
3. Clear Canvas: Gesture to clear the canvas
4. Save Drawing: Save your drawing to a file

Controls:
- Index finger: Draw
- Index + Middle fingers (up): Switch to red color
- Index + Middle + Ring fingers (up): Switch to blue color
- Peace sign: Switch to green color
- Thumbs up: Clear canvas
- Press 's' to save drawing
- Press 'q' to quit
"""

import cv2
import mediapipe as mp
import math
from datetime import datetime
import os

# Import MediaPipe hand detection modules
try:
    mp_hands = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils
    mp_styles = mp.solutions.drawing_styles
except AttributeError:
    from mediapipe.python.solutions import hands as mp_hands
    from mediapipe.python.solutions import drawing_utils as mp_draw
    from mediapipe.python.solutions import drawing_styles as mp_styles


class AirWriter:
    """
    Class to handle air writing functionality.
    """
    
    def __init__(self, canvas_width=1280, canvas_height=720):
        """
        Initialize air writer.
        
        Args:
            canvas_width: Width of drawing canvas
            canvas_height: Height of drawing canvas
        """
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        
        # Create blank canvas (white background)
        self.canvas = 255 * cv2.ones((canvas_height, canvas_width, 3), dtype=cv2.uint8)
        
        # Drawing settings
        self.current_color = (0, 0, 255)  # BGR format: Red
        self.brush_size = 5
        self.drawing = False
        self.last_point = None
        
        # Color options
        self.colors = {
            'red': (0, 0, 255),
            'green': (0, 255, 0),
            'blue': (255, 0, 0),
            'yellow': (0, 255, 255),
            'purple': (255, 0, 255),
            'cyan': (255, 255, 0),
        }
    
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
        Check if a finger is up.
        """
        tip_y = landmarks_dict[tip_idx][1]
        pip_y = landmarks_dict[pip_idx][1]
        return tip_y < pip_y
    
    def detect_color_gesture(self, landmarks_dict):
        """
        Detect color selection gesture.
        
        Returns:
            Color tuple or None
        """
        # Get finger positions
        index_up = self.is_finger_up(landmarks_dict, 8, 6)
        middle_up = self.is_finger_up(landmarks_dict, 12, 10)
        ring_up = self.is_finger_up(landmarks_dict, 16, 14)
        
        # Red: Only index finger up
        if index_up and not middle_up and not ring_up:
            return self.colors['red']
        
        # Green: Index and middle up
        if index_up and middle_up and not ring_up:
            return self.colors['green']
        
        # Blue: Index, middle, and ring up
        if index_up and middle_up and ring_up:
            return self.colors['blue']
        
        return None
    
    def map_to_canvas(self, frame_pos, frame_shape):
        """
        Map frame coordinates to canvas coordinates.
        
        Args:
            frame_pos: (x, y) position in frame
            frame_shape: Shape of video frame
        
        Returns:
            (canvas_x, canvas_y)
        """
        frame_x, frame_y = frame_pos
        frame_height, frame_width, _ = frame_shape
        
        # Map frame coordinates to canvas
        canvas_x = int((frame_x / frame_width) * self.canvas_width)
        canvas_y = int((frame_y / frame_height) * self.canvas_height)
        
        # Clamp coordinates to canvas bounds
        canvas_x = max(0, min(canvas_x, self.canvas_width - 1))
        canvas_y = max(0, min(canvas_y, self.canvas_height - 1))
        
        return (canvas_x, canvas_y)
    
    def draw_on_canvas(self, current_point):
        """
        Draw on canvas from last point to current point.
        
        Args:
            current_point: (x, y) current position on canvas
        """
        if self.last_point is not None:
            cv2.line(self.canvas, self.last_point, current_point, 
                    self.current_color, self.brush_size)
        else:
            cv2.circle(self.canvas, current_point, self.brush_size, 
                      self.current_color, -1)
        
        self.last_point = current_point
    
    def process_hand(self, hand_landmarks, frame_shape):
        """
        Process hand landmarks and update drawing.
        
        Returns:
            status_message (string)
        """
        landmarks_dict = self.get_landmark_coordinates(hand_landmarks, frame_shape)
        
        # Get finger positions
        index_tip = landmarks_dict[8]
        thumb_tip = landmarks_dict[4]
        
        # Get finger states
        index_up = self.is_finger_up(landmarks_dict, 8, 6)
        middle_up = self.is_finger_up(landmarks_dict, 12, 10)
        ring_up = self.is_finger_up(landmarks_dict, 16, 14)
        pinky_up = self.is_finger_up(landmarks_dict, 20, 18)
        
        # Check for color gesture
        color = self.detect_color_gesture(landmarks_dict)
        if color is not None:
            self.current_color = color
            self.drawing = False
            self.last_point = None
            return f"Color: {[k for k, v in self.colors.items() if v == color][0].upper()}"
        
        # Check for clear gesture (thumbs up: thumb up, others down)
        if not index_up and not middle_up and not ring_up and not pinky_up:
            thumb_index_distance = self.distance(thumb_tip, index_tip)
            if thumb_index_distance > 100:
                # Thumbs up gesture detected
                self.canvas = 255 * cv2.ones((self.canvas_height, self.canvas_width, 3), 
                                            dtype=cv2.uint8)
                self.last_point = None
                self.drawing = False
                return "CANVAS CLEARED"
        
        # Check if index finger is up (drawing mode)
        if index_up:
            # Map index finger position to canvas
            canvas_pos = self.map_to_canvas(index_tip, frame_shape)
            
            # Draw on canvas
            self.draw_on_canvas(canvas_pos)
            self.drawing = True
            return "DRAWING"
        else:
            self.last_point = None
            self.drawing = False
            return "READY"
    
    def save_drawing(self):
        """
        Save drawing to file.
        
        Returns:
            filename (string)
        """
        # Create drawings folder if it doesn't exist
        if not os.path.exists('drawings'):
            os.makedirs('drawings')
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"drawings/nimmo_drawing_{timestamp}.png"
        
        # Save canvas
        cv2.imwrite(filename, self.canvas)
        
        return filename


def main():
    """
    Main function for air writing.
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
    
    # Initialize air writer
    air_writer = AirWriter(canvas_width=640, canvas_height=480)
    
    print("Air Writing started. Press 'q' to quit, 's' to save drawing.")
    print("\nControls:")
    print("- Index finger up: Draw")
    print("- Index finger only: Red color")
    print("- Index + Middle: Green color")
    print("- Index + Middle + Ring: Blue color")
    print("- Close fist + thumbs up: Clear canvas")
    print("- 's' key: Save drawing")
    print("- 'q' key: Quit")
    
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
        
        status = "No hand detected"
        
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
                
                # Process hand and get status
                status = air_writer.process_hand(hand_landmarks, frame.shape)
        
        # Add text on frame
        cv2.putText(frame, "NIMMO - Step 5: Air Writing", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(frame, f"Status: {status}", (10, 65),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, air_writer.current_color, 2)
        cv2.putText(frame, "Press 's' to save, 'q' to quit", (10, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # Resize canvas to fit display
        display_canvas = cv2.resize(air_writer.canvas, (frame_width, frame_height))
        
        # Stack video frame and canvas side by side
        combined = cv2.hconcat([frame, display_canvas])
        
        # Display combined view
        cv2.imshow("NIMMO - Air Writing (Left: Video | Right: Canvas)", combined)
        
        # Handle key presses
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord("q"):
            break
        elif key == ord("s"):
            filename = air_writer.save_drawing()
            print(f"Drawing saved to: {filename}")
    
    # Cleanup
    hands.close()
    cap.release()
    cv2.destroyAllWindows()
    print("Air Writing stopped.")


if __name__ == "__main__":
    main()
