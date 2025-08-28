# src/dzienniki/screen.py
# Ekrany UI: logo, tytuł, menu główne, wprowadzenie (NVDA/klawiatura).
# Uwaga: brak logiki kamery i rozgrywki – to jest wyłącznie warstwa ekranów.

import pygame
from dzienniki.audio.tts import manager
from dzienniki import settings


# ---------- Narzędzia TTS ----------

def speak_now(text: str):
    """Natychmiast przerwij bieżącą kwestię i wypowiedz nowy tekst."""
    try:
        manager.engine.stop()
        manager.engine.say(text)
        manager.engine.runAndWait()
    except Exception:
        # awaryjnie: bez wyciszenia – minimalny fallback
        try:
            manager.engine.say(text)
            manager.engine.runAndWait()
        except Exception:
            pass


# ---------- Narzędzia rysowania ----------

def _draw_centered_lines(screen, lines, font_size=48, color=(255, 255, 0), line_spacing=12, y_offset=0):
    """Wyrenderuj listę linii wyśrodkowanych na ekranie."""
    font = pygame.font.SysFont(None, font_size)
    total_h = sum(font.size(txt)[1] for txt in lines) + line_spacing * (len(lines) - 1)
    start_y = screen.get_height() // 2 - total_h // 2 + y_offset
    for i, txt in enumerate(lines):
        surf = font.render(txt, True, color)
        rect = surf.get_rect(center=(screen.get_width() // 2, start_y))
        screen.blit(surf, rect)
        start_y += surf.get_height() + line_spacing


def _wait_or_skip(seconds: float) -> bool:
    """
    Czeka do 'seconds' lub do wciśnięcia klawisza / kliknięcia myszy.
    Zwraca True, jeśli przerwano (skipped), False jeśli doczekało końca.
    """
    clock = pygame.time.Clock()
    elapsed = 0.0
    while elapsed < seconds:
        for e in pygame.event.get():
            if e.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.QUIT):
                return True
        clock.tick(settings.FPS)
        elapsed += 1.0 / settings.FPS
    return False


# ---------- Ekrany ----------

def show_logo(screen, seconds: float = 2.0):
    screen.fill((0, 0, 0))
    _draw_centered_lines(screen, ["LOGO GRY"], font_size=64)
    pygame.display.flip()
    speak_now("Logo.")
    _wait_or_skip(seconds)


def show_title(screen, seconds: float = 3.0):
    screen.fill((0, 0, 0))
    _draw_centered_lines(screen, ["Dzienniki", "Bieszczadzkie"], font_size=100, line_spacing=20)
    pygame.display.flip()
    speak_now("Dzienniki Bieszczadzkie.")
    _wait_or_skip(seconds)


def main_menu(screen):
    """
    Proste menu:
      - Strzałki góra/dół – nawigacja
      - Enter – zatwierdź
      - ESC – wyjście (zwraca None)
    Zwraca string w formacie 'nowa_gra' / 'załaduj_grę' / 'wyjście'
    """
    options = ["Nowa Gra", "Załaduj Grę", "Wyjście"]
    selected = 0
    clock = pygame.time.Clock()
    # Powiedz instrukcję + pierwszy element
    speak_now("Menu główne. Strzałki góra, dół. Enter zatwierdza. Escape wychodzi.")
    speak_now(options[selected])

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return None
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    speak_now("Wyjście.")
                    return None
                elif e.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                    speak_now(options[selected])
                elif e.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                    speak_now(options[selected])
                elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    speak_now(f"Wybrano: {options[selected]}")
                    # krótka pauza by nie uciąć TTS
                    pygame.time.wait(200)
                    return options[selected].lower().replace(" ", "_")

        screen.fill((0, 0, 0))
        # rysowanie opcji
        font = pygame.font.SysFont(None, 48)
        top_y = 200
        for i, opt in enumerate(options):
            is_sel = (i == selected)
            color = (255, 255, 255) if is_sel else (255, 255, 0)
            lbl = font.render(opt, True, color)
            x = screen.get_width() // 2 - lbl.get_width() // 2
            y = top_y + i * 60
            screen.blit(lbl, (x, y))
            if is_sel:
                pygame.draw.rect(screen, color, (x - 6, y - 6, lbl.get_width() + 12, lbl.get_height() + 12), 2)

        pygame.display.flip()
        clock.tick(settings.FPS)


def show_introduction(screen):
    """
    Ekran wprowadzenia. Dowolny klawisz / klik wyjdzie.
    """
    lines = [
        "Witamy w Dziennikach Bieszczadzkich!",
        "Jesteś wędrowcem przemierzającym wzgórza i doliny.",
        "Odkryj tajemnice tej spokojnej krainy.",
        "Powodzenia!"
    ]
    screen.fill((0, 0, 0))
    _draw_centered_lines(screen, lines, font_size=36, line_spacing=8, y_offset=-40)
    pygame.display.flip()

    speak_now(" ".join(lines) + " Naciśnij dowolny klawisz, aby kontynuować.")
    clock = pygame.time.Clock()
    while True:
        for e in pygame.event.get():
            if e.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.QUIT):
                return
        clock.tick(settings.FPS)
