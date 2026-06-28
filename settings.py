import os
import pygame

# Screen Configuration
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Colors
COLOR_ROAD = (40, 40, 40)
COLOR_GRASS = (34, 139, 34)
COLOR_WALL = (165, 42, 42)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (220, 20, 60)
COLOR_BLUE = (30, 144, 255)
COLOR_YELLOW = (255, 215, 0)
COLOR_GREEN = (50, 205, 50)
COLOR_NITRO = (0, 255, 255)
COLOR_TEXT = (245, 245, 245)
COLOR_PANEL = (20, 20, 20, 220)

# Directory Setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_DIR = os.path.join(BASE_DIR, "saves")
SAVE_FILE = os.path.join(SAVE_DIR, "progress.json")

# Ensure Directories Exist
os.makedirs(os.path.join(BASE_DIR, "assets", "cars"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "assets", "sounds"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "assets", "images"), exist_ok=True)
os.makedirs(SAVE_DIR, exist_ok=True)

# Vehicle Archetypes Data
CAR_TYPES = {
    "Interceptor": {
        "max_speed": 320.0,
        "acceleration": 180.0,
        "handling": 4.5,
        "max_health": 100.0,
        "color": COLOR_BLUE,
        "cost": 0
    },
    "Apex Ranger": {
        "max_speed": 360.0,
        "acceleration": 210.0,
        "handling": 4.0,
        "max_health": 90.0,
        "color": COLOR_RED,
        "cost": 1500
    },
    "Juggernaut": {
        "max_speed": 290.0,
        "acceleration": 150.0,
        "handling": 5.0,
        "max_health": 160.0,
        "color": COLOR_YELLOW,
        "cost": 2500
    }
}