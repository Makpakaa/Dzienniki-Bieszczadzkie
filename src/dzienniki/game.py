import pygame
from dzienniki import settings
from dzienniki.audio import tts
from dzienniki.systems.maps import TileMap
from dzienniki.entities.player import Player
from dzienniki.systems import inventory
from dzienniki.systems.object_tracker import ObjectTracker
from dzienniki.ui.text_input import ask_text  # okno nazwy punktu


def clamp(v, vmin, vmax):
    return max(vmin, min(vmax, v))


def compute_camera(player, map_cols, map_rows_count):
    """Kamera jak w Stardew: centrowanie na graczu, z ograniczeniem do granic mapy."""
    tile = settings.TILE_SIZE
    view_w, view_h = settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT
    world_w = map_cols * tile
    world_h = map_rows_count * tile

    # Środek gracza
    px_center = player.pixel_x + tile / 2
    py_center = player.pixel_y + tile / 2

    cam_x = px_center - view_w / 2
    cam_y = py_center - view_h / 2

    # Ograniczenia do świata
    cam_x = clamp(cam_x, 0, max(0, world_w - view_w))
    cam_y = clamp(cam_y, 0, max(0, world_h - view_h))
    return cam_x, cam_y


def draw_world(screen, map_rows, cam_x, cam_y):
    """Rysuje tylko kafle widoczne w oknie, z przesunięciem kamery."""
    tile = settings.TILE_SIZE
    view_w, view_h = settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT

    # Zakres widocznych kolumn/wierszy
    start_col = int(cam_x // tile)
    start_row = int(cam_y // tile)
    end_col = int((cam_x + view_w) // tile) + 1
    end_row = int((cam_y + view_h) // tile) + 1

    max_rows = len(map_rows)
    max_cols = len(map_rows[0]) if max_rows > 0 else 0

    start_col = clamp(start_col, 0, max_cols)
    start_row = clamp(start_row, 0, max_rows)
    end_col = clamp(end_col, 0, max_cols)
    end_row = clamp(end_row, 0, max_rows)

    for row_idx in range(start_row, end_row):
        row = map_rows[row_idx]
        for col_idx in range(start_col, end_col):
            cell = row[col_idx]
            # Proste kolory placeholder:
            color = (34, 139, 34)  # trawa
            if cell == "w":
                color = (0, 0, 255)      # woda
            elif cell == "s":
                color = (128, 128, 128)  # kamień

            screen_x = col_idx * tile - cam_x
            screen_y = row_idx * tile - cam_y
            pygame.draw.rect(screen, color, (screen_x, screen_y, tile, tile))


def draw_flag(screen, tracker, cam_x, cam_y):
    """Rysuje flagę celu z uwzględnieniem kamery (fallback, bez zależności od metody trackera)."""
    if hasattr(tracker, "flag") and tracker.flag:
        tile = settings.TILE_SIZE
        fx, fy = tracker.flag  # współrzędne w siatce
        sx = fx * tile - cam_x
        sy = fy * tile - cam_y
        # Prosty marker – obrysowany kwadrat
        rect = pygame.Rect(sx, sy, tile, tile)
        pygame.draw.rect(screen, (255, 215, 0), rect, width=3)  # złota ramka


def topdown_game_loop(screen):
    clock = pygame.time.Clock()

    # Najpierw mapa – bo ona definiuje spawn
    tilemap = TileMap()  # np. TileMap(seed=42)
    map_rows = tilemap.rows
    passable = tilemap.passable
    names = tilemap.names
    spawn_x, spawn_y = getattr(tilemap, "spawn", (0, 0))

    # Gracz startuje wg spawnu z mapy
    player = Player(start_x=spawn_x, start_y=spawn_y)

    tracker = ObjectTracker()
    tracker.rename_provider = lambda old_name: ask_text(screen, "Nazwa punktu", old_name)

    # Auto-load zapisanych punktów
    try:
        tracker.load_points_from_file()
    except Exception:
        pass  # metoda sama gada TTS-em o błędzie, jeśli wystąpi

    # Jednorazowy sanity komunikat (tu minimalistyczny)
    try:
        tts.speak(
            f"Start gry. Pozycja {player.grid_x} {player.grid_y}. "
            f"Stoisz na {names.get(map_rows[player.grid_y][player.grid_x], 'nieznanym terenie')}."
        )
    except Exception:
        pass

    inventory.init_font()
    show_inventory = False
    tracker_mode = False  # tryb przeglądania obiektów

    while True:
        dt = clock.tick(settings.FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            elif event.type == pygame.KEYDOWN:
                # Inventory ma priorytet na klawisze, ale najpierw obsłuż E/ESC do zamykania
                if show_inventory:
                    if event.key in (pygame.K_ESCAPE, pygame.K_e):
                        show_inventory = False
                        tts.speak("Zamknięto ekwipunek.")
                        continue
                    inventory.handle_inventory_navigation(event)
                    continue

                # ESC - wyjście lub zamknięcie menu
                if event.key == pygame.K_ESCAPE:
                    if show_inventory:
                        show_inventory = False
                        tts.speak("Zamknięto ekwipunek.")
                    elif tracker_mode:
                        tracker_mode = False
                        tts.speak("Zamknięto listę obiektów.")
                    else:
                        return

                # E - ekwipunek
                elif event.key == pygame.K_e:
                    show_inventory = not show_inventory
                    if show_inventory:
                        inventory.selected_section = 1
                        inventory.selected_item_index = 0
                        tts.speak("Ekwipunek otwarty.")
                        inventory.speak_current_item()
                    else:
                        tts.speak("Zamknięto ekwipunek.")

                # R - powtórz ostatni komunikat (tracker albo gracz)
                elif event.key == pygame.K_r:
                    if tracker_mode:
                        tracker.repeat_last_message()
                    else:
                        if hasattr(player, "repeat_last_message"):
                            player.repeat_last_message()
                        else:
                            tts.speak("Brak komunikatu do powtórzenia.")

                # T - tryb object tracker
                elif event.key == pygame.K_t:
                    tracker.activate(player)
                    tracker.scan_area(player, map_rows, names)
                    tracker.speak_selected()
                    tracker_mode = True

                # Ctrl+F - anuluj flagę
                elif event.key == pygame.K_f and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    tracker.clear_flag()

                # Ctrl+S - zapisz zapisane punkty
                elif event.key == pygame.K_s and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    tracker.save_points_to_file()

                # Ctrl+L - wczytaj zapisane punkty (ręcznie)
                elif event.key == pygame.K_l and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    tracker.load_points_from_file()

                # F - kierunek do flagi
                elif event.key == pygame.K_f:
                    tracker.speak_target_direction(player)

                # Enter - akcja w trackerze (ustaw flagę / ustaw punkt / submenu)
                elif event.key == pygame.K_RETURN and tracker_mode:
                    if tracker.submenu_open:
                        tracker.submenu_select()
                    else:
                        # Lewa lista: Zeskanowane obiekty
                        if tracker.list_index == 0:
                            if tracker.objects:
                                try:
                                    o = tracker.objects[tracker.selected_index]
                                    tracker.set_flag((o["x"], o["y"]))
                                    if hasattr(tracker, "flag_label"):
                                        tracker.flag_label = o.get("name")
                                except Exception:
                                    tracker.activate_selection()
                            else:
                                tts.speak("Brak obiektów.")
                        # Prawa lista: Zapisane punkty
                        else:
                            if tracker.selected_index == 0:
                                tracker.activate_selection()  # „Ustaw punkt”
                            else:
                                idx = tracker.selected_index - 1
                                if 0 <= idx < len(tracker.saved_points):
                                    sp = tracker.saved_points[idx]
                                    tracker.set_flag(sp["pos"])
                                    if hasattr(tracker, "flag_label"):
                                        tracker.flag_label = sp.get("name")
                                else:
                                    tts.speak("Błędny wybór zapisanego punktu.")

                # Spacja - submenu (tylko w trackerze)
                elif event.key == pygame.K_SPACE and tracker_mode:
                    if tracker.submenu_open:
                        tracker.submenu_select()
                    else:
                        tracker.open_submenu(player)

                # W/S - góra/dół (tylko w trackerze)
                elif event.key in (pygame.K_w, pygame.K_s) and tracker_mode:
                    if tracker.submenu_open:
                        if event.key == pygame.K_w:
                            tracker.submenu_prev()
                        else:
                            tracker.submenu_next()
                    else:
                        if event.key == pygame.K_w:
                            tracker.previous_object()
                        else:
                            tracker.next_object()

                # Tab / Shift+Tab - przełączanie list (tracker)
                elif event.key == pygame.K_TAB and tracker_mode:
                    tracker.switch_list(backwards=bool(pygame.key.get_mods() & pygame.KMOD_SHIFT))

        # Aktualizacja gracza (poza trybem menu/trackera)
        if not show_inventory and not tracker_mode:
            keys = pygame.key.get_pressed()
            player.handle_input(keys)
            player.update(dt, map_rows, passable, names)

            # Autoclear flagi, gdy ramka przed graczem dojdzie do celu
            if hasattr(tracker, "auto_clear_flag_if_front_reached"):
                tracker.auto_clear_flag_if_front_reached(player, map_rows, names)

        # --- Kamera & rysowanie jak w Stardew ---
        cam_x, cam_y = compute_camera(player, len(map_rows[0]), len(map_rows))

        screen.fill((0, 0, 0))
        draw_world(screen, map_rows, cam_x, cam_y)
        draw_flag(screen, tracker, cam_x, cam_y)
        player.draw(screen, cam_x, cam_y)

        if show_inventory:
            inventory.draw(screen)
        elif tracker_mode:
            tracker.draw(screen)

        pygame.display.flip()
