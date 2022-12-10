# Telegram Helper Module
## A helper module built on top of Telethon library for a personal project to extremely facilitate the following tasks:
- connect/disconnect to telegram client
- receive messages from all or some chats and set a callback function to handle it
- get all chats names and IDs
- send messages

## Basic Usage:
### Save all chats names and IDs in a JSON file
```python
from telegram import Telegram

if __name__ == "__main__":
    telegram = Telegram(api_id=API_ID, api_hash=API_HASH)
    telegram.connect()
    telegram.save_all_chats()
    telegram.disconnect()
```

### Set messages handler (handle new messages)
```python
from telegram import Telegram

def on_new_message(chat_id, message):
    print(f"New message from {chat_id}: {message}")

if __name__ == "__main__":
    telegram = Telegram(api_id=API_ID, api_hash=API_HASH)
    telegram.connect()
    # set message handler for all chats
    telegram.set_message_handler(on_new_message)
    # wait for messages (blocking)
    telegram.wait_for_messages()
```