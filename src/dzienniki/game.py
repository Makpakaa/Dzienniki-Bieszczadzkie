import pygame
from dzienniki import settings
from dzienniki.audio import tts
from dzienniki.entities.player import Player
from dzienniki.systems.maps import TileMap
from dzienniki.systems import inventory
from dzienniki.systems.object_tracker import ObjectTracker

def topdown_game_loop(screen):
    clock = pygame.time.Clock()
    player = Player()
    tracker = ObjectTracker()

    prev_x = player.grid_x
    prev_y = player.grid_y
    prev_facing = player.facing
    last_tts_message = ""

    tilemap = TileMap()
    map_rows = tilemap.rows
    passable = tilemap.passable
    names = tilemap.names

    inventory.init_font()
    show_inventory = False
    tracker_mode = False

    direction_names = {
        "up": "północ",
        "down": "południe",
        "left": "zachód",
        "right": "wschód"
    }

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
                    elif tracker_mode:
                        tracker_mode = False
                        tts.speak("Zamknięto listę obiektów.")
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

                elif event.key == pygame.K_r:
                    if last_tts_message:
                        tts.speak(last_tts_message)

                elif event.key == pygame.K_t:
                    tracker.scan_area(player, map_rows, names)
                    tracker.speak_selected()
                    tracker_mode = True

                elif event.key == pygame.K_RETURN and tracker_mode:
                    tracker.set_flag(player)

                elif event.key == pygame.K_f:
                    tracker.speak_target_direction(player)

                elif event.key == pygame.K_TAB and tracker_mode:
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        tracker.switch_list(backwards=True)
                    else:
                        tracker.switch_list()

                elif event.key == pygame.K_SPACE and tracker_mode:
                    tracker.open_submenu(player)

                elif event.key == pygame.K_w and tracker_mode:
                    tracker.previous_object()

                elif event.key == pygame.K_s and tracker_mode:
                    tracker.next_object()

                elif event.key == pygame.K_f and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    tracker.flag = None
                    tts.speak("Anulowano flagę.")

                elif show_inventory:
                    inventory.handle_inventory_navigation(event)

        if not show_inventory and not tracker_mode:
            keys = pygame.key.get_pressed()
            player.handle_input(keys)
            player.update(dt, map_rows, passable)

            x = player.grid_x
            y = player.grid_y

            if x != prev_x or y != prev_y or player.facing != prev_facing:
                dx, dy = {
                    "up": (0, -1),
                    "down": (0, 1),
                    "left": (-1, 0),
                    "right": (1, 0)
                }.get(player.facing, (0, 0))

                tx, ty = x + dx, y + dy

                current_tile = map_rows[y][x] if 0 <= y < len(map_rows) and 0 <= x < len(map_rows[0]) else None
                tile_ahead = map_rows[ty][tx] if 0 <= ty < len(map_rows) and 0 <= tx < len(map_rows[0]) else None

                current_tile_name = names.get(current_tile, "nieznane") if current_tile else "poza mapą"
                tile_ahead_name = names.get(tile_ahead, "nieznane") if tile_ahead else "poza mapą"

                direction_label = direction_names.get(player.facing, player.facing)
                message = f"X {x}, Y {y}, {direction_label}, stoisz na {current_tile_name}."

                if tile_ahead_name != current_tile_name:
                    message += f" Przed tobą {tile_ahead_name}."

                tts.speak(message)
                last_tts_message = message

                prev_x = x
                prev_y = y
                prev_facing = player.facing

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
