import threading
import queue
import pyttsx3

class TTSManager:
    def __init__(self):
        # Inicjalizacja silnika
        self.engine = pyttsx3.init()
        rate = self.engine.getProperty("rate")
        self.engine.setProperty("rate", min(rate + 100, 350))

        # Kolejka tekstów do przeczytania
        self._q = queue.Queue()
        # Worker w oddzielnym wątku (daemon)
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

    def _worker(self):
        while True:
            text = self._q.get()         # czekaj na nowy tekst
            self.engine.stop()           # przerwij ewentualne czytanie
            self.engine.say(text)
            self.engine.runAndWait()
            self._q.task_done()

    def speak(self, text: str):
        """Asynchronicznie przeczytaj tekst, kasując stare w kolejce."""
        with self._q.mutex:
            self._q.queue.clear()       # wyrzuć stare komunikaty
        self._q.put(text)              # dodaj tylko ten

    def stop(self):
        """Przerwij mowę natychmiast."""
        try:
            self.engine.stop()
        except Exception:
            pass

# globalna instancja
manager = TTSManager()
speak   = manager.speak
stop    = manager.stop
