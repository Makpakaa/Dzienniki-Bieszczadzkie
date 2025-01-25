import pygame
import sys

# === Funkcja inicjalizująca grę ===
def initialize_game():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Dzienniki Bieszczadzkie")
    return screen

# === Wyświetlenie logo ===
def show_logo(screen):
    screen.fill((0, 0, 0))
    font = pygame.font.SysFont(None, 64)
    label = font.render("LOGO GRY", True, (255, 255, 0))
    screen.blit(label, (300, 250))
    pygame.display.flip()
    pygame.time.wait(10000)

# === Wyświetlenie tytułu ===
def show_title(screen):
    screen.fill((0, 0, 0))
    font = pygame.font.SysFont(None, 100)
    title_text = "Dzienniki\nBieszczadzkie"
    for i, line in enumerate(title_text.split("\n")):
        line_label = font.render(line, True, (255, 255, 0))
        text_rect = line_label.get_rect(center=(400, 250 + i * 100))
        screen.blit(line_label, text_rect)
    pygame.display.flip()
    pygame.time.wait(10000)

# === Menu główne gry ===
def main_menu(screen):
    running = True
    clock = pygame.time.Clock()
    selected_option = 0
    options = ["Nowa Gra", "Załaduj Grę", "Wyjście"]

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if selected_option == 0:
                        return "new_game"
                    elif selected_option == 1:
                        print("Załaduj Grę - w przygotowaniu")
                    elif selected_option == 2:
                        pygame.quit()
                        sys.exit()

        screen.fill((0, 0, 0))
        font = pygame.font.SysFont(None, 48)
        for i, option in enumerate(options):
            color = (255, 255, 255) if i == selected_option else (255, 255, 0)
            label = font.render(option, True, color)
            screen.blit(label, (300, 200 + i * 60))
            if i == selected_option:
                pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(295, 195 + i * 60, 310, 60), 2)

        pygame.display.flip()
        clock.tick(30)

# === Wyświetlenie wprowadzenia ===
def show_introduction(screen):
    screen.fill((0, 0, 0))
    font = pygame.font.SysFont(None, 36)
    intro_text = [
        "Witamy w Dziennikach Bieszczadzkich!",
        "Jesteś wędrowcem przemierzającym spokojne wzgórza i doliny.",
        "Twoim celem jest odkrycie tajemnic tej krainy.",
        "Powodzenia!"
    ]
    for i, line in enumerate(intro_text):
        label = font.render(line, True, (255, 255, 0))
        screen.blit(label, (50, 200 + i * 40))
    pygame.display.flip()
    pygame.time.wait(5000)

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
    game_time['minute'] += elapsed_time // 20000  # 20000 ms = 20 sekund w realnym czasie = 10 minut w grze
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

        if time_accumulator >= 20000:  # Aktualizacja co 20 sekund
            update_game_time(game_time, time_accumulator)
            time_accumulator = 0

        screen.fill((0, 0, 0))
        draw_game_clock(screen, game_time)
        pygame.display.flip()

if __name__ == "__main__":
    screen = initialize_game()
    show_logo(screen)
    show_title(screen)
    selected_action = main_menu(screen)
    if selected_action == "new_game":
        show_introduction(screen)
        game_loop(screen)
