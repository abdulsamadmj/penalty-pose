import cv2
import mediapipe as mp
import time
import threading
import vgamepad as vg
import numpy as np
from pose.utils import (
    capture_frame,
    draw_landmarks,
    configuration_exists,
)

class PenaltyKickController:
    def __init__(self):
        # Initialize MediaPipe pose detection
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5, min_tracking_confidence=0.5
        )
        self.cap = None
        
        # Create virtual Xbox 360 controller
        self.gamepad = vg.VX360Gamepad()
        
        # Circle configuration (center of screen)
        self.circle_center = (0.5, 0.5)  # Normalized coordinates (center of frame)
        self.circle_radius = 0.15  # Normalized radius (15% of frame width)
        
        # Action state tracking
        self.action_active = False
        self.last_action_time = 0
        self.action_cooldown = 3.0  # 3 seconds cooldown between kicks
        self.action_duration = 2.0  # Hold inputs for 2 seconds
        
        # Current action thread
        self.action_thread = None
        
        print("Penalty Kick Controller Initialized!")
        print("Position your leg to touch the circle in the center to trigger a penalty kick.")
        print("Controls will be held for 2 seconds: Left Stick Up + B Button")
        print("Press ESC to exit")

    def is_point_in_circle(self, point_x, point_y):
        """Check if a point is inside the center circle"""
        # Calculate distance from point to circle center
        dx = point_x - self.circle_center[0]
        dy = point_y - self.circle_center[1]
        distance = np.sqrt(dx*dx + dy*dy)
        
        return distance <= self.circle_radius

    def draw_target_circle(self, frame):
        """Draw the target circle on the frame"""
        h, w, _ = frame.shape
        
        # Convert normalized coordinates to pixel coordinates
        center_x = int(self.circle_center[0] * w)
        center_y = int(self.circle_center[1] * h)
        radius = int(self.circle_radius * w)
        
        # Draw the circle
        color = (0, 255, 0) if not self.action_active else (0, 0, 255)  # Green when ready, red when active
        cv2.circle(frame, (center_x, center_y), radius, color, 3)
        
        # Add text label
        cv2.putText(frame, "TARGET ZONE", (center_x - 50, center_y - radius - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    def execute_penalty_kick(self):
        """Execute the penalty kick action (left stick up + B button for 2 seconds)"""
        print("🥅 PENALTY KICK TRIGGERED! Holding Left Stick Up + B Button for 2 seconds...")
        
        try:
            # Press and hold left stick up and B button
            self.gamepad.left_joystick_float(x_value_float=0.0, y_value_float=1.0)  # Left stick up
            self.gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_B)  # B button
            self.gamepad.update()
            
            # Hold for the specified duration
            time.sleep(self.action_duration)
            
            # Release controls
            self.gamepad.left_joystick_float(x_value_float=0.0, y_value_float=0.0)  # Reset stick
            self.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_B)  # Release B button
            self.gamepad.update()
            
            print("✅ Penalty kick completed! Controls released.")
            
        except Exception as e:
            print(f"Error during penalty kick execution: {e}")
        finally:
            self.action_active = False
            self.last_action_time = time.time()

    def trigger_penalty_kick(self):
        """Trigger penalty kick if cooldown has passed"""
        current_time = time.time()
        
        # Check if we're already executing an action
        if self.action_active:
            return
            
        # Check cooldown
        if current_time - self.last_action_time < self.action_cooldown:
            return
            
        # Set action as active and start execution thread
        self.action_active = True
        self.action_thread = threading.Thread(target=self.execute_penalty_kick)
        self.action_thread.daemon = True
        self.action_thread.start()

    def check_leg_detection(self, landmarks):
        """Check if either leg (knee or ankle) is in the target circle"""
        # Check left knee
        left_knee = landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE]
        if self.is_point_in_circle(left_knee.x, left_knee.y):
            return True, "Left Knee"
            
        # Check right knee  
        right_knee = landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE]
        if self.is_point_in_circle(right_knee.x, right_knee.y):
            return True, "Right Knee"
            
        # Check left ankle
        left_ankle = landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE]
        if self.is_point_in_circle(left_ankle.x, left_ankle.y):
            return True, "Left Ankle"
            
        # Check right ankle
        right_ankle = landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE]
        if self.is_point_in_circle(right_ankle.x, right_ankle.y):
            return True, "Right Ankle"
            
        return False, None

    def draw_status_info(self, frame):
        """Draw status information on the frame"""
        h, w, _ = frame.shape
        
        # Status text
        if self.action_active:
            status_text = "🥅 EXECUTING PENALTY KICK..."
            color = (0, 0, 255)  # Red
        else:
            time_since_last = time.time() - self.last_action_time
            if time_since_last < self.action_cooldown:
                remaining = self.action_cooldown - time_since_last
                status_text = f"⏱️ Cooldown: {remaining:.1f}s"
                color = (0, 165, 255)  # Orange
            else:
                status_text = "✅ Ready for penalty kick"
                color = (0, 255, 0)  # Green
                
        cv2.putText(frame, status_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        # Instructions
        instructions = [
            "Touch the green circle with your leg to trigger penalty kick",
            "Left Stick Up + B Button will be held for 2 seconds",
            "Press ESC to exit"
        ]
        
        for i, instruction in enumerate(instructions):
            cv2.putText(frame, instruction, (10, h - 80 + (i * 25)), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    def start(self):
        """Start the penalty kick pose detection"""
        print("Starting penalty kick pose detection...")
        
        # Initialize camera
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Could not open camera.")
            return
            
        print("Penalty kick system activated. Position your leg in the target circle to kick!")
        
        while self.cap.isOpened():
            frame = capture_frame(self.cap)
            if frame is None:
                break
                
            # Process the frame with MediaPipe Pose
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(frame_rgb)
            
            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                
                # Draw landmarks for visualization
                draw_landmarks(frame, landmarks, self.mp_pose)
                
                # Check if leg is in target circle
                leg_detected, detected_part = self.check_leg_detection(landmarks)
                
                if leg_detected:
                    # Draw detection indicator
                    cv2.putText(frame, f"{detected_part} DETECTED!", (10, 70), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                    
                    # Trigger penalty kick
                    self.trigger_penalty_kick()
            
            # Draw the target circle
            self.draw_target_circle(frame)
            
            # Draw status information
            self.draw_status_info(frame)
            
            # Show the frame
            cv2.imshow("Penalty Kick Controller", frame)
            
            # Check for exit
            if cv2.waitKey(1) & 0xFF == 27:  # ESC to exit
                break
        
        # Clean up
        self.cleanup()

    def cleanup(self):
        """Clean up resources"""
        # Wait for any active action thread to complete
        if self.action_thread and self.action_thread.is_alive():
            print("Waiting for current action to complete...")
            self.action_thread.join(timeout=3.0)
        
        # Reset gamepad
        try:
            self.gamepad.left_joystick_float(x_value_float=0.0, y_value_float=0.0)
            self.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_B)
            self.gamepad.update()
        except:
            pass
            
        # Release camera
        if self.cap and self.cap.isOpened():
            self.cap.release()
            
        cv2.destroyAllWindows()
        print("Penalty kick controller terminated.")

def start_penalty_kick_gaming():
    """Main function to start penalty kick pose detection"""
    controller = PenaltyKickController()
    try:
        controller.start()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    finally:
        controller.cleanup()

if __name__ == "__main__":
    start_penalty_kick_gaming()
