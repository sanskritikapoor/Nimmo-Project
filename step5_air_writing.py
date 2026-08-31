"""
NIMMO - Step 5: Air Writing with Color Palette
===============================================
This is the main feature! Write in the air with your finger.

Features:
1. Drawing Mode: Index finger acts as a pen
2. Color Palette: Visual color selector with multiple colors
3. Brush Size Control: Change line thickness
4. Clear Canvas: Gesture to clear the canvas
5. Save Drawing: Save your drawing to a file

Controls:
- Index finger up: Draw
- Index finger only: Switch between colors (cycle through palette)
- Index + Middle: Increase brush size
- Index + Middle + Ring: Decrease brush size
- Closed fist + thumbs distance > 100: Clear canvas
- Press 's' to save drawing
- Press 'q' to quit

Color Palette:
- Red, Green, Blue, Yellow, Purple, Cyan, Orange, Pink, Black, White
"""

import cv2
import mediapipe as mp
import math
from datetime import datetime
import os

# Initialize MediaPipe
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
mp_styles = mp.solutions.drawing_styles


class AirWriter:
    """
    Class to handle air writing functionality with color palette.
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
        
        # Extended color palette (BGR format)
        self.colors = {
            0: {'name': 'Red', 'bgr': (0, 0, 255)},
            1: {'name': 'Green', 'bgr': (0, 255, 0)},
            2: {'name': 'Blue', 'bgr': (255, 0, 0)},
            3: {'name': 'Yellow', 'bgr': (0, 255, 255)},
            4: {'name': 'Purple', 'bgr': (255, 0, 255)},
            5: {'name': 'Cyan', 'bgr': (255, 255, 0)},
            6: {'name': 'Orange', 'bgr': (0, 165, 255)},
            7: {'name': 'Pink', 'bgr': (203, 192, 255)},
            8: {'name': 'Black', 'bgr': (0, 0, 0)},
            9: {'name': 'White', 'bgr': (255, 255, 255)},
        }
        
        # Current settings
        self.current_color_index = 0
        self.current_color = self.colors[0]['bgr']
        self.brush_size = 5
        self.drawing = False
        self.last_point = None
    
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
    
    def cycle_color(self):
        """
        Cycle to next color in palette.
        """
        self.current_color_index = (self.current_color_index + 1) % len(self.colors)
        self.current_color = self.colors[self.current_color_index]['bgr']
        return self.colors[self.current_color_index]['name']
    
    def increase_brush_size(self):
        """
        Increase brush size (max 20).
        """
        if self.brush_size < 20:
            self.brush_size += 2
        return self.brush_size
    
    def decrease_brush_size(self):
        """
        Decrease brush size (min 1).
        """
        if self.brush_size > 1:
            self.brush_size -= 2
        return self.brush_size
    
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
        middle_tip = landmarks_dict[12]
        ring_tip = landmarks_dict[16]
        
        # Get finger states
        index_up = self.is_finger_up(landmarks_dict, 8, 6)
        middle_up = self.is_finger_up(landmarks_dict, 12, 10)
        ring_up = self.is_finger_up(landmarks_dict, 16, 14)
        pinky_up = self.is_finger_up(landmarks_dict, 20, 18)
        thumb_up = self.is_finger_up(landmarks_dict, 4, 3)
        
        # Check for brush size gestures BEFORE checking drawing
        
        # Increase brush size: Index + Middle up (but ring down)
        if index_up and middle_up and not ring_up and not pinky_up:
            new_size = self.increase_brush_size()
            self.drawing = False
            self.last_point = None
            return f"BRUSH SIZE: {new_size}px"
        
        # Decrease brush size: Index + Middle + Ring up
        if index_up and middle_up and ring_up and not pinky_up:
            new_size = self.decrease_brush_size()
            self.drawing = False
            self.last_point = None
            return f"BRUSH SIZE: {new_size}px"
        
        # Cycle color: Index + Thumb close (but other fingers down)
        thumb_index_distance = self.distance(thumb_tip, index_tip)
        if thumb_index_distance < 50 and not middle_up and not ring_up and not pinky_up:
            color_name = self.cycle_color()
            self.drawing = False
            self.last_point = None
            return f"COLOR: {color_name}"
        
        # Check for clear gesture (thumbs up: thumb up, others down)
        if not index_up and not middle_up and not ring_up and not pinky_up and thumb_up:
            # Check if thumb is significantly away from hand (thumbs up gesture)
            wrist = landmarks_dict[0]
            thumb_base = landmarks_dict[2]
            if thumb_tip[1] > wrist[1] + 100:  # Thumb significantly below wrist
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
    
    def draw_color_palette(self, frame):
        """
        Draw color palette on the video frame.
        
        Args:
            frame: Video frame to draw palette on
        """
        palette_x = 20
        palette_y = 20
        color_box_size = 30
        spacing = 5
        
        # Draw palette background
        cv2.rectangle(frame, (palette_x - 5, palette_y - 5), 
                     (palette_x + (len(self.colors) * (color_box_size + spacing)), palette_y + color_box_size + 5),
                     (50, 50, 50), -1)
        cv2.rectangle(frame, (palette_x - 5, palette_y - 5), 
                     (palette_x + (len(self.colors) * (color_box_size + spacing)), palette_y + color_box_size + 5),
                     (200, 200, 200), 2)
        
        # Draw each color
        for idx, color_data in self.colors.items():
            x = palette_x + (idx * (color_box_size + spacing))
            y = palette_y
            
            # Draw color box
            cv2.rectangle(frame, (x, y), (x + color_box_size, y + color_box_size),
                         color_data['bgr'], -1)
            
            # Highlight current color
            if idx == self.current_color_index:
                cv2.rectangle(frame, (x - 3, y - 3), (x + color_box_size + 3, y + color_box_size + 3),
                             (255, 255, 255), 3)


def main():
    """
    Main function for air writing with color palette.
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
    
    print("=" * 70)
    print("Air Writing with Color Palette Started")
    print("=" * 70)
    print("\nGesture Controls:")
    print("- Index finger up           → DRAW")
    print("- Thumb + Index close       → CYCLE COLOR (next in palette)")
    print("- Index + Middle up         → INCREASE BRUSH SIZE")
    print("- Index + Middle + Ring up  → DECREASE BRUSH SIZE")
    print("- Thumbs up (away from hand)→ CLEAR CANVAS")
    print("- Press 's' key             → SAVE DRAWING")
    print("- Press 'q' key             → QUIT")
    print("\nColor Palette: Red, Green, Blue, Yellow, Purple, Cyan, Orange, Pink, Black, White")
    print("=" * 70 + "\n")
    
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
        
        # Draw color palette on frame
        air_writer.draw_color_palette(frame)
        
        # Add text on frame
        cv2.putText(frame, "NIMMO - Air Writing with Color Palette", (10, frame_height - 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(frame, f"Status: {status}", (10, frame_height - 45),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, air_writer.current_color, 2)
        cv2.putText(frame, f"Current Color: {air_writer.colors[air_writer.current_color_index]['name']} | Brush: {air_writer.brush_size}px", 
                    (10, frame_height - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, air_writer.current_color, 2)
        
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
            print(f"✅ Drawing saved to: {filename}")
    
    # Cleanup
    hands.close()
    cap.release()
    cv2.destroyAllWindows()
    print("Air Writing stopped.")


if __name__ == "__main__":
    main()
