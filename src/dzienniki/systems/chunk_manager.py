# src/dzienniki/systems/chunk_manager.py

from pathlib import Path
from collections import deque
from typing import Dict, Tuple, Any

import numpy as np
from .world_io import load_chunk
from .collision import build_collision_mask

Key = Tuple[str, int, int]  # (layer, cx, cy)

class ChunkManager:
    """
    Trzyma aktywne chunki (tiles + collision mask dla warstwy 'block'),
    dba o prosty LRU i preloading sąsiadów.
    """
    def __init__(self, base_dir: Path, chunk_size: int, layers: list[str], legend: dict, capacity: int = 48):
        self.base_dir = base_dir
        self.chunk_size = chunk_size
        self.layers = layers
        self.legend = legend
        self.capacity = capacity

        self.active: Dict[Key, Dict[str, Any]] = {}
        self.order: deque[Key] = deque()

    def _touch(self, key: Key):
        """Oznacza element jako najświeżej użyty i wyrzuca najstarsze, gdy przekroczymy pojemność."""
        try:
            self.order.remove(key)
        except ValueError:
            pass
        self.order.appendleft(key)
        while len(self.order) > self.capacity:
            k = self.order.pop()
            self.active.pop(k, None)

    def ensure_loaded(self, cx: int, cy: int):
        """Gwarantuje, że wszystkie warstwy chunku (cx, cy) są w pamięci."""
        for layer in self.layers:
            key: Key = (layer, cx, cy)
            if key not in self.active:
                grid = load_chunk(layer, cx, cy, self.base_dir, self.chunk_size)
                mask = build_collision_mask(grid, self.legend) if layer == "block" else None
                self.active[key] = {"tiles": grid, "mask": mask}
            self._touch(key)

    def preload_radius(self, center_cx: int, center_cy: int, radius: int = 1):
        """Preloaduje pierścień chunków wokół (center_cx, center_cy)."""
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                self.ensure_loaded(center_cx + dx, center_cy + dy)

    def get_grid(self, layer: str, cx: int, cy: int):
        key = (layer, cx, cy)
        item = self.active.get(key)
        return item["tiles"] if item else None

    def get_mask(self, cx: int, cy: int):
        key = ("block", cx, cy)
        item = self.active.get(key)
        return item["mask"] if item else None

    def is_blocked(self, grid_x: int, grid_y: int) -> bool:
        """
        Szybki test kolizji w skali całego świata (mapuje globalny grid na chunk + offset).
        """
        cs = self.chunk_size
        cx, cy = grid_x // cs, grid_y // cs
        ox, oy = grid_x % cs, grid_y % cs
        self.ensure_loaded(cx, cy)
        mask = self.get_mask(cx, cy)
        if mask is None:
            return False
        if 0 <= oy < mask.shape[0] and 0 <= ox < mask.shape[1]:
            return bool(mask[oy, ox])
        return False
