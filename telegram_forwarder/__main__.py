import logging
from .config import Config          # ← importeer de klasse, niet het module
from .forwarder import Forwarder


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    cfg = Config()                  # ← instantie maken
    forwarder = Forwarder(cfg)      # ← object met attributes api_id, …
    forwarder.start()


if __name__ == "__main__":
    main()
