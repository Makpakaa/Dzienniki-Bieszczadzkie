from dataclasses import dataclass
import pygame
from dzienniki import settings

@dataclass(unsafe_hash=True)
class Player(pygame.sprite.Sprite):
    """Prosty biały kwadrat jako gracz."""
    x: float = settings.SCREEN_WIDTH / 2
    y: float = settings.SCREEN_HEIGHT / 2
    speed: float = 200.0
    facing: str = "down"  # domyślny kierunek: "up","down","left","right"

    def __post_init__(self):
        super().__init__()
        # tworzymy biały kwadrat
        self.image = pygame.Surface((settings.TILE_SIZE, settings.TILE_SIZE))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def update(self, dt: float):
        """Przesuwa gracza wg czasu dt i wciśniętych klawiszy."""
        keys = pygame.key.get_pressed()
        dx = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * self.speed * dt
        dy = (keys[pygame.K_DOWN]  - keys[pygame.K_UP])    * self.speed * dt
        # aktualizacja kierunku patrzenia
        if dx > 0:
            self.facing = "right"
        elif dx < 0:
            self.facing = "left"
        elif dy > 0:
            self.facing = "down"
        elif dy < 0:
            self.facing = "up"
        self.rect.x += dx
        self.rect.y += dy
        # ograniczenie do granic ekranu
        self.rect.x = max(0, min(self.rect.x, settings.SCREEN_WIDTH - settings.TILE_SIZE))
        self.rect.y = max(0, min(self.rect.y, settings.SCREEN_HEIGHT - settings.TILE_SIZE))
