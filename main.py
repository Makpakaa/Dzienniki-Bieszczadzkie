import pygame
import sys

# ZMIANA (1) – importujemy pyttsx3 do syntezy mowy (TTS):
import pyttsx3

# === Funkcja inicjalizująca TTS ===
def initialize_tts():
    engine = pyttsx3.init()
    # Możesz tu ustawić głośność, prędkość czy głos syntezatora:
    # engine.setProperty('rate', 150)
    # engine.setProperty('volume', 1.0)
    return engine

# === Funkcja inicjalizująca grę w trybie pełnoekranowym ===
def initialize_game():
    pygame.init()

    # ZMIANA (2) – pobieramy informację o rozdzielczości ekranu
    info = pygame.display.Info()
    screen_width = info.current_w
    screen_height = info.current_h

    # ZMIANA (2) – ustawiamy tryb FULLSCREEN
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    pygame.display.set_caption("Dzienniki Bieszczadzkie")
    return screen

# === Wyświetlenie logo ===
def show_logo(screen, engine):
    screen.fill((0, 0, 0))
    font = pygame.font.SysFont(None, 64)
    label_text = "LOGO GRY"
    label = font.render(label_text, True, (255, 255, 0))
    # Wstawiamy na środek ekranu
    rect = label.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    screen.blit(label, rect)
    pygame.display.flip()

    # ZMIANA (3) – odczyt na głos
    engine.say("Wyświetlam logo gry. Naciśnij dowolny klawisz, aby przejść dalej.")
    engine.runAndWait()

    # ZMIANA (4) – zastępujemy pygame.time.wait() pętlą zdarzeń
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

# === Wyświetlenie tytułu ===
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

    # ZMIANA (3) – odczyt na głos
    engine.say("Dzienniki Bieszczadzkie. Naciśnij dowolny klawisz, aby przejść dalej.")
    engine.runAndWait()

    # ZMIANA (4) – zamiast time.wait()
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

# === Menu główne gry ===
def main_menu(screen, engine):
    running = True
    clock = pygame.time.Clock()
    selected_option = 0
    options = ["Nowa Gra", "Załaduj Grę", "Wyjście"]

    # ZMIANA (3) – powitanie w menu
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
                    # Odczyt na głos aktualnie wybranej opcji
                    engine.say(options[selected_option])
                    engine.runAndWait()
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(options)
                    # Odczyt na głos aktualnie wybranej opcji
                    engine.say(options[selected_option])
                    engine.runAndWait()
                elif event.key == pygame.K_RETURN:
                    # Odczyt na głos wybranej opcji przy zatwierdzeniu
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

# === Wyświetlenie wprowadzenia ===
def show_introduction(screen, engine):
    screen.fill((0, 0, 0))
    font = pygame.font.SysFont(None, 36)
    intro_text = [
        "Witamy w Dziennikach Bieszczadzkich!",
        "Jesteś wędrowcem przemierzającym spokojne wzgórza i doliny.",
        "Twoim celem jest odkrycie tajemnic tej krainy.",
        "Powodzenia!"
    ]
    # Tekst do odczytania
    tts_text = "\n".join(intro_text)

    for i, line in enumerate(intro_text):
        label = font.render(line, True, (255, 255, 0))
        screen.blit(label, (50, 200 + i * 40))
    pygame.display.flip()

    # ZMIANA (3) – odczyt wstępu
    engine.say(tts_text + " Naciśnij dowolny klawisz, aby przejść dalej.")
    engine.runAndWait()

    # ZMIANA (4) – zamiast pygame.time.wait(5000)
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

# === Wyświetlanie zegara gry ===
def draw_game_clock(screen, game_time):
    font = pygame.font.SysFont(None, 24)
    time_text = f"Czas: {game_time['hour']:02}:{game_time['minute']:02}"
    date_text = f"Data: {game_time['day']} Wiosna, Rok {game_time['year']}"

    time_label = font.render(time_text, True, (255, 255, 0))
    date_label = font.render(date_text, True, (255, 255, 0))

    screen.blit(time_label, (20, 10))
    screen.blit(date_label, (20, 40))

# === Aktualizacja czasu gry ===
def update_game_time(game_time, elapsed_time):
    game_time['minute'] += elapsed_time // 20000  # 20000 ms = 20 sek w realnym czasie => ok. 10 min w grze
    if game_time['minute'] >= 60:
        game_time['minute'] = 0
        game_time['hour'] += 1
    if game_time['hour'] >= 24:
        game_time['hour'] = 0
        game_time['day'] += 1

# === Pętla gry ===
def game_loop(screen):
    running = True
    clock = pygame.time.Clock()
    game_time = {"hour": 6, "minute": 0, "day": 1, "year": 1}
    time_accumulator = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        elapsed_time = clock.tick(60)
        time_accumulator += elapsed_time

        # Aktualizacja czasu gry
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
        game_loop(screen)
