# Ten plik zawiera główną pętlę gry, inicjalizację pygame oraz menu główne.
# Odpowiada za uruchamianie gry i integrację wszystkich modułów.

import pygame
import sys
from player import Player
from map import Map
from npc import NPC
from quest import Quest

# Inicjalizacja pygame
def initialize_game():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))  # Rozdzielczość okna gry
    pygame.display.set_caption("Dzienniki Bieszczadzkie")
    return screen

def main_menu():
    print("=== Dzienniki Bieszczadzkie ===")
    print("1. Rozpocznij grę")
    print("2. Wyjdź")

    choice = input("Wybierz opcję: ")
    return choice

def game_loop(screen):
    player = Player()
    game_map = Map()
    npc_list = [NPC("Sołtys", {"hello": "Witaj w naszej wiosce!"}),
                NPC("Babcia", {"quest": "Przynieś mi zioła z lasu."})]
    quest_list = [Quest("Zioła Mocy", "Zbierz rzadkie zioła dla Babci.", ["Zioła"])]

    running = True
    clock = pygame.time.Clock()

    while running:
        screen.fill((255, 255, 255))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        print("\nMapa:")
        game_map.display_map(player.position)

        action = input("Wybierz akcję (move/talk/inventory/quit): ")

        if action == "move":
            direction = input("Wybierz kierunek (up/down/left/right): ")
            player.move(direction)
        elif action == "talk":
            npc_name = input("Podaj nazwę NPC: ")
            npc = next((n for n in npc_list if n.name == npc_name), None)
            if npc:
                print(npc.talk())
            else:
                print("Nie ma takiego NPC.")
        elif action == "inventory":
            print("Ekwipunek: ", player.inventory)
        elif action == "quit":
            running = False

        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    screen = initialize_game()
    choice = main_menu()

    if choice == "1":
        game_loop(screen)
    elif choice == "2":
        pygame.quit()
        sys.exit()

