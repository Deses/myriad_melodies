from bot import RhythmBot
from config import Config
from overlay import Overlay

if __name__ == "__main__":
    config = Config()
    bot = RhythmBot(config)
    overlay = Overlay(config, bot)
    bot.start()
    overlay.run()  # bloque sur mainloop tkinter
    bot.stop()
