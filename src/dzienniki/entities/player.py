# src/dzienniki/entities/player.py

import pygame
from dzienniki import settings
from dzienniki.utils.loader import load_image

SPRITE_PATH = "assets/images/player/player_walk.png"

DIRECTION_MAP = {
    "down": 0,
    "left": 1,
    "right": 2,
    "up": 3
}

class Player:
    def __init__(self):
        self.grid_x = 50  # ✅ startowa pozycja X
        self.grid_y = 50  # ✅ startowa pozycja Y
        self.pixel_x = self.grid_x * settings.TILE_SIZE
        self.pixel_y = self.grid_y * settings.TILE_SIZE
        self.target_x = self.pixel_x
        self.target_y = self.pixel_y
        self.direction = "down"
        self.facing = "down"
        self.frame = 0
        self.animation_timer = 0
        self.moving = False
        self.speed = 100  # px/s

        original = load_image(SPRITE_PATH)
        self.sprite_sheet = pygame.transform.scale(original, (96, 128))
        self.frames = self.load_frames(settings.TILE_SIZE, settings.TILE_SIZE)

        self.rect = pygame.Rect(
            self.pixel_x,
            self.pixel_y,
            settings.TILE_SIZE,
            settings.TILE_SIZE
        )

    def load_frames(self, width, height):
        frames = {dir: [] for dir in DIRECTION_MAP}
        for dir_name, row in DIRECTION_MAP.items():
            for col in range(3):  # 3 klatki animacji
                rect = pygame.Rect(col * width, row * height, width, height)
                image = self.sprite_sheet.subsurface(rect)
                frames[dir_name].append(image)
        return frames

    def handle_input(self, keys):
        if self.moving:
            return

        dx = dy = 0
        if keys[pygame.K_w]:
            self.direction = "up"
            self.facing = "up"
            dy = -1
        elif keys[pygame.K_s]:
            self.direction = "down"
            self.facing = "down"
            dy = 1
        elif keys[pygame.K_a]:
            self.direction = "left"
            self.facing = "left"
            dx = -1
        elif keys[pygame.K_d]:
            self.direction = "right"
            self.facing = "right"
            dx = 1

        if dx != 0 or dy != 0:
            self.try_move(dx, dy)

    def try_move(self, dx, dy):
        self.grid_x += dx
        self.grid_y += dy
        self.target_x = self.grid_x * settings.TILE_SIZE
        self.target_y = self.grid_y * settings.TILE_SIZE
        self.moving = True

    def update(self, dt, map_rows, passable):
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

            self.animation_timer += dt
            if self.animation_timer >= 0.15:
                self.frame = (self.frame + 1) % 3
                self.animation_timer = 0

        self.rect.topleft = (round(self.pixel_x), round(self.pixel_y))

    def draw(self, surface):
        frame = self.frames[self.direction][self.frame]
        surface.blit(frame, (round(self.pixel_x), round(self.pixel_y)))
