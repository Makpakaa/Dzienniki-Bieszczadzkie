import pygame
import sys
from dzienniki.audio import tts

def show_logo(screen):
    screen.fill((0, 0, 0))
    font = pygame.font.SysFont(None, 64)
    label = font.render("LOGO GRY", True, (255, 255, 0))
    rect = label.get_rect(center=(screen.get_width()//2, screen.get_height()//2))
    screen.blit(label, rect)
    pygame.display.flip()
    tts.speak("Wyświetlam logo gry. Naciśnij dowolny klawisz, aby przejść dalej.")
    start = pygame.time.get_ticks()
    while True:
        for e in pygame.event.get():
            if e.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.QUIT):
                return
        if pygame.time.get_ticks() - start > 3000:
            return

def show_title(screen):
    screen.fill((0, 0, 0))
    font = pygame.font.SysFont(None, 100)
    lines = ["Dzienniki", "Bieszczadzkie"]
    for i, txt in enumerate(lines):
        lbl = font.render(txt, True, (255, 255, 0))
        r = lbl.get_rect(center=(screen.get_width()//2, screen.get_height()//2 + i*100))
        screen.blit(lbl, r)
    pygame.display.flip()
    tts.speak("Dzienniki Bieszczadzkie. Naciśnij dowolny klawisz, aby przejść dalej.")
    start = pygame.time.get_ticks()
    while True:
        for e in pygame.event.get():
            if e.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.QUIT):
                return
        if pygame.time.get_ticks() - start > 3000:
            return

def main_menu(screen):
    """Pokazuje menu główne z wyborem opcji klawiszami i TTS."""
    import pygame
    from dzienniki.audio import tts

    options = ["Nowa Gra", "Załaduj Grę", "Wyjście"]
    selected = 0
    clock = pygame.time.Clock()

    tts.speak("Menu główne. Strzałki góra, dół. Enter zatwierdza.")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                    tts.speak(options[selected])
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                    tts.speak(options[selected])
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    tts.speak(f"Wybrano {options[selected]}")
                    pygame.time.delay(300)
                    return options[selected].lower().replace(" ", "_")

        # Rysowanie menu
        screen.fill((0, 0, 0))
        font = pygame.font.SysFont(None, 48)
        for i, opt in enumerate(options):
            color = (255,255,255) if i == selected else (255,255,0)
            lbl = font.render(opt, True, color)
            x = screen.get_width()//2 - lbl.get_width()//2
            y = 200 + i*60
            screen.blit(lbl, (x,y))
            if i == selected:
                pygame.draw.rect(screen, color,
                                 (x-5, y-5, lbl.get_width()+10, lbl.get_height()+10), 2)

        pygame.display.flip()
        clock.tick(30)

def show_introduction(screen):
    """Pokazuje tekst wprowadzający grę z TTS."""
    import pygame
    from dzienniki.audio import tts

    lines = [
        "Witamy w Dziennikach Bieszczadzkich!",
        "Jesteś wędrowcem przemierzającym wzgórza i doliny.",
        "Odkryj tajemnice tej spokojnej krainy.",
        "Powodzenia!"
    ]
    tts_text = " ".join(lines)

    screen.fill((0, 0, 0))
    font = pygame.font.SysFont(None, 36)
    for i, text in enumerate(lines):
        lbl = font.render(text, True, (255, 255, 0))
        screen.blit(lbl, (50, 150 + i * 40))
    pygame.display.flip()

    tts.speak(tts_text + " Naciśnij dowolny klawisz, aby kontynuować.")

    start = pygame.time.get_ticks()
    while True:
        for e in pygame.event.get():
            if e.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.QUIT):
                return
        if pygame.time.get_ticks() - start > 5000:
            return

def topdown_game_loop(screen):
    """Prosta, czarna pętla gry; tu wstawisz właściwą logikę."""
    import pygame
    from dzienniki import settings

    clock = pygame.time.Clock()
    running = True

    while running:
        # delta_time w sekundach
        dt = clock.tick( settings.FPS ) / 1000.0

        # obsługa zdarzeń
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        # rysowanie tła
        screen.fill((0, 0, 0))

        # TODO: tutaj zostanie logika ruchu, rysowania świata itd.

        pygame.display.flip()

    # wyjście z pętli
    return
