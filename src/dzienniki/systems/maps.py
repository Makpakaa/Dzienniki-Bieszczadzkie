# src/dzienniki/systems/maps.py

import random

class TileMap:
    def __init__(self, width=100, height=100):
        self.width = width
        self.height = height

        self.rows = self.generate_map()

        self.names = {
            "g": "trawa",
            "w": "woda",
            "s": "kamień"
        }

        self.passable = {
            "g": True,
            "w": False,
            "s": False
        }

    def generate_map(self):
        rows = []
        for _ in range(self.height):
            row = []
            for _ in range(self.width):
                r = random.random()
                if r < 0.05:
                    row.append("w")  # 5% szansa na wodę
                elif r < 0.10:
                    row.append("s")  # 5% szansa na kamień
                else:
                    row.append("g")  # 90% szansa na trawę
            rows.append(row)
        return rows
