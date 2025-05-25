from dataclasses import dataclass
import pygame
from dzienniki import settings

@dataclass(unsafe_hash=True)
class Player(pygame.sprite.Sprite):
    """Prosty biały kwadrat jako gracz."""
    x: float     = settings.SCREEN_WIDTH  / 2
    y: float     = settings.SCREEN_HEIGHT / 2
    speed: float = 200.0
    facing: str  = "down"

    def __post_init__(self):
        super().__init__()
        self.image = pygame.Surface((settings.TILE_SIZE, settings.TILE_SIZE))
        self.image.fill((255, 255, 255))
        self.rect  = self.image.get_rect(center=(self.x, self.y))

    def update(self, dt: float, map_rows, passable: dict):
        """
        Przesuwa gracza z kolizją wg czasu dt i mapy.
        passable: dict znak->bool, czy można wejść.
        """
        keys = pygame.key.get_pressed()
        dx = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * self.speed * dt
        dy = (keys[pygame.K_DOWN]  - keys[pygame.K_UP])   * self.speed * dt

        # aktualizacja kierunku
        if dx > 0:
            self.facing = "right"
        elif dx < 0:
            self.facing = "left"
        elif dy > 0:
            self.facing = "down"
        elif dy < 0:
            self.facing = "up"

        size = settings.TILE_SIZE

        # ruch w osi X z kolizją
        new_rect = self.rect.copy()
        new_rect.x += dx
        col = new_rect.centerx // size
        row = self.rect.centery   // size
        # zabezpieczamy na wypadek braku mapy lub indeksów
        if 0 <= row < len(map_rows) and 0 <= col < len(map_rows[0]):
            if passable.get(map_rows[row][col], True):
                self.rect.x = new_rect.x
        else:
            # gdy poza mapą, nie ruszamy się w X
            pass

        # ruch w osi Y z kolizją
        new_rect = self.rect.copy()
        new_rect.y += dy
        col = self.rect.centerx // size
        row = new_rect.centery   // size
        if 0 <= row < len(map_rows) and 0 <= col < len(map_rows[0]):
            if passable.get(map_rows[row][col], True):
                self.rect.y = new_rect.y
        else:
            # gdy poza mapą, nie ruszamy się w Y
            pass

        # ograniczenie do granic okna
        self.rect.x = max(0, min(self.rect.x, settings.SCREEN_WIDTH  - size))
        self.rect.y = max(0, min(self.rect.y, settings.SCREEN_HEIGHT - size))
