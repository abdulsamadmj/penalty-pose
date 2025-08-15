# Motion Gaming

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-blue.svg" alt="Python 3.12">
  <img src="https://img.shields.io/badge/OpenCV-4.11-green.svg" alt="OpenCV 4.11">
  <img src="https://img.shields.io/badge/MediaPipe-0.10-orange.svg" alt="MediaPipe 0.10">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT License">
</p>

Control games and applications through body gestures - a hands-free gaming experience using computer vision and motion tracking.

## 📖 Overview

Motion Gaming is an innovative project that allows you to control games and applications using body movements captured via webcam. The system provides multiple control methods:

1. **Pose Detection System** - Uses MediaPipe's pose detection for full-body skeletal tracking
2. **Motion Tracking System** - Uses OpenCV's CSRT tracker for facial movement tracking  
3. **Penalty Kick Controller** - Specialized controller for football/soccer penalty kicks using virtual Xbox gamepad
4. **Keyboard to Xbox Mapper** - Maps keyboard input to virtual Xbox controller for legacy game compatibility

## ✨ Features

- **No additional hardware required** - Just a standard webcam
- **Multiple control systems** to choose from:
  - **Pose-based control** (full-body skeletal tracking with MediaPipe)
  - **Face motion tracking** (tracks face movement for controls)
  - **Virtual gamepad control** (Xbox 360 controller emulation)
  - **Keyboard mapping** (keyboard to gamepad conversion)
- **Customizable trigger zones** that move with your face
- **Configurable key mappings** to adapt to different games
- **Intelligent cooldown system** to prevent action spamming
- **Interactive setup process** for easy configuration
- **Real-time motion detection** with adjustable sensitivity

## 🚀 Getting Started

### Prerequisites

- Python 3.12 or higher
- Webcam
- Target games/applications (compatible with keyboard or Xbox controller input)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd motion-gaming

# Create and activate a virtual environment (recommended)
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install opencv-python mediapipe pynput vgamepad imutils numpy
```

## 🎮 Usage

The project offers multiple control methods depending on your needs:

### 1. Pose-Based Control System

```bash
python -m pose.pose
```

This system uses MediaPipe to track your full body posture:

- **Movement**: Lean left/right with your shoulders to move your character
- **Actions**: Move your hands or knees into the trigger zone to perform game actions
  - Left hand in trigger zone → Punch action
  - Right hand in trigger zone → Block action  
  - Left knee in trigger zone → Kick2 action
  - Right knee in trigger zone → Kick action

### 2. Motion Tracking System

```bash
python -m track.tracking
```

This system tracks your face position for control:

- **Movement**: Move your face left/right/up/down to control your character
- **Actions**: Define motion regions that trigger specific actions when movement is detected
- **Setup**: Interactive configuration to define face tracking and gesture regions

### 3. Penalty Kick Controller

```bash
python pose_penalty_kick.py
```

Specialized controller for football/soccer penalty kicks:

- **Target Zone**: Position your leg (knee or ankle) in the center circle to trigger penalty kick
- **Xbox Controller**: Emulates Xbox 360 controller with Left Stick Up + B Button combination
- **Timing**: 2-second action duration with 3-second cooldown between kicks

### 4. Keyboard to Xbox Mapper

```bash
python xbox.py
```

Maps keyboard input to virtual Xbox controller:

```
Key Mappings:
- L → X button (Shoot)
- K → A button (Pass)  
- J → B button (Lob/Cross)
- I → Y button (Through Ball)
- SPACE → Right Bumper (Sprint)
- SHIFT → Left Bumper
- WASD → Left Analog Stick (Movement)
- Arrow Keys → Right Analog Stick (Camera/Skills)
- ENTER → Start/Menu
- TAB → Back/Select
```

## ⚙️ Configuration

### First-Time Setup

Both pose and motion tracking systems have interactive setup processes:

#### Pose System Configuration
1. Run the pose system for the first time
2. Position yourself naturally in the camera frame
3. Define trigger zones relative to your face position
4. Set cooldown duration (0.1-2.0 seconds)
5. Configuration is saved automatically

#### Motion Tracking Configuration  
1. Run the motion tracking system for the first time
2. Select facial tracking region with mouse
3. Define gesture detection regions for different actions
4. Configuration is saved automatically

### Key Mappings

The systems use configurable key mappings that can be customized. Default mappings include:

- **Movement**: Arrow keys (up, down, left, right)
- **Actions**: Letter keys (a, x, z, s, d) for punch, kick, kick2, block, grab

## 🧠 Technical Architecture

The project follows a modular architecture with clear separation of concerns:

### Core Components
- **Input Simulation**: Handles keyboard input simulation across systems
- **Configuration Management**: Loads/saves system configurations
- **Camera Handling**: Standardized camera capture and frame processing

### Pose Module
- `pose.py`: Main pose detection and control logic using MediaPipe
- `setup.py`: Interactive configuration for pose system
- `utils.py`: Helper functions for pose detection and trigger zones

### Track Module  
- `tracking.py`: Main face tracking control loop using OpenCV CSRT
- `motion_detector.py`: Motion detection and action triggering
- `setup.py`: Interactive configuration for tracking system
- `utils.py`: Helper functions for motion tracking

### Specialized Controllers
- `penalty_kick.py`: Football penalty kick controller with Xbox gamepad emulation
- `xbox.py`: Keyboard to Xbox controller mapper

## 📊 Performance Considerations

All systems are optimized for responsive gameplay:

- **Frame rate optimization** to reduce input lag (600x600 resolution)
- **Movement thresholds** to filter out unintentional movements  
- **Cooldown timers** to prevent action spamming (configurable 0.1-2.0s)
- **Reference position tracking** to adapt to user movement over time
- **Sensitivity adjustment** for motion detection
- **Real-time processing** with efficient computer vision algorithms

## 🛠️ Dependencies

- **OpenCV** (`opencv-python`): Computer vision and camera handling
- **MediaPipe** (`mediapipe`): Pose detection and skeletal tracking
- **PyInput** (`pynput`): Keyboard input simulation
- **VGamepad** (`vgamepad`): Virtual Xbox controller emulation
- **Imutils** (`imutils`): Image processing utilities
- **NumPy** (`numpy`): Numerical computations

## 🔧 Troubleshooting

### Common Issues

1. **Camera not detected**: Ensure your webcam is connected and not being used by other applications
2. **High CPU usage**: Reduce camera resolution or increase frame skip intervals
3. **Delayed responses**: Check system performance and close unnecessary applications
4. **Actions not triggering**: Reconfigure trigger zones through the setup process

### Performance Tips

- Ensure good lighting for better pose/face detection
- Position yourself at arm's length from the camera
- Minimize background movement for better tracking
- Use a solid color background when possible

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [OpenCV](https://opencv.org/) for computer vision capabilities
- [MediaPipe](https://mediapipe.dev/) for pose detection
- [PyInput](https://github.com/moses-palmer/pynput) for input simulation
- [VGamepad](https://github.com/yannbouteiller/vgamepad) for Xbox controller emulation
- [Imutils](https://github.com/PyImageSearch/imutils) for image processing utilities

## 🚀 Getting Started Examples

### Quick Start - Pose Control
```bash
# Install dependencies
pip install opencv-python mediapipe pynput imutils numpy

# Run pose-based control (will prompt for setup on first run)
python -m pose.pose

# Follow the interactive setup to configure trigger zones
# Start playing your game and use body movements to control!
```

### Quick Start - Penalty Kicks
```bash
# Install additional dependencies for gamepad emulation
pip install vgamepad

# Run penalty kick controller
python penalty_kick.py

# Position your leg in the center circle to trigger penalty kicks
# Perfect for FIFA or other football games!
```

---

**Ready to game with your body? Choose your control method and start playing! 🎮**
