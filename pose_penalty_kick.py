import cv2
import mediapipe as mp
import numpy as np
import time
import vgamepad as vg
import threading

class PenaltyKickDetector:
    def __init__(self):
        # Initialize MediaPipe pose detection
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Initialize Xbox controller
        self.gamepad = vg.VX360Gamepad()
        
        # Football circle properties (football size ~22cm diameter, scaled for screen)
        self.circle_radius = 80  # pixels (roughly football size on screen)
        self.circle_color = (0, 255, 0)  # Green circle
        self.circle_thickness = 3
        
        # Cooldown system
        self.last_kick_time = 0
        self.cooldown_duration = 5  # 5 seconds cooldown
        self.kick_duration = 2  # 2 seconds penalty kick
        self.is_kicking = False
        
        # Detection threshold (distance in pixels)
        self.touch_threshold = self.circle_radius + 20  # Some tolerance
        
        print("Penalty Kick Detector Initialized!")
        print("Position your foot near the green circle at the bottom to trigger penalty kick!")
        print("Penalty kick: Left stick up + B button for 2 seconds")
        print("Cooldown: 5 seconds between kicks")
        print("Press 'q' to quit")
    
    def calculate_distance(self, point1, point2):
        """Calculate Euclidean distance between two points"""
        return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    def is_foot_touching_circle(self, landmarks, image_width, image_height, circle_center):
        """Check if any foot/leg landmark is touching the circle"""
        # Relevant pose landmarks for legs and feet
        leg_landmarks = [
            self.mp_pose.PoseLandmark.LEFT_HIP,      # 23
            self.mp_pose.PoseLandmark.RIGHT_HIP,     # 24
            self.mp_pose.PoseLandmark.LEFT_KNEE,     # 25
            self.mp_pose.PoseLandmark.RIGHT_KNEE,    # 26
            self.mp_pose.PoseLandmark.LEFT_ANKLE,    # 27
            self.mp_pose.PoseLandmark.RIGHT_ANKLE,   # 28
            self.mp_pose.PoseLandmark.LEFT_HEEL,     # 29
            self.mp_pose.PoseLandmark.RIGHT_HEEL,    # 30
            self.mp_pose.PoseLandmark.LEFT_FOOT_INDEX,  # 31
            self.mp_pose.PoseLandmark.RIGHT_FOOT_INDEX, # 32
        ]
        
        for landmark_id in leg_landmarks:
            if landmark_id.value < len(landmarks.landmark):
                landmark = landmarks.landmark[landmark_id.value]
                
                # Convert normalized coordinates to pixel coordinates
                x = int(landmark.x * image_width)
                y = int(landmark.y * image_height)
                
                # Check if landmark is visible (confidence check)
                if landmark.visibility > 0.5:
                    distance = self.calculate_distance((x, y), circle_center)
                    if distance <= self.touch_threshold:
                        return True, (x, y), landmark_id.name
        
        return False, None, None
    
    def execute_penalty_kick(self):
        """Execute penalty kick in separate thread"""
        if self.is_kicking:
            return
            
        self.is_kicking = True
        print("🥅 PENALTY KICK EXECUTED!")
        
        try:
            # Press left stick up and B button
            self.gamepad.left_joystick_float(x_value_float=0.0, y_value_float=1.0)  # Left stick up
            self.gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_B)  # B button
            self.gamepad.update()
            
            # Hold for 2 seconds
            time.sleep(self.kick_duration)
            
            # Release controls
            self.gamepad.left_joystick_float(x_value_float=0.0, y_value_float=0.0)  # Reset stick
            self.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_B)  # Release B
            self.gamepad.update()
            
            print("⚽ Penalty kick completed!")
            
        except Exception as e:
            print(f"Error executing penalty kick: {e}")
        finally:
            self.is_kicking = False
            self.last_kick_time = time.time()
    
    def draw_cooldown_timer(self, image, remaining_time):
        """Draw cooldown timer on screen"""
        timer_text = f"Cooldown: {remaining_time:.1f}s"
        cv2.putText(image, timer_text, (50, 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    
    def draw_kick_status(self, image):
        """Draw kicking status on screen"""
        if self.is_kicking:
            kick_text = "EXECUTING PENALTY KICK!"
            cv2.putText(image, kick_text, (50, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3)
    
    def run(self):
        """Main detection loop"""
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Error: Could not open webcam")
            return
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Error: Could not read frame")
                    break
                
                # Flip frame horizontally for mirror effect
                frame = cv2.flip(frame, 1)
                image_height, image_width, _ = frame.shape
                
                # Convert BGR to RGB for MediaPipe
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Process pose detection
                results = self.pose.process(rgb_frame)
                
                # Calculate circle position (bottom center)
                circle_center = (image_width // 2, image_height - 100)
                
                # Draw the target circle
                cv2.circle(frame, circle_center, self.circle_radius, 
                          self.circle_color, self.circle_thickness)
                
                # Draw circle label
                cv2.putText(frame, "Penalty Spot", 
                           (circle_center[0] - 60, circle_center[1] + 120),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Draw pose landmarks
                if results.pose_landmarks:
                    self.mp_drawing.draw_landmarks(
                        frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
                    
                    # Check if foot is touching circle
                    is_touching, touch_point, landmark_name = self.is_foot_touching_circle(
                        results.pose_landmarks, image_width, image_height, circle_center)
                    
                    if is_touching:
                        # Highlight the touching point
                        if touch_point:
                            cv2.circle(frame, touch_point, 10, (0, 0, 255), -1)
                            cv2.putText(frame, f"TOUCHING: {landmark_name}", 
                                       (50, image_height - 50),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        
                        # Check cooldown before executing kick
                        current_time = time.time()
                        time_since_last_kick = current_time - self.last_kick_time
                        
                        if time_since_last_kick >= self.cooldown_duration and not self.is_kicking:
                            # Execute penalty kick in separate thread
                            kick_thread = threading.Thread(target=self.execute_penalty_kick)
                            kick_thread.daemon = True
                            kick_thread.start()
                
                # Draw status information
                current_time = time.time()
                time_since_last_kick = current_time - self.last_kick_time
                
                if time_since_last_kick < self.cooldown_duration:
                    remaining_cooldown = self.cooldown_duration - time_since_last_kick
                    self.draw_cooldown_timer(frame, remaining_cooldown)
                
                self.draw_kick_status(frame)
                
                # Draw instructions
                cv2.putText(frame, "Move your foot to the green circle for penalty kick", 
                           (50, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Show frame
                cv2.imshow('Penalty Kick Detector', frame)
                
                # Check for quit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
        except KeyboardInterrupt:
            print("\nProgram interrupted by user")
        except Exception as e:
            print(f"Error in main loop: {e}")
        finally:
            cap.release()
            cv2.destroyAllWindows()
            print("Camera and windows closed")

def main():
    try:
        detector = PenaltyKickDetector()
        detector.run()
    except Exception as e:
        print(f"Error initializing detector: {e}")
        print("\nMake sure you have all required packages installed:")
        print("pip install mediapipe opencv-python vgamepad")

if __name__ == "__main__":
    main()
