import pygame
from dzienniki.audio import tts
from dzienniki.audio.tts_utils import speak_ui  # krótkie, przerywane komunikaty UI
from dzienniki.systems.item import Item

FONT_SIZE = 24
FONT = None

TEXT_COLOR = (255, 255, 255)
BG_COLOR = (30, 30, 30)
HEADER_COLOR = (255, 255, 0)

SECTIONS = ["Ubiór", "Ekwipunek", "Podręczne"]
BACKPACK_CAPACITY = 30

backpack_items = [
    Item(name="Kilof", count=1, item_type="tool"),
    Item(name="Pochodnia", count=3, item_type="tool"),
    Item(name="Ziemniak", count=5, item_type="food"),
    Item(name="Kurtka", count=1, item_type="clothing", slot="torso")
]

equipment_slots = {
    "head": None,
    "torso": None,
    "hands": None,
    "legs": None,
    "feet": None,
    "back": None
}

quick_access_items = [None] * 9

inventory_mode = "browse"
sub_menu_open = False
sub_menu_options = []
selected_sub_menu_option = 0
selected_section = 1  # startowo ekwipunek
selected_item_index = 0
moving_item = None
moving_item_source = None
sort_mode = 0  # 0=A-Z, 1=Z-A, 2=ilość malejąco, 3=ilościowo rosnąco

def init_font():
    global FONT
    FONT = pygame.font.SysFont(None, FONT_SIZE)

def get_section_items(section_idx):
    if section_idx == 0:
        result = []
        for slot, item in equipment_slots.items():
            if item:
                result.append(f"Slot {slot}: {item.get_display_name()}, założone")
            else:
                result.append(f"Slot {slot}: (puste)")
        return result
    elif section_idx == 1:
        items = list(backpack_items)
        if sort_mode == 0:
            items = sorted(items, key=lambda i: i.name.lower())
        elif sort_mode == 1:
            items = sorted(items, key=lambda i: i.name.lower(), reverse=True)
        elif sort_mode == 2:
            items = sorted(items, key=lambda i: i.count, reverse=True)
        elif sort_mode == 3:
            items = sorted(items, key=lambda i: i.count)
        display = [item.get_display_name() for item in items]
        display += ["(puste miejsce)"] * (BACKPACK_CAPACITY - len(backpack_items))
        return display
    elif section_idx == 2:
        result = []
        for idx, item in enumerate(quick_access_items):
            if item:
                result.append(f"{idx+1}: {item.get_display_name()}")
            else:
                result.append(f"{idx+1}: (puste)")
        return result
    return []

def speak_current_item():
    items = get_section_items(selected_section)
    if not items:
        speak_ui("Brak elementów.")
        return
    if selected_item_index < 0 or selected_item_index >= len(items):
        speak_ui("Poza zakresem listy.")
        return
    current = selected_item_index + 1
    total = len(items)
    text = items[selected_item_index]
    speak_ui(f"{text}. Pozycja {current} z {total}.")

def get_selected_item():
    if selected_section == 0:
        keys = list(equipment_slots.keys())
        if 0 <= selected_item_index < len(keys):
            return equipment_slots[keys[selected_item_index]]
        return None
    elif selected_section == 1:
        items = list(backpack_items)
        if sort_mode == 0:
            items = sorted(items, key=lambda i: i.name.lower())
        elif sort_mode == 1:
            items = sorted(items, key=lambda i: i.name.lower(), reverse=True)
        elif sort_mode == 2:
            items = sorted(items, key=lambda i: i.count, reverse=True)
        elif sort_mode == 3:
            items = sorted(items, key=lambda i: i.count)
        if 0 <= selected_item_index < len(items):
            return items[selected_item_index]
        return None
    elif selected_section == 2:
        if 0 <= selected_item_index < len(quick_access_items):
            return quick_access_items[selected_item_index]
    return None

def build_sub_menu_options(item, section_idx):
    options = []
    if not item:
        return options
    if section_idx == 0:
        options.append("Zdejmij")
    elif section_idx == 1:
        if item.can_equip():
            options.append("Załóż")
        if item.item_type == "food":
            options.append("Użyj")
        options.append("Przenieś")
        options.append("Upuść")
        options.append("Właściwości")
    elif section_idx == 2:
        if item.item_type in ("tool", "food"):
            options.append("Użyj")
        options.append("Przenieś")
        options.append("Upuść")
        options.append("Właściwości")
    return options

def speak_current_submenu():
    if sub_menu_options:
        speak_ui(sub_menu_options[selected_sub_menu_option])
    else:
        speak_ui("Brak opcji.")

def handle_inventory_navigation(event):
    global selected_section, selected_item_index
    global inventory_mode, sub_menu_open, selected_sub_menu_option
    global moving_item, moving_item_source, sub_menu_options, sort_mode

    if event.type != pygame.KEYDOWN:
        return

    key = event.key

    # Tryb przenoszenia
    if inventory_mode == "moving":
        if key == pygame.K_ESCAPE:
            inventory_mode = "browse"
            moving_item = None
            moving_item_source = None
            speak_ui("Anulowano przenoszenie.")
            return
        if key == pygame.K_TAB and not pygame.key.get_mods() & pygame.KMOD_SHIFT:
            selected_section = (selected_section + 1) % len(SECTIONS)
            selected_item_index = 0
            speak_ui(SECTIONS[selected_section])
            speak_current_item()
            return
        if key == pygame.K_TAB and pygame.key.get_mods() & pygame.KMOD_SHIFT:
            selected_section = (selected_section - 1) % len(SECTIONS)
            selected_item_index = 0
            speak_ui(SECTIONS[selected_section])
            speak_current_item()
            return
        if key in (pygame.K_UP, pygame.K_DOWN):
            items = get_section_items(selected_section)
            max_index = len(items) - 1
            if key == pygame.K_UP:
                selected_item_index = (selected_item_index - 1) % (max_index + 1)
            else:
                selected_item_index = (selected_item_index + 1) % (max_index + 1)
            speak_current_item()
            return
        if key == pygame.K_RETURN:
            confirm_move_target()
        return

    # Sortowanie w trybie browse
    if inventory_mode == "browse" and key == pygame.K_r:
        sort_mode = (sort_mode + 1) % 4
        modes = ["A do Z", "Z do A", "ilościowo malejąco", "ilościowo rosnąco"]
        speak_ui(f"Sortowanie: {modes[sort_mode]}")
        return

    # Nawigacja w browse
    if inventory_mode == "browse":
        if key == pygame.K_TAB and not pygame.key.get_mods() & pygame.KMOD_SHIFT:
            selected_section = (selected_section + 1) % len(SECTIONS)
            selected_item_index = 0
            speak_ui(SECTIONS[selected_section])
            speak_current_item()
            return
        if key == pygame.K_TAB and pygame.key.get_mods() & pygame.KMOD_SHIFT:
            selected_section = (selected_section - 1) % len(SECTIONS)
            selected_item_index = 0
            speak_ui(SECTIONS[selected_section])
            speak_current_item()
            return
        if key == pygame.K_UP:
            items = get_section_items(selected_section)
            max_index = len(items) - 1
            selected_item_index = (selected_item_index - 1) % (max_index + 1)
            speak_current_item()
            return
        if key == pygame.K_DOWN:
            items = get_section_items(selected_section)
            max_index = len(items) - 1
            selected_item_index = (selected_item_index + 1) % (max_index + 1)
            speak_current_item()
            return
        if key == pygame.K_SPACE:
            item = get_selected_item()
            if not item:
                speak_ui("Brak przedmiotu.")
                return
            sub_menu_options.clear()
            sub_menu_options.extend(build_sub_menu_options(item, selected_section))
            if sub_menu_options:
                inventory_mode = "submenu"
                sub_menu_open = True
                selected_sub_menu_option = 0
                speak_current_submenu()
            else:
                speak_ui("Brak dostępnych opcji.")
        return

    # Nawigacja w submenu
    if inventory_mode == "submenu":
        if key == pygame.K_UP:
            selected_sub_menu_option = (selected_sub_menu_option - 1) % len(sub_menu_options)
            speak_current_submenu()
            return
        if key == pygame.K_DOWN:
            selected_sub_menu_option = (selected_sub_menu_option + 1) % len(sub_menu_options)
            speak_current_submenu()
            return
        if key == pygame.K_RETURN:
            execute_submenu_action()
            return
        if key == pygame.K_ESCAPE:
            inventory_mode = "browse"
            sub_menu_open = False
            speak_ui("Anulowano.")
        return

def execute_submenu_action():
    global inventory_mode, sub_menu_open, moving_item, moving_item_source

    item = get_selected_item()
    if not item:
        speak_ui("Brak przedmiotu.")
        return

    option = sub_menu_options[selected_sub_menu_option]

    if option == "Załóż":
        slot = item.slot
        if equipment_slots.get(slot):
            speak_ui(f"Slot {slot} jest już zajęty.")
        else:
            equipment_slots[slot] = item
            item.equipped = True
            if item in backpack_items:
                backpack_items.remove(item)
            for i in range(len(quick_access_items)):
                if quick_access_items[i] == item:
                    quick_access_items[i] = None
            speak_ui(f"Założono: {item.name}")
        inventory_mode = "browse"
        sub_menu_open = False

    elif option == "Zdejmij":
        keys = list(equipment_slots.keys())
        slot = keys[selected_item_index]
        if equipment_slots[slot]:
            backpack_items.append(equipment_slots[slot])
            equipment_slots[slot] = None
            speak_ui("Zdjęto przedmiot.")
        else:
            speak_ui("Slot był pusty.")
        inventory_mode = "browse"
        sub_menu_open = False

    elif option == "Użyj":
        speak_ui(f"Użyto: {item.name}")
        inventory_mode = "browse"
        sub_menu_open = False

    elif option == "Przenieś":
        moving_item = item
        moving_item_source = (selected_section, selected_item_index)
        inventory_mode = "moving"
        sub_menu_open = False
        speak_ui(f"Przenoszenie: {item.name}. Wybierz miejsce docelowe i naciśnij Enter.")

    elif option == "Upuść":
        speak_ui(f"Upuszczono: {item.name}")
        inventory_mode = "browse"
        sub_menu_open = False

    elif option == "Właściwości":
        speak_ui(f"Przedmiot: {item.name}, ilość: {item.count}")
        inventory_mode = "browse"
        sub_menu_open = False

def confirm_move_target():
    global inventory_mode, moving_item, moving_item_source

    if not moving_item or not moving_item_source:
        speak_ui("Brak przedmiotu do przeniesienia.")
        return

    if selected_section == 1:
        if len(backpack_items) >= BACKPACK_CAPACITY:
            speak_ui("Brak miejsca w ekwipunku.")
            return
        backpack_items.append(moving_item)

    elif selected_section == 2:
        if quick_access_items[selected_item_index] is not None:
            speak_ui("Slot zajęty.")
            return
        quick_access_items[selected_item_index] = moving_item

    elif selected_section == 0:
        keys = list(equipment_slots.keys())
        if selected_item_index >= len(keys):
            speak_ui("Nieprawidłowy slot.")
            return
        slot = keys[selected_item_index]
        if equipment_slots[slot] is not None:
            speak_ui("Slot zajęty.")
            return
        if not moving_item.can_equip() or moving_item.slot != slot:
            speak_ui("Nie pasuje do slotu.")
            return
        equipment_slots[slot] = moving_item
        moving_item.equipped = True

    # usuwanie z miejsca źródłowego
    src_section, src_index = moving_item_source
    if src_section == 1 and src_index < len(backpack_items):
        del backpack_items[src_index]
    elif src_section == 2:
        quick_access_items[src_index] = None
    elif src_section == 0:
        keys = list(equipment_slots.keys())
        equipment_slots[keys[src_index]] = None

    speak_ui(f"Przeniesiono {moving_item.name}.")
    moving_item = None
    moving_item_source = None
    inventory_mode = "browse"

def draw_inventory(screen):
    screen.fill(BG_COLOR)
    label = FONT.render("Ekwipunek postaci", True, HEADER_COLOR)
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
        for i, item_text in enumerate(items):
            color = TEXT_COLOR
            if section_idx == selected_section and i == selected_item_index:
                color = (255, 255, 255)
            label = FONT.render(item_text, True, color)
            screen.blit(label, (x + 20, y))
            if section_idx == selected_section and i == selected_item_index:
                rect = label.get_rect(topleft=(x + 20, y))
                pygame.draw.rect(screen, (255, 255, 255), rect.inflate(6, 6), 2)
            y += FONT_SIZE + 6
    pygame.display.flip()

def draw(screen):
    draw_inventory(screen)
