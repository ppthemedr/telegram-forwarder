import os
import logging
from telethon import TelegramClient, events
from telethon.tl.types import InputChannel

# CONFIGURATION LOADING
class Config:
    def __init__(self):
        self.bot_token = os.environ['BOT_TOKEN']
        self.api_id = int(os.environ['API_ID'])
        self.api_hash = os.environ['API_HASH']
        self.input_chat_ids = [c.strip() for c in os.environ['INPUT_CHATS'].split(',')]
        self.output_chat_ids = [c.strip() for c in os.environ['OUTPUT_CHATS'].split(',')]
        self.message_pattern = os.environ.get('MESSAGE_PATTERN', None)

# FORWARDER CLASS
class Forwarder:
    def __init__(self, config):
        self.config = config
        self.telegram = TelegramClient("bot", config.api_id, config.api_hash)
        self.input_chats = []
        self.output_chats = []

    def start(self):
        self.__connect()
        self.__load_chats()
        self.__forward_loop()

    def __connect(self):
        self.telegram.start(bot_token=self.config.bot_token)

    def __load_chats(self):
        dialogs = self.telegram.loop.run_until_complete(self.telegram.get_dialogs())

        for chat_id in self.config.input_chat_ids:
            dialog = next((d for d in dialogs if getattr(d.entity, 'username', None) == chat_id or str(d.entity.id) == chat_id), None)
            if dialog:
                self.input_chats.append(InputChannel(dialog.entity.id, dialog.entity.access_hash))
            else:
                raise RuntimeError(f"Input chat '{chat_id}' not found.")

        for chat_id in self.config.output_chat_ids:
            dialog = next((d for d in dialogs if getattr(d.entity, 'username', None) == chat_id or str(d.entity.id) == chat_id), None)
            if dialog:
                self.output_chats.append(InputChannel(dialog.entity.id, dialog.entity.access_hash))
            else:
                raise RuntimeError(f"Output chat '{chat_id}' not found.")

    def __forward_loop(self):
        @self.telegram.on(events.NewMessage(chats=self.input_chats, pattern=self.config.message_pattern))
        async def handler(event):
            logging.info("Forwarding message")
            for output_chat in self.output_chats:
                await self.telegram.forward_messages(output_chat, event.message)

        logging.info(f"Listening to {len(self.input_chats)} input chats")
        logging.info(f"Forwarding to {len(self.output_chats)} output chats")

        self.telegram.run_until_disconnected()

# MAIN ENTRYPOINT
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    config = Config()
    forwarder = Forwarder(config)
    forwarder.start()
