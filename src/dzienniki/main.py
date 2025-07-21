import pygame
from dzienniki import settings
from dzienniki.utils.loader import load_image, load_sound
from dzienniki.ui.screens import show_logo, show_title, main_menu, show_introduction, topdown_game_loop
from dzienniki.systems.player import Player
from dzienniki.systems.map import Map

def main():
    pygame.init()
    screen = pygame.display.set_mode(
        (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
    )
    pygame.display.set_caption(settings.WINDOW_TITLE)

    # Ekrany startowe
    show_logo(screen)
    show_title(screen)

    # Menu główne
    choice = main_menu(screen)
    if choice != "nowa_gra":
        pygame.quit()
        return

    # wprowadzenie do gry
    show_introduction(screen)

    # uruchamiamy główną pętlę gry
    topdown_game_loop(screen)

    # Dodatkowy testowy loop do gry z animowaną postacią
    clock = pygame.time.Clock()
    running = True

    mapa = Map()
    player = Player(1, 1)

    while running:
        # delta_time (w sekundach)
        dt = clock.tick(settings.FPS) / 1000.0

        # obsługa zdarzeń
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_UP:
                    player.grid_y = max(0, player.grid_y - 1)
                    player.direction = "up"
                elif event.key == pygame.K_DOWN:
                    player.grid_y = min(2, player.grid_y + 1)
                    player.direction = "down"
                elif event.key == pygame.K_LEFT:
                    player.grid_x = max(0, player.grid_x - 1)
                    player.direction = "left"
                elif event.key == pygame.K_RIGHT:
                    player.grid_x = min(2, player.grid_x + 1)
                    player.direction = "right"

        # rysowanie tła
        screen.fill((0, 0, 0))

        # aktualizacja i rysowanie postaci
        player.pixel_x = player.grid_x * 32
        player.pixel_y = player.grid_y * 32
        player.update()
        player.draw(screen)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
