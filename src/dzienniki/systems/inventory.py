import pygame
from dzienniki.audio import tts
from dzienniki.systems.item import Item

# === Stałe i zasoby ===
FONT_SIZE = 24
FONT = None

TEXT_COLOR = (255, 255, 255)
BG_COLOR = (30, 30, 30)
HEADER_COLOR = (255, 255, 0)

# Sekcje ekwipunku
SECTIONS = ["Ubiór", "Ekwipunek", "Podręczne"]

# Pojemność plecaka (może się zmieniać w grze)
BACKPACK_CAPACITY = 30

# Ekwipunek gracza
backpack_items = [
    Item(name="Kilof", count=1, item_type="tool"),
    Item(name="Pochodnia", count=3, item_type="tool"),
    Item(name="Ziemniak", count=5, item_type="food"),
]

# Sloty ubioru
equipment_slots = {
    "head": None,
    "torso": None,
    "hands": None,
    "legs": None,
    "feet": None,
    "back": None
}

# Podręczne przedmioty 1–9
quick_access_items = [None] * 9

# Stan ekwipunku
inventory_open = False
inventory_mode = "browse"  # browse, submenu, moving
sub_menu_open = False
sub_menu_options = ["Użyj", "Przenieś", "Upuść", "Właściwości"]
selected_sub_menu_option = 0
selected_section = 0  # 0 = Ubiór, 1 = Ekwipunek, 2 = Podręczne
selected_item_index = 0
moving_item = None
moving_item_source = None  # (sekcja, indeks)

def init_font():
    global FONT
    FONT = pygame.font.SysFont(None, FONT_SIZE)

def get_section_items(section_idx):
    if section_idx == 0:  # Ubiór
        result = []
        for slot, item in equipment_slots.items():
            if item:
                result.append(f"Slot {slot}: {item.get_display_name()}, założone")
            else:
                result.append(f"Slot {slot}: (puste)")
        return result
    elif section_idx == 1:  # Ekwipunek
        return [item.get_display_name() for item in backpack_items] + \
               ["(puste miejsce)"] * (BACKPACK_CAPACITY - len(backpack_items))
    elif section_idx == 2:  # Podręczne
        result = []
        for i in range(9):
            item = quick_access_items[i]
            if item:
                result.append(f"{i+1}: {item.get_display_name()}")
            else:
                result.append(f"{i+1}: (puste)")
        return result
    else:
        return []

def speak_current_item():
    items = get_section_items(selected_section)
    if not items:
        tts.speak("Brak elementów.")
        return
    if selected_item_index < 0 or selected_item_index >= len(items):
        tts.speak("Poza zakresem listy.")
        return

    current = selected_item_index + 1
    total = len(items)
    text = items[selected_item_index]
    tts.speak(f"{text}. Pozycja {current} z {total}.")

def handle_inventory_navigation(event):
    global selected_section, selected_item_index
    global inventory_mode, sub_menu_open, selected_sub_menu_option
    global moving_item, moving_item_source

    items = get_section_items(selected_section)
    max_index = len(items) - 1

    if event.type == pygame.KEYDOWN:
        if inventory_mode == "browse":
            if event.key == pygame.K_TAB:
                selected_section = (selected_section + 1) % len(SECTIONS)
                selected_item_index = 0
                tts.speak(SECTIONS[selected_section])
                speak_current_item()
            elif event.key == pygame.K_UP:
                if max_index >= 0:
                    selected_item_index = (selected_item_index - 1) % (max_index + 1)
                    speak_current_item()
            elif event.key == pygame.K_DOWN:
                if max_index >= 0:
                    selected_item_index = (selected_item_index + 1) % (max_index + 1)
                    speak_current_item()
            elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                if items and 0 <= selected_item_index < len(items):
                    inventory_mode = "submenu"
                    sub_menu_open = True
                    selected_sub_menu_option = 0
                    tts.speak("Opcje: Użyj, Przenieś, Upuść, Właściwości. Strzałki góra dół, Enter zatwierdza.")

        elif inventory_mode == "submenu":
            if event.key == pygame.K_UP:
                selected_sub_menu_option = (selected_sub_menu_option - 1) % len(sub_menu_options)
                tts.speak(sub_menu_options[selected_sub_menu_option])
            elif event.key == pygame.K_DOWN:
                selected_sub_menu_option = (selected_sub_menu_option + 1) % len(sub_menu_options)
                tts.speak(sub_menu_options[selected_sub_menu_option])
            elif event.key == pygame.K_ESCAPE:
                inventory_mode = "browse"
                sub_menu_open = False
                tts.speak("Anulowano.")
            elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                chosen_option = sub_menu_options[selected_sub_menu_option]
                if not items or selected_item_index >= len(items):
                    tts.speak("Nieprawidłowy wybór.")
                    return

                if chosen_option == "Użyj":
                    tts.speak(f"Używasz: {items[selected_item_index]}")
                    inventory_mode = "browse"
                    sub_menu_open = False

                elif chosen_option == "Przenieś":
                    moving_item = items[selected_item_index]
                    moving_item_source = (selected_section, selected_item_index)
                    inventory_mode = "moving"
                    sub_menu_open = False
                    tts.speak(f"Przenoszę {moving_item}. Wybierz miejsce docelowe i naciśnij Enter.")

                elif chosen_option == "Upuść":
                    import world
                    player_x, player_y = 100, 100
                    world.drop_item("Ziemniak", 1, player_x, player_y, "right")
                    tts.speak(f"Upuszczono: {items[selected_item_index]}")
                    inventory_mode = "browse"
                    sub_menu_open = False

                elif chosen_option == "Właściwości":
                    tts.speak(f"Właściwości: {items[selected_item_index]}")
                    inventory_mode = "browse"
                    sub_menu_open = False

def update():
    pass

def draw_inventory(screen):
    screen.fill(BG_COLOR)
    title = "Ekwipunek"
    label = FONT.render(title, True, HEADER_COLOR)
    screen.blit(label, (50, 20))

    column_width = 400
    margin_top = 80

    for section_idx in range(len(SECTIONS)):
        x = 50 + section_idx * column_width
        y = margin_top
        section_label = FONT.render(SECTIONS[section_idx], True, HEADER_COLOR)
        screen.blit(section_label, (x, y))
        y += FONT_SIZE + 10

        items = get_section_items(section_idx)
        for i, item in enumerate(items):
            color = TEXT_COLOR
            if section_idx == selected_section and i == selected_item_index:
                color = (255, 255, 255)
            label = FONT.render(item, True, color)
            screen.blit(label, (x + 20, y))

            if section_idx == selected_section and i == selected_item_index:
                rect = label.get_rect(topleft=(x + 20, y))
                pygame.draw.rect(screen, (255, 255, 255), rect.inflate(6, 6), 2)

            y += (FONT_SIZE + 6)

    pygame.display.flip()

def draw(screen):
    draw_inventory(screen)
