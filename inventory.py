import pygame

# Stałe (możesz dostosować pod własne potrzeby)
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
SLOT_SIZE = 48      # Rozmiar pojedynczego slotu (szerokość i wysokość w pikselach)
MAX_STACK = 99      # Maksymalna liczba przedmiotów w jednym slocie
BG_COLOR = (50, 50, 50)   # Kolor tła ekwipunku (zwykły szary)
FONT_COLOR = (255, 255, 255)

# Wskaźnik czy ekwipunek jest otwarty (na początek zamknięty)
inventory_open = False

# Przykładowa klasa na przedmioty (można rozbudować)
class Item:
    def __init__(self, name, icon=None, stackable=True):
        self.name = name
        self.icon = icon        # powierzchnia Pygame z grafiką itemu
        self.stackable = stackable

# Klasa slotu – przechowuje informację o przedmiocie i ilości
class InventorySlot:
    def __init__(self, x, y, width=SLOT_SIZE, height=SLOT_SIZE):
        self.rect = pygame.Rect(x, y, width, height)
        self.item = None    # obiekt klasy Item
        self.quantity = 0   # ile sztuk itemu w slocie

    def add_item(self, item, quantity=1):
        """
        Dodaje item do slotu. Sprawdza, czy slot jest pusty lub czy to ten sam typ itemu.
        Zwraca liczbę przedmiotów, których nie udało się dodać (jeśli przekroczyłoby limit stosu).
        """
        if self.item is None:
            # Slot pusty – przypisz przedmiot
            self.item = item
            self.quantity = min(quantity, MAX_STACK)
            return max(0, quantity - MAX_STACK)
        else:
            # Slot nie jest pusty, sprawdzamy czy to ten sam przedmiot i czy jest stackowalny
            if self.item.name == item.name and self.item.stackable:
                wolne_miejsce = MAX_STACK - self.quantity
                dodane = min(wolne_miejsce, quantity)
                self.quantity += dodane
                return quantity - dodane
            else:
                # Nie można dodać przedmiotu (inny typ itemu lub nie stackuje się)
                return quantity

    def remove_item(self, quantity=1):
        """
        Usuwa przedmioty ze slotu. Jeśli ilość w slocie spadnie do 0, slot resetuje się.
        Zwraca faktycznie usuniętą ilość.
        """
        if self.item is not None:
            usuniete = min(self.quantity, quantity)
            self.quantity -= usuniete
            if self.quantity <= 0:
                self.item = None
                self.quantity = 0
            return usuniete
        return 0

    def draw(self, surface, font):
        """
        Rysuje slot i znajdujący się w nim przedmiot (jeśli istnieje).
        """
        # obramowanie slotu
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 2)

        # jeśli slot nie jest pusty – wyświetl przedmiot i ilość
        if self.item:
            # przykładowe rysowanie ikony
            if self.item.icon:
                icon_rect = self.item.icon.get_rect(center=self.rect.center)
                surface.blit(self.item.icon, icon_rect)

            # wyświetlanie ilości
            if self.quantity > 1:
                text_surface = font.render(str(self.quantity), True, FONT_COLOR)
                surface.blit(text_surface, (self.rect.right - 15, self.rect.bottom - 20))

# Klasa całego ekwipunku
class Inventory:
    def __init__(self):
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 18)

        # Ustawiamy pozycję lewego-górnego rogu okna ekwipunku
        self.x = 100
        self.y = 50

        # 1. Portret + sloty na ubrania (czapka, kurtka, spodnie, buty, rękawice)
        #    Przyjmijmy, że chcemy je umieścić w lewym górnym rogu ekranu ekwipunku
        self.equipment_slots = []

        equipment_slot_names = ["Czapka", "Kurtka", "Spodnie", "Buty", "Rękawice"]
        for i in range(len(equipment_slot_names)):
            slot_x = self.x + 10
            slot_y = self.y + 80 + i * (SLOT_SIZE + 10)
            self.equipment_slots.append(InventorySlot(slot_x, slot_y))

        # 2. Sloty na dodatki (np. pierścienie, amulety) – domyślnie ukryte
        self.accessory_slots = []
        accessory_count = 4
        for i in range(accessory_count):
            slot_x = self.x + 10 + i * (SLOT_SIZE + 10)
            slot_y = self.y + 10
            self.accessory_slots.append(InventorySlot(slot_x, slot_y))

        # 3. Crafting 2x2 + slot wynikowy (po prawej)
        self.crafting_slots = []
        rows = 2
        cols = 2
        crafting_start_x = self.x + 300
        crafting_start_y = self.y + 50
        for row in range(rows):
            for col in range(cols):
                slot_x = crafting_start_x + col * (SLOT_SIZE + 5)
                slot_y = crafting_start_y + row * (SLOT_SIZE + 5)
                self.crafting_slots.append(InventorySlot(slot_x, slot_y))

        # Slot na wynik craftingu (po prawej)
        self.crafting_result_slot = InventorySlot(crafting_start_x + 2*(SLOT_SIZE + 5) + 30,
                                                  crafting_start_y + SLOT_SIZE // 2)

        # 4. Sloty główne (3 rzędy po 9 slotów)
        self.main_slots = []
        main_rows = 3
        main_cols = 9
        main_start_x = self.x + 50
        main_start_y = self.y + 200
        for row in range(main_rows):
            for col in range(main_cols):
                slot_x = main_start_x + col * (SLOT_SIZE + 5)
                slot_y = main_start_y + row * (SLOT_SIZE + 5)
                self.main_slots.append(InventorySlot(slot_x, slot_y))

        # 5. Pasek szybkiego wyboru (1 rząd z 9 slotów)
        self.hotbar_slots = []
        hotbar_y = main_start_y + main_rows * (SLOT_SIZE + 5) + 20
        for col in range(main_cols):
            slot_x = main_start_x + col * (SLOT_SIZE + 5)
            slot_y = hotbar_y
            self.hotbar_slots.append(InventorySlot(slot_x, slot_y))

        # Flaga do ukrywania/wyświetlania slotów dodatków
        self.accessory_unlocked = False

        # Wczytanie (lub stworzenie) grafiki portretu gracza (opcjonalnie)
        # self.player_portrait = pygame.image.load("player_portrait.png").convert_alpha()
        self.player_portrait = None  # placeholder, jeśli nie mamy pliku

    def toggle_accessory_slots(self, unlocked: bool):
        """Włącza/Wyłącza widoczność slotów na dodatki."""
        self.accessory_unlocked = unlocked

    def update(self):
        """
        Główna logika ekwipunku – tutaj można sprawdzać np.
        - czy gracz zdobył nową umiejętność i trzeba odblokować sloty,
        - czy w slotach craftingowych pojawił się przepis itd.
        """
        # Prosty przykład: jeśli odblokowano sloty, można tu w jakiś sposób
        # dodać logikę do ich obsługi
        pass

    def draw(self, surface):
        """
        Rysowanie całego okna ekwipunku.
        """
        # Tło "okna" – prostokąt
        inventory_width = 600
        inventory_height = 400
        pygame.draw.rect(surface, BG_COLOR, (self.x, self.y, inventory_width, inventory_height))

        # Rysujemy portret gracza (opcjonalnie)
        if self.player_portrait:
            portrait_rect = self.player_portrait.get_rect()
            portrait_rect.topleft = (self.x + 10, self.y + 10)
            surface.blit(self.player_portrait, portrait_rect)
        else:
            # Zamiast grafiki – placeholder
            pygame.draw.rect(surface, (100, 100, 100), (self.x+10, self.y+10, 64, 64))

        # Rysowanie slotów na ubrania
        for slot in self.equipment_slots:
            slot.draw(surface, self.font)

        # Rysowanie slotów na dodatki (jeśli odblokowane)
        if self.accessory_unlocked:
            for slot in self.accessory_slots:
                slot.draw(surface, self.font)

        # Rysowanie slotów craftingowych i slotu wynikowego
        for slot in self.crafting_slots:
            slot.draw(surface, self.font)
        self.crafting_result_slot.draw(surface, self.font)

        # Rysowanie slotów głównych
        for slot in self.main_slots:
            slot.draw(surface, self.font)

        # Rysowanie paska szybkiego wyboru
        for slot in self.hotbar_slots:
            slot.draw(surface, self.font)

        # Ewentualnie można wypisać podpisy czy tytuły sekcji:
        title_text = self.font.render("Ekwipunek", True, FONT_COLOR)
        surface.blit(title_text, (self.x + inventory_width // 2 - 30, self.y + 10))

    def handle_event(self, event):
        """
        Obsługa zdarzeń myszy/klawiatury na oknie ekwipunku.
        Można tu zaimplementować:
        - kliknięcia na slot,
        - przeciąganie przedmiotów (drag & drop),
        - sprawdzanie receptury craftingu.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()

            # Przykładowo sprawdź, czy kliknęliśmy któryś slot
            for slot in (self.equipment_slots + self.main_slots + self.hotbar_slots +
                         self.crafting_slots + [self.crafting_result_slot]):
                if slot.rect.collidepoint(mouse_pos):
                    # Tutaj można dodać logikę typu:
                    # "Jeśli mamy kursor z itemem, to odłóż go, w przeciwnym razie podnieś item ze slotu" itd.
                    pass

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    # Tworzymy instancję ekwipunku
    player_inventory = Inventory()

    # Główna pętla gry
    running = True
    global inventory_open

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Naciśnięcie klawisza
            if event.type == pygame.KEYDOWN:
                # Toggling ekwipunku przyciskiem E
                if event.key == pygame.K_e:
                    inventory_open = not inventory_open

            # Jeśli ekwipunek jest otwarty, przechwyć zdarzenia
            if inventory_open:
                player_inventory.handle_event(event)

        # Logika gry
        if inventory_open:
            # Pauzujemy grę – np. nie wykonujemy update logiki gry
            # Ale update ekwipunku może się dziać (np. sprawdzanie receptur)
            player_inventory.update()
        else:
            # Tu normalnie wykonujemy update gry
            pass

        # Rysowanie
        screen.fill((0, 0, 0))

        if inventory_open:
            # Rysuj ekwipunek
            player_inventory.draw(screen)
        else:
            # Rysuj np. scenę gry
            pass

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
