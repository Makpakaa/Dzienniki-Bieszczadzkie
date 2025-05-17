import pygame
from dzienniki import settings
from dzienniki.utils.loader import load_image, load_sound
from dzienniki.ui.screens import show_logo, show_title, main_menu, show_introduction, topdown_game_loop

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

    clock = pygame.time.Clock()
    running = True
    while running:
        # delta_time (w sekundach)
        dt = clock.tick(settings.FPS) / 1000.0

        # obsługa zdarzeń
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        # rysowanie tła
        screen.fill((0, 0, 0))
        # TODO: tutaj wstawi się właściwa logika gry

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
