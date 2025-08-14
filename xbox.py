import time
import threading
import signal
import sys
from pynput import keyboard
import vgamepad as vg

class KeyboardToXboxMapper:
    def __init__(self):
        # Create a virtual Xbox 360 controller
        self.gamepad = vg.VX360Gamepad()
        
        # Dictionary to track pressed keys
        self.pressed_keys = set()
        
        # Flag to control the program loop
        self.running = True
        
        # Setup signal handler for Ctrl+C
        signal.signal(signal.SIGINT, self.signal_handler)
        
        # Key mapping dictionary - customize these as needed
        self.key_mappings = {
            'l': vg.XUSB_BUTTON.XUSB_GAMEPAD_X,           # L -> X button (shoot in FIFA)
            'k': vg.XUSB_BUTTON.XUSB_GAMEPAD_A,           # K -> A button (pass)
            'j': vg.XUSB_BUTTON.XUSB_GAMEPAD_B,           # J -> B button (lob/cross)
            'i': vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,           # I -> Y button (through ball)
            'space': vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,  # Space -> Right Bumper (sprint)
            'shift': vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER,   # Shift -> Left Bumper
            'enter': vg.XUSB_BUTTON.XUSB_GAMEPAD_START,   # Enter -> Start/Menu
            'tab': vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,      # Tab -> Back/Select
        }
        
        # Analog stick mappings (WASD for left stick, arrow keys for right stick)
        self.analog_mappings = {
            'w': ('left_stick', 0, 1),      # W -> Left stick up
            's': ('left_stick', 0, -1),     # S -> Left stick down
            'a': ('left_stick', -1, 0),     # A -> Left stick left
            'd': ('left_stick', 1, 0),      # D -> Left stick right
            'up': ('right_stick', 0, 1),    # Up arrow -> Right stick up
            'down': ('right_stick', 0, -1), # Down arrow -> Right stick down
            'left': ('right_stick', -1, 0), # Left arrow -> Right stick left
            'right': ('right_stick', 1, 0), # Right arrow -> Right stick right
        }
        
        # Current analog stick positions
        self.left_stick_x = 0.0
        self.left_stick_y = 0.0
        self.right_stick_x = 0.0
        self.right_stick_y = 0.0
        
        print("Keyboard to Xbox Controller Mapper Started!")
        print("Key Mappings:")
        print("  L -> X button (Shoot)")
        print("  K -> A button (Pass)")
        print("  J -> B button (Lob/Cross)")
        print("  I -> Y button (Through Ball)")
        print("  SPACE -> Right Bumper (Sprint)")
        print("  SHIFT -> Left Bumper")
        print("  WASD -> Left Analog Stick (Movement)")
        print("  Arrow Keys -> Right Analog Stick (Camera/Skills)")
        print("  ENTER -> Start/Menu")
        print("  TAB -> Back/Select")
        print("\nPress ESC to exit, or use Ctrl+C in terminal...")

    def signal_handler(self, signum, frame):
        """Handle Ctrl+C signal"""
        print("\nReceived interrupt signal. Exiting...")
        self.running = False
        sys.exit(0)

    def normalize_key(self, key):
        """Convert key object to string representation"""
        try:
            if hasattr(key, 'char') and key.char:
                return key.char.lower()
            else:
                # Handle special keys
                key_name = str(key).replace('Key.', '')
                return key_name.lower()
        except:
            return None

    def update_analog_sticks(self):
        """Update analog stick positions based on pressed keys"""
        # Reset positions
        self.left_stick_x = 0.0
        self.left_stick_y = 0.0
        self.right_stick_x = 0.0
        self.right_stick_y = 0.0
        
        # Calculate positions based on pressed keys
        for key_str in self.pressed_keys:
            if key_str in self.analog_mappings:
                stick, x_offset, y_offset = self.analog_mappings[key_str]
                if stick == 'left_stick':
                    self.left_stick_x += x_offset
                    self.right_stick_y += y_offset
                elif stick == 'right_stick':
                    self.right_stick_x += x_offset
                    self.right_stick_y += y_offset
        
        # Normalize values to [-1, 1] range
        self.left_stick_x = max(-1.0, min(1.0, self.left_stick_x))
        self.left_stick_y = max(-1.0, min(1.0, self.left_stick_y))
        self.right_stick_x = max(-1.0, min(1.0, self.right_stick_x))
        self.right_stick_y = max(-1.0, min(1.0, self.right_stick_y))
        
        # Update gamepad
        self.gamepad.left_joystick_float(x_value_float=self.left_stick_x, y_value_float=self.left_stick_y)
        self.gamepad.right_joystick_float(x_value_float=self.right_stick_x, y_value_float=self.right_stick_y)

    def on_key_press(self, key):
        """Handle key press events"""
        try:
            # Allow Ctrl+C to work by not intercepting it
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                return True
                
            key_str = self.normalize_key(key)
            if not key_str:
                return True
                
            # Exit on ESC
            if key_str == 'esc':
                print("Exiting via ESC key...")
                self.running = False
                return False
            
            # Add key to pressed keys set
            self.pressed_keys.add(key_str)
            
            # Handle button mappings
            if key_str in self.key_mappings:
                xbox_button = self.key_mappings[key_str]
                self.gamepad.press_button(button=xbox_button)
                print(f"Pressed: {key_str.upper()} -> {xbox_button}")
            
            # Handle analog stick mappings
            if key_str in self.analog_mappings:
                self.update_analog_sticks()
            
            # Update the gamepad state
            self.gamepad.update()
            
            return True
            
        except Exception as e:
            print(f"Error in key press: {e}")
            return True

    def on_key_release(self, key):
        """Handle key release events"""
        try:
            # Allow Ctrl+C to work by not intercepting it
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                return True
                
            key_str = self.normalize_key(key)
            if not key_str:
                return True
                
            # Remove key from pressed keys set
            self.pressed_keys.discard(key_str)
            
            # Handle button mappings
            if key_str in self.key_mappings:
                xbox_button = self.key_mappings[key_str]
                self.gamepad.release_button(button=xbox_button)
                print(f"Released: {key_str.upper()}")
            
            # Handle analog stick mappings
            if key_str in self.analog_mappings:
                self.update_analog_sticks()
            
            # Update the gamepad state
            self.gamepad.update()
            
            return True
            
        except Exception as e:
            print(f"Error in key release: {e}")
            return True

    def start_listening(self):
        """Start listening for keyboard input"""
        try:
            with keyboard.Listener(
                on_press=self.on_key_press,
                on_release=self.on_key_release,
                suppress=False) as listener:
                
                # Keep the program running until stopped
                while self.running and listener.running:
                    time.sleep(0.1)
                    
                listener.stop()
                
        except Exception as e:
            print(f"Error in listener: {e}")
        finally:
            print("Keyboard listener stopped.")

def main():
    try:
        mapper = KeyboardToXboxMapper()
        mapper.start_listening()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you have installed the required packages:")
        print("pip install pynput vgamepad")

if __name__ == "__main__":
    main()