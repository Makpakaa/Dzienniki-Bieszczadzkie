# src/dzienniki/systems/player.py

import pygame
import os

SPRITE_PATH = os.path.join(os.path.dirname(__file__), "../assets/images/player/player_walk.png")
SPRITE_PATH = os.path.abspath(SPRITE_PATH)

DIRECTION_MAP = {
    "down": 0,
    "left": 1,
    "right": 2,
    "up": 3
}

class Player:
    def __init__(self, x, y):
        self.grid_x = x
        self.grid_y = y
        self.pixel_x = x * 32
        self.pixel_y = y * 32
        self.direction = "down"
        self.frame = 0
        self.animation_timer = 0

        self.sprite_sheet = pygame.image.load(SPRITE_PATH).convert_alpha()
        self.frames = self.load_frames(32, 32)

    def load_frames(self, width, height):
        frames = {dir: [] for dir in DIRECTION_MAP}
        for dir_name, row in DIRECTION_MAP.items():
            for col in range(3):  # zakładamy 3 klatki na kierunek
                rect = pygame.Rect(col * width, row * height, width, height)
                image = self.sprite_sheet.subsurface(rect)
                frames[dir_name].append(image)
        return frames

    def update(self):
        self.animation_timer += 1
        if self.animation_timer >= 10:
            self.frame = (self.frame + 1) % 3
            self.animation_timer = 0

    def draw(self, surface):
        current_frame = self.frames[self.direction][self.frame]
        surface.blit(current_frame, (self.pixel_x, self.pixel_y))
