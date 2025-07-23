# src/dzienniki/utils/loader.py

import pygame
import os

def load_image(relative_path):
    """Wczytuje obraz z podanej ścieżki względnej (np. 'assets/images/player/sprite.png')"""
    full_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../", relative_path))
    try:
        image = pygame.image.load(full_path).convert_alpha()
        return image
    except Exception as e:
        print(f"Nie udało się wczytać obrazu: {relative_path}\n{e}")
        return pygame.Surface((32, 32))  # zapasowy placeholder

def load_sound(relative_path):
    """Wczytuje dźwięk z podanej ścieżki względnej (np. 'assets/sounds/blip.wav')"""
    full_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../", relative_path))
    try:
        return pygame.mixer.Sound(full_path)
    except Exception as e:
        print(f"Nie udało się wczytać dźwięku: {relative_path}\n{e}")
        return None
