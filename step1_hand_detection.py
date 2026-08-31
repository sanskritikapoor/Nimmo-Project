"""
NIMMO - Step 1: Hand Detection
================================
This is the basic hand detection module.
It captures video from the webcam and detects if a hand is present.

What happens here:
1. OpenCV captures frames from webcam
2. MediaPipe detects hand landmarks (21 key points on hand)
3. Detected hands are drawn on the video frame
4. Press 'q' to quit

Run this to test if hand detection is working correctly.
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


def main():
    """
    Main function for hand detection.
    """
    # Open webcam (0 = default webcam)
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("ERROR: Could not open webcam.")
        return
    
    # Initialize MediaPipe Hand Landmarker
    hands = mp_hands.Hands(
        static_image_mode=False,      # For video, not static images
        max_num_hands=1,              # Detect only 1 hand
        model_complexity=1,           # 0=lite, 1=full
        min_detection_confidence=0.6, # Minimum confidence to detect hand
        min_tracking_confidence=0.6,  # Minimum confidence to track hand
    )
    
    print("Hand Detection started. Press 'q' to quit.")
    
    while True:
        # Read frame from webcam
        ok, frame = cap.read()
        
        if not ok:
            print("Failed to read frame from webcam")
            break
        
        # Flip frame horizontally for selfie view (mirror effect)
        frame = cv2.flip(frame, 1)
        
        # Get frame height and width
        h, w, c = frame.shape
        
        # Convert BGR to RGB (MediaPipe uses RGB)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process frame with MediaPipe
        result = hands.process(rgb)
        
        # If hands are detected
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                # Draw landmarks on frame
                mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,  # Draw connections between landmarks
                    mp_styles.get_default_hand_landmarks_style(),
                    mp_styles.get_default_hand_connections_style(),
                )
        
        # Add text on frame
        cv2.putText(frame, "NIMMO - Step 1: Hand Detection", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        if result.multi_hand_landmarks:
            cv2.putText(frame, "Hand Detected!", (10, 65),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "No hand detected", (10, 65),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        cv2.putText(frame, "Press 'q' to quit", (10, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # Display frame
        cv2.imshow("NIMMO - Hand Detection", frame)
        
        # Exit if 'q' is pressed
        if (cv2.waitKey(1) & 0xFF) == ord("q"):
            break
    
    # Cleanup
    hands.close()
    cap.release()
    cv2.destroyAllWindows()
    print("Hand Detection stopped.")


if __name__ == "__main__":
    main()
