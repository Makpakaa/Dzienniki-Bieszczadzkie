import pyttsx3

class TTSManager:
    def __init__(self):
        self.engine = pyttsx3.init()
        # podbij tempo, ale bez przesady (domyślnie ~200)
        rate = self.engine.getProperty("rate")
        self.engine.setProperty("rate", min(rate + 100, 350))

    def speak(self, text: str):
        """Blokująco przeczytaj cały tekst."""
        # przerwij co się czyta
        self.engine.stop()
        # powiedz i czekaj na zakończenie
        self.engine.say(text)
        self.engine.runAndWait()

    def stop(self):
        """Przerwij mowę (gdyby coś było w trakcie)."""
        try:
            self.engine.stop()
        except Exception:
            pass

# globalna instancja
manager = TTSManager()
speak = manager.speak
stop  = manager.stop
