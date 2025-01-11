# Ten plik zawiera klasę Player, która reprezentuje gracza, jego statystyki oraz metody obsługujące ruch i ekwipunek.

class Player:
    def __init__(self):
        self.name = "Podróżnik"
        self.health = 100
        self.stamina = 100
        self.inventory = []  # Lista przedmiotów w ekwipunku
        self.position = [0, 0]  # Pozycja gracza na mapie

    def move(self, direction):
        if direction == "up":
            self.position[1] -= 1
        elif direction == "down":
            self.position[1] += 1
        elif direction == "left":
            self.position[0] -= 1
        elif direction == "right":
            self.position[0] += 1

    def add_item(self, item):
        self.inventory.append(item)

    def remove_item(self, item):
        if item in self.inventory:
            self.inventory.remove(item)
