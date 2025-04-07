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

BACKPACK_CAPACITY = 10
backpack_items = [("Kilof", 12), ("Pochodnia", 34), ("Ziemniak", 3)]
quick_slots = [None] * 9

# === Stan trybu ekwipunku ===
inventory_open = False
inventory_mode = "browse"  # browse, submenu, moving
sub_menu_open = False
sub_menu_options = ["Przenieś", "Upuść"]
selected_sub_menu_option = 0
selected_section = 0
selected_item_index = 0
moving_item = None
moving_item_source = None  # (sekcja, indeks)

# === Inicjalizacja TTS ===
engine = pyttsx3.init()

def speak(text):
    engine.stop()
    engine.say(text)
    engine.runAndWait()

def init_font():
    global FONT
    FONT = pygame.font.SysFont(None, FONT_SIZE)

def get_section_items(section_idx):
    section_name = SECTIONS[section_idx]
    if section_name == "Ubiór":
        return [f"{slot}: {gear_equipped[i] or '(puste)'}" for i, slot in enumerate(gear_slots)]
    elif section_name == "Dodatki":
        if accessory_slots_unlocked:
            return [f"Slot {i+1}: {item or '(puste)'}" for i, item in enumerate(accessory_slots)]
        else:
            return ["Dodatki zablokowane"]
    elif section_name == "Ekwipunek":
        items_in_backpack = [f"{name} ({count})" for (name, count) in backpack_items]
        while len(items_in_backpack) < BACKPACK_CAPACITY:
            items_in_backpack.append("(puste miejsce)")
        return items_in_backpack
    elif section_name == "Podręczne":
        return [f"{i+1}: {slot or '(puste)'}" for i, slot in enumerate(quick_slots)]
    else:
        return []

def speak_current_item():
    items = get_section_items(selected_section)
    if not items:
        speak("Brak elementów w tej sekcji.")
        return
    if selected_item_index < 0 or selected_item_index >= len(items):
        speak("Poza zakresem listy.")
        return
    speak(items[selected_item_index])

def handle_inventory_navigation(event):
    global selected_section, selected_item_index
    global inventory_mode, sub_menu_open, selected_sub_menu_option
    global moving_item, moving_item_source

    items = get_section_items(selected_section)
    max_index = len(items) - 1

    if event.type == pygame.KEYDOWN:
        if inventory_mode == "browse":
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
                    inventory_mode = "submenu"
                    sub_menu_open = True
                    selected_sub_menu_option = 0
                    speak("Opcje: Przenieś lub Upuść. Użyj strzałek góra i dół, Enter aby zatwierdzić.")

        elif inventory_mode == "submenu":
            if event.key == pygame.K_UP:
                selected_sub_menu_option = (selected_sub_menu_option - 1) % len(sub_menu_options)
                speak(sub_menu_options[selected_sub_menu_option])
            elif event.key == pygame.K_DOWN:
                selected_sub_menu_option = (selected_sub_menu_option + 1) % len(sub_menu_options)
                speak(sub_menu_options[selected_sub_menu_option])
            elif event.key == pygame.K_ESCAPE:
                inventory_mode = "browse"
                sub_menu_open = False
                speak("Anulowano.")
            elif event.key == pygame.K_RETURN:
                chosen_option = sub_menu_options[selected_sub_menu_option]
                if not items or selected_item_index >= len(items):
                    speak("Nieprawidłowy wybór.")
                    return

                if chosen_option == "Przenieś":
                    moving_item = items[selected_item_index]
                    moving_item_source = (selected_section, selected_item_index)
                    inventory_mode = "moving"
                    sub_menu_open = False
                    speak(f"Przenoszę {moving_item}. Wybierz miejsce docelowe i naciśnij Enter.")
                elif chosen_option == "Upuść":
                    speak(f"Upuszczono: {items[selected_item_index]}")
                    inventory_mode = "browse"
                    sub_menu_open = False

def update():
    pass

def draw_inventory(screen):
    screen.fill(BG_COLOR)

    title_text = "Ekwipunek (wszystkie sekcje)"
    title_label = FONT.render(title_text, True, HEADER_COLOR)
    screen.blit(title_label, (50, 20))

    column_width = 300
    top_margin = 80

    for section_idx, section_name in enumerate(SECTIONS):
        x = 50 + section_idx * column_width
        y = top_margin

        name_label = FONT.render(section_name, True, HEADER_COLOR)
        screen.blit(name_label, (x, y))
        y += FONT_SIZE + 6

        items = get_section_items(section_idx)

        for i, item_text in enumerate(items):
            if section_idx == selected_section and i == selected_item_index:
                color = (255, 255, 255)
            else:
                color = TEXT_COLOR

            label = FONT.render(item_text, True, color)
            screen.blit(label, (x + 20, y))

            if section_idx == selected_section and i == selected_item_index:
                rect = label.get_rect(topleft=(x + 20, y))
                pygame.draw.rect(screen, (255, 255, 255), rect.inflate(6, 6), 2)

            y += (FONT_SIZE + 4)

    pygame.display.flip()

def draw(screen):
    draw_inventory(screen)
