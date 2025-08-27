# src/dzienniki/entities/player.py

import pygame
from dzienniki import settings
from dzienniki.utils.loader import load_image
from dzienniki.audio import tts

SPRITE_PATH = "assets/images/player/player_walk.png"

DIRECTION_MAP = {
    "down": 0,
    "left": 1,
    "right": 2,
    "up": 3
}

def _facing_vec(facing: str):
    return {
        "up": (0, -1),
        "down": (0, 1),
        "left": (-1, 0),
        "right": (1, 0),
    }.get(facing, (0, 0))

def _dir_word(facing: str) -> str:
    return {
        "up": "północ",
        "down": "południe",
        "left": "zachód",
        "right": "wschód",
    }.get(facing, "tu")

def _tile_name_at(x: int, y: int, map_rows, names):
    # Bezpieczne pobranie ID kafla
    tid = None
    try:
        if 0 <= y < len(map_rows) and 0 <= x < len(map_rows[0]):
            tid = map_rows[y][x]
    except Exception:
        tid = None

    # Jeśli names to dict mapujący ID -> nazwa
    if tid is not None and isinstance(names, dict):
        pretty = names.get(tid)
        if pretty and str(pretty).strip():
            return str(pretty)

    # Jeśli names to 2D lista/stringi „na pozycji”
    try:
        return names[y][x]
    except Exception:
        pass

    # Inne warianty słowników współrzędnych
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

def _tile_id_at(x: int, y: int, map_rows):
    try:
        if 0 <= y < len(map_rows) and 0 <= x < len(map_rows[0]):
            return map_rows[y][x]
    except Exception:
        pass
    return None


class Player:
    def __init__(self):
        self.grid_x = 50
        self.grid_y = 50
        self.pixel_x = self.grid_x * settings.TILE_SIZE
        self.pixel_y = self.grid_y * settings.TILE_SIZE
        self.target_x = self.pixel_x
        self.target_y = self.pixel_y

        self.direction = "down"   # dla animacji
        self.facing = "down"      # dla systemów (tracker, „przed tobą”)
        self.frame = 0
        self.animation_timer = 0.0
        self.moving = False
        self.speed = 100.0  # px/s

        self._held_dir = (0, 0)      # kierunek trzymanego klawisza
        self._last_tts = ""          # do powtórzenia komunikatu
        self._last_blocked = None    # (nx, ny) ostatnio zablokowany cel; anty-spam

        # Autowykrywanie semantyki siatki 2D passable (jeśli używana)
        self._pass_mode_2d = None    # 'zero_is_free' | 'nonzero_is_free' | None

        original = load_image(SPRITE_PATH)
        # Zakładamy 3 kolumny x 4 wiersze, skalowanie do TILE_SIZE
        self.sprite_sheet = pygame.transform.scale(
            original,
            (3 * settings.TILE_SIZE, 4 * settings.TILE_SIZE)
        )
        self.frames = self.load_frames(settings.TILE_SIZE, settings.TILE_SIZE)

        self.rect = pygame.Rect(
            self.pixel_x,
            self.pixel_y,
            settings.TILE_SIZE,
            settings.TILE_SIZE
        )

    def load_frames(self, width, height):
        frames = {dir: [] for dir in DIRECTION_MAP}
        for dir_name, row in DIRECTION_MAP.items():
            for col in range(3):
                rect = pygame.Rect(col * width, row * height, width, height)
                image = self.sprite_sheet.subsurface(rect)
                frames[dir_name].append(image)
        return frames

    # ---------- Wejście ----------
    def handle_input(self, keys):
        # Ustal kierunek z priorytetem: W/S > A/D (unikamy diagonali)
        dx = dy = 0
        if keys[pygame.K_w]:
            self.facing = "up"
            self.direction = "up"
            dy = -1
        elif keys[pygame.K_s]:
            self.facing = "down"
            self.direction = "down"
            dy = 1
        elif keys[pygame.K_a]:
            self.facing = "left"
            self.direction = "left"
            dx = -1
        elif keys[pygame.K_d]:
            self.facing = "right"
            self.direction = "right"
            dx = 1

        self._held_dir = (dx, dy)

    # ---------- Mowa ----------
    def _speak(self, msg: str):
        self._last_tts = msg or ""
        tts.speak(msg)

    def repeat_last_message(self):
        if self._last_tts:
            tts.speak(self._last_tts)

    def _speak_after_arrival(self, map_rows, names):
        pos = f"Pozycja: {self.grid_x} {self.grid_y}."
        dir_word = _dir_word(self.facing)
        kier = f"Kierunek: {dir_word}."
        here = _tile_name_at(self.grid_x, self.grid_y, map_rows, names)
        if here and str(here).strip():
            here_msg = f"Stoisz na {here}."
        else:
            here_msg = "Stoisz na nieznanym terenie."
        dx, dy = _facing_vec(self.facing)
        front_name = _tile_name_at(self.grid_x + dx, self.grid_y + dy, map_rows, names)
        front_msg = ""
        if front_name and front_name != here:
            front_msg = f"Przed tobą {front_name}."
        msg = " ".join([pos, kier, here_msg, front_msg]).strip()
        self._speak(msg)

    def _speak_collision(self, map_rows, names, nx, ny):
        # Anty-spam: mów tylko przy pierwszym uderzeniu w daną kratkę
        if self._last_blocked == (nx, ny):
            return
        self._last_blocked = (nx, ny)

        block = _tile_name_at(nx, ny, map_rows, names)
        if block and str(block).strip():
            info = f"Kolizja: {block}."
        else:
            info = "Kolizja: nieprzejezdne."
        if self._last_tts:
            tts.speak(self._last_tts)
        self._speak(info)

    # ---------- Ruch i kolizje ----------
    def _infer_pass_mode_2d(self, passable_2d):
        """Ustal, czy 0 oznacza przejście, czy blokadę — na podstawie kratki startowej."""
        try:
            cell = passable_2d[self.grid_y][self.grid_x]
        except Exception:
            self._pass_mode_2d = None
            return
        if isinstance(cell, (int, float)):
            self._pass_mode_2d = 'zero_is_free' if cell == 0 else 'nonzero_is_free'
        else:
            self._pass_mode_2d = None  # dla bool nie potrzeba

    def _is_passable(self, x: int, y: int, map_rows, passable) -> bool:
        """Obsługuje zarówno 2D siatkę, jak i dict {tile_id: bool/int}."""
        if passable is None:
            return True

        # 1) Słownik {tile_id: bool/int}
        if isinstance(passable, dict):
            tid = _tile_id_at(x, y, map_rows)
            # Domyślnie traktujemy brak wpisu jako przejście
            val = passable.get(tid, True)
            if isinstance(val, bool):
                return val
            if isinstance(val, (int, float)):
                # Najbezpieczniej: 0 -> przejście, !=0 -> blokada
                return val == 0 or val is True
            return bool(val)

        # 2) Siatka 2D
        try:
            if 0 <= y < len(passable) and 0 <= x < len(passable[0]):
                cell = passable[y][x]
            else:
                return False
        except Exception:
            return False

        if isinstance(cell, bool):
            return cell
        if isinstance(cell, (int, float)):
            if self._pass_mode_2d is None:
                self._infer_pass_mode_2d(passable)
            if self._pass_mode_2d == 'zero_is_free':
                return cell == 0
            if self._pass_mode_2d == 'nonzero_is_free':
                return cell != 0
            # fallback: przyjmij, że 0 = wolne
            return cell == 0

        # Inne typy: traktuj truthy jako przejście
        return bool(cell)

    def _begin_step(self, dx: int, dy: int):
        # Rozpocznij ruch do kolejnej kratki
        self.grid_x += dx
        self.grid_y += dy
        self.target_x = self.grid_x * settings.TILE_SIZE
        self.target_y = self.grid_y * settings.TILE_SIZE
        self.moving = True
        # reset anty-spamu blokady — cel zmieni się po ruchu
        self._last_blocked = None

    def update(self, dt, map_rows, passable, names):
        # 1) Jeśli nie poruszamy się: spróbuj zacząć krok zgodnie z trzymanym klawiszem
        if not self.moving:
            dx, dy = self._held_dir
            if dx != 0 or dy != 0:
                nx = self.grid_x + dx
                ny = self.grid_y + dy
                if self._is_passable(nx, ny, map_rows, passable):
                    self._begin_step(dx, dy)
                else:
                    # Kolizja — nie zmieniamy pozycji; informujemy TTS (jednorazowo na kratkę)
                    self._speak_collision(map_rows, names, nx, ny)

        # 2) Interpolacja ruchu (płynne dojście do targetu)
        if self.moving:
            distance = self.speed * dt
            dx_px = self.target_x - self.pixel_x
            dy_px = self.target_y - self.pixel_y

            if abs(dx_px) > 0:
                step_x = max(-distance, min(distance, dx_px))
                self.pixel_x += step_x
            if abs(dy_px) > 0:
                step_y = max(-distance, min(distance, dy_px))
                self.pixel_y += step_y

            # Zakończenie ruchu (przyklej do celu)
            if abs(self.pixel_x - self.target_x) < 0.5 and abs(self.pixel_y - self.target_y) < 0.5:
                self.pixel_x = self.target_x
                self.pixel_y = self.target_y
                self.moving = False
                self.frame = 0
                # Po zakończeniu kroku — komunikat TTS
                self._speak_after_arrival(map_rows, names)

            # Animacja chodzenia
            self.animation_timer += dt
            if self.animation_timer >= 0.15:
                self.frame = (self.frame + 1) % 3
                self.animation_timer = 0.0

        # Pozycja do rysowania
        self.rect.topleft = (round(self.pixel_x), round(self.pixel_y))

    # ---------- Render ----------
    def draw(self, surface):
        frame = self.frames[self.direction][self.frame]
        surface.blit(frame, (round(self.pixel_x), round(self.pixel_y)))
