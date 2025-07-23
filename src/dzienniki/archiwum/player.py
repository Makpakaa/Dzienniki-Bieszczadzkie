import pygame
import os
from dzienniki.audio import tts

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
        self.target_x = self.pixel_x
        self.target_y = self.pixel_y
        self.direction = "down"
        self.frame = 0
        self.animation_timer = 0
        self.moving = False
        self.speed = 100  # px/sekundę

        self.sprite_sheet = pygame.image.load(SPRITE_PATH).convert_alpha()
        self.frames = self.load_frames(32, 32)

    def load_frames(self, width, height):
        frames = {dir: [] for dir in DIRECTION_MAP}
        for dir_name, row in DIRECTION_MAP.items():
            for col in range(3):  # 3 klatki na kierunek
                rect = pygame.Rect(col * width, row * height, width, height)
                image = self.sprite_sheet.subsurface(rect)
                frames[dir_name].append(image)
        return frames

    def handle_input(self, keys):
        if self.moving:
            return

        if keys[pygame.K_w]:
            self.direction = "up"
            self.try_move(0, -1)
        elif keys[pygame.K_s]:
            self.direction = "down"
            self.try_move(0, 1)
        elif keys[pygame.K_a]:
            self.direction = "left"
            self.try_move(-1, 0)
        elif keys[pygame.K_d]:
            self.direction = "right"
            self.try_move(1, 0)

    def try_move(self, dx, dy):
        self.grid_x += dx
        self.grid_y += dy
        self.target_x = self.grid_x * 32
        self.target_y = self.grid_y * 32
        self.moving = True

    def update(self, dt):
        if self.moving:
            dx = self.target_x - self.pixel_x
            dy = self.target_y - self.pixel_y

            distance = self.speed * dt

            if abs(dx) > 0:
                self.pixel_x += min(distance, abs(dx)) * (1 if dx > 0 else -1)
            if abs(dy) > 0:
                self.pixel_y += min(distance, abs(dy)) * (1 if dy > 0 else -1)

            if abs(self.pixel_x - self.target_x) < 1 and abs(self.pixel_y - self.target_y) < 1:
                self.pixel_x = self.target_x
                self.pixel_y = self.target_y
                self.moving = False
                self.frame = 0
                tts.speak(f"Pozycja: {self.grid_x}, {self.grid_y}")
            # animacja tylko w ruchu
            self.animation_timer += dt
            if self.animation_timer >= 0.15:
                self.frame = (self.frame + 1) % 3
                self.animation_timer = 0

    def draw(self, surface):
        frame = self.frames[self.direction][self.frame]
        surface.blit(frame, (round(self.pixel_x), round(self.pixel_y)))
