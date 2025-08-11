import pygame
from dzienniki.audio import tts

# -----------------------------
# Ustawienia
# -----------------------------
SCAN_RADIUS = 10

FONT_SIZE = 24
TEXT_COLOR = (255, 255, 255)
HIGHLIGHT_COLOR = (255, 255, 0)
BOX_COLOR = (60, 60, 60)
PADDING = 10
LINE_SPACING = 6
BORDER_WIDTH = 2

# Domyślne filtry nazw (case-insensitive)
IGNORE_NAMES = {"trawa"}

# -----------------------------
# Lazy init font (pygame musi być już zainicjalizowane)
# -----------------------------
_FONT = None
def _font():
    global _FONT
    if _FONT is None:
        _FONT = pygame.font.SysFont(None, FONT_SIZE)
    return _FONT


# -----------------------------
# Pomocnicze
# -----------------------------
def _dir_and_distance(px, py, tx, ty):
    """Kierunek słownie i dystans Manhattan od pozycji gracza (kratki)."""
    dx = tx - px
    dy = ty - py
    adx = abs(dx)
    ady = abs(dy)

    if dx == 0 and dy == 0:
        direction = "tu"
    else:
        vertical = "północ" if dy < 0 else ("południe" if dy > 0 else "")
        horizontal = "wschód" if dx > 0 else ("zachód" if dx < 0 else "")
        direction = f"{vertical}-{horizontal}" if (vertical and horizontal) else (vertical or horizontal)

    distance = adx + ady
    return direction, distance


def _safe_tile_id(map_rows, x, y):
    """Bezpiecznie zwraca ID kafla z mapy (np. 'w', 's') albo None."""
    try:
        if 0 <= y < len(map_rows) and 0 <= x < len(map_rows[0]):
            return map_rows[y][x]
    except Exception:
        pass
    return None


def _get_tile_name_from_names(names, x, y):
    """
    Fallback: gdy 'names' jest strukturą współrzędnych (2D lista / dicty z (y,x) itp.).
    W normalnym trybie nazwy bierzemy z mapowania ID -> nazwa.
    """
    if names is None:
        return None

    # 2D lista
    try:
        return names[y][x]
    except Exception:
        pass

    # dict warianty
    if isinstance(names, dict):
        try:
            if (y, x) in names:
                return names[(y, x)]
        except Exception:
            pass
        try:
            if (x, y) in names:
                return names[(x, y)]
        except Exception:
            pass
        try:
            row = names.get(y)
            if isinstance(row, dict):
                return row.get(x)
        except Exception:
            pass

    return None


def _tile_display_name(map_rows, names, x, y):
    """
    1) czyta ID z map_rows[y][x]
    2) jeśli names jest dictem: names[ID] -> nazwa (np. 'w' -> 'woda')
    3) inaczej fallback (_get_tile_name_from_names)
    """
    tile_id = _safe_tile_id(map_rows, x, y)
    if tile_id is not None and isinstance(names, dict):
        pretty = names.get(tile_id)
        if pretty and str(pretty).strip():
            return str(pretty)

    # Fallback na stare formaty
    return _get_tile_name_from_names(names, x, y)


def _facing_vec(facing: str):
    """Wektor kratki przed graczem dla facing: up/down/left/right."""
    return {
        "up": (0, -1),
        "down": (0, 1),
        "left": (-1, 0),
        "right": (1, 0),
    }.get(facing, (0, 0))


# -----------------------------
# Klasa główna
# -----------------------------
class ObjectTracker:
    """
    Dwie listy:
      - self.objects      -> zeskanowane obiekty (lista 1)
      - self.saved_points -> zapisane punkty użytkownika (lista 2)
    """
    def __init__(self):
        # Dane
        self.objects = []
        self.saved_points = []

        # Stan UI
        self.list_index = 0          # 0 = objects, 1 = saved_points
        self.selected_index = 0
        self.active = False

        # Przewijanie list
        self._scroll_offset_left = 0
        self._scroll_offset_right = 0

        # Flaga celu (x, y) jako krotka lub None
        self.flag = None
        # Etykieta celu do wypowiedzenia przy dotarciu
        self.flag_label = None

        # Submenu
        self.show_submenu = False
        self.submenu_options = ["Edytuj", "Usuń"]
        self.submenu_index = 0

        # Referencje i callbacki
        self._player_ref = None
        self.rename_provider = None   # def get_new_name(old_name:str)->str | None
        self.on_flag_reached = None   # def on_flag_reached(pos:(x,y)) -> None

        # Ostatni komunikat TTS
        self._last_tts = ""

        # Rysowanie
        self.tile_size = 32  # domyślny rozmiar kafla

        # Filtry (nazwy ignorowane, case-insensitive)
        self.ignore_names = {n.strip().casefold() for n in IGNORE_NAMES}

    # ---------- API filtrów ----------
    def set_ignore_names(self, names):
        """Ustaw listę nazw do ignorowania w skanie (np. ['trawa', 'piasek'])."""
        try:
            self.ignore_names = {str(n).strip().casefold() for n in names}
        except Exception:
            pass

    def add_ignore_name(self, name):
        """Dodaj pojedynczą nazwę do ignorowania."""
        try:
            self.ignore_names.add(str(name).strip().casefold())
        except Exception:
            pass

    def clear_ignore_names(self):
        """Wyczyść listę ignorowanych nazw."""
        self.ignore_names.clear()

    # ---------- TTS ----------
    def _speak(self, msg: str):
        self._last_tts = msg or ""
        tts.speak(msg)

    def repeat_last_message(self):
        if self._last_tts:
            tts.speak(self._last_tts)

    def speak_selected(self):
        self._announce_focus()

    # ---------- Integracja / API ----------
    def set_tile_size(self, tile_size: int):
        """Ustaw rozmiar kafla używany podczas rysowania flagi."""
        try:
            tile_size = int(tile_size)
            if tile_size > 0:
                self.tile_size = tile_size
        except Exception:
            pass

    def draw(self, screen):
        """Uniwersalne rysowanie dla game.py: flaga + UI."""
        self.draw_flag_on_map(screen, self.tile_size)
        self.draw_ui(screen)

    def activate(self, player):
        self.active = True
        self._player_ref = player
        self.list_index = 0
        self.selected_index = 0
        self._scroll_offset_left = 0
        self._scroll_offset_right = 0
        self.show_submenu = False
        self.submenu_index = 0
        self._speak("Tryb nawigacji obiektów włączony. Zeskanowane obiekty.")

    def deactivate(self):
        self.active = False
        self._player_ref = None  # (FIX) poprawne wcięcie
        self.show_submenu = False
        self._speak("Zamknięto nawigację obiektów.")

    def scan_area(self, player, map_rows, names):
        """
        Skanuje obszar wokół gracza:
        - Kafle bierzemy z map_rows.
        - Nazwy tłumaczymy przez 'names' jako słownik {ID: nazwa}.
        - Pomijamy nazwy ustawione w self.ignore_names (np. 'trawa').
        """
        self.objects.clear()
        px, py = player.grid_x, player.grid_y

        x_min = px - SCAN_RADIUS
        x_max = px + SCAN_RADIUS
        y_min = py - SCAN_RADIUS
        y_max = py + SCAN_RADIUS

        for y in range(y_min, y_max + 1):
            for x in range(x_min, x_max + 1):
                if x == px and y == py:
                    continue

                tile_name = _tile_display_name(map_rows, names, x, y)
                if not (tile_name and str(tile_name).strip()):
                    continue

                # --- filtr nazw (case-insensitive) ---
                name_norm = str(tile_name).strip().casefold()
                if name_norm in self.ignore_names:
                    continue

                direction, distance = _dir_and_distance(px, py, x, y)
                self.objects.append({
                    "name": str(tile_name),
                    "x": x,
                    "y": y,
                    "direction": direction,
                    "distance": distance
                })

        self.objects.sort(key=lambda o: (o["distance"], o["name"]))
        self.selected_index = 0
        self._scroll_offset_left = 0

        if self.objects:
            first = self.objects[0]
            self._speak(
                f"Znaleziono {len(self.objects)} obiektów. "
                f"Pierwszy: {first['name']}, {first['x']} {first['y']}, "
                f"z {first['distance']} kratek na {first['direction']}."
            )
        else:
            self._speak("Nie znaleziono obiektów w pobliżu.")

    # ---------- Flaga ----------
    def set_flag(self, pos_or_player):
        """
        Ustawia flagę:
        - (x, y)  -> bezpośrednio
        - player  -> na pozycji gracza
        Uwaga: zawsze zeruje flag_label (żeby nie został stary opis).
        """
        if hasattr(pos_or_player, "grid_x") and hasattr(pos_or_player, "grid_y"):
            x, y = pos_or_player.grid_x, pos_or_player.grid_y
        elif isinstance(pos_or_player, (tuple, list)) and len(pos_or_player) >= 2:
            x, y = int(pos_or_player[0]), int(pos_or_player[1])
        else:
            self._speak("Nieprawidłowa pozycja flagi.")
            return
        self.flag = (int(x), int(y))
        self.flag_label = None
        self._speak(f"Ustawiono flagę. Cel: {self.flag[0]} {self.flag[1]}.")

    def clear_flag(self):
        self.flag = None
        self.flag_label = None
        self._speak("Anulowano flagę.")

    def speak_target_direction(self, player, consider_front_tile: bool = False):
        """Informuje, gdzie jest flaga względem pozycji GRACZA (nie kratki przed nim)."""
        if not self.flag:
            return
        px = getattr(player, "grid_x", None)
        py = getattr(player, "grid_y", None)
        if px is None or py is None:
            return
        tx, ty = self.flag
        direction, distance = _dir_and_distance(px, py, tx, ty)
        if distance == 0:
            msg = "Flaga jest dokładnie na Twojej kratce."
        elif distance == 1:
            msg = f"Flaga: 1 kratka na {direction}."
        else:
            msg = f"Flaga: {distance} kratek na {direction}."
        self._speak(msg)

    def check_flag_reached(self, player, consider_front_tile: bool = False):
        """Zwraca True, jeśli gracz stanął na kracie z flagą (i flaga została usunięta)."""
        if not self.flag:
            return False
        refx = getattr(player, "grid_x", None)
        refy = getattr(player, "grid_y", None)
        if refx is None or refy is None:
            return False
        if (int(refx), int(refy)) == (int(self.flag[0]), int(self.flag[1])):
            pos = self.flag
            self.clear_flag()
            self._speak("Cel osiągnięty. Flaga usunięta.")
            if callable(self.on_flag_reached):
                try:
                    self.on_flag_reached(pos)
                except Exception:
                    pass
            return True
        return False

    def auto_clear_flag_if_front_reached(self, player, map_rows, names):
        """
        Jeśli kratka PRZED graczem == pozycja flagi:
         - usuń flagę
         - powiedz: 'Jesteś u celu. {nazwa}' (najpierw flag_label, potem nazwa kafla, inaczej współrzędne)
        Zwraca True, gdy flaga została skasowana.
        """
        if not self.flag:
            return False

        px = getattr(player, "grid_x", None)
        py = getattr(player, "grid_y", None)
        facing = getattr(player, "facing", None)
        if px is None or py is None or not facing:
            return False

        dx, dy = _facing_vec(facing)
        front = (px + dx, py + dy)
        if front == tuple(self.flag):
            # 1) nazwa z wyboru (obiekt / zapisany punkt), 2) nazwa kafla, 3) współrzędne
            name = self.flag_label or _tile_display_name(map_rows, names, front[0], front[1]) or f"{front[0]} {front[1]}"
            self.flag = None
            self.flag_label = None
            self._speak(f"Jesteś u celu. {name}")
            if callable(self.on_flag_reached):
                try:
                    self.on_flag_reached(front)
                except Exception:
                    pass
            return True

        return False

    # ---------- Rysowanie ----------
    def _compute_visible_rows(self, rect_height):
        f = _font()
        row_h = f.get_height() + LINE_SPACING
        title_h = f.get_height() + LINE_SPACING + PADDING
        usable = max(0, rect_height - title_h - PADDING)
        count = max(1, usable // row_h)
        return count, row_h

    def _draw_list_box(self, screen, rect, title, rows, selected_idx, is_left_list):
        pygame.draw.rect(screen, BOX_COLOR, rect)
        pygame.draw.rect(screen, HIGHLIGHT_COLOR, rect, BORDER_WIDTH)

        f = _font()
        title_surf = f.render(title, True, TEXT_COLOR)
        screen.blit(title_surf, (rect.x + PADDING, rect.y + PADDING))

        visible, row_h = self._compute_visible_rows(rect.height)
        offset = self._scroll_offset_left if is_left_list else self._scroll_offset_right

        if selected_idx >= 0:
            if selected_idx < offset:
                offset = selected_idx
            elif selected_idx >= offset + visible:
                offset = selected_idx - visible + 1

        if is_left_list:
            self._scroll_offset_left = offset
        else:
            self._scroll_offset_right = offset

        start = offset
        end = min(len(rows), offset + visible)
        y = rect.y + PADDING + title_surf.get_height() + LINE_SPACING

        for i in range(start, end):
            is_sel = (i == selected_idx)
            color = HIGHLIGHT_COLOR if is_sel else TEXT_COLOR
            surf = f.render(rows[i], True, color)
            screen.blit(surf, (rect.x + PADDING, y))
            y += row_h

        if len(rows) > visible:
            bar_w = 6
            bar_x = rect.right - bar_w - 3
            inner_top = rect.y + title_surf.get_height() + 3 * PADDING
            inner_h = rect.height - (inner_top - rect.y) - PADDING
            frac = visible / float(len(rows))
            bar_h = max(12, int(inner_h * frac))
            max_scroll = max(1, len(rows) - visible)
            pos_frac = (offset / float(max_scroll)) if max_scroll else 0.0
            bar_y = inner_top + int((inner_h - bar_h) * pos_frac)
            pygame.draw.rect(screen, (200, 200, 200), pygame.Rect(bar_x, bar_y, bar_w, bar_h))

    def _format_object_row(self, obj):
        return f"{obj['name']}, {obj['x']} {obj['y']}, z {obj['distance']} kratek na {obj['direction']}"

    def _saved_rows_with_action(self):
        rows = ["Ustaw punkt"]
        for sp in self.saved_points:
            rows.append(f"{sp['name']}, {sp['pos'][0]} {sp['pos'][1]}")
        return rows

    def draw_ui(self, screen):
        sw, sh = screen.get_size()
        panel_w = max(320, int(sw * 0.42))
        panel_h = max(220, int(sh * 0.6))

        left_rect = pygame.Rect(PADDING, PADDING, panel_w, panel_h)
        right_rect = pygame.Rect(sw - panel_w - PADDING, PADDING, panel_w, panel_h)

        objects_rows = [self._format_object_row(o) for o in self.objects] or ["(brak obiektów)"]
        saved_rows = self._saved_rows_with_action()

        sel_left = self.selected_index if self.list_index == 0 and self.objects else (-1 if self.list_index != 0 else 0)
        sel_right = self.selected_index if self.list_index == 1 else -1

        self._draw_list_box(screen, left_rect, "Zeskanowane obiekty", objects_rows, sel_left, True)
        self._draw_list_box(screen, right_rect, "Zapisane punkty", saved_rows, sel_right, False)

        if self.show_submenu and self.list_index == 1 and self.selected_index > 0:
            self._draw_submenu(screen, right_rect)

    def _draw_submenu(self, screen, parent_rect):
        f = _font()
        width = 220
        height = (FONT_SIZE + LINE_SPACING) * len(self.submenu_options) + PADDING * 2
        rect = pygame.Rect(parent_rect.right - width - PADDING,
                           parent_rect.y + PADDING * 2,
                           width, height)
        pygame.draw.rect(screen, BOX_COLOR, rect)
        pygame.draw.rect(screen, HIGHLIGHT_COLOR, rect, BORDER_WIDTH)

        y = rect.y + PADDING
        for i, option in enumerate(self.submenu_options):
            color = HIGHLIGHT_COLOR if i == self.submenu_index else TEXT_COLOR
            surf = f.render(option, True, color)
            screen.blit(surf, (rect.x + PADDING, y))
            y += FONT_SIZE + LINE_SPACING

    def draw_flag_on_map(self, screen, tile_size):
        if self.flag is None:
            return
        fx, fy = self.flag
        flag_rect = pygame.Rect(fx * tile_size, fy * tile_size, tile_size, tile_size)
        pygame.draw.rect(screen, (255, 0, 0), flag_rect, 3)
        cx = flag_rect.centerx
        cy = flag_rect.centery
        pygame.draw.line(screen, (255, 0, 0), (cx - tile_size // 4, cy), (cx + tile_size // 4, cy), 2)
        pygame.draw.line(screen, (255, 0, 0), (cx, cy - tile_size // 4), (cx, cy + tile_size // 4), 2)

    # ---------- Obsługa klawiszy ----------
    def handle_key(self, key):
        mods = pygame.key.get_mods()

        # Ctrl+F -> anulowanie flagi
        if (mods & pygame.KMOD_CTRL) and key == pygame.K_f:
            if self.flag is not None:
                self.clear_flag()
            else:
                self._speak("Brak aktywnej flagi.")
            return

        if self.show_submenu:
            if key in (pygame.K_w, pygame.K_UP):
                self.submenu_prev()
                return
            if key in (pygame.K_s, pygame.K_DOWN):
                self.submenu_next()
                return
            if key == pygame.K_RETURN:
                self._execute_submenu_action()
                return
            if key == pygame.K_ESCAPE:
                self.show_submenu = False
                self._speak("Zamknięto menu.")
                return
            return

        # Główna nawigacja list
        if key in (pygame.K_w, pygame.K_UP):
            self._move_selection(-1)
            return
        if key in (pygame.K_s, pygame.K_DOWN):
            self._move_selection(+1)
            return

        if key == pygame.K_TAB:
            self._switch_list(next_=not (mods & pygame.KMOD_SHIFT))
            return

        if key == pygame.K_RETURN:
            self._activate_selection()
            return

        if key == pygame.K_SPACE:
            self._open_submenu_if_available()
            return

        if key == pygame.K_ESCAPE:
            self._speak("Brak menu do zamknięcia.")
            return

    # ---------- Alias kompatybilności z Twoim game.py ----------
    @property
    def submenu_open(self):
        return self.show_submenu

    def activate_selection(self):
        """ENTER/SPACE w trackerze (publiczne API)"""
        self._activate_selection()

    def submenu_select(self):
        """ENTER/SPACE w submenu."""
        if self.show_submenu:
            self._execute_submenu_action()

    def open_submenu(self, _player=None):
        """SPACE poza submenu -> otwórz jeśli dostępne."""
        self._open_submenu_if_available()

    def previous_object(self):
        """W poprzedni wiersz (lista aktywna)."""
        self._move_selection(-1)

    def next_object(self):
        """W następny wiersz (lista aktywna)."""
        self._move_selection(+1)

    def switch_list(self, backwards=False):
        """Tab / Shift+Tab."""
        self._switch_list(next_=not backwards)

    def submenu_prev(self):
        """W wiersz wyżej w submenu."""
        if self.show_submenu:
            self.submenu_index = (self.submenu_index - 1) % len(self.submenu_options)
            self._speak(self.submenu_options[self.submenu_index])

    def submenu_next(self):
        """W wiersz niżej w submenu."""
        if self.show_submenu:
            self.submenu_index = (self.submenu_index + 1) % len(self.submenu_options)
            self._speak(self.submenu_options[self.submenu_index])

    # --- Wewnętrzne akcje list ---
    def _move_selection(self, step):
        if self.list_index == 0:
            max_rows = max(1, len(self.objects))
        else:
            max_rows = max(1, len(self.saved_points) + 1)  # +1 za „Ustaw punkt”
        self.selected_index = (self.selected_index + step) % max_rows
        self._announce_focus()

    def _switch_list(self, next_=True):
        self.list_index = (self.list_index + (1 if next_ else -1)) % 2
        self.selected_index = 0
        self._speak("Zeskanowane obiekty." if self.list_index == 0 else "Zapisane punkty.")

    def _announce_focus(self):
        if self.list_index == 0:
            if not self.objects:
                self._speak("Brak obiektów.")
                return
            o = self.objects[self.selected_index]
            self._speak(f"{o['name']}, {o['x']} {o['y']}, z {o['distance']} kratek na {o['direction']}")
        else:
            if self.selected_index == 0:
                self._speak("Ustaw punkt.")
            else:
                sp = self.saved_points[self.selected_index - 1]
                self._speak(f"{sp['name']}, {sp['pos'][0]} {sp['pos'][1]}")

    def _activate_selection(self):
        if self.list_index == 0:
            if not self.objects:
                self._speak("Brak obiektów.")
                return
            o = self.objects[self.selected_index]
            # Najpierw ustaw flagę, potem etykietę (set_flag czyści label)
            self.set_flag((o["x"], o["y"]))
            self.flag_label = o["name"]
        else:
            if self.selected_index == 0:
                if not self._player_ref:
                    self._speak("Brak odniesienia do gracza.")
                    return
                px, py = self._player_ref.grid_x, self._player_ref.grid_y
                new_name = f"Punkt {len(self.saved_points) + 1}"
                self.saved_points.append({"name": new_name, "pos": (px, py)})
                self._speak(f"Dodano punkt: {new_name}, {px} {py}.")
            else:
                sp = self.saved_points[self.selected_index - 1]
                # Najpierw flaga, potem etykieta
                self.set_flag(sp["pos"])
                self.flag_label = sp["name"]

    def _open_submenu_if_available(self):
        if self.list_index == 1 and self.selected_index > 0 and self.saved_points:
            self.show_submenu = True
            self.submenu_index = 0
            self._speak("Menu. Edytuj.")
        else:
            self._speak("Brak opcji.")

    def _execute_submenu_action(self):
        idx = self.selected_index - 1
        if not (0 <= idx < len(self.saved_points)):
            self.show_submenu = False
            self._speak("Błąd. Zamknięto menu.")
            return

        action = self.submenu_options[self.submenu_index]
        sp = self.saved_points[idx]

        if action == "Edytuj":
            new_name = None
            if callable(self.rename_provider):
                try:
                    new_name = self.rename_provider(sp["name"])
                except Exception:
                    new_name = None
            if new_name and isinstance(new_name, str) and new_name.strip():
                sp["name"] = new_name.strip()
                self._speak(f"Zmieniono nazwę na {sp['name']}.")
            else:
                sp["name"] = f"{sp['name']}*"
                self._speak(f"Zmieniono nazwę na {sp['name']}.")
        elif action == "Usuń":
            removed = self.saved_points.pop(idx)
            if self.flag and self.flag == tuple(removed["pos"]):
                self.clear_flag()
            self._speak("Usunięto punkt.")
            if self.selected_index > len(self.saved_points):
                self.selected_index = max(0, len(self.saved_points))

        self.show_submenu = False
