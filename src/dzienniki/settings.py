import os

# Tytuł i rozmiar okna
WINDOW_TITLE = "Dzienniki Bieszczadzkie"
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Ścieżki do zasobów
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "..", "..", "assets")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")