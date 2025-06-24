import os
import logging
from telethon import TelegramClient, events
from telethon.tl.types import InputChannel

# -------------------------------------------------
# CONFIGURATION CLASS
# -------------------------------------------------
class Config:
    def __init__(self):
        self.bot_token = os.environ["BOT_TOKEN"]
        self.api_id    = int(os.environ["API_ID"])
        self.api_hash  = os.environ["API_HASH"]

        self.input_chat_ids  = [c.strip() for c in os.environ["INPUT_CHATS"].split(",")]
        self.output_chat_ids = [c.strip() for c in os.environ["OUTPUT_CHATS"].split(",")]
        self.message_pattern = os.environ.get("MESSAGE_PATTERN", None)

# -------------------------------------------------
# FORWARDER CLASS
# -------------------------------------------------
class Forwarder:
    def __init__(self, cfg: Config):
        self.cfg       = cfg
        self.telegram  = TelegramClient("bot", cfg.api_id, cfg.api_hash)
        self.in_chats  = []
        self.out_chats = []

    # ---------- lifecycle ----------
    def start(self):
        self.telegram.start(bot_token=self.cfg.bot_token)
        self._load_chats()
        self._run_loop()

    # ---------- helpers ----------
    def _load_chats(self):
        dialogs = self.telegram.loop.run_until_complete(self.telegram.get_dialogs())

        # input
        for chat_id in self.cfg.input_chat_ids:
            dlg = next((d for d in dialogs if
                        getattr(d.entity, "username", None) == chat_id or
                        str(d.entity.id) == chat_id), None)
            if not dlg:
                raise RuntimeError(f"Input chat '{chat_id}' not found")
            self.in_chats.append(InputChannel(dlg.entity.id, dlg.entity.access_hash))

        # output
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
            logging.info("Forwarding message")
            for dest in self.out_chats:
                await self.telegram.forward_messages(dest, event.message)

        logging.info(f"Listening on {len(self.in_chats)} input chat(s)")
        logging.info(f"Forwarding to {len(self.out_chats)} output chat(s)")
        self.telegram.run_until_disconnected()

# -------------------------------------------------
# MAIN
# -------------------------------------------------
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")
    Forwarder(Config()).start()
