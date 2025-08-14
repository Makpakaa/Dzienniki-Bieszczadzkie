# src/dzienniki/ui/text_input.py
import pygame
from dzienniki.audio import tts

DIALOG_W = 720
DIALOG_H = 200
PADDING = 16

BG_OVERLAY = (0, 0, 0)
PANEL_COLOR = (30, 30, 30)
BORDER_COLOR = (255, 255, 0)
TEXT_COLOR = (255, 255, 255)
PROMPT_COLOR = (200, 200, 200)
CARET_COLOR = (255, 255, 255)

FONT_SIZE = 28
PROMPT_SIZE = 22
CARET_BLINK_MS = 500

# Echo klawiatury (ON domyślnie). F3 przełącza.
ECHO_DEFAULT = True

def _font(size=FONT_SIZE):
    return pygame.font.SysFont(None, size)

def _draw_dialog(surface, prompt, text, caret_visible, echo_on):
    sw, sh = surface.get_size()
    x = (sw - DIALOG_W) // 2
    y = (sh - DIALOG_H) // 2
    panel = pygame.Rect(x, y, DIALOG_W, DIALOG_H)

    pygame.draw.rect(surface, PANEL_COLOR, panel)
    pygame.draw.rect(surface, BORDER_COLOR, panel, 2)

    f_prompt = _font(PROMPT_SIZE)
    prompt_surf = f_prompt.render(prompt, True, PROMPT_COLOR)
    surface.blit(prompt_surf, (x + PADDING, y + PADDING))

    input_y = y + PADDING + prompt_surf.get_height() + 12
    input_h = _font().get_height() + 16
    input_rect = pygame.Rect(x + PADDING, input_y, DIALOG_W - 2 * PADDING, input_h)
    pygame.draw.rect(surface, (50, 50, 50), input_rect)
    pygame.draw.rect(surface, (120, 120, 120), input_rect, 1)

    f = _font()
    text_to_draw = text
    txt_surf = f.render(text_to_draw, True, TEXT_COLOR)
    max_w = input_rect.width - 12
    while txt_surf.get_width() > max_w and len(text_to_draw) > 0:
        text_to_draw = text_to_draw[1:]
        txt_surf = f.render(text_to_draw, True, TEXT_COLOR)

    tx = input_rect.x + 6
    ty = input_rect.y + (input_rect.height - txt_surf.get_height()) // 2
    surface.blit(txt_surf, (tx, ty))

    if caret_visible:
        caret_x = tx + txt_surf.get_width() + 2
        caret_top = input_rect.y + 4
        caret_bottom = input_rect.y + input_rect.height - 4
        pygame.draw.line(surface, CARET_COLOR, (caret_x, caret_top), (caret_x, caret_bottom), 2)

    tips = (
        "Enter: zatwierdź, Esc: anuluj, Backspace: usuń, "
        "Ctrl+Backspace: usuń słowo, F2: przeczytaj, F3: echo "
        + ("ON" if echo_on else "OFF")
    )
    tips_surf = _font(18).render(tips, True, PROMPT_COLOR)
    surface.blit(tips_surf, (x + PADDING, input_rect.bottom + 12))

def _speak_char(ch: str):
    """Czyta nazwę wpisanego znaku po polsku (prosto)."""
    if ch == " ":
        tts.speak("spacja")
    elif ch == "\t":
        tts.speak("tabulator")
    elif ch == "\n":
        tts.speak("nowa linia")
    else:
        # dla liter/cyfr/znaków po prostu czytamy znak; NVDA zwykle dobrze to czyta
        tts.speak(ch)

def ask_text(screen, prompt="Podaj tekst", initial=""):
    """
    Blokujące okno edycyjne. Zwraca wpisany tekst (str) lub None, jeśli anulowano.
    Obsługa:
      - wpisywanie znaków (event.unicode)
      - Enter -> zaakceptuj (jeśli puste, zwraca initial, a jeśli i to puste -> 'Punkt')
      - Esc -> anuluj (None)
      - Backspace -> usuń znak (mówi 'Usunięto')
      - Ctrl+Backspace -> usuń ostatnie słowo (mówi 'Usunięto słowo')
      - F2 -> przeczytaj bieżący tekst
      - F3 -> przełącz echo klawiatury ON/OFF (mówi stan)
    """
    clock = pygame.time.Clock()
    text = str(initial or "")
    caret_visible = True
    caret_timer = 0
    echo_on = ECHO_DEFAULT

    tts.speak(f"{prompt}. Wpisz nazwę i naciśnij Enter. Escape, aby anulować. Echo { 'włączone' if echo_on else 'wyłączone' }. Aktualnie: {text or 'puste'}.")

    running = True
    while running:
        dt = clock.tick(60)
        caret_timer += dt
        if caret_timer >= CARET_BLINK_MS:
            caret_timer = 0
            caret_visible = not caret_visible

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                tts.speak("Anulowano.")
                return None

            if event.type == pygame.KEYDOWN:
                mods = pygame.key.get_mods()

                if event.key == pygame.K_RETURN:
                    final = text.strip() or str(initial or "").strip() or "Punkt"
                    tts.speak(f"Zatwierdzono: {final}.")
                    return final

                elif event.key == pygame.K_ESCAPE:
                    tts.speak("Anulowano.")
                    return None

                elif event.key == pygame.K_F2:
                    tts.speak(f"Aktualnie: {text or 'puste'}.")

                elif event.key == pygame.K_F3:
                    echo_on = not echo_on
                    tts.speak(f"Echo {'włączone' if echo_on else 'wyłączone'}.")

                elif event.key == pygame.K_BACKSPACE:
                    if (mods & pygame.KMOD_CTRL):
                        before = text.rstrip()
                        cut = before.rfind(" ")
                        if cut == -1:
                            text = ""
                        else:
                            text = before[:cut]
                        tts.speak("Usunięto słowo.")
                    else:
                        if len(text) > 0:
                            text = text[:-1]
                            tts.speak("Usunięto.")
                        else:
                            tts.speak("Nic do usunięcia.")

                else:
                    ch = event.unicode
                    if ch and ch.isprintable():
                        text += ch
                        if echo_on:
                            _speak_char(ch)

        screen.fill(BG_OVERLAY)
        _draw_dialog(screen, prompt, text, caret_visible, echo_on)
        pygame.display.flip()
