# src/dzienniki/systems/world_api.py

from pathlib import Path
from typing import Optional

from .chunk_manager import ChunkManager
from .collision import load_legend

class World:
    """
    Wysokopoziomowy interfejs do świata:
    - ładowanie legendy
    - zarządzanie chunkami
    - test kolizji
    - dostęp do kafli
    """
    def __init__(self, base_dir: Path, chunk_size: int = 64, layers: Optional[list[str]] = None):
        self.base_dir = base_dir
        self.chunk_size = chunk_size
        self.layers = layers or ["ground", "block", "decor"]

        # Wczytaj legendę kafli
        legend_file = base_dir / "assets" / "config" / "map_legend.json"
        if not legend_file.exists():
            raise FileNotFoundError(f"Brak pliku legendy: {legend_file}")
        self.legend = load_legend(legend_file)

        # Stwórz menedżer chunków
        self.manager = ChunkManager(
            base_dir=base_dir,
            chunk_size=self.chunk_size,
            layers=self.layers,
            legend=self.legend,
            capacity=64,
        )

    def preload(self, grid_x: int, grid_y: int, radius: int = 1):
        """Preload chunków wokół pozycji gracza."""
        cs = self.chunk_size
        cx, cy = grid_x // cs, grid_y // cs
        self.manager.preload_radius(cx, cy, radius)

    def is_blocked(self, grid_x: int, grid_y: int) -> bool:
        """Sprawdza kolizję na współrzędnych siatki."""
        return self.manager.is_blocked(grid_x, grid_y)

    def get_tile(self, layer: str, grid_x: int, grid_y: int) -> Optional[str]:
        """Zwraca symbol kafla na wskazanej warstwie."""
        cs = self.chunk_size
        cx, cy = grid_x // cs, grid_y // cs
        ox, oy = grid_x % cs, grid_y % cs
        self.manager.ensure_loaded(cx, cy)
        grid = self.manager.get_grid(layer, cx, cy)
        if grid is None:
            return None
        if 0 <= oy < len(grid) and 0 <= ox < len(grid[0]):
            return grid[oy][ox]
        return None
