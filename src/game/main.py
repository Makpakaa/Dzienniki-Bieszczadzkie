import pygame
import sys
import threading
from game import tts
from game import inventory
from game import container
from game import shop
from game import world
from game import map
from game import quest
from game import npc
from game import plants
from game import animals
from game import building
from game import clothing
from game import player
from game import tools

TILE_SIZE = 16
MAP_SIZE = 200
MOVE_COOLDOWN = 300

def initialize_game():
    pygame.init()
    inventory.init_font()
    info = pygame.display.Info()
    screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
    pygame.display.set_caption("Dzienniki Bieszczadzkie - Widok 2D")
    return screen

def show_logo(screen):
    screen.fill((0, 0, 0))
    font = pygame.font.SysFont(None, 64)
    label = font.render("LOGO GRY", True, (255, 255, 0))
    rect = label.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    screen.blit(label, rect)
    pygame.display.flip()

    tts.speak("Wyświetlam logo gry. Naciśnij dowolny klawisz, aby przejść dalej.")

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
                waiting = False
        if current_time - start_time >= wait_duration:
            waiting = False

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

    tts.speak("Dzienniki Bieszczadzkie. Naciśnij dowolny klawisz, aby przejść dalej.")

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
                waiting = False
        if current_time - start_time >= wait_duration:
            waiting = False

def main_menu(screen):
    running = True
    clock = pygame.time.Clock()
    selected_option = 0
    options = ["Nowa Gra", "Załaduj Grę", "Wyjście"]

    tts.speak("Menu główne. Użyj strzałek góra i dół, by wybrać opcję, Enter aby zatwierdzić.")

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(options)
                    tts.speak(options[selected_option])
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(options)
                    tts.speak(options[selected_option])
                elif event.key == pygame.K_RETURN:
                    tts.speak(f"Wybrano opcję: {options[selected_option]}")
                    pygame.time.delay(300)

                    if selected_option == 0:
                        return "new_game"
                    elif selected_option == 1:
                        tts.speak("Załaduj Grę - opcja w przygotowaniu.")
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
                pygame.draw.rect(
                    screen, (255, 255, 255),
                    pygame.Rect(295, 195 + i * 60, 310, 60),
                    2
                )

        pygame.display.flip()
        clock.tick(30)

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

    tts.speak(tts_text + ". Naciśnij dowolny klawisz, aby przejść dalej.")

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
                waiting = False
        if current_time - start_time >= wait_duration:
            waiting = False

def clamp(value, min_val, max_val):
    return max(min_val, min(value, max_val))

def draw_2d_grid(screen, offset_x, offset_y, color=(255, 255, 0)):
    for row in range(MAP_SIZE + 1):
        y = offset_y + row * TILE_SIZE
        start_x = offset_x
        end_x = offset_x + MAP_SIZE * TILE_SIZE
        pygame.draw.line(screen, color, (start_x, y), (end_x, y), 1)

    for col in range(MAP_SIZE + 1):
        x = offset_x + col * TILE_SIZE
        start_y = offset_y
        end_y = offset_y + MAP_SIZE * TILE_SIZE
        pygame.draw.line(screen, color, (x, start_y), (x, end_y), 1)

def topdown_game_loop(screen):
    clock = pygame.time.Clock()
    chest = container.Container("Skrzynia", capacity=10)
    chest.add_item("Złoty pierścień", 1)
    chest.add_item("Kurtka", 1)

    village_shop = shop.Shop("Sklep wiejski")
    village_shop.add_item("Kilof", 1, 150)
    village_shop.add_item("Ziemniak", 5, 5)
    village_shop.add_item("Chleb", 2, 10)

    player_col = 100
    player_row = 100
    screen_width, screen_height = screen.get_size()
    offset_x = screen_width // 2 - (player_col * TILE_SIZE)
    offset_y = screen_height // 2 - (player_row * TILE_SIZE)

    next_move_time = 0
    keys_held = {
        pygame.K_UP: False,
        pygame.K_DOWN: False,
        pygame.K_LEFT: False,
        pygame.K_RIGHT: False
    }

    inventory.inventory_open = False

    npc_col = 98
    npc_row = 100
    chest_col = 102
    chest_row = 100

    running = True
    while running:
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if inventory.inventory_open:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    inventory.inventory_open = False
                    tts.speak("Zamykam ekwipunek")
                else:
                    inventory.handle_inventory_navigation(event)
            continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    if abs(player_col - npc_col) <= 1 and player_row == npc_row:
                        inventory.container_items = village_shop.items_for_sale
                        inventory.inventory_open = True
                        inventory.selected_section = 0
                        inventory.selected_item_index = 0
                        tts.speak("Rozpoczynam handel.")
                    elif abs(player_col - chest_col) <= 1 and player_row == chest_row:
                        inventory.container_items = chest.items
                        inventory.inventory_open = True
                        inventory.selected_section = 0
                        inventory.selected_item_index = 0
                        tts.speak("Otwieram skrzynię.")
                    else:
                        tts.speak("Tutaj nic nie ma.")

                elif event.key == pygame.K_e:
                    inventory.inventory_open = not inventory.inventory_open
                    if inventory.inventory_open:
                        tts.speak("Otwieram ekwipunek")
                    else:
                        tts.speak("Zamykam ekwipunek")

                if event.key in keys_held:
                    keys_held[event.key] = True

            if event.type == pygame.KEYUP:
                if event.key in keys_held:
                    keys_held[event.key] = False

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

            player_col = clamp(player_col, 0, MAP_SIZE - 1)
            player_row = clamp(player_row, 0, MAP_SIZE - 1)

            if (player_col, player_row) != (original_col, original_row):
                tts.speak(f"Przechodzę na {player_col}, {player_row}")
                next_move_time = current_time + MOVE_COOLDOWN

        offset_x = screen_width // 2 - (player_col * TILE_SIZE)
        offset_y = screen_height // 2 - (player_row * TILE_SIZE)

        screen.fill((0, 0, 0))

        if inventory.inventory_open:
            inventory.update()
            inventory.draw(screen)
        else:
            draw_2d_grid(screen, offset_x, offset_y, (255, 255, 0))

            npc_x = offset_x + npc_col * TILE_SIZE
            npc_y = offset_y + npc_row * TILE_SIZE
            pygame.draw.rect(screen, (0, 0, 255), (npc_x, npc_y, TILE_SIZE, TILE_SIZE))

            chest_x = offset_x + chest_col * TILE_SIZE
            chest_y = offset_y + chest_row * TILE_SIZE
            pygame.draw.rect(screen, (139, 69, 19), (chest_x, chest_y, TILE_SIZE, TILE_SIZE))

            for item in world.dropped_items:
                item_x = offset_x + item.x * TILE_SIZE
                item_y = offset_y + item.y * TILE_SIZE
                pygame.draw.rect(screen, (0, 255, 0), (item_x, item_y, TILE_SIZE, TILE_SIZE))

            gx = offset_x + player_col * TILE_SIZE
            gy = offset_y + player_row * TILE_SIZE
            pygame.draw.rect(screen, (255, 255, 255), (gx, gy, TILE_SIZE, TILE_SIZE))

        pygame.display.flip()
        clock.tick(60)

def main():
    screen = initialize_game()
    show_logo(screen)
    show_title(screen)

    action = main_menu(screen)
    if action == "new_game":
        show_introduction(screen)
        topdown_game_loop(screen)

    tts.manager.stop()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
