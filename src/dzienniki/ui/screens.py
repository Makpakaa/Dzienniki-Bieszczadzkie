import os
import pygame
from dzienniki.audio.tts import speak, stop
from dzienniki.audio.tts import manager
from dzienniki import settings
from dzienniki.entities.player import Player
from dzienniki.utils.loader import load_image

def speak_now(text: str):
    """Powiedz tekst blokująco, czekając na zakończenie mowy."""
    manager.engine.stop()
    manager.engine.say(text)
    manager.engine.runAndWait()

def show_logo(screen):
    """Logo — do 5 s lub do naciśnięcia, TTS mówi 'Logo.'"""
    screen.fill((0, 0, 0))
    font = pygame.font.SysFont(None, 64)
    label = font.render("LOGO GRY", True, (255, 255, 0))
    rect = label.get_rect(center=(screen.get_width()//2, screen.get_height()//2))
    screen.blit(label, rect)
    pygame.display.flip()

    stop()
    speak("Logo.")
    clock = pygame.time.Clock()
    start = pygame.time.get_ticks()
    while True:
        for e in pygame.event.get():
            if e.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.QUIT):
                stop()
                return
        if pygame.time.get_ticks() - start >= 5000:
            stop()
            return
        clock.tick(30)

def show_title(screen):
    """Tytuł — do 5 s lub do naciśnięcia, TTS mówi 'Dzienniki Bieszczadzkie.'"""
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

    stop()
    speak("Dzienniki Bieszczadzkie.")
    clock = pygame.time.Clock()
    start = pygame.time.get_ticks()
    while True:
        for e in pygame.event.get():
            if e.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.QUIT):
                stop()
                return
        if pygame.time.get_ticks() - start >= 5000:
            stop()
            return
        clock.tick(30)

def main_menu(screen):
    """Menu główne z blokującym TTS: strzałki wybierają, Enter zatwierdza."""
    options = ["Nowa Gra", "Załaduj Grę", "Wyjście"]
    selected = 0
    clock = pygame.time.Clock()

    # Włącz powtarzanie klawiszy (dłuższe przytrzymanie → kolejne KEYDOWN)
    pygame.key.set_repeat(300, 100)

    # Powiedz instrukcję i pierwszą opcję, blokująco
    stop()
    speak("Menu główne. Strzałki góra, dół. Enter zatwierdza.")
    speak(options[selected])

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                stop()
                return None

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                    speak(options[selected])

                elif e.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                    speak(options[selected])

                elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    speak(f"Wybrano: {options[selected]}")
                    pygame.time.delay(300)
                    return options[selected].lower().replace(" ", "_")
                # inne klawisze ignorujemy

        # Rysowanie menu
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
    """Wprowadzenie — TTS czyta, dowolny klawisz przerywa."""
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

    stop()
    speak(tts_text + " Naciśnij dowolny klawisz, aby kontynuować.")
    while True:
        for e in pygame.event.get():
            if e.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.QUIT):
                stop()
                return

def topdown_game_loop(screen):
    """Główna pętla gry: KEYDOWN = kierunek, KEYUP = nazwa terenu."""
    clock = pygame.time.Clock()
    player = Player()
    all_sprites = pygame.sprite.Group(player)

    tile = load_image(os.path.join("tiles", "grass.png"))
    path = os.path.join(settings.ASSETS_DIR, "map.txt")
    try:
        with open(path, "r", encoding="utf-8") as f:
            map_rows = [list(line.strip()) for line in f if line.strip()]
    except FileNotFoundError:
        cols = settings.SCREEN_WIDTH // settings.TILE_SIZE
        rows = settings.SCREEN_HEIGHT // settings.TILE_SIZE
        map_rows = [["g"] * cols for _ in range(rows)]

    names = {"g": "trawa", "w": "woda"}

    while True:
        dt = clock.tick(settings.FPS) / 1000.0

        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                return

            # KEYDOWN → kierunek
            if e.type == pygame.KEYDOWN and e.key in (
                pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT
            ):
                stop()
                if e.key == pygame.K_UP:
                    player.facing = "north";  speak("północ")
                elif e.key == pygame.K_DOWN:
                    player.facing = "south";  speak("południe")
                elif e.key == pygame.K_LEFT:
                    player.facing = "west";   speak("zachód")
                elif e.key == pygame.K_RIGHT:
                    player.facing = "east";   speak("wschód")

            # KEYUP → zawsze nazwa terenu przed graczem
            if e.type == pygame.KEYUP and e.key in (
                pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT
            ):
                all_sprites.update(dt)
                col = player.rect.centerx // settings.TILE_SIZE
                row = player.rect.centery // settings.TILE_SIZE
                if player.facing == "north": row -= 1
                elif player.facing == "south": row += 1
                elif player.facing == "west":  col -= 1
                elif player.facing == "east":  col += 1

                if 0 <= row < len(map_rows) and 0 <= col < len(map_rows[0]):
                    stop()
                    speak(names.get(map_rows[row][col], "nieznany teren"))

        # rysowanie
        all_sprites.update(dt)
        screen.fill((0, 0, 0))
        for ry, row in enumerate(map_rows):
            for cx, cell in enumerate(row):
                if cell == "g":
                    screen.blit(tile, (cx * settings.TILE_SIZE, ry * settings.TILE_SIZE))
        all_sprites.draw(screen)
        pygame.display.flip()
