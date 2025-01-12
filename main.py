# === FILE: main.py ===
# Ten plik zawiera główną pętlę gry, inicjalizację pygame oraz menu główne.
# Odpowiada za uruchamianie gry i integrację wszystkich modułów.
#
# Wymagane pliki:
# - player.py (zawiera klasę Player)
# - map.py (zawiera klasę Map)
# - npc.py (zawiera klasę NPC)
# - quest.py (zawiera klasę Quest)
# - building.py (zawiera klasę Building)
# - tools.py (zawiera klasy Tool i Weapon)
# - clothing.py (zawiera klasę Clothing)
# - animals.py (zawiera klasę Animal)
# - plants.py (zawiera klasy Plant, Crop, Tree, Bush, Seedling)
# - shop.py (zawiera klasę Shop)
#

import pygame
import sys
import json
from player import Player
from map import Map, Tile
from npc import NPC
from quest import Quest
from building import Building
from tools import Tool, Weapon
from clothing import Clothing
from animals import Animal
from plants import Plant, Crop, Tree, Bush, Seedling
from shop import Shop

# Inicjalizacja pygame
def initialize_game():
    def show_logo():
        print("=== LOGO ===")
        pygame.time.wait(2000)  # Wyświetlenie logo przez 2 sekundy

    def show_title():
        print("=== Dzienniki Bieszczadzkie ===")
        pygame.time.wait(2000)  # Wyświetlenie tytułu przez 2 sekundy

    pygame.init()
    screen = pygame.display.set_mode((800, 600))  # Rozdzielczość okna gry
    pygame.display.set_caption("Dzienniki Bieszczadzkie")
    show_logo()
    show_title()
    return screen


def save_game(player, filename=None):
    """Zapisuje stan gry do pliku."""
    save_data = {
        "name": player.name,
        "health": player.health,
        "stamina": player.stamina,
        "inventory": player.inventory,
        "position": player.position
    }
    if filename is None:
        from datetime import datetime
        filename = datetime.now().strftime('%Y.%m.%d.%H:%M:%S.json')
    with open(filename, "w") as save_file:
        json.dump(save_data, save_file)
    print("Gra została zapisana.")


def load_game(filename=None):
    """Wczytuje stan gry z pliku."""
    try:
        if filename is None:
            filename = "save_game.json"
        with open(filename, "r") as save_file:
            save_data = json.load(save_file)
            player = Player()
            player.name = save_data["name"]
            player.health = save_data["health"]
            player.stamina = save_data["stamina"]
            player.inventory = save_data["inventory"]
            player.position = save_data["position"]
            print("Gra została wczytana.")
            return player
    except FileNotFoundError:
        print("Brak zapisanego stanu gry. Rozpocznij nową grę.")
        return None


def main_menu():
    while True:
        print("=== Dzienniki Bieszczadzkie ===")
        print("1. Gra")
        print("2. Opcje")
        print("3. Wyjdź")

        choice = input("Wybierz opcję: ")

        if choice == "1":
            return "game"
        elif choice == "2":
            print("Opcje: (funkcja w przygotowaniu)")
        elif choice == "3":
            pygame.quit()
            sys.exit()
        else:
            print("Nieprawidłowa opcja, spróbuj ponownie.")


def game_menu():
    while True:
        print("=== Menu Gry ===")
        print("1. Nowa gra")
        print("2. Wczytaj grę")
        print("3. Wróć")

        choice = input("Wybierz opcję: ")

        if choice == "1":
            return "new_game"
        elif choice == "2":
            return "load_game"
        elif choice == "3":
            return "back"
        else:
            print("Nieprawidłowa opcja, spróbuj ponownie.")


def game_loop(screen, player):
    def initialize_starting_map():
        starting_map = Map(10, 20)  # Wymiary mapy 10x20 kratek

        # Dodajemy ściany chaty
        for x in range(10):
            starting_map.set_tile(x, 0, Tile("wall"))  # Ściana północna
            starting_map.set_tile(x, 19, Tile("wall"))  # Ściana południowa
        for y in range(1, 19):
            starting_map.set_tile(0, y, Tile("wall"))  # Ściana zachodnia
            starting_map.set_tile(9, y, Tile("wall"))  # Ściana wschodnia

        # Dodajemy drzwi na południowej ścianie
        starting_map.set_tile(5, 19, Tile("door"))

        # Dodajemy gracza na środku chaty
        starting_map.set_tile(5, 10, Tile("player"))

        return starting_map
    def use_bed():
        print("Gracz korzysta z łóżka. Autozapis gry...")
        save_game(player)
        print("Autozapis zakończony.")

    game_map = Map()
    npc_list = [NPC("Sołtys", {"hello": "Witaj w naszej wiosce!"}),
                NPC("Babcia", {"quest": "Przynieś mi zioła z lasu."})]
    quest_list = [Quest("Zioła Mocy", "Zbierz rzadkie zioła dla Babci.", ["Zioła"])]

    running = True
    clock = pygame.time.Clock()

    while running:
        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # Dodajemy czytanie klawiszy
                if event.key == pygame.K_UP:
                    print("Naciśnięto strzałkę w górę")
                elif event.key == pygame.K_DOWN:
                    print("Naciśnięto strzałkę w dół")
                elif event.key == pygame.K_LEFT:
                    print("Naciśnięto strzałkę w lewo")
                elif event.key == pygame.K_RIGHT:
                    print("Naciśnięto strzałkę w prawo")

        print("\nMapa:")
        game_map.display_map(player.position)

        action = input("Wybierz akcję (move/talk/inventory/save/quit): ")

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
        elif action == "save":
            save_game(player, filename="save_game.json")
        elif action == "quit":
            running = False

        pygame.display.flip()
        # Dodajemy kolor żółty dla elementów
        pygame.draw.rect(screen, (255, 255, 0), pygame.Rect(50, 50, 700, 500), 1)
        clock.tick(30)


if __name__ == "__main__":
    screen = initialize_game()
    while True:
        menu_choice = main_menu()

        if menu_choice == "game":
            game_choice = game_menu()

            if game_choice == "new_game":
                def show_story():
                    print("=== Historia Gracza ===")
                    print("Jesteś wędrowcem przemierzającym Bieszczady...")
                    print("Twoim celem jest odkrycie tajemnic tej krainy.")
                    pygame.time.wait(5000)  # Wyświetlanie historii przez 5 sekund

                show_story()
                player = Player()
                game_loop(screen, player)
            elif game_choice == "load_game":
                player = load_game(filename="save_game.json")
                if player:
                    game_loop(screen, player)
            elif game_choice == "back":
                continue
