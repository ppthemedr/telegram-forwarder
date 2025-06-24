print("⚙️  Starting forwarder.py...")

import os
print("📦 ENV:", {k: os.getenv(k) for k in [
    "BOT_TOKEN", "API_ID", "API_HASH", "INPUT_CHATS", "OUTPUT_CHATS", "MESSAGE_PATTERN"
]})
import logging
from telethon import TelegramClient, events, errors
from telethon.tl.types import InputChannel

# ---------------------------------------------
# CONFIGURATION
# ---------------------------------------------
class Config:
    def __init__(self):
        self.bot_token = os.environ["BOT_TOKEN"]
        self.api_id    = int(os.environ["API_ID"])
        self.api_hash  = os.environ["API_HASH"]

        self.input_chat_ids  = [c.strip() for c in os.environ["INPUT_CHATS"].split(",")]
        self.output_chat_ids = [c.strip() for c in os.environ["OUTPUT_CHATS"].split(",")]
        self.message_pattern = os.environ.get("MESSAGE_PATTERN") or None

        # Optional: logging level (DEBUG, INFO, WARNING…)
        self.log_level = os.environ.get("LOG_LEVEL", "INFO").upper()

# ---------------------------------------------
# FORWARDER
# ---------------------------------------------
class Forwarder:
    def __init__(self, cfg: Config):
        self.cfg      = cfg
        self.log      = logging.getLogger("Forwarder")
        self.telegram  = TelegramClient("sessions/bot", cfg.api_id, cfg.api_hash)

        self.in_chats, self.out_chats = [], []

    # ------------- lifecycle -------------------
    def start(self):
        self._setup_logging()
        self.telegram.start(bot_token=self.cfg.bot_token)
        self._load_chats()
        self._run_loop()

    # ------------- intern ----------------------
    def _setup_logging(self):
        logging.basicConfig(
            level=self.cfg.log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        # Telethon debug (optioneel, lawaaierig)
        if self.cfg.log_level == "DEBUG":
            logging.getLogger("telethon").setLevel(logging.DEBUG)

    def _load_chats(self):
        dialogs = self.telegram.loop.run_until_complete(self.telegram.get_dialogs())

        self.log.debug("Loading input chats: %s", self.cfg.input_chat_ids)
        for chat_id in self.cfg.input_chat_ids:
            dlg = next((d for d in dialogs if
                        getattr(d.entity, "username", None) == chat_id or
                        str(d.entity.id) == chat_id), None)
            if not dlg:
                raise RuntimeError(f"Input chat '{chat_id}' not found")
            self.in_chats.append(InputChannel(dlg.entity.id, dlg.entity.access_hash))

        self.log.debug("Loading output chats: %s", self.cfg.output_chat_ids)
        for chat_id in self.cfg.output_chat_ids:
            dlg = next((d for d in dialogs if
                        getattr(d.entity, "username", None) == chat_id or
                        str(d.entity.id) == chat_id), None)
            if not dlg:
                raise RuntimeError(f"Output chat '{chat_id}' not found")
            self.out_chats.append(InputChannel(dlg.entity.id, dlg.entity.access_hash))

    def _run_loop(self):
        @self.telegram.on(events.NewMessage(chats=self.in_chats,
                                            pattern=self.cfg.message_pattern))
        async def handler(event):
            self.log.info("Forwarding message %s from chat %s",
                          event.id, event.chat_id)
            for dest in self.out_chats:
                try:
                    await self.telegram.forward_messages(dest, event.message)
                    self.log.debug(" → forwarded to %s", dest.channel_id)
                except errors.rpcerrorlist.ChatWriteForbiddenError:
                    self.log.error("Bot lacks permission to send to %s", dest.channel_id)
                except Exception as ex:
                    self.log.exception("Unexpected error during forward: %s", ex)

        self.log.info("Listening on %d input chat(s)", len(self.in_chats))
        self.log.info("Forwarding to %d output chat(s)", len(self.out_chats))
        self.telegram.run_until_disconnected()

# -------------------------------------------------
# MAIN
# -------------------------------------------------
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    try:
        Forwarder(Config()).start()
    except Exception as e:
        logging.exception("Fatal error during startup")
        raise
