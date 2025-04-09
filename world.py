# world.py

class DroppedItem:
    def __init__(self, name, quantity, x, y):
        self.name = name
        self.quantity = quantity
        self.x = x  # współrzędna X na mapie
        self.y = y  # współrzędna Y na mapie

    def __str__(self):
        return f"{self.name} ({self.quantity}) na pozycji ({self.x}, {self.y})"

# Świat, w którym leżą upuszczone przedmioty
dropped_items = []

def drop_item(name, quantity, player_x, player_y, facing_direction):
    # Upuszczenie przed graczem w zależności od kierunku patrzenia
    dx, dy = 0, 0
    if facing_direction == "up":
        dy = -1
    elif facing_direction == "down":
        dy = 1
    elif facing_direction == "left":
        dx = -1
    elif facing_direction == "right":
        dx = 1

    new_x = player_x + dx
    new_y = player_y + dy

    dropped = DroppedItem(name, quantity, new_x, new_y)
    dropped_items.append(dropped)
    return dropped
