import random
import pickle
import sys
from plants import plants, Seed


# Klasa wyposażenia gracza (Equipment)
class Equipment:
    def __init__(self):
        self.headgear = None  # Czapka, hełm
        self.chest = None  # Bluza, zbroja
        self.legs = None  # Spodnie
        self.feet = None  # Buty
        self.amulet1 = None  # Amulet 1
        self.amulet2 = None  # Amulet 2
        self.ring1 = None  # Pierścień 1
        self.ring2 = None  # Pierścień 2

    def equip_item(self, slot, item):
        """Zakłada przedmiot na wybrane miejsce (slot)"""
        if slot in self.__dict__:
            self.__dict__[slot] = item
            print(f"Założono {item.name} na {slot}.")
        else:
            print("Nieprawidłowy slot.")

    def remove_item(self, slot):
        """Zdejmuje przedmiot z wybranego miejsca (slot)"""
        if slot in self.__dict__:
            removed_item = self.__dict__[slot]
            self.__dict__[slot] = None
            print(f"Zdjęto {removed_item.name} z {slot}.")
            return removed_item
        else:
            print("Nieprawidłowy slot.")
            return None


from plants import plants  # Importuj rośliny z pliku


# Klasa Gracza
class Player:
    def __init__(self, name):
        self.name = name
        self.energy = 100
        self.health = 100
        self.inventory = Inventory()
        self.equipment = Equipment()
        self.strength = 1
        self.coins = 0
        self.skills = {
            'rolnictwo': Skill(),
            'zbieractwo': Skill(),
            'ryboustwo': Skill(),
            'walka': Skill(),
            'rzemiosło': Skill()
        }
        self.speed = 1
        self.luck = 1
        self.experience_points = 0

        # Dodaj początkowe rośliny (nasiona) do ekwipunku gracza
        for seed in plants[:2]:  # Pierwsze dwa nasiona jako startowe
            self.inventory.add_item(seed, quantity=3)  # Dodaj po 3 sztuki każdego nasiona



        self.inventory.add_item(Tool("Motyka"))
        self.inventory.add_item(Tool("Konewka", capacity=100))
        self.inventory.add_item(Tool("Siekiera"))
        self.inventory.add_item(Tool("Kilof"))
        self.inventory.add_item(Tool("Kosa"))
        self.inventory.add_item(Seed(seed_id=1, growth_days=10, yield_range=4, sell_price=15, quantity=5))
        self.inventory.add_item(Seed(seed_id=2, growth_days=15, yield_range=6, sell_price=20, quantity=5))


    def use_tool(self, tool_name, plot):
        tool = self.inventory.get_tool(tool_name)
        if not tool:
            print(f"Nie masz narzędzia: {tool_name}.")
            return
        if tool_name == "Motyka" and plot.state == "empty":
            plot.till()
            print("Pole zostało przygotowane pod zasiew.")
        elif tool_name == "Konewka":
            if plot.is_planted and not plot.is_watered:
                if tool.use_water(2):
                    plot.water()
                    print("Pole zostało podlane.")
                else:
                    print("Konewka jest pusta. Uzupełnij wodę.")
        else:
            print(f"Użycie narzędzia {tool_name} nie jest dostępne.")

    def add_to_inventory(self, item):
        """Dodaje zebrany plon do ekwipunku gracza"""
        if len(self.inventory.items) < self.inventory.max_capacity:
            self.inventory.add_item(item)
            print(f"Dodano {item.name} do ekwipunku.")
        else:
            print("Brak miejsca w ekwipunku. Nie można zebrać plonu.")






# Klasa Inventory
class Inventory:
    def __init__(self):
        self.items = []
        self.max_capacity = 10

    def add_item(self, item, quantity=1):
        """Dodaje przedmiot do ekwipunku, jeśli jest miejsce"""
        for existing_item in self.items:
            # Jeśli przedmiot to Seed i już istnieje w ekwipunku, zwiększ ilość
            if isinstance(existing_item, type(item)) and hasattr(existing_item,
                                                                 'seed_id') and existing_item.seed_id == getattr(item,
                                                                                                                 'seed_id',
                                                                                                                 None):
                existing_item.quantity += quantity
                print(f"Zwiększono ilość {item.name} w ekwipunku o {quantity}.")
                return

        # Jeśli nie istnieje, dodaj nowy przedmiot, o ile jest miejsce
        if len(self.items) < self.max_capacity:
            if hasattr(item, 'quantity'):  # Jeśli przedmiot ma atrybut quantity, ustaw ilość
                item.quantity = quantity
            self.items.append(item)
            print(f"Dodano {item.name} do ekwipunku ({quantity} szt.).")
        else:
            print("Brak miejsca w ekwipunku.")

    def get_tool(self, tool_name):
        """Zwraca narzędzie o podanej nazwie"""
        for item in self.items:
            if isinstance(item, Tool) and item.name == tool_name:
                return item
        print(f"Nie znaleziono narzędzia o nazwie {tool_name}.")
        return None

    def get_seed(self, seed_name):
        """Zwraca nasiono o podanej nazwie"""
        for item in self.items:
            if isinstance(item, Seed) and item.name == seed_name:
                return item
        print(f"Nie znaleziono nasiona o nazwie {seed_name}.")
        return None


# Klasa Tool
class Tool:
    def __init__(self, name, capacity=None):
        self.name = name
        self.capacity = capacity

    def use_water(self, amount):
        if self.capacity and self.capacity >= amount:
            self.capacity -= amount
            return True
        print("Za mało wody!")
        return False


# Klasa Plot
class Plot:
    def __init__(self):
        self.state = "empty"  # Możliwe stany: "empty", "tilled", "planted", "watered"
        self.days_to_harvest = 0
        self.seed = None

    def change_state(self, new_state):
        """Zmienia stan pola na podany"""
        self.state = new_state

    def till(self):
        if self.state == "empty":
            self.change_state("tilled")
            print("Pole zostało zaorane.")
        else:
            print("Pole nie może być zaorane w obecnym stanie.")

    def plant(self, seed):
        if self.state == "tilled":
            self.seed = seed
            self.days_to_harvest = seed.growth_days
            self.change_state("planted")
            print(f"Zasadzono {seed.name}.")
        else:
            print("Pole musi być najpierw zaorane.")

    def water(self):
        if self.state == "planted":
            self.change_state("watered")
            print("Pole zostało podlane.")
        else:
            print("Pole nie jest zasiane lub jest już podlane.")

    def harvest(self):
        if self.state == "watered" and self.days_to_harvest == 0:
            harvested_yield = {
                "name": self.seed.yield_name,
                "amount": self.seed.yield_range
            }
            self.reset()
            print(f"Zebrano plony: {harvested_yield['name']} ({harvested_yield['amount']} szt.).")
            return harvested_yield
        print("Roślina nie jest gotowa do zbioru.")
        return None

    def reset(self):
        """Resetuje pole do stanu początkowego"""
        self.state = "empty"
        self.seed = None
        self.days_to_harvest = 0


# Klasa Skill
class Skill:
    def __init__(self):
        self.level = 1
        self.experience = 0


# Klasa Game
class Game:
    def __init__(self):
        self.running = True
        self.player = Player("Gracz1")
        self.plots = [Plot() for _ in range(5)]
        self.day = 1

    def main_menu(self):
        print("\n--- Menu Główne ---")
        print("1. Zarządzaj polem uprawnym")
        print("2. Zarządzaj ekwipunkiem")
        print("3. Odpocznij (przejdź do następnego dnia)")
        print("4. Wyjdź z gry")
        choice = input("Wybierz akcję: ")
        if choice not in ["1", "2", "3", "4"]:
            print("Nieprawidłowy wybór. Spróbuj ponownie.")
            return self.main_menu()
        return choice

    def manage_plots(self):
        while True:  # Pętla umożliwia pozostanie w menu zarządzania polami
            print("\n--- Zarządzanie polami ---")
            for idx, plot in enumerate(self.plots, 1):
                status = (
                    f"Pole {idx}: "
                    f"{'Puste' if plot.state == 'empty' else ''}"
                    f"{'Zaorane' if plot.state == 'tilled' else ''}"
                    f"{'Zasiane' if plot.state == 'planted' else ''}"
                    f"{'Podlane' if plot.state == 'watered' else ''}"
                    f", Do zbioru: {plot.days_to_harvest} dni" if plot.days_to_harvest > 0 else ''
                )
                print(status)

            action = input("\n1. Przygotuj pola | 2. Posadź rośliny | 3. Zbierz plony | 4. Wróć: ")

            if action == "1":
                self.prepare_fields()
            elif action == "2":
                self.plant_seeds()
            elif action == "3":
                self.harvest_crops()
            elif action == "4":
                print("Powrót do menu głównego.")
                break  # Wyjście z pętli
            else:
                print("Nieprawidłowy wybór. Spróbuj ponownie.")

    def prepare_fields(self):
        while True:
            print("\nWybierz pola do zaorania (oddzielaj numery spacją). Dostępne pola:")
            available_fields = [idx + 1 for idx, plot in enumerate(self.plots) if plot.state == "empty"]

            if not available_fields:
                print("Brak dostępnych pól do zaorania.")
                return

            print(", ".join(map(str, available_fields)))
            choice = input("Wybierz pola (np. 1 2 3) lub wpisz 0, aby wrócić: ")

            if choice == "0":
                print("Anulowano zaorywanie.")
                return

            try:
                chosen_fields = list(map(int, choice.split()))
                for field_idx in chosen_fields:
                    if field_idx in available_fields:
                        # Sprawdź, czy gracz ma motykę
                        if not self.player.inventory.get_tool("Motyka"):
                            print("Nie masz motyki. Nie można zaorać pola.")
                            return

                        self.plots[field_idx - 1].till()
                        print(f"Pole {field_idx} zostało zaorane.")
                    else:
                        print(f"Pole {field_idx} nie jest dostępne do zaorania.")
            except ValueError:
                print("Nieprawidłowy wybór. Spróbuj ponownie.")

    def plant_seeds(self):
        while True:
            print("\nWybierz pola do zasiania (oddzielaj numery spacją). Dostępne pola:")
            available_fields = [idx + 1 for idx, plot in enumerate(self.plots) if plot.state == "tilled"]

            if not available_fields:
                print("Brak dostępnych pól do zasiania.")
                return

            print(", ".join(map(str, available_fields)))
            choice = input("Wybierz pola (np. 1 2 3) lub wpisz 0, aby wrócić: ")

            if choice == "0":
                print("Anulowano sianie.")
                return

            available_seeds = [seed for seed in self.player.inventory.items if isinstance(seed, Seed)]
            if not available_seeds:
                print("Brak nasion w ekwipunku.")
                return

            print("Dostępne nasiona:")
            for idx, seed in enumerate(available_seeds, 1):
                print(f"{idx}. {seed.name} (Czas wzrostu: {seed.growth_days} dni)")

            try:
                chosen_fields = list(map(int, choice.split()))
                seed_choice = int(input("Wybierz nasiono (np. 1): ")) - 1
                if seed_choice < 0 or seed_choice >= len(available_seeds):
                    print("Nieprawidłowy wybór nasiona.")
                    continue

                seed = available_seeds[seed_choice]
                for field_idx in chosen_fields:
                    if field_idx in available_fields:
                        self.plots[field_idx - 1].plant(seed)
                        print(f"Zasadzono {seed.name} na polu {field_idx}.")
                    else:
                        print(f"Pole {field_idx} nie jest dostępne do siania.")
            except ValueError:
                print("Nieprawidłowy wybór. Spróbuj ponownie.")

    def harvest_crops(self):
        while True:
            print("\nWybierz pola do zbioru (oddzielaj numery spacją). Dostępne pola:")
            available_fields = [idx + 1 for idx, plot in enumerate(self.plots) if
                                plot.state == "watered" and plot.days_to_harvest == 0]

            if not available_fields:
                print("Brak pól gotowych do zbioru.")
                return

            print(", ".join(map(str, available_fields)))
            choice = input("Wybierz pola (np. 1 2 3) lub wpisz 0, aby wrócić: ")

            if choice == "0":
                print("Anulowano zbiór.")
                return

            try:
                chosen_fields = list(map(int, choice.split()))
                for field_idx in chosen_fields:
                    if field_idx in available_fields:
                        harvested_yield = self.plots[field_idx - 1].harvest()
                        if harvested_yield:
                            self.player.add_to_inventory(Seed(
                                seed_id=int(harvested_yield["name"].split()[-1]),
                                growth_days=0,
                                yield_range=(harvested_yield["amount"], harvested_yield["amount"]),
                                sell_price=0,
                                quantity=1
                            ))
                            print(f"Zebrano {harvested_yield['name']} z pola {field_idx}.")
                    else:
                        print(f"Pole {field_idx} nie jest dostępne do zbioru.")
            except ValueError:
                print("Nieprawidłowy wybór. Spróbuj ponownie.")

    def run(self):
        print("Gra rozpoczęta!")
        while self.running:
            choice = self.main_menu()
            if choice == "1":
                self.manage_plots()
            elif choice == "2":
                print("\nEkwipunek gracza:")
                for item in self.player.inventory.items:
                    print(f"- {item.name}")
            elif choice == "3":
                print("\nOdpoczywasz i przechodzisz do następnego dnia...")
                self.day += 1
                for idx, plot in enumerate(self.plots, 1):
                    if plot.state == "watered" and plot.days_to_harvest > 0:
                        plot.days_to_harvest -= 1
                        plot.change_state("planted")  # Reset stanu do "planted" po podlewaniu
                        print(f"Pole {idx}: Roślina rośnie. Pozostało {plot.days_to_harvest} dni do zbioru.")
                    elif plot.state == "planted":
                        print(f"Pole {idx}: Wymaga podlania, aby roślina mogła rosnąć.")
                    elif plot.state == "watered" and plot.days_to_harvest == 0:
                        print(f"Pole {idx}: Roślina jest gotowa do zbioru!")
            elif choice == "4":
                print("\nZakończono grę.")
                self.running = False
            else:
                print("\nNieprawidłowy wybór. Spróbuj ponownie.")














if __name__ == "__main__":
    game = Game()
    game.run()

