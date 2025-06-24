import os

class Config:
    def __init__(self):
        self.bot_token = os.environ['BOT_TOKEN']
        self.api_id = int(os.environ['API_ID'])
        self.api_hash = os.environ['API_HASH']

        input_chats = os.environ['INPUT_CHATS']
        output_chats = os.environ['OUTPUT_CHATS']

        self.input_chat_ids = [chat.strip() for chat in input_chats.split(',')]
        self.output_chat_ids = [chat.strip() for chat in output_chats.split(',')]
        self.message_pattern = os.environ.get('MESSAGE_PATTERN', None)
