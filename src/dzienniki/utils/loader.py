import os
import pygame

_image_cache = {}
_sound_cache = {}

def load_image(name: str) -> pygame.Surface:
    """Ładuje i buforuje obrazek z assets/images."""
    path = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "images", name)
    if path not in _image_cache:
        _image_cache[path] = pygame.image.load(path).convert_alpha()
    return _image_cache[path]

def load_sound(name: str) -> pygame.mixer.Sound:
    """Ładuje i buforuje dźwięk z assets/sounds."""
    path = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "sounds", name)
    if path not in _sound_cache:
        _sound_cache[path] = pygame.mixer.Sound(path)
    return _sound_cache[path]