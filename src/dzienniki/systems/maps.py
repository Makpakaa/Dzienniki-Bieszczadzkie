import random

class TileMap:
    """
    Zgodne z player.py:
    - rows: 2D siatka ID kafli (np. "g", "w", "s")
    - names: dict {tile_id: nazwa}
    - passable: dict {tile_id: bool} -> True = przejście, False = blokada
    - spawn: (x, y) – punkt startowy gracza (wyznaczany automatycznie)
    """

    T_GRASS = "g"
    T_WATER = "w"
    T_STONE = "s"

    def __init__(self, width=100, height=100, seed=None):
        self.width = width
        self.height = height

        if seed is not None:
            random.seed(seed)

        self.rows = self.generate_map()

        self.names = {
            self.T_GRASS: "trawa",
            self.T_WATER: "woda",
            self.T_STONE: "kamień",
        }

        self.passable = {
            self.T_GRASS: True,   # przejście
            self.T_WATER: False,  # blokada
            self.T_STONE: False,  # blokada
        }

        # Profesjonalnie: spawn definiuje MAPA (nie Player).
        # Spróbujemy centrum, a jeśli blokada, szukamy najbliższej trawy.
        self.spawn = self._compute_spawn()

    def generate_map(self):
        rows = []
        for _ in range(self.height):
            row = []
            for _ in range(self.width):
                r = random.random()
                if r < 0.05:
                    row.append(self.T_WATER)  # 5% wody
                elif r < 0.10:
                    row.append(self.T_STONE)  # 5% kamienia
                else:
                    row.append(self.T_GRASS)  # 90% trawy
            rows.append(row)
        return rows

    # --- pomocnicze ---

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= y < len(self.rows) and 0 <= x < len(self.rows[0])

    def tile_id_at(self, x: int, y: int):
        if not self.in_bounds(x, y):
            return None
        return self.rows[y][x]

    def tile_name_at(self, x: int, y: int):
        tid = self.tile_id_at(x, y)
        if tid is None:
            return None
        return self.names.get(tid, None)

    def is_passable_xy(self, x: int, y: int) -> bool:
        if not self.in_bounds(x, y):
            return False
        tid = self.rows[y][x]
        val = self.passable.get(tid, True)
        if isinstance(val, bool):
            return val
        if isinstance(val, (int, float)):
            return val != 0
        return bool(val)

    def _compute_spawn(self):
        # 1) Celuj w centrum
        cx = max(0, min(self.width - 1, self.width // 2))
        cy = max(0, min(self.height - 1, self.height // 2))
        if self.is_passable_xy(cx, cy):
            return (cx, cy)

        # 2) Szukaj najbliższego przejścia pierścieniami wokół centrum
        max_radius = max(self.width, self.height)
        for r in range(1, max_radius):
            for dx in range(-r, r + 1):
                for dy in (-r, r):
                    x, y = cx + dx, cy + dy
                    if self.in_bounds(x, y) and self.is_passable_xy(x, y):
                        return (x, y)
            for dy in range(-r + 1, r):
                for dx in (-r, r):
                    x, y = cx + dx, cy + dy
                    if self.in_bounds(x, y) and self.is_passable_xy(x, y):
                        return (x, y)

        # 3) Awaryjnie – pierwszy napotkany kafel przejściowy
        for y in range(self.height):
            for x in range(self.width):
                if self.is_passable_xy(x, y):
                    return (x, y)

        # 4) Jeśli naprawdę nie ma przejścia (niezdarzające się) – (0,0)
        return (0, 0)

    # (opcjonalnie) jednorazowy sanity-check TTS – możesz dopisać tu,
    # jeśli masz moduł tts pod ręką; w przeciwnym razie zostaje w game.py.
