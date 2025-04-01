# inventory.py
import pygame
import pyttsx3

# === Stałe i zasoby ===
FONT_SIZE = 24
FONT = None

TEXT_COLOR = (255, 255, 255)
BG_COLOR = (30, 30, 30)
HEADER_COLOR = (255, 255, 0)

# Sekcje ekwipunku
SECTIONS = ["Ubiór", "Dodatki", "Ekwipunek", "Podręczne"]

# === Przykładowe dane ekwipunku ===
gear_slots = ["Czapka", "Kurtka", "Rękawice", "Spodnie", "Buty", "Plecak"]
gear_equipped = [None] * len(gear_slots)

accessory_slots_unlocked = False
accessory_slots = [None, None, None, None]  # np. 2 pierścienie, 2 amulety

backpack_items = [("Kilof", 12), ("Pochodnia", 34), ("Ziemniak", 3)]
quick_slots = [None] * 9

# === Stan nawigacji w ekwipunku ===
inventory_open = False
selected_section = 0
selected_item_index = 0

# === Inicjalizacja TTS ===
engine = pyttsx3.init()

def speak(text):
    """
    Zatrzymuje aktualną wypowiedź TTS (jeśli trwa) i odczytuje podany tekst.
    """
    engine.stop()
    engine.say(text)
    engine.runAndWait()

def init_font():
    """
    Inicjalizuje czcionkę po wywołaniu pygame.init().
    """
    global FONT
    FONT = pygame.font.SysFont(None, FONT_SIZE)

def get_section_items(section_idx):
    """
    Zwraca listę elementów w formie tekstu dla danej sekcji ekwipunku.
    """
    section_name = SECTIONS[section_idx]
    if section_name == "Ubiór":
        # Lista postaci "Czapka: (puste)", "Kurtka: (puste)", ...
        return [f"{slot}: {gear_equipped[i] or '(puste)'}"
                for i, slot in enumerate(gear_slots)]
    elif section_name == "Dodatki":
        if accessory_slots_unlocked:
            return [f"Slot {i+1}: {item or '(puste)'}"
                    for i, item in enumerate(accessory_slots)]
        else:
            return ["Dodatki zablokowane"]
    elif section_name == "Ekwipunek":
        # Z krotek ("Kilof", 12) tworzymy "Kilof (12)"
        return [f"{name} ({count})" for (name, count) in backpack_items]
    elif section_name == "Podręczne":
        return [f"{i+1}: {slot or '(puste)'}"
                for i, slot in enumerate(quick_slots)]
    else:
        return []

def speak_current_item():
    """
    Odczytuje aktualnie wybrany element w danej sekcji (np. "Czapka: (puste)").
    """
    items = get_section_items(selected_section)
    if not items:
        speak("Brak elementów w tej sekcji.")
        return
    if selected_item_index < 0 or selected_item_index >= len(items):
        speak("Poza zakresem listy.")
        return

    speak(items[selected_item_index])

def handle_inventory_navigation(event):
    """
    Obsługa klawiszy, gdy ekwipunek jest otwarty:
      - Strzałka góra/dół: nawigacja po elementach aktualnej sekcji.
      - Strzałka lewo/prawo: przełączanie się między sekcjami.
      - Enter: prosta akcja (np. 'Używam').
      - Zamknięcie ekwipunku obsługujesz w main.py (np. klawisz E lub ESC).
    """
    global selected_section, selected_item_index

    items = get_section_items(selected_section)
    max_index = len(items) - 1

    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_UP:
            if max_index >= 0:
                selected_item_index = (selected_item_index - 1) % (max_index + 1)
                speak_current_item()
        elif event.key == pygame.K_DOWN:
            if max_index >= 0:
                selected_item_index = (selected_item_index + 1) % (max_index + 1)
                speak_current_item()
        elif event.key == pygame.K_LEFT:
            selected_section = (selected_section - 1) % len(SECTIONS)
            selected_item_index = 0
            speak(SECTIONS[selected_section])
            speak_current_item()
        elif event.key == pygame.K_RIGHT:
            selected_section = (selected_section + 1) % len(SECTIONS)
            selected_item_index = 0
            speak(SECTIONS[selected_section])
            speak_current_item()
        elif event.key == pygame.K_RETURN:
            if items and 0 <= selected_item_index < len(items):
                speak(f"Używam: {items[selected_item_index]}")
            else:
                speak("Brak elementu do użycia.")

def update():
    """
    Tutaj można umieścić ewentualną logikę związaną z ekwipunkiem:
    sortowanie, sprawdzanie stanu gracza, itp.
    Na razie puste.
    """
    pass

def draw_inventory(screen):
    screen.fill(BG_COLOR)

    # Tytuł ogólny
    title_text = "Ekwipunek (wszystkie sekcje)"
    title_label = FONT.render(title_text, True, HEADER_COLOR)
    screen.blit(title_label, (50, 20))

    # Szerokość każdej kolumny
    column_width = 300
    # Górny margines tekstu
    top_margin = 80

    for section_idx, section_name in enumerate(SECTIONS):
        # Obliczamy X kolumny: przesunięcie co column_width od lewej
        x = 50 + section_idx * column_width
        y = top_margin

        # Rysujemy nazwę sekcji
        name_label = FONT.render(section_name, True, HEADER_COLOR)
        screen.blit(name_label, (x, y))
        y += FONT_SIZE + 6

        # Pobieramy listę przedmiotów z danej sekcji
        items = get_section_items(section_idx)

        # Rysujemy każdy przedmiot
        for i, item_text in enumerate(items):
            # Jeśli ta sekcja i indeks pasują do naszego wybranego elementu,
            # to wyróżnijmy go kolorem białym:
            if section_idx == selected_section and i == selected_item_index:
                color = (255, 255, 255)
            else:
                color = TEXT_COLOR

            label = FONT.render(item_text, True, color)
            screen.blit(label, (x + 20, y))
            y += (FONT_SIZE + 4)

    pygame.display.flip()


def draw(screen):
    """
    Funkcja wywoływana z głównej pętli gry do narysowania ekwipunku.
    """
    draw_inventory(screen)
