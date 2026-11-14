"""
Configuration settings for the Gestural Agentic Alien Tech & Iron Man Animation.
Tuned for maximum sensitivity, instantaneous hand response, and glassy alien aesthetics.
"""
import os

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
MODEL_PATH = os.path.join(BASE_DIR, "hand_landmarker.task")

# Camera Configuration
CAMERA_INDEX = 0
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
FPS_TARGET = 60

# Hand Tracking & Sensitivity (Zero-Lag & Instant Response)
MIN_DETECTION_CONFIDENCE = 0.40
MIN_PRESENCE_CONFIDENCE = 0.40
MIN_TRACKING_CONFIDENCE = 0.40

# Adaptive One-Euro Smoothing
# Instant response to fast hand movements, smooth stability when holding still
VELOCITY_THRESHOLD = 0.05
SMOOTH_FACTOR_SLOW = 0.50
SMOOTH_FACTOR_FAST = 0.98    # Snaps instantly to hand motions

# Avatar Configuration
DEFAULT_AVATAR = "alien"     # Default to "alien" (glassy bluish alien-tech suit)
AVATAR_WIDTH = 380           # Big, imposing, majestic suit size
AVATAR_HEIGHT = 540
AGENT_NAME = "A.L.I.E.N. // MARK-X"
USER_TAG = "kal@gestural-agentic:~$"

# Colors (BGR Format) - Glassy Bluish & Quantum Cyan
COLOR_CYAN_GLOW = (255, 230, 40)      # Luminous Cyan
COLOR_CYAN_CORE = (255, 255, 255)     # White Hot Core
COLOR_ELECTRIC_BLUE = (255, 180, 0)   # Electric Blue
COLOR_GOLD_STRING = (60, 210, 255)    # Glowing Golden-Cyan Tendrils
COLOR_ORANGE_HUD = (30, 160, 255)     # Cyberpunk Orange
COLOR_HUD_BG = (12, 14, 20)           # Glassy Deep Blue-Black HUD
COLOR_TEXT_WHITE = (245, 245, 250)
COLOR_TEXT_CYAN = (255, 235, 100)

# Neural Puppet Strings
NUM_STRINGS_PER_FINGER = 4
STRING_SAG = 35.0
STRING_WAVE_SPEED = 7.0
