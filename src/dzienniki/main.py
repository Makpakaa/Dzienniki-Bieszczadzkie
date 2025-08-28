# src/dzienniki/main.py

import pygame
from dzienniki import settings
from dzienniki.ui.screens import show_logo, show_title, main_menu, show_introduction
from dzienniki.game import topdown_game_loop

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

    # Wprowadzenie
    show_introduction(screen)

    # Główna pętla gry
    topdown_game_loop(screen)

    pygame.quit()

if __name__ == "__main__":
    main()
