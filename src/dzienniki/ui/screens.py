import os
import pygame
import sys
from dzienniki.audio.tts import speak, stop
from dzienniki import settings
from dzienniki.entities.player import Player
from dzienniki.utils.loader import load_image

def show_logo(screen):
    """Logo — oczekuj tylko na klawisz/mysz, przerywaj mowę."""
    screen.fill((0, 0, 0))
    font = pygame.font.SysFont(None, 64)
    label = font.render("LOGO GRY", True, (255, 255, 0))
    rect = label.get_rect(center=(screen.get_width()//2, screen.get_height()//2))
    screen.blit(label, rect)
    pygame.display.flip()

    speak("Wyświetlam logo gry. Naciśnij dowolny klawisz, aby przejść dalej.")
    while True:
        for e in pygame.event.get():
            if e.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.QUIT):
                stop()
                return

def show_title(screen):
    """Tytuł — to samo, czekaj na interakcję."""
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

    speak("Dzienniki Bieszczadzkie. Naciśnij dowolny klawisz, aby przejść dalej.")
    while True:
        for e in pygame.event.get():
            if e.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.QUIT):
                stop()
                return

def main_menu(screen):
    """Menu z TTS: przerwij stop() i przeczytaj od razu nową opcję."""
    options = ["Nowa Gra", "Załaduj Grę", "Wyjście"]
    selected = 0
    clock = pygame.time.Clock()

    # instrukcja + pierwsza opcja
    speak("Menu główne. Strzałki góra, dół. Enter zatwierdza.")
    speak(options[selected])

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                stop()
                return None
            if e.type == pygame.KEYDOWN:
                stop()
                if e.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                    speak(options[selected])
                elif e.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                    speak(options[selected])
                elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    stop()
                    speak(f"Wybrano {options[selected]}")
                    pygame.time.delay(300)
                    return options[selected].lower().replace(" ", "_")

        # rysowanie
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
        clock.tick(30)

def show_introduction(screen):
    """Wprowadzenie — tylko KEYDOWN, bez timeoutu."""
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

    speak(tts_text + " Naciśnij dowolny klawisz, aby kontynuować.")
    while True:
        for e in pygame.event.get():
            if e.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.QUIT):
                stop()
                return

def topdown_game_loop(screen):
    """Główna pętla gry: rysuj trawę, ramkę i TTS przed graczem."""
    clock       = pygame.time.Clock()
    player      = Player()
    all_sprites = pygame.sprite.Group(player)

    # fallbackowa mapa
    tile = load_image(os.path.join("tiles", "grass.png"))
    path = os.path.join(settings.ASSETS_DIR, "map.txt")
    try:
        with open(path, "r", encoding="utf-8") as f:
            map_rows = [list(line.strip()) for line in f if line.strip()]
    except FileNotFoundError:
        cols = settings.SCREEN_WIDTH//settings.TILE_SIZE
        rows = settings.SCREEN_HEIGHT//settings.TILE_SIZE
        map_rows = [["g"]*cols for _ in range(rows)]

    while True:
        dt = clock.tick(settings.FPS)/1000.0

        # eventy
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type==pygame.KEYDOWN and e.key==pygame.K_ESCAPE):
                return

        # czyszczenie ekranu
        screen.fill((0, 0, 0))

        # rysuj mapę
        for ry, row in enumerate(map_rows):
            for cx, cell in enumerate(row):
                if cell=="g":
                    screen.blit(tile, (cx*settings.TILE_SIZE, ry*settings.TILE_SIZE))

        # oblicz kafelek przed graczem
        col = player.rect.centerx//settings.TILE_SIZE
        row = player.rect.centery//settings.TILE_SIZE
        if player.facing=="up":    row-=1
        if player.facing=="down":  row+=1
        if player.facing=="left":  col-=1
        if player.facing=="right": col+=1

        if 0<=row<len(map_rows) and 0<=col<len(map_rows[0]):
            x, y = col*settings.TILE_SIZE, row*settings.TILE_SIZE
            terrain = map_rows[row][col]
            names   = {"g":"trawa","w":"woda"}
            speak(f"Przed tobą: {names.get(terrain,'nieznany teren')}")
            pygame.draw.rect(screen, (255,255,0), (x,y,settings.TILE_SIZE,settings.TILE_SIZE), 2)

        # ruch gracza + rysowanie
        all_sprites.update(dt)
        all_sprites.draw(screen)

        pygame.display.flip()
