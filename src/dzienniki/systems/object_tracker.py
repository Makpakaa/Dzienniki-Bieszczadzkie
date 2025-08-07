import pygame
from dzienniki.audio import tts

SCAN_RADIUS = 10

class ObjectTracker:
    def __init__(self):
        self.objects = []  # Lista 1: zeskanowane obiekty
        self.saved_points = []  # Lista 2: zapisane punkty użytkownika
        self.selected_index = 0
        self.list_index = 0  # 0 = obiekty, 1 = punkty
        self.flag = None
        self.font = pygame.font.SysFont(None, 24)

    def scan_area(self, player, map_rows, names):
        self.objects.clear()
        px, py = player.grid_x, player.grid_y

        for dy in range(-SCAN_RADIUS, SCAN_RADIUS + 1):
            for dx in range(-SCAN_RADIUS, SCAN_RADIUS + 1):
                x, y = px + dx, py + dy
                if 0 <= y < len(map_rows) and 0 <= x < len(map_rows[0]):
                    symbol = map_rows[y][x]
                    name = names.get(symbol, None)
                    if name and name != names.get(map_rows[py][px], None):
                        distance = abs(dx) + abs(dy)
                        direction = self._get_direction(dx, dy)
                        self.objects.append({
                            "name": name,
                            "x": x,
                            "y": y,
                            "distance": distance,
                            "direction": direction
                        })

        self.objects.sort(key=lambda o: o["distance"])
        self.selected_index = 0
        self.list_index = 0

    def _get_direction(self, dx, dy):
        if dx == 0 and dy < 0:
            return "północ"
        elif dx == 0 and dy > 0:
            return "południe"
        elif dy == 0 and dx < 0:
            return "zachód"
        elif dy == 0 and dx > 0:
            return "wschód"
        elif dx > 0 and dy < 0:
            return "północny wschód"
        elif dx < 0 and dy < 0:
            return "północny zachód"
        elif dx > 0 and dy > 0:
            return "południowy wschód"
        elif dx < 0 and dy > 0:
            return "południowy zachód"
        else:
            return "tu"

    def speak_selected(self):
        if self.list_index == 0 and self.objects:
            obj = self.objects[self.selected_index]
            tts.speak(f"{obj['name']}, X {obj['x']} Y {obj['y']}, {obj['distance']} kratek na {obj['direction']}")
        elif self.list_index == 1:
            if self.selected_index == 0:
                tts.speak("Ustaw punkt w miejscu gracza")
            else:
                name, x, y = self.saved_points[self.selected_index - 1]
                tts.speak(f"{name}, X {x} Y {y}")

    def next_object(self):
        max_index = len(self.objects) if self.list_index == 0 else len(self.saved_points) + 1
        self.selected_index = (self.selected_index + 1) % max_index
        self.speak_selected()

    def previous_object(self):
        max_index = len(self.objects) if self.list_index == 0 else len(self.saved_points) + 1
        self.selected_index = (self.selected_index - 1 + max_index) % max_index
        self.speak_selected()

    def set_flag(self, player):
        if self.list_index == 1 and self.selected_index == 0:
            self.saved_points.insert(0, ("Punkt", player.grid_x, player.grid_y))
            tts.speak("Dodano punkt.")
        elif self.list_index == 0 and self.objects:
            obj = self.objects[self.selected_index]
            self.flag = (obj["x"], obj["y"])
            tts.speak(f"Ustawiono flagę na {obj['name']}, X {obj['x']}, Y {obj['y']}")
        elif self.list_index == 1 and self.selected_index > 0:
            name, x, y = self.saved_points[self.selected_index - 1]
            self.flag = (x, y)
            tts.speak(f"Ustawiono flagę na punkcie {name}, X {x}, Y {y}")

    def clear_flag(self):
        if self.flag:
            tts.speak("Anulowano śledzenie celu.")
            self.flag = None
        else:
            tts.speak("Nie ustawiono żadnego celu.")

    def speak_target_direction(self, player):
        if not self.flag:
            tts.speak("Nie ustawiono flagi.")
            return

        dx = self.flag[0] - player.grid_x
        dy = self.flag[1] - player.grid_y
        distance = abs(dx) + abs(dy)
        direction = self._get_direction(dx, dy)

        if (player.grid_x, player.grid_y) == self.flag:
            self.flag = None
            tts.speak("Osiągnięto punkt docelowy.")
        else:
            tts.speak(f"Flaga: {distance} kratek na {direction}.")

    def switch_list(self, backwards=False):
        self.list_index = (self.list_index - 1 if backwards else self.list_index + 1) % 2
        self.selected_index = 0
        self.speak_selected()

    def open_submenu(self, player):
        if self.list_index == 1 and self.selected_index > 0:
            name, x, y = self.saved_points[self.selected_index - 1]
            tts.speak(f"Opcje: Edytuj lub Usuń punkt {name}")

    def draw(self, screen):
        pass  # Placeholder
