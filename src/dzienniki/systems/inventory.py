import pygame
from dzienniki.audio import tts
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
sort_mode = 0  # 0=A-Z, 1=Z-A, 2=ilość malejąco, 3=ilość rosnąco

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
        items = backpack_items
        if sort_mode == 0:
            items = sorted(items, key=lambda i: i.name.lower())
        elif sort_mode == 1:
            items = sorted(items, key=lambda i: i.name.lower(), reverse=True)
        elif sort_mode == 2:
            items = sorted(items, key=lambda i: i.count, reverse=True)
        elif sort_mode == 3:
            items = sorted(items, key=lambda i: i.count)
        return [item.get_display_name() for item in items] + \
               ["(puste miejsce)"] * (BACKPACK_CAPACITY - len(backpack_items))
    elif section_idx == 2:
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

def get_selected_item():
    if selected_section == 0:
        keys = list(equipment_slots.keys())
        slot = keys[selected_item_index] if selected_item_index < len(keys) else None
        return equipment_slots.get(slot) if slot else None
    elif selected_section == 1:
        if selected_item_index < len(backpack_items):
            sorted_items = backpack_items
            if sort_mode == 0:
                sorted_items = sorted(backpack_items, key=lambda i: i.name.lower())
            elif sort_mode == 1:
                sorted_items = sorted(backpack_items, key=lambda i: i.name.lower(), reverse=True)
            elif sort_mode == 2:
                sorted_items = sorted(backpack_items, key=lambda i: i.count, reverse=True)
            elif sort_mode == 3:
                sorted_items = sorted(backpack_items, key=lambda i: i.count)
            if selected_item_index < len(sorted_items):
                return sorted_items[selected_item_index]
        return None
    elif selected_section == 2:
        return quick_access_items[selected_item_index]
    return None

def build_sub_menu_options(item, section_idx):
    options = []
    if not item:
        return []
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
        tts.speak(sub_menu_options[selected_sub_menu_option])
    else:
        tts.speak("Brak opcji.")

def handle_inventory_navigation(event):
    global selected_section, selected_item_index
    global inventory_mode, sub_menu_open, selected_sub_menu_option
    global moving_item, moving_item_source, sub_menu_options, sort_mode

    items = get_section_items(selected_section)
    max_index = len(items) - 1

    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_r and inventory_mode == "browse":
            sort_mode = (sort_mode + 1) % 4
            modes = ["A do Z", "Z do A", "ilościowo malejąco", "ilościowo rosnąco"]
            tts.speak(f"Sortowanie: {modes[sort_mode]}")
        elif inventory_mode == "browse":
            if event.key == pygame.K_TAB and not pygame.key.get_mods() & pygame.KMOD_SHIFT:
                selected_section = (selected_section + 1) % len(SECTIONS)
                selected_item_index = 0
                tts.speak(SECTIONS[selected_section])
                speak_current_item()
            elif event.key == pygame.K_TAB and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                selected_section = (selected_section - 1) % len(SECTIONS)
                selected_item_index = 0
                tts.speak(SECTIONS[selected_section])
                speak_current_item()
            elif event.key == pygame.K_UP:
                selected_item_index = (selected_item_index - 1) % (max_index + 1)
                speak_current_item()
            elif event.key == pygame.K_DOWN:
                selected_item_index = (selected_item_index + 1) % (max_index + 1)
                speak_current_item()
            elif event.key == pygame.K_SPACE:
                item = get_selected_item()
                if not item:
                    tts.speak("Brak przedmiotu.")
                    return
                sub_menu_options.clear()
                sub_menu_options.extend(build_sub_menu_options(item, selected_section))
                if sub_menu_options:
                    inventory_mode = "submenu"
                    sub_menu_open = True
                    selected_sub_menu_option = 0
                    speak_current_submenu()
                else:
                    tts.speak("Brak dostępnych opcji.")
        elif inventory_mode == "submenu":
            if event.key == pygame.K_UP:
                selected_sub_menu_option = (selected_sub_menu_option - 1) % len(sub_menu_options)
                speak_current_submenu()
            elif event.key == pygame.K_DOWN:
                selected_sub_menu_option = (selected_sub_menu_option + 1) % len(sub_menu_options)
                speak_current_submenu()
            elif event.key == pygame.K_RETURN:
                execute_submenu_action()
            elif event.key == pygame.K_ESCAPE:
                inventory_mode = "browse"
                sub_menu_open = False
                tts.speak("Anulowano.")
        elif inventory_mode == "moving":
            if event.key == pygame.K_RETURN:
                confirm_move_target()

def execute_submenu_action():
    global inventory_mode, sub_menu_open, moving_item, moving_item_source

    item = get_selected_item()
    if not item:
        tts.speak("Brak przedmiotu.")
        return

    option = sub_menu_options[selected_sub_menu_option]

    if option == "Załóż":
        slot = item.slot
        if equipment_slots.get(slot):
            tts.speak(f"Slot {slot} jest już zajęty.")
        else:
            equipment_slots[slot] = item
            item.equipped = True
            if item in backpack_items:
                backpack_items.remove(item)
            elif item in quick_access_items:
                for i in range(len(quick_access_items)):
                    if quick_access_items[i] == item:
                        quick_access_items[i] = None
                        break
            tts.speak(f"Założono: {item.name}")

    elif option == "Zdejmij":
        keys = list(equipment_slots.keys())
        slot = keys[selected_item_index]
        if equipment_slots[slot]:
            backpack_items.append(equipment_slots[slot])
            equipment_slots[slot] = None
            tts.speak("Zdjęto przedmiot.")
        else:
            tts.speak("Slot był pusty.")

    elif option == "Użyj":
        tts.speak(f"Użyto: {item.name}")

    elif option == "Przenieś":
        moving_item = item
        moving_item_source = (selected_section, selected_item_index)
        inventory_mode = "moving"
        sub_menu_open = False
        tts.speak(f"Przenoszenie: {item.name}. Wybierz miejsce docelowe i naciśnij Enter.")

    elif option == "Upuść":
        tts.speak(f"Upuszczono: {item.name}")

    elif option == "Właściwości":
        tts.speak(f"Przedmiot: {item.name}, ilość: {item.count}")

    inventory_mode = "browse"
    sub_menu_open = False

def confirm_move_target():
    global inventory_mode, moving_item, moving_item_source

    if not moving_item or not moving_item_source:
        tts.speak("Brak przedmiotu do przeniesienia.")
        return

    if selected_section == 1:
        if len(backpack_items) >= BACKPACK_CAPACITY:
            tts.speak("Brak miejsca w ekwipunku.")
            return
        backpack_items.append(moving_item)

    elif selected_section == 2:
        if quick_access_items[selected_item_index] is not None:
            tts.speak("Slot zajęty.")
            return
        quick_access_items[selected_item_index] = moving_item

    elif selected_section == 0:
        keys = list(equipment_slots.keys())
        if selected_item_index >= len(keys):
            tts.speak("Nieprawidłowy slot.")
            return
        slot = keys[selected_item_index]
        if equipment_slots[slot] is not None:
            tts.speak("Slot zajęty.")
            return
        if not moving_item.can_equip() or moving_item.slot != slot:
            tts.speak("Nie pasuje do slotu.")
            return
        equipment_slots[slot] = moving_item
        moving_item.equipped = True

    # usuwanie z poprzedniego miejsca
    src_section, src_index = moving_item_source
    if src_section == 1 and src_index < len(backpack_items):
        del backpack_items[src_index]
    elif src_section == 2:
        quick_access_items[src_index] = None
    elif src_section == 0:
        keys = list(equipment_slots.keys())
        equipment_slots[keys[src_index]] = None

    tts.speak(f"Przeniesiono {moving_item.name}.")
    moving_item = None
    moving_item_source = None
    inventory_mode = "browse"

def draw_inventory(screen):
    screen.fill(BG_COLOR)
    title = "Ekwipunek postaci"
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
