# src/dzienniki/utils/loader.py

import os
import pygame
from dzienniki import settings

_image_cache = {}
_sound_cache = {}

def load_image(name: str) -> pygame.Surface:
    """Ładuje i buforuje obrazek z assets/images."""
    if name in _image_cache:
        return _image_cache[name]

    path = os.path.join(settings.IMAGES_DIR, name)
    if os.path.exists(path):
        img = pygame.image.load(path).convert_alpha()
    else:
        img = pygame.Surface((settings.TILE_SIZE, settings.TILE_SIZE))
        img.fill((34, 177, 76))  # zielony placeholder
    _image_cache[name] = img
    return img

def load_sound(name: str) -> pygame.mixer.Sound:
    """Ładuje i buforuje dźwięk z assets/sounds."""
    if name in _sound_cache:
        return _sound_cache[name]

    path = os.path.join(settings.SOUNDS_DIR, name)
    if os.path.exists(path):
        sound = pygame.mixer.Sound(path)
    else:
        class Silent:
            def play(self, *args, **kwargs): pass
        sound = Silent()
    _sound_cache[name] = sound
    return sound

def load_icons_from_folder(relative_path):
    """
    Ładuje wszystkie pliki PNG z folderu i zwraca słownik:
    {'nazwa_pliku_bez_rozszerzenia': pygame.Surface}
    """
    import glob
    icon_dict = {}

    folder = os.path.join("assets", "images", relative_path)
    files = glob.glob(os.path.join(folder, "*.png"))

    for path in files:
        name = os.path.splitext(os.path.basename(path))[0]
        try:
            icon = pygame.image.load(path).convert_alpha()
            icon_dict[name] = icon
        except Exception as e:
            print(f"❌ Nie udało się załadować {path}: {e}")

    print(f"✔️ Załadowano {len(icon_dict)} ikon z {relative_path}")
    return icon_dict
