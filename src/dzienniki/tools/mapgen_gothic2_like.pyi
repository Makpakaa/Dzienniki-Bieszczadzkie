"""
Generator chunków w RLE pod świat 1024×1024 (64×64 per chunk).
Uproszczona topografia inspirowana Gothic 2: spawn przy "wieży Xardasa".

Uruchom (z katalogu projektu):
  python -m dzienniki.tools.mapgen_gothic2_like

Wynik:
  assets/maps/world.meta.json
  assets/maps/chunks/{ground,block,decor}/*.rle.txt
  assets/config/map_legend.json (jeśli nie istnieje)
"""

from pathlib import Path
import json
import math
import random

from dzienniki.systems.world_io import rle_encode_chunk

# Uwaga: plik jest w src/dzienniki/tools; root projektu jest 3 poziomy wyżej
BASE_DIR = Path(__file__).resolve().parents[3]
MAP_DIR = BASE_DIR / "assets" / "maps"
CHUNKS_DIR = MAP_DIR / "chunks"
CONFIG_DIR = BASE_DIR / "assets" / "config"

WORLD_SIZE = (1024, 1024)  # siatka pól
CHUNK_SIZE = 64
LAYERS = ["ground", "block", "decor"]

LEGEND_DEFAULT = {
    "tileset_version": 1,
    "tiles": {
        ".": {"name": "trawa",   "collide": False, "sprite": "tiles/grass.png"},
        ",": {"name": "sciezka", "collide": False, "sprite": "tiles/path.png"},
        "^": {"name": "skala",   "collide": True,  "sprite": "tiles/rock.png"},
        "~": {"name": "woda",    "collide": True,  "sprite": "tiles/water.png"},
        "#": {"name": "mur",     "collide": True,  "sprite": "tiles/wall.png"},
        "D": {"name": "drzewo",  "collide": True,  "sprite": "tiles/tree.png"},
        "K": {"name": "krzak",   "collide": True,  "sprite": "tiles/bush.png"},
        "S": {"name": "spawn",   "collide": False, "sprite": "tiles/grass.png"}
    }
}

def ensure_dirs():
    (CHUNKS_DIR / "ground").mkdir(parents=True, exist_ok=True)
    (CHUNKS_DIR / "block").mkdir(parents=True, exist_ok=True)
    (CHUNKS_DIR / "decor").mkdir(parents=True, exist_ok=True)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def write_json(p: Path, data: dict):
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def base_layer(world_w: int, world_h: int, fill: str = "."):
    return [[fill for _ in range(world_w)] for _ in range(world_h)]

def add_plateau_and_spawn(ground, block, spawn=(128, 128)):
    """
    Płaskowyż (trawa) z obwódką skalną. Spawn (S) na środku.
    """
    cx, cy = spawn
    radius = 40
    for y in range(cy - radius, cy + radius + 1):
        if y < 0 or y >= len(ground):
            continue
        for x in range(cx - radius, cx + radius + 1):
            if x < 0 or x >= len(ground[0]):
                continue
            dist = math.hypot(x - cx, y - cy)
            if dist <= radius:
                ground[y][x] = "."
            # kamienista obwódka
            if radius - 3 <= dist <= radius + 1:
                if random.random() < 0.4:
                    block[y][x] = "^"
    ground[cy][cx] = "S"

def add_path_to_valley(ground, start=(128, 128), end=(700, 700)):
    """
    Kręta ścieżka prowadząca ze spawnu do doliny.
    """
    x, y = start
    ex, ey = end
    steps = 1100
    for _ in range(steps):
        ground[y][x] = ","
        dx = 1 if x < ex else (-1 if x > ex else 0)
        dy = 1 if y < ey else (-1 if y > ey else 0)
        # krętość
        if random.random() < 0.3:
            dx, dy = dy, dx
        x = max(1, min(len(ground[0]) - 2, x + dx))
        y = max(1, min(len(ground) - 2, y + dy))
        if random.random() < 0.25:
            ground[y][x + 1] = ","
        if random.random() < 0.25:
            ground[y + 1][x] = ","

def add_ridges(block, count=14):
    """
    Pasma skał (gardła, naturalne korytarze).
    """
    h, w = len(block), len(block[0])
    for _ in range(count):
        x = random.randint(100, w - 100)
        y = random.randint(100, h - 100)
        length = random.randint(150, 300)
        angle = random.random() * math.tau
        for i in range(length):
            px = int(x + math.cos(angle) * i + math.sin(i * 0.1) * 2)
            py = int(y + math.sin(angle) * i + math.cos(i * 0.1) * 2)
            if 0 <= px < w and 0 <= py < h:
                block[py][px] = "^"
                if random.random() < 0.6 and px + 1 < w:
                    block[py][px + 1] = "^"
                if random.random() < 0.4 and py + 1 < h:
                    block[py + 1][px] = "^"

def add_lake(ground, block, center=(800, 300), radius=90):
    """
    Jezioro z kamienistym brzegiem i nieco udeptaną ścieżką wokół.
    """
    cx, cy = center
    for y in range(cy - radius - 3, cy + radius + 4):
        if y < 0 or y >= len(ground):
            continue
        for x in range(cx - radius - 3, cx + radius + 4):
            if x < 0 or x >= len(ground[0]):
                continue
            dist = math.hypot(x - cx, y - cy)
            if dist <= radius:
                block[y][x] = "~"  # woda (kolizja)
            elif radius < dist <= radius + 2:
                if random.random() < 0.4:
                    block[y][x] = "^"
                if random.random() < 0.2:
                    ground[y][x] = ","

def add_forest(block, decor, density=0.07):
    """
    Lasy: drzewa z kolizją (D), trochę krzaków dekoracyjnych (K).
    """
    h, w = len(block), len(block[0])
    for y in range(h):
        for x in range(w):
            if block[y][x] in ("^", "~"):
                continue
            r = random.random()
            if r < density:
                block[y][x] = "D"
            elif r < density + 0.02:
                decor[y][x] = "K"

def save_chunks(layer_grids, layer_name: str):
    """
    Zapisuje siatkę warstwy do plików RLE per chunk (64×64).
    """
    world_h = len(layer_grids)
    world_w = len(layer_grids[0])
    for cy in range(0, world_h, CHUNK_SIZE):
        for cx in range(0, world_w, CHUNK_SIZE):
            chunk = [row[cx:cx + CHUNK_SIZE] for row in layer_grids[cy:cy + CHUNK_SIZE]]
            text = rle_encode_chunk(chunk)
            p = CHUNKS_DIR / layer_name / f"{cx // CHUNK_SIZE:04d}_{cy // CHUNK_SIZE:04d}.rle.txt"
            p.write_text(text, encoding="utf-8")

def main():
    ensure_dirs()

    # Legenda – jeśli brak, zapisz domyślną
    legend_path = CONFIG_DIR / "map_legend.json"
    if not legend_path.exists():
        legend_path.write_text(json.dumps(LEGEND_DEFAULT, ensure_ascii=False, indent=2), encoding="utf-8")

    world_w, world_h = WORLD_SIZE
    ground = base_layer(world_w, world_h, ".")
    block  = base_layer(world_w, world_h, ".")
    decor  = base_layer(world_w, world_h, ".")

    spawn = (128, 128)
    add_plateau_and_spawn(ground, block, spawn)
    add_path_to_valley(ground, start=spawn, end=(700, 700))
    add_ridges(block, count=14)
    add_lake(ground, block, center=(800, 300), radius=90)
    add_forest(block, decor, density=0.07)

    save_chunks(ground, "ground")
    save_chunks(block,  "block")
    save_chunks(decor,  "decor")

    world_meta = {
        "tile_size": 32,
        "world_size": [WORLD_SIZE[0], WORLD_SIZE[1]],
        "chunk_size": [CHUNK_SIZE, CHUNK_SIZE],
        "layers": LAYERS,
        "spawn": {"grid_x": spawn[0], "grid_y": spawn[1], "hint": "xardas_tower"}
    }
    (MAP_DIR / "world.meta.json").write_text(json.dumps(world_meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print("OK: wygenerowano świat 1024×1024 (chunk 64×64).")
    print("Spawn: 128,128 (plateau). Woda/góry/drzewa mają kolizję. Ścieżka do doliny jest kręta.")

if __name__ == "__main__":
    main()
