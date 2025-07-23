# src/dzienniki/game.py

import pygame
from dzienniki import settings
from dzienniki.audio import tts
from dzienniki.entities.player import Player
from dzienniki.systems.maps import TileMap
from dzienniki.systems import inventory

def topdown_game_loop(screen):
    clock = pygame.time.Clock()
    player = Player()
    tilemap = TileMap()

    map_rows = tilemap.rows
    passable = tilemap.passable
    names = tilemap.names

    inventory.init_font()
    show_inventory = False

    while True:
        dt = clock.tick(settings.FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if show_inventory:
                        show_inventory = False
                        tts.speak("Zamknięto ekwipunek.")
                    else:
                        return

                elif event.key == pygame.K_e:
                    show_inventory = not show_inventory
                    if show_inventory:
                        inventory.selected_section = 1
                        inventory.selected_item_index = 0
                        tts.speak("Ekwipunek otwarty.")
                        inventory.speak_current_item()
                    else:
                        tts.speak("Zamknięto ekwipunek.")

                elif show_inventory:
                    inventory.handle_inventory_navigation(event)

        if not show_inventory:
            player.update(dt, map_rows, passable)
            x = player.rect.centerx // settings.TILE_SIZE
            y = player.rect.centery // settings.TILE_SIZE
            dx, dy = {
                "up": (0, -1),
                "down": (0, 1),
                "left": (-1, 0),
                "right": (1, 0)
            }.get(player.facing, (0, 0))

            tx, ty = x + dx, y + dy
            tile_info = "poza mapą"

            if 0 <= ty < len(map_rows) and 0 <= tx < len(map_rows[0]):
                tile_symbol = map_rows[ty][tx]
                tile_info = names.get(tile_symbol, "nieznane")

            tts.speak(f"Pozycja: X {x}, Y {y}. Kierunek: {player.facing}. Przed tobą: {tile_info}")

        # Rysowanie
        screen.fill((0, 0, 0))
        size = settings.TILE_SIZE

        for row_idx, row in enumerate(map_rows):
            for col_idx, cell in enumerate(row):
                color = (34, 139, 34)  # trawa
                if cell == "w":
                    color = (0, 0, 255)  # woda
                elif cell == "s":
                    color = (128, 128, 128)  # kamień
                pygame.draw.rect(screen, color, (col_idx * size, row_idx * size, size, size))

        player.draw(screen)

        if show_inventory:
            inventory.draw(screen)

        pygame.display.flip()
