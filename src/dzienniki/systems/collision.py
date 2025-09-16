# src/dzienniki/systems/collision.py

from pathlib import Path
import json
import numpy as np
from typing import List, Dict, Any

def load_legend(path: Path) -> Dict[str, Any]:
    """
    Wczytuje legendę kafli z JSON:
    {
      "tileset_version": 1,
      "tiles": {
        ".": {"name": "...", "collide": false, "sprite": "tiles/grass.png"},
        ...
      }
    }
    """
    return json.loads(path.read_text(encoding="utf-8"))

def build_collision_mask(chunk_grid: List[List[str]], legend: Dict[str, Any]) -> np.ndarray:
    """
    Tworzy maskę kolizji (True = blokada) na podstawie siatki znaków chunku.
    Oczekuje gridu o wymiarach [wysokość][szerokość].
    """
    h, w = len(chunk_grid), len(chunk_grid[0]) if chunk_grid else 0
    mask = np.zeros((h, w), dtype=np.bool_)

    tiles: Dict[str, Any] = legend.get("tiles", {})
    get = tiles.get

    for y, row in enumerate(chunk_grid):
        for x, ch in enumerate(row):
            info = get(ch)
            if info and info.get("collide", False):
                mask[y, x] = True

    return mask
