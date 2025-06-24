import logging
from .config import Config          # <-- importeer de klasse
from .forwarder import Forwarder

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    cfg = Config()                  # <-- instantie maken
    forwarder = Forwarder(cfg)      # <-- geef object door
    forwarder.start()

if __name__ == "__main__":
    main()
