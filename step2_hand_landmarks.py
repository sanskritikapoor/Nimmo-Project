"""
NIMMO - Step 2: Hand Landmarks Analysis
========================================
This module detects hand and displays all 21 hand landmarks with their coordinates.

The 21 hand landmarks are:
0: Wrist
1-4: Thumb (base to tip)
5-8: Index finger (base to tip)
9-12: Middle finger (base to tip)
13-16: Ring finger (base to tip)
17-20: Pinky finger (base to tip)

What happens here:
1. Detects hand landmarks
2. Displays all 21 landmark positions
3. Shows connections between landmarks
4. Prints landmark coordinates in console
"""

import cv2
import mediapipe as mp

# Import MediaPipe hand detection modules
try:
    mp_hands = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils
    mp_styles = mp.solutions.drawing_styles
except AttributeError:
    # Fallback for different MediaPipe builds
    from mediapipe.python.solutions import hands as mp_hands
    from mediapipe.python.solutions import drawing_utils as mp_draw
    from mediapipe.python.solutions import drawing_styles as mp_styles


def get_landmark_coordinates(hand_landmarks, frame_shape):
    """
    Extract coordinates of all hand landmarks.
    
    Args:
        hand_landmarks: MediaPipe hand landmarks object
        frame_shape: Shape of video frame (height, width, channels)
    
    Returns:
        Dictionary with landmark indices as keys and (x, y) coordinates as values
    """
    h, w, c = frame_shape
    landmarks_dict = {}
    
    for idx, lm in enumerate(hand_landmarks.landmark):
        # Convert normalized coordinates to pixel coordinates
        x = int(lm.x * w)
        y = int(lm.y * h)
        landmarks_dict[idx] = (x, y)
    
    return landmarks_dict


def print_landmarks(hand_landmarks, frame_shape):
    """
    Print all hand landmarks coordinates to console.
    """
    landmarks_dict = get_landmark_coordinates(hand_landmarks, frame_shape)
    
    print("\n" + "="*50)
    print("HAND LANDMARKS COORDINATES")
    print("="*50)
    
    landmark_names = [
        "Wrist",
        "Thumb_CMC", "Thumb_MCP", "Thumb_IP", "Thumb_Tip",
        "Index_MCP", "Index_PIP", "Index_DIP", "Index_Tip",
        "Middle_MCP", "Middle_PIP", "Middle_DIP", "Middle_Tip",
        "Ring_MCP", "Ring_PIP", "Ring_DIP", "Ring_Tip",
        "Pinky_MCP", "Pinky_PIP", "Pinky_DIP", "Pinky_Tip"
    ]
    
    for idx, (x, y) in landmarks_dict.items():
        print(f"{idx}: {landmark_names[idx]:15s} -> X: {x:4d}, Y: {y:4d}")
    
    print("="*50 + "\n")


def main():
    """
    Main function for hand landmarks analysis.
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
    
    print("Hand Landmarks Detection started. Press 'q' to quit.")
    frame_count = 0
    
    while True:
        ok, frame = cap.read()
        
        if not ok:
            break
        
        # Flip frame for selfie view
        frame = cv2.flip(frame, 1)
        h, w, c = frame.shape
        
        # Convert to RGB
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process frame
        result = hands.process(rgb)
        
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
                
                # Get landmark coordinates
                landmarks_dict = get_landmark_coordinates(hand_landmarks, frame.shape)
                
                # Draw landmark indices on frame
                for idx, (x, y) in landmarks_dict.items():
                    cv2.circle(frame, (x, y), 3, (0, 255, 255), -1)
                    cv2.putText(frame, str(idx), (x + 5, y - 5),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 0, 0), 1)
                
                # Print landmarks every 30 frames
                frame_count += 1
                if frame_count % 30 == 0:
                    print_landmarks(hand_landmarks, frame.shape)
        
        # Add text on frame
        cv2.putText(frame, "NIMMO - Step 2: Hand Landmarks", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(frame, "Check console for landmark coordinates", (10, 65),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        cv2.putText(frame, "Press 'q' to quit", (10, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # Display frame
        cv2.imshow("NIMMO - Hand Landmarks", frame)
        
        # Exit if 'q' is pressed
        if (cv2.waitKey(1) & 0xFF) == ord("q"):
            break
    
    # Cleanup
    hands.close()
    cap.release()
    cv2.destroyAllWindows()
    print("Hand Landmarks Detection stopped.")


if __name__ == "__main__":
    main()
