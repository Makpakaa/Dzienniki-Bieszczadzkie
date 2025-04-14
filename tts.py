import pyttsx3
import threading
from queue import Queue

class TTSManager:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.queue = Queue()
        self.running = True
        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self):
        while self.running:
            text = self.queue.get()
            if text is None:
                break
            try:
                self.engine.stop()  # natychmiast przerywaj poprzednie mówienie
                self.engine.say(text)
                self.engine.runAndWait()
            except RuntimeError:
                pass  # jeżeli engine został zamknięty, ignoruj błędy

    def speak(self, text):
        """Dodaje tekst do kolejki do przeczytania."""
        self.queue.put(text)

    def stop(self):
        """Zatrzymuje silnik TTS i kończy wątek."""
        self.running = False
        self.queue.put(None)
        self.engine.stop()

# Tworzymy globalną instancję TTSManager
manager = TTSManager()

# Udostępniamy skrót funkcji speak() dla łatwego użycia
speak = manager.speak
