import pygame
import sys
import threading
import pyttsx3
import inventory
import container
import shop
import world

# --- Ustawienia ---
TILE_SIZE = 16
MAP_SIZE = 200   # mapa 200x200
MOVE_COOLDOWN = 300  # co ile ms można wykonać kolejny krok przy przytrzymaniu klawisza

# === Zmienne globalne dla TTS ===
stop_tts_flag = False      # Flaga do przerwania mowy
tts_running_flag = False   # Czy aktualnie trwa mówienie

def tts_thread_function(text):
    global stop_tts_flag, tts_running_flag
    tts_running_flag = True

    try:
        engine = pyttsx3.init()
        chunks = text.split(". ")

        for chunk in chunks:
            if stop_tts_flag:
                break
            engine.say(chunk)
            engine.runAndWait()
            if stop_tts_flag:
                break

        engine.stop()
    except RuntimeError:
        pass  # Silnik już działa – ignorujemy błąd

    tts_running_flag = False
    stop_tts_flag = False

def start_tts(text):
    """
    Uruchamia nowy wątek TTS z podanym tekstem, o ile nie trwa już mówienie.
    """
    global stop_tts_flag, tts_running_flag
    # Jeśli TTS obecnie nie mówi, tworzymy nowy wątek.
    if not tts_running_flag:
        stop_tts_flag = False
        t = threading.Thread(target=tts_thread_function, args=(text,))
        t.start()

def stop_tts():
    """
    Ustawia flagę przerwania mowy.
    """
    global stop_tts_flag
    stop_tts_flag = True

# === Funkcja inicjalizująca grę w trybie pełnoekranowym ===
def initialize_game():
    pygame.init()
    inventory.init_font()
    info = pygame.display.Info()
    screen_width = info.current_w
    screen_height = info.current_h
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    pygame.display.set_caption("Dzienniki Bieszczadzkie - Widok 2D")
    return screen


# === Wyświetlanie logo (przykład) ===
def show_logo(screen):
    screen.fill((0, 0, 0))
    font = pygame.font.SysFont(None, 64)
    label_text = "LOGO GRY"
    label = font.render(label_text, True, (255, 255, 0))
    rect = label.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    screen.blit(label, rect)
    pygame.display.flip()

    # Rozpoczynamy czytanie w osobnym wątku
    start_tts("Wyświetlam logo gry. Naciśnij dowolny klawisz, aby przejść dalej.")

    # Czekamy, aż użytkownik wciśnie klawisz lub minie pewien czas
    wait_duration = 3000  # ms
    start_time = pygame.time.get_ticks()
    waiting = True
    while waiting:
        current_time = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                # Przerywamy TTS i przechodzimy dalej
                stop_tts()
                waiting = False
        if current_time - start_time >= wait_duration:
            # Po 3 sekundach też przerywamy automatycznie
            stop_tts()
            waiting = False

# === Wyświetlanie tytułu (przykład) ===
def show_title(screen):
    screen.fill((0, 0, 0))
    font = pygame.font.SysFont(None, 100)
    title_text = "Dzienniki\nBieszczadzkie"
    lines = title_text.split("\n")

    for i, line in enumerate(lines):
        line_label = font.render(line, True, (255, 255, 0))
        text_rect = line_label.get_rect(
            center=(screen.get_width() // 2, (screen.get_height() // 2) + i * 100)
        )
        screen.blit(line_label, text_rect)

    pygame.display.flip()

    start_tts("Dzienniki Bieszczadzkie. Naciśnij dowolny klawisz, aby przejść dalej.")

    wait_duration = 3000
    start_time = pygame.time.get_ticks()
    waiting = True
    while waiting:
        current_time = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                stop_tts()
                waiting = False
        if current_time - start_time >= wait_duration:
            stop_tts()
            waiting = False

# === Menu główne gry ===
def main_menu(screen):
    running = True
    clock = pygame.time.Clock()
    selected_option = 0
    options = ["Nowa Gra", "Załaduj Grę", "Wyjście"]

    # TTS menu głównego
    start_tts("Menu główne. Użyj strzałek góra i dół, by wybrać opcję, Enter aby zatwierdzić.")

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(options)
                    stop_tts()  # przerywamy poprzednią wypowiedź
                    start_tts(options[selected_option])
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(options)
                    stop_tts()
                    start_tts(options[selected_option])
                elif event.key == pygame.K_RETURN:
                    stop_tts()
                    # Komunikat TTS z wybraną opcją
                    start_tts(f"Wybrano opcję: {options[selected_option]}")
                    # Poczekajmy krótką chwilę, żeby usłyszeć choć kawałek komunikatu
                    pygame.time.delay(300)

                    if selected_option == 0:  # Nowa Gra
                        return "new_game"
                    elif selected_option == 1:  # Załaduj Grę (stub)
                        start_tts("Załaduj Grę - opcja w przygotowaniu.")
                    elif selected_option == 2:  # Wyjście
                        pygame.quit()
                        sys.exit()

        screen.fill((0, 0, 0))
        font = pygame.font.SysFont(None, 48)
        for i, option in enumerate(options):
            color = (255, 255, 255) if i == selected_option else (255, 255, 0)
            label = font.render(option, True, color)
            screen.blit(label, (300, 200 + i * 60))
            if i == selected_option:
                pygame.draw.rect(
                    screen, (255, 255, 255),
                    pygame.Rect(295, 195 + i * 60, 310, 60),
                    2
                )

        pygame.display.flip()
        clock.tick(30)

# === Wyświetlenie wprowadzenia (przykład) ===
def show_introduction(screen):
    screen.fill((0, 0, 0))
    font = pygame.font.SysFont(None, 36)
    intro_text = [
        "Witamy w Dziennikach Bieszczadzkich!",
        "Jesteś wędrowcem przemierzającym spokojne wzgórza i doliny.",
        "Twoim celem jest odkrycie tajemnic tej krainy.",
        "Powodzenia!"
    ]
    tts_text = ". ".join(intro_text)

    for i, line in enumerate(intro_text):
        label = font.render(line, True, (255, 255, 0))
        screen.blit(label, (50, 200 + i * 40))
    pygame.display.flip()

    start_tts(tts_text + ". Naciśnij dowolny klawisz, aby przejść dalej.")

    wait_duration = 3000
    start_time = pygame.time.get_ticks()
    waiting = True
    while waiting:
        current_time = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                stop_tts()
                waiting = False
        if current_time - start_time >= wait_duration:
            stop_tts()
            waiting = False

# === Funkcja potwierdzająca wyjście z gry (z pauzy) ===
def confirm_quit(screen):
    options = ["Tak", "Nie"]
    selected_option = 0

    start_tts("Czy na pewno zapisałeś stan gry? Wybierz Tak lub Nie.")

    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_UP, pygame.K_DOWN]:
                    selected_option = (selected_option + 1) % 2
                    stop_tts()
                    start_tts(options[selected_option])
                elif event.key == pygame.K_RETURN:
                    stop_tts()
                    start_tts(f"Wybrano: {options[selected_option]}")
                    pygame.time.delay(300)  # krótkie opóźnienie
                    if selected_option == 0:
                        return "yes"
                    else:
                        return "no"

        screen.fill((0, 0, 0))
        font = pygame.font.SysFont(None, 48)
        prompt_label = font.render("Czy na pewno zapisałeś stan gry?", True, (255, 255, 0))
        prompt_rect = prompt_label.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 60))
        screen.blit(prompt_label, prompt_rect)

        for i, opt in enumerate(options):
            color = (255, 255, 255) if i == selected_option else (255, 255, 0)
            label = font.render(opt, True, color)
            label_rect = label.get_rect(center=(screen.get_width() // 2, (screen.get_height() // 2) + i * 60))
            screen.blit(label, label_rect)
            if i == selected_option:
                pygame.draw.rect(
                    screen, (255, 255, 255),
                    pygame.Rect(label_rect.left - 5, label_rect.top - 5, label_rect.width + 10, label_rect.height + 10),
                    2
                )

        pygame.display.flip()
        clock.tick(30)

# === Menu pauzy (w trakcie gry) ===
def pause_menu(screen):
    options = ["Wróć do gry", "Zapisz grę", "Wczytaj grę", "Ustawienia", "Wyjdź z gry"]
    selected_option = 0

    start_tts("Menu pauzy. Użyj strzałek góra i dół, aby wybrać opcję, Enter aby zatwierdzić.")

    clock = pygame.time.Clock()
    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(options)
                    stop_tts()
                    start_tts(options[selected_option])
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(options)
                    stop_tts()
                    start_tts(options[selected_option])
                elif event.key == pygame.K_RETURN:
                    stop_tts()
                    start_tts(f"Wybrano: {options[selected_option]}")
                    pygame.time.delay(300)
                    if selected_option == 0:  # Wróć do gry
                        return "resume"
                    elif selected_option == 1:  # Zapisz grę
                        start_tts("Zapisz grę - opcja w przygotowaniu.")
                    elif selected_option == 2:  # Wczytaj grę
                        start_tts("Wczytaj grę - opcja w przygotowaniu.")
                    elif selected_option == 3:  # Ustawienia
                        start_tts("Ustawienia - opcja w przygotowaniu.")
                    elif selected_option == 4:  # Wyjdź z gry
                        return "quit"

        # Rysowanie menu pauzy
        screen.fill((0, 0, 0))
        font = pygame.font.SysFont(None, 48)
        pause_label = font.render("Pauza", True, (255, 255, 0))
        screen.blit(pause_label, (50, 50))

        for i, opt in enumerate(options):
            color = (255, 255, 255) if i == selected_option else (255, 255, 0)
            label = font.render(opt, True, color)
            screen.blit(label, (300, 200 + i * 60))
            if i == selected_option:
                pygame.draw.rect(
                    screen, (255, 255, 255),
                    pygame.Rect(295, 195 + i * 60, 310, 60),
                    2
                )

        pygame.display.flip()
        clock.tick(30)

# === Rysowanie siatki 2D 200x200 cienką żółtą linią w pionie i poziomie ===
def draw_2d_grid(screen, offset_x, offset_y, color=(255, 255, 0)):
    # Linie poziome
    for row in range(MAP_SIZE + 1):
        y = offset_y + row * TILE_SIZE
        start_x = offset_x
        end_x = offset_x + MAP_SIZE * TILE_SIZE
        pygame.draw.line(screen, color, (start_x, y), (end_x, y), 1)

    # Linie pionowe
    for col in range(MAP_SIZE + 1):
        x = offset_x + col * TILE_SIZE
        start_y = offset_y
        end_y = offset_y + MAP_SIZE * TILE_SIZE
        pygame.draw.line(screen, color, (x, start_y), (x, end_y), 1)

# === Ograniczanie wartości do zakresu [min_val, max_val] ===
def clamp(value, min_val, max_val):
    return max(min_val, min(value, max_val))





# === Pętla gry 2D (top-down) ===
def topdown_game_loop(screen):
    action = None
    clock = pygame.time.Clock()

    # 🛑 ← tutaj WSTAW to:

    chest = container.Container("Skrzynia", capacity=10)
    chest.add_item("Złoty pierścień", 1)
    chest.add_item("Kurtka", 1)

    village_shop = shop.Shop("Sklep wiejski")
    village_shop.add_item("Kilof", 1, 150)
    village_shop.add_item("Ziemniak", 5, 5)
    village_shop.add_item("Chleb", 2, 10)

    # Pozycja startowa gracza (środek planszy)
    player_col = 100
    player_row = 100

    # Rozmiar okna
    screen_width, screen_height = screen.get_size()

    # Ustawiamy offset tak, by gracz był w środku ekranu
    offset_x = screen_width // 2 - (player_col * TILE_SIZE)
    offset_y = screen_height // 2 - (player_row * TILE_SIZE)

    # Kontrola powtarzania ruchu
    next_move_time = 0
    keys_held = {
        pygame.K_UP: False,
        pygame.K_DOWN: False,
        pygame.K_LEFT: False,
        pygame.K_RIGHT: False
    }

    running = True
    # Ustawiamy ekwipunek na domyślnie zamknięty
    inventory.inventory_open = False

    while running:
        current_time = pygame.time.get_ticks()

        # Obsługa zdarzeń
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    # Tutaj sprawdzimy, co jest przed graczem
                    # Na razie robimy test: zawsze otwierajmy skrzynię
                    inventory.container_items = chest.items  # chest będzie naszym przykładowym kontenerem
                    inventory.inventory_open = True
                    inventory.selected_section = 0
                    inventory.selected_item_index = 0
                    start_tts("Otwieram skrzynię lub sklep.")
                if event.key == pygame.K_ESCAPE:
                    if inventory.inventory_open:
                        inventory.inventory_open = False
                        start_tts("Zamykam ekwipunek")
                    else:
                        action = pause_menu(screen)
                    if action == "resume":
                        pass
                    elif action == "quit":
                        confirm = confirm_quit(screen)
                        if confirm == "yes":
                            running = False

                elif event.key == pygame.K_e:
                    inventory.inventory_open = not inventory.inventory_open
                    if inventory.inventory_open:
                        start_tts("Otwieram ekwipunek")
                    else:
                        start_tts("Zamykam ekwipunek")

                if event.key in keys_held:
                    keys_held[event.key] = True

            if event.type == pygame.KEYUP:
                if event.key in keys_held:
                    keys_held[event.key] = False

        if inventory.inventory_open:
            inventory.handle_inventory_navigation(event)

        if not inventory.inventory_open and current_time >= next_move_time:
            original_col, original_row = player_col, player_row

            if keys_held[pygame.K_UP]:
                player_row -= 1
            if keys_held[pygame.K_DOWN]:
                player_row += 1
            if keys_held[pygame.K_LEFT]:
                player_col -= 1
            if keys_held[pygame.K_RIGHT]:
                player_col += 1

            # Granice mapy
            player_col = clamp(player_col, 0, MAP_SIZE - 1)
            player_row = clamp(player_row, 0, MAP_SIZE - 1)

            if (player_col, player_row) != (original_col, original_row):
                stop_tts()
                start_tts(f"Przechodzę na {player_col}, {player_row}")
                next_move_time = current_time + MOVE_COOLDOWN

        # Aktualizacja widoku
        offset_x = screen_width // 2 - (player_col * TILE_SIZE)
        offset_y = screen_height // 2 - (player_row * TILE_SIZE)

        # Rysowanie
        screen.fill((0, 0, 0))

        if inventory.inventory_open:
            inventory.update()
            inventory.draw(screen)
        else:
            draw_2d_grid(screen, offset_x, offset_y, (255, 255, 0))
            # Rysuj upuszczone przedmioty
            for item in world.dropped_items:
                item_x = offset_x + item.x * TILE_SIZE
                item_y = offset_y + item.y * TILE_SIZE
                item_rect = pygame.Rect(item_x, item_y, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(screen, (0, 255, 0), item_rect)  # zielony kwadrat

            gx = offset_x + player_col * TILE_SIZE
            gy = offset_y + player_row * TILE_SIZE
            player_rect = pygame.Rect(gx, gy, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, (255, 255, 255), player_rect)

        pygame.display.flip()
        clock.tick(60)


# === Główna funkcja uruchamiająca całą grę ===
def main():
    screen = initialize_game()

    # Ekrany logo/tytuł
    show_logo(screen)
    show_title(screen)

    # Menu główne
    action = main_menu(screen)
    if action == "new_game":
        show_introduction(screen)
        topdown_game_loop(screen)



    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
