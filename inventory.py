# inventory.py
import pygame
import pyttsx3

# === Stałe ===
FONT_SIZE = 24
FONT = None  # Placeholder, zostanie zainicjalizowany po pygame.init()

TEXT_COLOR = (255, 255, 255)
BG_COLOR = (30, 30, 30)
HEADER_COLOR = (255, 255, 0)

# === Globalny stan ===
inventory_open = False
current_section = 0  # 0=ubior, 1=dodatki, 2=ekwipunek, 3=podreczne

# === Nazwy sekcji ===
SECTIONS = ["Ubiór", "Dodatki", "Ekwipunek", "Podręczne"]

# === Przykładowe dane ===
gear_slots = ["Czapka", "Kurtka", "Rękawice", "Spodnie", "Buty", "Plecak"]
gear_equipped = [None] * len(gear_slots)

accessory_slots_unlocked = False
accessory_slots = [None, None, None, None]  # 2 pierścienie, 2 amulety

backpack_items = [("Kilof", 12), ("Pochodnia", 34), ("Ziemniak", 3)]
quick_slots = [None] * 9

# === TTS ===
engine = pyttsx3.init()
def speak(text):
    engine.stop()
    engine.say(text)
    engine.runAndWait()

def draw_section_title(screen, text, x, y):
    label = FONT.render(text, True, HEADER_COLOR)
    screen.blit(label, (x, y))

def draw_list(screen, items, x, y_start):
    y = y_start
    for item in items:
        if item is None:
            label = FONT.render("(puste)", True, TEXT_COLOR)
        elif isinstance(item, tuple):
            name, count = item
            label = FONT.render(f"{name} ({count})", True, TEXT_COLOR)
        else:
            label = FONT.render(str(item), True, TEXT_COLOR)
        screen.blit(label, (x, y))
        y += FONT_SIZE + 4

def draw_inventory(screen):
    screen.fill(BG_COLOR)

    # Awatar gracza (lewy górny róg)
    pygame.draw.rect(screen, (100, 100, 255), pygame.Rect(20, 20, 64, 64))

    # Ubiór
    draw_section_title(screen, "Ubiór", 100, 20)
    draw_list(screen, [f"{slot}: {gear_equipped[i] or '(puste)'}" for i, slot in enumerate(gear_slots)], 100, 50)

    # Dodatki (tylko jeśli odblokowane)
    if accessory_slots_unlocked:
        draw_section_title(screen, "Dodatki", 100, 230)
        draw_list(screen, [f"Slot {i+1}: {item or '(puste)'}" for i, item in enumerate(accessory_slots)], 100, 260)

    # Ekwipunek
    draw_section_title(screen, "Ekwipunek", 400, 20)
    draw_list(screen, backpack_items, 400, 50)

    # Podręczne
    draw_section_title(screen, "Podręczne", 400, 230)
    draw_list(screen, [f"{i+1}: {item or '(puste)'}" for i, item in enumerate(quick_slots)], 400, 260)

    pygame.display.flip()

def handle_tab_navigation(shift_held):
    global current_section
    if shift_held:
        current_section = (current_section - 1) % len(SECTIONS)
    else:
        current_section = (current_section + 1) % len(SECTIONS)
    speak(SECTIONS[current_section])

def update():
    pass  # W przyszłości: sortowanie, interakcje, itp.

def draw(screen):
    draw_inventory(screen)


def init_font():
    global FONT
    FONT = pygame.font.SysFont(None, FONT_SIZE)
