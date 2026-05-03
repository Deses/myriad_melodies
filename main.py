from bot import RhythmBot
from config import Config
from overlay import Overlay

if __name__ == "__main__":
    config = Config()
    bot = RhythmBot(config)
    overlay = Overlay(config, bot)
    try:
        bot.start()
        overlay.run()
    except KeyboardInterrupt:
        print("\n[main] stopping...")
    finally:
        bot.stop()
        print("[main] done")
