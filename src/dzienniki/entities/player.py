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
    tid = None
    try:
        if 0 <= y < len(map_rows) and 0 <= x < len(map_rows[0]):
            tid = map_rows[y][x]
    except Exception:
        tid = None

    if tid is not None and isinstance(names, dict):
        pretty = names.get(tid)
        if pretty and str(pretty).strip():
            return str(pretty)

    try:
        return names[y][x]
    except Exception:
        pass

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
    def __init__(self, start_x: int = 0, start_y: int = 0):
        # Pozycja startowa przekazywana z mapy (spawn)
        self.grid_x = int(start_x)
        self.grid_y = int(start_y)

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

        self._held_dir = (0, 0)
        self._last_tts = ""
        self._last_blocked = None

        original = load_image(SPRITE_PATH)
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

    # Publiczny setter – przyda się przy respawnie / wczytywaniu save’a
    def set_position(self, x: int, y: int):
        self.grid_x = int(x)
        self.grid_y = int(y)
        self.pixel_x = self.grid_x * settings.TILE_SIZE
        self.pixel_y = self.grid_y * settings.TILE_SIZE
        self.target_x = self.pixel_x
        self.target_y = self.pixel_y
        self.moving = False
        self.frame = 0

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
        if self._last_blocked == (nx, ny):
            return
        self._last_blocked = (nx, ny)

        block = _tile_name_at(nx, ny, map_rows, names)
        if block and str(block).strip():
            info = f"Kolizja: {block}."
        else:
            info = "Kolizja: nieprzejezdne."
        self._speak(info)

    # ---------- Ruch i kolizje ----------
    def _is_passable(self, x: int, y: int, map_rows, passable) -> bool:
        """
        Spójna konwencja:
        - dict: True/False albo liczby (0=blokada, !=0=przejście), brak wpisu => przejście
        - siatka 2D: bool (True=przejście) lub liczby (0=blokada, !=0=przejście)
        - poza mapą => blokada
        """
        if passable is None:
            return True

        if isinstance(passable, dict):
            tid = _tile_id_at(x, y, map_rows)
            if tid is None:
                return True
            val = passable.get(tid, True)
            if isinstance(val, bool):
                return val
            if isinstance(val, (int, float)):
                return val != 0
            return bool(val)

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
            return cell != 0

        return bool(cell)

    def _begin_step(self, dx: int, dy: int):
        self.grid_x += dx
        self.grid_y += dy
        self.target_x = self.grid_x * settings.TILE_SIZE
        self.target_y = self.grid_y * settings.TILE_SIZE
        self.moving = True
        self._last_blocked = None

    def update(self, dt, map_rows, passable, names):
        if not self.moving:
            dx, dy = self._held_dir
            if dx != 0 or dy != 0:
                nx = self.grid_x + dx
                ny = self.grid_y + dy
                if self._is_passable(nx, ny, map_rows, passable):
                    self._begin_step(dx, dy)
                else:
                    self._speak_collision(map_rows, names, nx, ny)

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

            if abs(self.pixel_x - self.target_x) < 0.5 and abs(self.pixel_y - self.target_y) < 0.5:
                self.pixel_x = self.target_x
                self.pixel_y = self.target_y
                self.moving = False
                self.frame = 0
                self._speak_after_arrival(map_rows, names)

            self.animation_timer += dt
            if self.animation_timer >= 0.15:
                self.frame = (self.frame + 1) % 3
                self.animation_timer = 0.0

        self.rect.topleft = (round(self.pixel_x), round(self.pixel_y))

    # ---------- Render ----------
    def draw(self, surface, cam_x: float = 0.0, cam_y: float = 0.0):
        """Rysowanie z uwzględnieniem offsetu kamery."""
        frame = self.frames[self.direction][self.frame]
        surface.blit(frame, (round(self.pixel_x - cam_x), round(self.pixel_y - cam_y)))
