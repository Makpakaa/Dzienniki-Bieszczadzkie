import os
import pygame
from dzienniki.audio.tts import speak, stop, manager
from dzienniki import settings
from dzienniki.entities.player import Player

def speak_now(text: str):
    """Blokujące TTS używane w ekranach startowych."""
    manager.engine.stop()
    manager.engine.say(text)
    manager.engine.runAndWait()

def show_logo(screen):
    screen.fill((0, 0, 0))
    font = pygame.font.SysFont(None, 64)
    label = font.render("LOGO GRY", True, (255, 255, 0))
    rect = label.get_rect(center=(screen.get_width()//2, screen.get_height()//2))
    screen.blit(label, rect)
    pygame.display.flip()

    speak_now("Logo.")
    clock = pygame.time.Clock()
    start = pygame.time.get_ticks()
    while True:
        for e in pygame.event.get():
            if e.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.QUIT):
                return
        if pygame.time.get_ticks() - start >= 5000:
            return
        clock.tick(30)

def show_title(screen):
    screen.fill((0, 0, 0))
    font = pygame.font.SysFont(None, 100)
    lines = ["Dzienniki", "Bieszczadzkie"]
    for i, txt in enumerate(lines):
        lbl = font.render(txt, True, (255, 255, 0))
        r = lbl.get_rect(
            center=(screen.get_width()//2,
                    screen.get_height()//2 + i*100)
        )
        screen.blit(lbl, r)
    pygame.display.flip()

    speak_now("Dzienniki Bieszczadzkie.")
    clock = pygame.time.Clock()
    start = pygame.time.get_ticks()
    while True:
        for e in pygame.event.get():
            if e.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.QUIT):
                return
        if pygame.time.get_ticks() - start >= 5000:
            return
        clock.tick(30)

def main_menu(screen):
    options = ["Nowa Gra", "Załaduj Grę", "Wyjście"]
    selected = 0
    clock = pygame.time.Clock()
    pygame.key.set_repeat(300, 100)

    speak_now("Menu główne. Strzałki góra, dół. Enter zatwierdza.")
    speak_now(options[selected])

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return None
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                    speak_now(options[selected])
                elif e.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                    speak_now(options[selected])
                elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    speak_now(f"Wybrano: {options[selected]}")
                    pygame.time.delay(300)
                    return options[selected].lower().replace(" ", "_")

        screen.fill((0, 0, 0))
        font = pygame.font.SysFont(None, 48)
        for i, opt in enumerate(options):
            color = (255, 255, 255) if i == selected else (255, 255, 0)
            lbl = font.render(opt, True, color)
            x = screen.get_width()//2 - lbl.get_width()//2
            y = 200 + i*60
            screen.blit(lbl, (x, y))
            if i == selected:
                pygame.draw.rect(
                    screen, color,
                    (x-5, y-5, lbl.get_width()+10, lbl.get_height()+10),
                    2
                )
        pygame.display.flip()
        clock.tick(settings.FPS)

def show_introduction(screen):
    lines = [
        "Witamy w Dziennikach Bieszczadzkich!",
        "Jesteś wędrowcem przemierzającym wzgórza i doliny.",
        "Odkryj tajemnice tej spokojnej krainy.",
        "Powodzenia!"
    ]
    tts_text = " ".join(lines)

    screen.fill((0, 0, 0))
    font = pygame.font.SysFont(None, 36)
    for i, txt in enumerate(lines):
        lbl = font.render(txt, True, (255, 255, 0))
        screen.blit(lbl, (50, 150 + i*40))
    pygame.display.flip()

    speak_now(tts_text + " Naciśnij dowolny klawisz, aby kontynuować.")
    while True:
        for e in pygame.event.get():
            if e.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.QUIT):
                return

def topdown_game_loop(screen):
    clock = pygame.time.Clock()
    player = Player()
    size = settings.TILE_SIZE

    # wczytanie mapy
    path = os.path.join(settings.ASSETS_DIR, "map.txt")
    try:
        with open(path, "r", encoding="utf-8") as f:
            map_rows = [list(line.strip()) for line in f if line.strip()]
    except FileNotFoundError:
        map_rows = []

    # gdy brak lub pusta mapa, wypełnij trawą
    if not map_rows or not map_rows[0]:
        cols = settings.SCREEN_WIDTH // size
        rows = settings.SCREEN_HEIGHT // size
        map_rows = [["g"] * cols for _ in range(rows)]

    # umieść kamień po lewej, wodę po prawej (4 bloki od startu)
    max_row = len(map_rows) - 1
    max_col = len(map_rows[0]) - 1
    start_col = (settings.SCREEN_WIDTH // 2) // size
    start_row = (settings.SCREEN_HEIGHT // 2) // size
    left_col = max(0, start_col - 4)
    right_col = min(max_col, start_col + 4)
    if 0 <= start_row <= max_row:
        map_rows[start_row][left_col]  = 's'
        map_rows[start_row][right_col] = 'w'

    # — placeholderowe kafelki —
    grass_tile = pygame.Surface((size, size)); grass_tile.fill((34, 139, 34))
    water_tile = pygame.Surface((size, size)); water_tile.fill((0, 0, 255))
    stone_tile = pygame.Surface((size, size)); stone_tile.fill((128, 128, 128))

    # kolizje i nazwy do TTS
    passable = {'g': True, 'w': False, 's': False}
    names    = {'g': "trawa", 'w': "woda", 's': "kamień"}

    last_dir = None

    while True:
        dt = clock.tick(settings.FPS) / 1000.0

        for e in pygame.event.get():
            # wyjście
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                return

            # na KEYDOWN ustaw kierunek
            if e.type == pygame.KEYDOWN and e.key in (
                pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT
            ):
                if e.key == pygame.K_UP:    last_dir = "północ"
                elif e.key == pygame.K_DOWN: last_dir = "południe"
                elif e.key == pygame.K_LEFT: last_dir = "zachód"
                elif e.key == pygame.K_RIGHT:last_dir = "wschód"

            # na KEYUP: sprawdzenie bloku, ruch i TTS z koordynatami
            elif e.type == pygame.KEYUP and e.key in (
                pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT
            ):
                # oblicz docelową kratkę
                col = player.rect.centerx // size
                row = player.rect.centery  // size
                if last_dir == "północ":    row -= 1
                elif last_dir == "południe":row += 1
                elif last_dir == "zachód":  col -= 1
                elif last_dir == "wschód":  col += 1

                # zabezpiecz indeksy
                row = max(0, min(row, max_row))
                col = max(0, min(col, max_col))

                cell    = map_rows[row][col]
                terrain = names.get(cell, "nieznany teren")

                # TTS zawsze wypowie blok i koordynaty
                if not passable.get(cell, True):
                    speak(f"{last_dir}. {terrain}. X:{col}, Y:{row}")
                else:
                    # przesuń o jedną kratkę
                    player.rect.topleft = (col * size, row * size)
                    speak(f"{last_dir}. {terrain}. X:{col}, Y:{row}")

                last_dir = None

        # rysowanie mapy i gracza
        screen.fill((0, 0, 0))
        for ry, row_data in enumerate(map_rows):
            for cx, cell in enumerate(row_data):
                if cell == "g":
                    screen.blit(grass_tile, (cx * size, ry * size))
                elif cell == "w":
                    screen.blit(water_tile, (cx * size, ry * size))
                elif cell == "s":
                    screen.blit(stone_tile, (cx * size, ry * size))
                else:
                    screen.blit(grass_tile, (cx * size, ry * size))

        screen.blit(player.image, player.rect)
        pygame.display.flip()
