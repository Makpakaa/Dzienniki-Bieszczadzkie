# src/dzienniki/screen.py
# Ekrany UI: logo, tytuł, menu główne, wprowadzenie (NVDA/klawiatura).
# Uwaga: brak logiki kamery i rozgrywki – to jest wyłącznie warstwa ekranów.

import pygame
from dzienniki.audio.tts_utils import speak_ui, speak_long  # UI (przerywane) + narracja (bez przerywania)
from dzienniki import settings


# ---------- Narzędzia TTS ----------

def speak_now(text: str):
    """Natychmiast przerwij bieżącą kwestię i wypowiedz nowy tekst (klikowe)."""
    try:
        speak_ui(text)
    except Exception:
        pass


def kill_tts_now():
    """
    Twarde zatrzymanie mowy:
    1) jeśli istnieje dzienniki.audio.tts.manager.engine.stop() — użyj,
    2) jeśli tts_utils ma stop_all() — użyj,
    3) w ostateczności wstrzyknij pusty komunikat (przerywany kanał).
    """
    # 1) centralny manager (pyttsx3)
    try:
        from dzienniki.audio import tts as _tts  # type: ignore
        eng = getattr(getattr(_tts, "manager", None), "engine", None)
        if eng is not None:
            try:
                eng.stop()  # natychmiast ucina kolejkę
                return
            except Exception:
                pass
    except Exception:
        pass

    # 2) tts_utils.stop_all() jeśli istnieje
    try:
        from dzienniki.audio import tts_utils as _tu  # type: ignore
        stop_fn = getattr(_tu, "stop_all", None) or getattr(_tu, "stop", None)
        if callable(stop_fn):
            try:
                stop_fn()
                return
            except Exception:
                pass
    except Exception:
        pass

    # 3) miękki fallback — przerwij kanał klikowy
    try:
        speak_ui("")
    except Exception:
        pass


# ---------- Narzędzia rysowania i wejścia ----------

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


def _flush_inputs_and_wait_release():
    """
    Czyści kolejkę zdarzeń i czeka, aż WSZYSTKIE klawisze będą puszczone.
    Zabezpiecza przed „przeciekaniem” Entera z poprzedniego ekranu.
    """
    try:
        pygame.event.clear()
    except Exception:
        pass
    clock = pygame.time.Clock()
    while True:
        pygame.event.pump()
        pressed = pygame.key.get_pressed()
        if not any(pressed):
            break
        clock.tick(120)


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
    # Powiedz instrukcję + pierwszy element (klikowe, przerywane)
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
                    choice = options[selected].lower().replace(" ", "_")
                    speak_now(f"Wybrano: {options[selected]}")
                    pygame.time.wait(200)  # krótka pauza by nie uciąć TTS
                    _flush_inputs_and_wait_release()  # ważne
                    return choice

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
    Narracja leci w tle (bez przerywania), a komunikat „Naciśnij dowolny klawisz…”
    jest dołączony do tej samej kolejki, więc poleci po narracji.
    Po wyjściu — twardo uciszamy TTS, by nie ciągnął się na ekran gry.
    """
    _flush_inputs_and_wait_release()  # zabezpieczenie po wejściu z menu

    lines = [
        "Witamy w Dziennikach Bieszczadzkich!",
        "Jesteś wędrowcem przemierzającym wzgórza i doliny.",
        "Odkryj tajemnice tej spokojnej krainy.",
        "Powodzenia!"
    ]
    screen.fill((0, 0, 0))
    _draw_centered_lines(screen, lines, font_size=36, line_spacing=8, y_offset=-40)
    pygame.display.flip()

    # Dłuższa narracja – kolejkujemy
    try:
        speak_long(" ".join(lines))
        speak_long("Naciśnij dowolny klawisz, aby kontynuować.")
    except Exception:
        speak_now("Naciśnij dowolny klawisz, aby kontynuować.")

    clock = pygame.time.Clock()
    while True:
        for e in pygame.event.get():
            if e.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.QUIT):
                # Twarde CIĘCIE mowy zanim wyjdziemy do gry:
                kill_tts_now()
                # króciutkie okno na zatrzymanie audio backendu
                pygame.time.wait(80)
                _flush_inputs_and_wait_release()
                return
        clock.tick(settings.FPS)
