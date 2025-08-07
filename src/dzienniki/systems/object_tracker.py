import pygame
from dzienniki.audio import tts

SCAN_RADIUS = 10
FONT_SIZE = 24
TEXT_COLOR = (255, 255, 255)
HIGHLIGHT_COLOR = (255, 255, 0)
BOX_COLOR = (60, 60, 60)
PADDING = 10

class ObjectTracker:
    def __init__(self):
        self.objects = []  # Lista 1: zeskanowane obiekty
        self.saved_points = []  # Lista 2: zapisane punkty użytkownika
        self.selected_index = 0
        self.list_index = 0  # 0 = obiekty, 1 = punkty
        self.flag = None
        self.show_submenu = False
        self.submenu_options = ["Edytuj", "Usuń"]
        self.submenu_index = 0
        self.active = False
        self.font = pygame.font.SysFont(None, FONT_SIZE)  # ← tu przeniesione

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
        self.show_submenu = False
        self.active = True

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
        if self.show_submenu:
            self.submenu_index = (self.submenu_index + 1) % len(self.submenu_options)
            tts.speak(self.submenu_options[self.submenu_index])
        else:
            max_index = len(self.objects) if self.list_index == 0 else len(self.saved_points) + 1
            self.selected_index = (self.selected_index + 1) % max_index
            self.speak_selected()

    def previous_object(self):
        if self.show_submenu:
            self.submenu_index = (self.submenu_index - 1 + len(self.submenu_options)) % len(self.submenu_options)
            tts.speak(self.submenu_options[self.submenu_index])
        else:
            max_index = len(self.objects) if self.list_index == 0 else len(self.saved_points) + 1
            self.selected_index = (self.selected_index - 1 + max_index) % max_index
            self.speak_selected()

    def switch_list(self, backwards=False):
        if self.show_submenu:
            return
        self.list_index = (self.list_index - 1 if backwards else self.list_index + 1) % 2
        self.selected_index = 0
        self.speak_selected()

    def set_flag(self, player):
        if self.show_submenu:
            return
        if self.list_index == 1 and self.selected_index == 0:
            self.saved_points.insert(0, ("Punkt", player.grid_x, player.grid_y))
            tts.speak("Dodano punkt.")
        elif self.list_index == 0 and self.objects:
            obj = self.objects[self.selected_index]
            self.flag = (obj["x"], obj["y"])
            tts.speak(f"Ustawiono flagę na {obj['name']}, X {obj['x']}, Y {obj['y']}")
        elif self.list_index == 1 and self.selected_index > 0:
            x, y = self.saved_points[self.selected_index - 1][1:]
            self.flag = (x, y)
            tts.speak(f"Ustawiono flagę na punkt {self.saved_points[self.selected_index - 1][0]}, X {x}, Y {y}")

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

    def cancel_flag(self):
        if self.flag:
            self.flag = None
            tts.speak("Anulowano śledzenie flagi.")

    def open_submenu(self):
        if self.list_index == 1 and self.selected_index > 0:
            self.show_submenu = True
            self.submenu_index = 0
            tts.speak(f"Opcje: {self.submenu_options[0]}")

    def confirm_submenu_action(self):
        if not self.show_submenu:
            return
        option = self.submenu_options[self.submenu_index]
        idx = self.selected_index - 1
        if option == "Usuń" and idx >= 0:
            point = self.saved_points.pop(idx)
            if self.flag == (point[1], point[2]):
                self.flag = None
            tts.speak(f"Usunięto punkt {point[0]}")
        elif option == "Edytuj" and idx >= 0:
            name, x, y = self.saved_points[idx]
            self.saved_points[idx] = (f"{name}*", x, y)
            tts.speak(f"Zmieniono nazwę punktu na {name} gwiazdka.")
        self.show_submenu = False

    def cancel_submenu(self):
        if self.show_submenu:
            self.show_submenu = False
            tts.speak("Zamknięto submenu.")
        else:
            self.active = False
            tts.speak("Zamknięto listę obiektów.")

    def draw(self, screen):
        w = screen.get_width() // 2 - 20
        h = screen.get_height() - 100
        x0 = 20
        y0 = 50

        # Tło i ramki list
        pygame.draw.rect(screen, BOX_COLOR, (x0, y0, w, h))
        pygame.draw.rect(screen, BOX_COLOR, (x0 + w + 20, y0, w, h))

        # Lista 1 – zeskanowane obiekty
        for i, obj in enumerate(self.objects):
            text = f"{obj['name']}, X {obj['x']} Y {obj['y']}, {obj['distance']} kratek na {obj['direction']}"
            label = self.font.render(text, True, HIGHLIGHT_COLOR if self.list_index == 0 and self.selected_index == i else TEXT_COLOR)
            screen.blit(label, (x0 + PADDING, y0 + PADDING + i * FONT_SIZE))

        # Lista 2 – zapisane punkty
        points = [("Ustaw punkt", None, None)] + self.saved_points
        for i, (name, x, y) in enumerate(points):
            text = f"{name}" if x is None else f"{name}, X {x} Y {y}"
            label = self.font.render(text, True, HIGHLIGHT_COLOR if self.list_index == 1 and self.selected_index == i else TEXT_COLOR)
            screen.blit(label, (x0 + w + 20 + PADDING, y0 + PADDING + i * FONT_SIZE))

        # Submenu
        if self.show_submenu:
            for i, option in enumerate(self.submenu_options):
                label = self.font.render(option, True, HIGHLIGHT_COLOR if self.submenu_index == i else TEXT_COLOR)
                screen.blit(label, (x0 + w + 60, y0 + h - 60 + i * FONT_SIZE))

        # Flaga – podświetlenie
        if self.flag:
            size = 32  # TILE_SIZE
            fx, fy = self.flag
            pygame.draw.rect(screen, (255, 0, 0), (fx * size, fy * size, size, size), 2)
