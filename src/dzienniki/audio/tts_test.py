from time import sleep
from dzienniki.audio import tts

if __name__ == "__main__":
    tts.announce("Test przerwania. Za chwilę w połowie przerwę.")
    sleep(0.3)
    tts.announce("Drugi komunikat powinien natychmiast przerwać poprzedni.")
    sleep(0.8)
    tts.narrate("To jest narracja. Nie powinna przerwać poprzednich narracji.")
    tts.narrate("Druga narracja po sobie.")
    sleep(2.0)
    tts.stop()
