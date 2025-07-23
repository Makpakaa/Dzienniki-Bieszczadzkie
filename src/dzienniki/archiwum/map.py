from dataclasses import dataclass
import pygame
import os
from dzienniki import settings
from dzienniki.systems.item import Item
from dzienniki.audio import tts

SPRITE_PATH = os.path.join(os.path.dirname(__file__), "../assets/player/player_walk.png")
SPRITE_PATH = os.path.abspath(SPRITE_PATH)

DIRECTION_VECTORS = {
    "up": (0, -1),
    "down": (0, 1),
    "left": (-1, 0),
    "right": (1, 0),
}

DIRECTION_NAMES = {
    "up": "północ",
    "down": "południe",
    "left": "zachód",
    "right": "wschód"
}

KAFEL_NAZWY = {'g': "trawa", 'w': "woda", 's': "kamień"}

@dataclass(unsafe_hash=True)
class Player(pygame.sprite.Sprite):
    x: float = settings.SCREEN_WIDTH / 2
    y: float = settings.SCREEN_HEIGHT / 2
    speed: float = 200.0
    facing: str = "down"

    def __post_init__(self):
        super().__init__()
        self.image = pygame.Surface((settings.TILE_SIZE, settings.TILE_SIZE))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect(center=(self.x, self.y))

        # animacja
        self.sprite_sheet = pygame.image.load(SPRITE_PATH).convert_alpha()
        self.frames = self.load_frames(341, 256)
        self.frame_index = 0
        self.anim_timer = 0.0
        self.anim_speed = 0.15

        # ekwipunek
        self.inventory = [
            Item(name="Kilof", count=1, item_type="tool"),
            Item(name="Pochodnia", count=3, item_type="tool"),
            Item(name="Ziemniak", count=5, item_type="food"),
        ]
        self.equipment = {k: None for k in ["head", "torso", "hands", "legs", "feet", "back"]}
        self.quick_access = [None] * 9

        # pozycja gracza
        self.last_tile_pos = (-1, -1)  # do detekcji zmiany kafla

    def load_frames(self, w, h):
        frames = {d: [] for d in DIRECTION_VECTORS}
        for dir_name, row in enumerate(["down", "left", "right", "up"]):
            for col in range(3):
                rect = pygame.Rect(col * w, row * h, w, h)
                image = self.sprite_sheet.subsurface(rect).copy()
                image = pygame.transform.scale(image, (settings.TILE_SIZE, settings.TILE_SIZE))
                frames[row].append(image)
        return frames

    def update(self, dt, map_rows, passable):
        keys = pygame.key.get_pressed()
        dx = (keys[pygame.K_d] - keys[pygame.K_a]) * self.speed * dt
        dy = (keys[pygame.K_s] - keys[pygame.K_w]) * self.speed * dt

        if dx > 0:
            self.facing = "right"
        elif dx < 0:
            self.facing = "left"
        elif dy > 0:
            self.facing = "down"
        elif dy < 0:
            self.facing = "up"

        moved = False
        size = settings.TILE_SIZE

        # ruch w osi X
        new_rect = self.rect.copy()
        new_rect.x += dx
        col = new_rect.centerx // size
        row = self.rect.centery // size
        if 0 <= row < len(map_rows) and 0 <= col < len(map_rows[0]):
            if passable.get(map_rows[row][col], True):
                self.rect.x = new_rect.x
                moved = True

        # ruch w osi Y
        new_rect = self.rect.copy()
        new_rect.y += dy
        col = self.rect.centerx // size
        row = new_rect.centery // size
        if 0 <= row < len(map_rows) and 0 <= col < len(map_rows[0]):
            if passable.get(map_rows[row][col], True):
                self.rect.y = new_rect.y
                moved = True

        # granice
        self.rect.x = max(0, min(self.rect.x, settings.SCREEN_WIDTH - size))
        self.rect.y = max(0, min(self.rect.y, settings.SCREEN_HEIGHT - size))

        # animacja
        if moved:
            self.anim_timer += dt
            if self.anim_timer >= self.anim_speed:
                self.frame_index = (self.frame_index + 1) % 3
                self.anim_timer = 0
        else:
            self.frame_index = 1  # środkowa klatka spoczynkowa

        # mowa – tylko przy zmianie kratki
        tile_x = self.rect.centerx // size
        tile_y = self.rect.centery // size
        if (tile_x, tile_y) != self.last_tile_pos:
            self.last_tile_pos = (tile_x, tile_y)
            current_tile = map_rows[tile_y][tile_x]
            kierunek = DIRECTION_NAMES[self.facing]

            # kafel przed graczem
            dx_f, dy_f = DIRECTION_VECTORS[self.facing]
            next_x = tile_x + dx_f
            next_y = tile_y + dy_f
            if 0 <= next_y < len(map_rows) and 0 <= next_x < len(map_rows[0]):
                front_tile = map_rows[next_y][next_x]
                front_name = KAFEL_NAZWY.get(front_tile, "nieznane")
                tts.speak(f"Jesteś na: {KAFEL_NAZWY.get(current_tile, 'nieznane')}. X: {tile_x}, Y: {tile_y}. Kierunek: {kierunek}. Przed tobą: {front_name}.")
            else:
                tts.speak(f"Jesteś na: {KAFEL_NAZWY.get(current_tile, 'nieznane')}. X: {tile_x}, Y: {tile_y}. Kierunek: {kierunek}. Przed tobą: granica mapy.")

    def draw(self, screen):
        frame = self.frames[self.facing][self.frame_index]
        screen.blit(frame, self.rect)
