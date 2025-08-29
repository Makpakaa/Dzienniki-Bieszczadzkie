import os
import sys
import threading
import queue
import time

import pyttsx3


# --- NVDA wrapper (jeśli dostępny) ---

class _NVDAClient:
    def __init__(self):
        self.available = False
        self._lib = None
        # Możesz ustawić NVDA_PATH na folder z nvdaControllerClient*.dll
        candidate_dirs = [
            os.environ.get("NVDA_PATH"),
            r"C:\Program Files\NVDA",
            r"C:\Program Files (x86)\NVDA",
        ]
        candidate_dirs = [p for p in candidate_dirs if p]
        dll_names = ["nvdaControllerClient64.dll", "nvdaControllerClient.dll", "nvdaControllerClient32.dll"]

        try:
            from ctypes import WinDLL  # tylko Windows
        except Exception:
            WinDLL = None

        if WinDLL:
            # Szukaj po typowych lokalizacjach
            for base in candidate_dirs:
                for dll in dll_names:
                    path = os.path.join(base, dll)
                    if os.path.isfile(path):
                        try:
                            self._lib = WinDLL(path)
                            self.available = True
                            return
                        except Exception:
                            self._lib = None

            # Ostatnia próba: w PATH
            for dll in dll_names:
                try:
                    self._lib = WinDLL(dll)
                    self.available = True
                    return
                except Exception:
                    self._lib = None

    def speak(self, text: str) -> bool:
        if not self.available or not self._lib:
            return False
        try:
            from ctypes import c_wchar_p, c_int
            self._lib.nvdaController_speakText.argtypes = [c_wchar_p]
            self._lib.nvdaController_speakText.restype = c_int
            return self._lib.nvdaController_speakText(text) == 0
        except Exception:
            return False

    def cancel(self) -> bool:
        if not self.available or not self._lib:
            return False
        try:
            from ctypes import c_int
            self._lib.nvdaController_cancelSpeech.argtypes = []
            self._lib.nvdaController_cancelSpeech.restype = c_int
            return self._lib.nvdaController_cancelSpeech() == 0
        except Exception:
            return False


# --- Worker pyttsx3 (fallback) ---

class _Pyttsx3Worker(threading.Thread):
    """
    Wątek TTS dla pyttsx3 z obsługą:
    - interrupt=True: czyszczenie kolejki + stop() aktualnej mowy
    - interrupt=False: dopisywanie do kolejki (narracje)
    """
    def __init__(self, rate_boost=100, max_rate=350, volume=1.0, voice_id=None):
        super().__init__(daemon=True)
        self.engine = pyttsx3.init()
        try:
            base_rate = self.engine.getProperty("rate")
            self.engine.setProperty("rate", min(base_rate + rate_boost, max_rate))
            self.engine.setProperty("volume", volume)
            if voice_id:
                self.engine.setProperty("voice", voice_id)
        except Exception:
            pass

        self._q = queue.Queue()
        self._shutdown = threading.Event()
        self._qlock = threading.Lock()

    def run(self):
        while not self._shutdown.is_set():
            try:
                text, interrupt = self._q.get(timeout=0.05)
            except queue.Empty:
                continue

            if interrupt:
                self._clear_queue()
                try:
                    # Przerwij aktualną mowę (jeśli jakaś trwa)
                    self.engine.stop()
                except Exception:
                    pass

            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception:
                # Nie zabijaj całego wątku przy pojedynczym błędzie
                pass
            finally:
                self._q.task_done()

        # Sprzątanie
        try:
            self.engine.stop()
        except Exception:
            pass

    def speak(self, text: str, interrupt: bool):
        if interrupt:
            self._clear_queue()
        self._q.put((text, interrupt))

    def stop_all(self):
        self._clear_queue()
        try:
            self.engine.stop()
        except Exception:
            pass

    def _clear_queue(self):
        with self._qlock:
            try:
                while True:
                    self._q.get_nowait()
                    self._q.task_done()
            except queue.Empty:
                pass

    def shutdown(self):
        self._shutdown.set()
        # daj chwilę na domknięcie
        time.sleep(0.05)
        try:
            self.engine.stop()
        except Exception:
            pass


# --- Główny menedżer ---

class TTSManager:
    """
    Jednolity interfejs TTS:
    - NVDA (jeśli dostępne) = natychmiastowe przerwania
    - pyttsx3 fallback = wątek + kolejka + interrupt
    API:
      speak(text, interrupt=False)
      announce(text)   # krótkie, przerywa poprzednie
      narrate(text)    # długie, nie przerywa
      stop()
      set_rate/volume/voice (dla pyttsx3)
    """
    def __init__(self):
        self._nvda = _NVDAClient()
        self._use_nvda = (os.name == "nt") and self._nvda.available

        self._py_worker = None
        if not self._use_nvda:
            self._py_worker = _Pyttsx3Worker(rate_boost=100, max_rate=350, volume=1.0, voice_id=None)
            self._py_worker.start()

    # --- Public API ---

    def speak(self, text: str, interrupt: bool = False):
        if not text:
            return
        if self._use_nvda:
            if interrupt:
                self._nvda.cancel()
            self._nvda.speak(text)
        else:
            if self._py_worker is None or not self._py_worker.is_alive():
                self._py_worker = _Pyttsx3Worker(rate_boost=100, max_rate=350, volume=1.0, voice_id=None)
                self._py_worker.start()
            self._py_worker.speak(text, interrupt=interrupt)

    def announce(self, text: str):
        """Krótkie komunikaty UI (menu, listy, ruch) — zawsze przerywa."""
        self.speak(text, interrupt=True)

    def narrate(self, text: str):
        """Dłuższe wypowiedzi (dialogi, opisy) — nie przerywa."""
        self.speak(text, interrupt=False)

    def stop(self):
        """Natychmiast przerwij bieżące i wyczyść kolejkę."""
        if self._use_nvda:
            self._nvda.cancel()
        else:
            if self._py_worker:
                self._py_worker.stop_all()

    # --- Ustawienia pyttsx3 (gdy NVDA niedostępne) ---

    def set_rate(self, rate: int):
        if self._use_nvda or not self._py_worker:
            return
        try:
            self._py_worker.engine.setProperty("rate", int(rate))
        except Exception:
            pass

    def set_volume(self, volume: float):
        if self._use_nvda or not self._py_worker:
            return
        try:
            v = max(0.0, min(1.0, float(volume)))
            self._py_worker.engine.setProperty("volume", v)
        except Exception:
            pass

    def set_voice(self, voice_id: str):
        if self._use_nvda or not self._py_worker:
            return
        try:
            self._py_worker.engine.setProperty("voice", voice_id)
        except Exception:
            pass

    def shutdown(self):
        if self._use_nvda:
            return
        if self._py_worker:
            self._py_worker.shutdown()


# --- Globalna instancja i aliasy zgodne wstecz ---

manager = TTSManager()

def speak(text: str, interrupt: bool = False):
    """
    Zgodnie z Twoim oryginałem:
      speak("...")        -> czyści kolejkę i mówi (teraz realizowane przez announce)
    Teraz:
      speak("...", interrupt=False)  -> narracja (kolejkuje)
      speak("...", interrupt=True)   -> przerwij i powiedz teraz
    Dla pełnej zgodności starych wywołań, jeśli chcesz zawsze ciąć jak dawniej,
    zamień w kodzie miejsca „klikowe” na tts.announce(...).
    """
    # Jeśli chcesz odwzorować poprzednie „zawsze zastępuj”, użyj interrupt=True.
    manager.speak(text, interrupt=interrupt)

def announce(text: str):
    manager.announce(text)

def narrate(text: str):
    manager.narrate(text)

def stop():
    manager.stop()

def set_rate(rate: int):
    manager.set_rate(rate)

def set_volume(volume: float):
    manager.set_volume(volume)

def set_voice(voice_id: str):
    manager.set_voice(voice_id)

def shutdown():
    manager.shutdown()
