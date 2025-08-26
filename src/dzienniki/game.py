import pygame
from dzienniki import settings
from dzienniki.audio import tts
from dzienniki.entities.player import Player
from dzienniki.systems.maps import TileMap
from dzienniki.systems import inventory
from dzienniki.systems.object_tracker import ObjectTracker
from dzienniki.ui.text_input import ask_text  # okno nazwy punktu

def topdown_game_loop(screen):
    clock = pygame.time.Clock()
    player = Player()
    tracker = ObjectTracker()

    # okno wprowadzania nazwy punktu
    tracker.rename_provider = lambda old_name: ask_text(screen, "Nazwa punktu", old_name)

    # AUTOMATYCZNE WCZYTANIE zapisanych punktów przy starcie gry
    try:
        tracker.load_points_from_file()
    except Exception:
        # cicho — metoda sama powie TTS-em o błędzie, jeśli wystąpi
        pass

    tilemap = TileMap()
    map_rows = tilemap.rows
    passable = tilemap.passable
    names = tilemap.names

    inventory.init_font()
    show_inventory = False
    tracker_mode = False  # tryb przeglądania obiektów

    while True:
        dt = clock.tick(settings.FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            elif event.type == pygame.KEYDOWN:
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
                        # wymaga metody repeat_last_message() w Player (patrz niżej)
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
                                    tracker.set_flag((o["x"], o["y"]))  # tracker sam mówi "Ustawiono flagę..."
                                    if hasattr(tracker, "flag_label"):
                                        tracker.flag_label = o.get("name")
                                except Exception:
                                    tracker.activate_selection()
                            else:
                                tts.speak("Brak obiektów.")
                        # Prawa lista: Zapisane punkty
                        else:
                            if tracker.selected_index == 0:
                                # „Ustaw punkt” (wewnątrz tracker poprosi o nazwę i AUTO-zapisze)
                                tracker.activate_selection()
                            else:
                                idx = tracker.selected_index - 1
                                if 0 <= idx < len(tracker.saved_points):
                                    sp = tracker.saved_points[idx]
                                    tracker.set_flag(sp["pos"])  # tracker sam mówi
                                    if hasattr(tracker, "flag_label"):
                                        tracker.flag_label = sp.get("name")
                                else:
                                    tts.speak("Błędny wybór zapisanego punktu.")

                # Spacja - submenu
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

                # Tab / Shift+Tab - przełączanie list
                elif event.key == pygame.K_TAB and tracker_mode:
                    tracker.switch_list(backwards=bool(pygame.key.get_mods() & pygame.KMOD_SHIFT))

                # Obsługa inventory
                elif show_inventory:
                    inventory.handle_inventory_navigation(event)

        # Aktualizacja gracza (poza trybem menu/trackera)
        if not show_inventory and not tracker_mode:
            keys = pygame.key.get_pressed()
            player.handle_input(keys)
            player.update(dt, map_rows, passable, names)

            # Sprawdzaj automatyczne domknięcie flagi, gdy ramka przed graczem dojdzie do celu
            if hasattr(tracker, "auto_clear_flag_if_front_reached"):
                tracker.auto_clear_flag_if_front_reached(player, map_rows, names)

        # Rysowanie
        screen.fill((0, 0, 0))
        size = settings.TILE_SIZE

        for row_idx, row in enumerate(map_rows):
            for col_idx, cell in enumerate(row):
                color = (34, 139, 34)
                if cell == "w":
                    color = (0, 0, 255)
                elif cell == "s":
                    color = (128, 128, 128)
                pygame.draw.rect(screen, color, (col_idx * size, row_idx * size, size, size))

        tracker.draw_flag_on_map(screen, size)
        player.draw(screen)

        if show_inventory:
            inventory.draw(screen)
        elif tracker_mode:
            tracker.draw(screen)

        pygame.display.flip()
