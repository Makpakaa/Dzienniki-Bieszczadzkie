import os
import pygame
from dzienniki.audio.tts import speak, stop, manager
from dzienniki import settings
from dzienniki.entities.player import Player
from dzienniki.systems import inventory

def speak_now(text: str):
    manager.engine.stop()
    manager.engine.say(text)
    manager.engine.runAndWait()

def show_logo(screen):
    screen.fill((0, 0, 0))
    font = pygame.font.SysFont(None, 64)
    label = font.render("LOGO GRY", True, (255, 255, 0))
    rect = label.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    screen.blit(label, rect)
    pygame.display.flip()
    speak_now("Logo.")
    pygame.time.wait(3000)

def show_title(screen):
    screen.fill((0, 0, 0))
    font = pygame.font.SysFont(None, 100)
    lines = ["Dzienniki", "Bieszczadzkie"]
    for i, txt in enumerate(lines):
        lbl = font.render(txt, True, (255, 255, 0))
        r = lbl.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + i * 100))
        screen.blit(lbl, r)
    pygame.display.flip()
    speak_now("Dzienniki Bieszczadzkie.")
    pygame.time.wait(3000)

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
                    pygame.time.wait(300)
                    return options[selected].lower().replace(" ", "_")
        screen.fill((0, 0, 0))
        font = pygame.font.SysFont(None, 48)
        for i, opt in enumerate(options):
            color = (255, 255, 255) if i == selected else (255, 255, 0)
            lbl = font.render(opt, True, color)
            x = screen.get_width() // 2 - lbl.get_width() // 2
            y = 200 + i * 60
            screen.blit(lbl, (x, y))
            if i == selected:
                pygame.draw.rect(screen, color, (x - 5, y - 5, lbl.get_width() + 10, lbl.get_height() + 10), 2)
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
        screen.blit(lbl, (50, 150 + i * 40))
    pygame.display.flip()
    speak_now(tts_text + " Naciśnij dowolny klawisz, aby kontynuować.")
    while True:
        for e in pygame.event.get():
            if e.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.QUIT):
                return

def topdown_game_loop(screen):
    clock = pygame.time.Clock()
    player = Player()
    inventory.init_font()

    # Mapka awaryjna
    map_rows = [["g"] * (settings.SCREEN_WIDTH // settings.TILE_SIZE)
                for _ in range(settings.SCREEN_HEIGHT // settings.TILE_SIZE)]
    map_rows[len(map_rows) // 2][2] = "s"
    map_rows[len(map_rows) // 2][-3] = "w"

    # Kafelki
    size = settings.TILE_SIZE
    grass_tile = pygame.Surface((size, size)); grass_tile.fill((34, 139, 34))
    water_tile = pygame.Surface((size, size)); water_tile.fill((0, 0, 255))
    stone_tile = pygame.Surface((size, size)); stone_tile.fill((128, 128, 128))
    names = {'g': "trawa", 'w': "woda", 's': "kamień"}
    passable = {'g': True, 'w': False, 's': False}

    show_inventory = False
    last_dir = None

    while True:
        dt = clock.tick(settings.FPS) / 1000.0
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    return
                if e.key == pygame.K_e:
                    show_inventory = not show_inventory
                    if show_inventory:
                        # Ustaw startowy fokus na sekcję Ekwipunek
                        inventory.selected_section = 1
                        inventory.selected_item_index = 0
                        speak("Ekwipunek otwarty.")
                        inventory.speak_current_item()
                    else:
                        speak("Zamknięto ekwipunek.")
                if show_inventory:
                    inventory.handle_inventory_navigation(e)
            if e.type == pygame.KEYUP and not show_inventory:
                if e.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
                    row = player.rect.centery // size
                    col = player.rect.centerx // size
                    if e.key == pygame.K_UP:
                        row -= 1
                        last_dir = "północ"
                    elif e.key == pygame.K_DOWN:
                        row += 1
                        last_dir = "południe"
                    elif e.key == pygame.K_LEFT:
                        col -= 1
                        last_dir = "zachód"
                    elif e.key == pygame.K_RIGHT:
                        col += 1
                        last_dir = "wschód"
                    if 0 <= row < len(map_rows) and 0 <= col < len(map_rows[0]):
                        cell = map_rows[row][col]
                        if not passable.get(cell, True):
                            speak(f"{last_dir}. {names.get(cell)}. X:{col}, Y:{row}")
                        else:
                            player.rect.topleft = (col * size, row * size)
                            speak(f"{last_dir}. {names.get(cell)}. X:{col}, Y:{row}")

        screen.fill((0, 0, 0))
        for ry, row_data in enumerate(map_rows):
            for cx, cell in enumerate(row_data):
                tile = grass_tile
                if cell == "w": tile = water_tile
                elif cell == "s": tile = stone_tile
                screen.blit(tile, (cx * size, ry * size))
        screen.blit(player.image, player.rect)
        if show_inventory:
            inventory.draw(screen)
        pygame.display.flip()
