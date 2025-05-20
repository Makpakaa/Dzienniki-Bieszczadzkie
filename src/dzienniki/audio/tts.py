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
                # przerwij poprzednie mówienie
                self.engine.stop()
                self.engine.say(text)
                self.engine.runAndWait()
            except RuntimeError:
                pass

    def speak(self, text: str):
        """Dodaje tekst do kolejki do przeczytania."""
        self.queue.put(text)

    def stop(self):
        """Przerwij bieżące czytanie i wyrzuć wszystkie oczekujące komunikaty."""
        try:
            self.engine.stop()
        except RuntimeError:
            pass
        with self.queue.mutex:
            self.queue.queue.clear()

# globalna instancja
manager = TTSManager()

# eksportowane skróty
speak = manager.speak
stop  = manager.stop
