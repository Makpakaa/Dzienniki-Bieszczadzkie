from functools import lru_cache
from pathlib import Path
import json
from typing import List

RLE_SEP = "×"  # np.: .×20

def _safe_read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")

def rle_decode_line(line: str) -> List[str]:
    out: List[str] = []
    i = 0
    n = len(line)
    while i < n:
        ch = line[i]
        if ch in ("\n", "\r"):
            i += 1
            continue
        if i + 1 < n and line[i+1] == RLE_SEP:
            i += 2
            j = i
            while j < n and line[j].isdigit():
                j += 1
            count = int(line[i:j]) if i < j else 1
            out.extend([ch] * count)
            i = j
        else:
            out.append(ch)
            i += 1
    return out

def rle_decode_chunk(text: str, size: int) -> List[List[str]]:
    rows = text.splitlines()
    if len(rows) != size:
        raise ValueError(f"RLE: nieprawidłowa liczba wierszy: {len(rows)} != {size}")
    grid = [rle_decode_line(r) for r in rows]
    for y, row in enumerate(grid):
        if len(row) != size:
            raise ValueError(f"RLE: wiersz {y} ma {len(row)} kolumn zamiast {size}")
    return grid

def rle_encode_line(symbols: List[str]) -> str:
    if not symbols:
        return ""
    res = []
    cur = symbols[0]
    run = 1
    for s in symbols[1:]:
        if s == cur:
            run += 1
        else:
            res.append(cur if run == 1 else f"{cur}{RLE_SEP}{run}")
            cur = s
            run = 1
    res.append(cur if run == 1 else f"{cur}{RLE_SEP}{run}")
    return "".join(res)

def rle_encode_chunk(grid: List[List[str]]) -> str:
    return "\n".join(rle_encode_line(row) for row in grid)

def load_json(path: Path):
    return json.loads(_safe_read_text(path))

@lru_cache(maxsize=256)
def load_chunk(layer: str, cx: int, cy: int, base_dir: Path, chunk_size: int) -> List[List[str]]:
    p = base_dir / "assets" / "maps" / "chunks" / layer / f"{cx:04d}_{cy:04d}.rle.txt"
    if not p.exists():
        raise FileNotFoundError(f"Brak pliku chunku: {p}")
    text = _safe_read_text(p)
    grid = rle_decode_chunk(text, chunk_size)
    # Patches (delta) – opcjonalne
    patch_file = base_dir / "saves" / "world" / "changes" / layer / f"{cx:04d}_{cy:04d}.patch.json"
    if patch_file.exists():
        try:
            patches = load_json(patch_file)
            for it in patches:
                x = int(it["x"]); y = int(it["y"]); tile_id = str(it["id"])
                if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
                    grid[y][x] = tile_id
        except Exception:
            # jeśli patch uszkodzony – ignorujemy
            pass
    return grid
