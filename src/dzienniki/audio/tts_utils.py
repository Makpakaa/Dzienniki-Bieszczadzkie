import time
from dzienniki.audio import tts

_LAST_TEXT = ""
_LAST_TIME = 0.0
_DEBOUNCE_SEC = 0.20  # 200 ms

def speak_ui(text: str):
    """
    Do krótkich ogłoszeń UI (fokus w menu, ruch, kolizje, listy).
    - przerywa poprzedni komunikat,
    - de-duplikuje: nie powtarza tego samego tekstu w oknie 200 ms.
    """
    global _LAST_TEXT, _LAST_TIME
    now = time.perf_counter()
    if text and not _is_duplicate(text, now):
        tts.announce(text)
        _LAST_TEXT = text
        _LAST_TIME = now

def speak_long(text: str):
    """
    Do dłuższych narracji (wprowadzenie, dialogi). Nie przerywa.
    """
    global _LAST_TEXT, _LAST_TIME
    tts.narrate(text)
    if text:
        _LAST_TEXT = text
        _LAST_TIME = time.perf_counter()

def repeat_last():
    """Powtórz ostatni ogłoszony tekst (z przerwaniem)."""
    global _LAST_TEXT
    if _LAST_TEXT:
        tts.announce(_LAST_TEXT)

def set_debounce(seconds: float):
    """Opcjonalnie: zmień okno anty-spam (domyślnie 0.20 s)."""
    global _DEBOUNCE_SEC
    _DEBOUNCE_SEC = max(0.0, float(seconds))

def _is_duplicate(text: str, now: float) -> bool:
    global _LAST_TEXT, _LAST_TIME, _DEBOUNCE_SEC
    if text != _LAST_TEXT:
        return False
    return (now - _LAST_TIME) < _DEBOUNCE_SEC
