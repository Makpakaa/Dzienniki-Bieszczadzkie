import pygame
import sys
import pyttsx3

# === Funkcja inicjalizująca TTS (bez zmian) ===
def initialize_tts():
    engine = pyttsx3.init()
    # Możesz tu ustawić głośność, prędkość czy głos syntezatora:
    # engine.setProperty('rate', 150)
    # engine.setProperty('volume', 1.0)
    return engine

# === Funkcja inicjalizująca grę w trybie pełnoekranowym (bez zmian) ===
def initialize_game():
    pygame.init()
    info = pygame.display.Info()
    screen_width = info.current_w
    screen_height = info.current_h
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    pygame.display.set_caption("Dzienniki Bieszczadzkie")
    return screen

def show_logo(screen, engine):
    screen.fill((0, 0, 0))
    font = pygame.font.SysFont(None, 64)
    label_text = "LOGO GRY"
    label = font.render(label_text, True, (255, 255, 0))
    rect = label.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    screen.blit(label, rect)
    pygame.display.flip()

    engine.say("Wyświetlam logo gry. Naciśnij dowolny klawisz, aby przejść dalej.")
    engine.runAndWait()

    wait_duration = 10000  # ms
    start_time = pygame.time.get_ticks()
    waiting = True
    while waiting:
        current_time = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False

        if current_time - start_time >= wait_duration:
            waiting = False

def show_title(screen, engine):
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

    engine.say("Dzienniki Bieszczadzkie. Naciśnij dowolny klawisz, aby przejść dalej.")
    engine.runAndWait()

    wait_duration = 10000  # ms
    start_time = pygame.time.get_ticks()
    waiting = True
    while waiting:
        current_time = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False

        if current_time - start_time >= wait_duration:
            waiting = False

# === Menu główne gry (bez większych zmian) ===
def main_menu(screen, engine):
    running = True
    clock = pygame.time.Clock()
    selected_option = 0
    options = ["Nowa Gra", "Załaduj Grę", "Wyjście"]

    engine.say("Menu główne. Użyj strzałek góra i dół, by wybrać opcję, Enter aby zatwierdzić.")
    engine.runAndWait()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(options)
                    engine.say(options[selected_option])
                    engine.runAndWait()
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(options)
                    engine.say(options[selected_option])
                    engine.runAndWait()
                elif event.key == pygame.K_RETURN:
                    engine.say(f"Wybrano opcję: {options[selected_option]}")
                    engine.runAndWait()

                    if selected_option == 0:  # Nowa Gra
                        return "new_game"
                    elif selected_option == 1:  # Załaduj Grę
                        engine.say("Załaduj Grę - opcja w przygotowaniu.")
                        engine.runAndWait()
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
                pygame.draw.rect(screen, (255, 255, 255),
                                 pygame.Rect(295, 195 + i * 60, 310, 60), 2)

        pygame.display.flip()
        clock.tick(30)

def show_introduction(screen, engine):
    screen.fill((0, 0, 0))
    font = pygame.font.SysFont(None, 36)
    intro_text = [
        "Witamy w Dziennikach Bieszczadzkich!",
        "Jesteś wędrowcem przemierzającym spokojne wzgórza i doliny.",
        "Twoim celem jest odkrycie tajemnic tej krainy.",
        "Powodzenia!"
    ]
    tts_text = "\n".join(intro_text)

    for i, line in enumerate(intro_text):
        label = font.render(line, True, (255, 255, 0))
        screen.blit(label, (50, 200 + i * 40))
    pygame.display.flip()

    engine.say(tts_text + " Naciśnij dowolny klawisz, aby przejść dalej.")
    engine.runAndWait()

    wait_duration = 5000  # ms
    start_time = pygame.time.get_ticks()
    waiting = True
    while waiting:
        current_time = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False

        if current_time - start_time >= wait_duration:
            waiting = False

# === Funkcja wyświetlająca zegar gry (bez zmian) ===
def draw_game_clock(screen, game_time):
    font = pygame.font.SysFont(None, 24)
    time_text = f"Czas: {game_time['hour']:02}:{game_time['minute']:02}"
    date_text = f"Data: {game_time['day']} Wiosna, Rok {game_time['year']}"
    time_label = font.render(time_text, True, (255, 255, 0))
    date_label = font.render(date_text, True, (255, 255, 0))
    screen.blit(time_label, (20, 10))
    screen.blit(date_label, (20, 40))

# === Funkcja aktualizująca czas gry (bez zmian) ===
def update_game_time(game_time, elapsed_time):
    game_time['minute'] += elapsed_time // 20000  # 20000 ms = 20 sek w realnym => ~10 min w grze
    if game_time['minute'] >= 60:
        game_time['minute'] = 0
        game_time['hour'] += 1
    if game_time['hour'] >= 24:
        game_time['hour'] = 0
        game_time['day'] += 1

# === ZMIANA (1) – Funkcja potwierdzająca wyjście z gry ===
def confirm_quit(screen, engine):
    """
    Zwraca 'yes' jeśli użytkownik potwierdzi wyjście z gry,
    lub 'no' jeśli wróci do menu pauzy.
    """
    options = ["Tak", "Nie"]
    selected_option = 0

    # Komunikat TTS
    engine.say("Czy na pewno zapisałeś stan gry? Wybierz Tak lub Nie.")
    engine.runAndWait()

    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % 2  # przełączanie 0 <-> 1
                    engine.say(options[selected_option])
                    engine.runAndWait()
                elif event.key == pygame.K_RETURN:
                    engine.say(f"Wybrano: {options[selected_option]}")
                    engine.runAndWait()
                    if selected_option == 0:
                        return "yes"  # Tak
                    else:
                        return "no"   # Nie

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

# === ZMIANA (2) – Funkcja menu pauzy (in-game) ===
def pause_menu(screen, engine):
    """
    Zwraca:
      - "resume" jeśli gracz wybierze Wróć do gry
      - "quit" jeśli gracz wybierze Wyjdź z gry
      - "continue" przy innych opcjach (np. Zapisz/Wczytaj/Ustawienia – tu tylko stub)
    """
    options = ["Wróć do gry", "Zapisz grę", "Wczytaj grę", "Ustawienia", "Wyjdź z gry"]
    selected_option = 0

    engine.say("Menu pauzy. Użyj strzałek góra i dół, aby wybrać opcję, Enter aby zatwierdzić.")
    engine.runAndWait()

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
                    engine.say(options[selected_option])
                    engine.runAndWait()
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(options)
                    engine.say(options[selected_option])
                    engine.runAndWait()
                elif event.key == pygame.K_RETURN:
                    engine.say(f"Wybrano: {options[selected_option]}")
                    engine.runAndWait()

                    if selected_option == 0:  # Wróć do gry
                        return "resume"
                    elif selected_option == 1:  # Zapisz grę
                        engine.say("Zapisz grę - opcja w przygotowaniu.")
                        engine.runAndWait()
                        # Możesz tu wywołać własną logikę zapisu
                    elif selected_option == 2:  # Wczytaj grę
                        engine.say("Wczytaj grę - opcja w przygotowaniu.")
                        engine.runAndWait()
                        # Możesz tu wywołać własną logikę wczytywania
                    elif selected_option == 3:  # Ustawienia
                        engine.say("Ustawienia - opcja w przygotowaniu.")
                        engine.runAndWait()
                        # Możesz dodać menu ustawień
                    elif selected_option == 4:  # Wyjdź z gry
                        return "quit"

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

# === Pętla gry (rozszerzona o obsługę pauzy) ===
def game_loop(screen, engine):
    running = True
    clock = pygame.time.Clock()
    game_time = {"hour": 6, "minute": 0, "day": 1, "year": 1}
    time_accumulator = 0

    while running:
        # Obsługa zdarzeń
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # ZMIANA (3) – wciśnięcie ESC otwiera menu pauzy
                if event.key == pygame.K_ESCAPE:
                    action = pause_menu(screen, engine)
                    if action == "resume":
                        # Wróć do gry – nic nie zmieniamy, kontynuujemy pętlę
                        pass
                    elif action == "quit":
                        # Najpierw zapytaj, czy na pewno zapisałeś grę
                        confirm = confirm_quit(screen, engine)
                        if confirm == "yes":
                            running = False
                        else:
                            # powrót do menu pauzy
                            # Możemy ponownie wywołać pause_menu, aż wybierzemy Resume lub Quit yes
                            # Tu dla prostoty wracamy do pętli i ESC znowu otwiera menu
                            pass

        # Aktualizacja stanu gry (zegar itp.)
        elapsed_time = clock.tick(60)
        time_accumulator += elapsed_time
        # Czas upływa tylko gdy nie jesteśmy w pauzie!
        # Gdy pauza trwa, ta część i tak stoi w miejscu, bo pętla jest „zamrożona” w pause_menu.

        if time_accumulator >= 20000:
            update_game_time(game_time, time_accumulator)
            time_accumulator = 0

        # Rysowanie tła i elementów gry
        screen.fill((0, 0, 0))
        draw_game_clock(screen, game_time)

        pygame.display.flip()

if __name__ == "__main__":
    # Inicjalizacja TTS
    engine = initialize_tts()
    # Inicjalizacja okna w trybie fullscreen
    screen = initialize_game()

    # Wyświetlanie logo i tytułu
    show_logo(screen, engine)
    show_title(screen, engine)

    # Przejście do menu głównego
    selected_action = main_menu(screen, engine)
    if selected_action == "new_game":
        show_introduction(screen, engine)
        game_loop(screen, engine)
    # W innych wypadkach można zdefiniować dalszą logikę (np. wczytanie gry).
