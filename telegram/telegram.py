from telethon import TelegramClient, events
import json


class Telegram:
    def __init__(self, api_id: int, api_hash: str) -> None:
        self._API_ID: int = api_id
        self._API_HASH: str = api_hash
        # telegram client
        self._client: "TelegramClient|None" = None

    # ========== connect/disconnect ==========#
    def connect(self) -> None:
        """Connect to Telegram, start Telegram client. If connection failed, raise Exception."""
        try:
            self._client = TelegramClient("session", self._API_ID, self._API_HASH)
            self._client.start()
        except Exception as e:
            raise Exception(f"Failed to connect to Telegram: {e}")

    def disconnect(self) -> None:
        """Disconnect from Telegram, stop Telegram client."""
        self._client.disconnect()

    # ========== get chats info  ==========#
    def save_all_chats(self) -> None:
        """Save all chats names and IDs to chats.json file"""
        # get all chats
        chats = list(self._client.iter_dialogs())
        chats_info = {int(str(chat.id)[4:]): chat.name for chat in chats}
        # save to json
        try:
            print(f"{len(chats)} chats found...", end=" ")
            with open("chats.json", "w", encoding="utf-8") as f:
                json.dump(chats_info, f, indent=2)
                print("Saved to chats.json")
        except Exception as e:
            print(f"Failed: {e}")

    def save_all_channels(self) -> None:
        """Save all channels names and IDs to channels.json file"""
        # get all channels
        channels = list(
            filter(lambda dialog: dialog.is_channel, self._client.iter_dialogs())
        )
        channels_info = {int(str(channel.id)[4:]): channel.name for channel in channels}
        # save to json
        try:
            print(f"{len(channels)} channels found...", end=" ")
            with open("channels.json", "w", encoding="utf-8") as f:
                json.dump(channels_info, f, indent=2)
                print("Saved to channels.json")
        except Exception as e:
            print(f"Failed: {e}")

    # ========== message event handler ==========#
    def set_message_handler(
        self, message_handler: "function", chats: "list[int] | None" = None
    ) -> None:
        """Set message handler. If chats is None, handler will be called for all messages

        Args:
            message_handler (function): a function that will be called when new message received, must have 2 parameters: chat_id and message
            chats (list[int], optional): IDs of all needed chats. Defaults is None.
        """
        @self._client.on(events.NewMessage(chats=chats))
        async def async_message_handler(event):
            message_handler(int(str(event.chat_id)[4:]), event.raw_text)

    # ========== send message ==========#
    async def send_message(self, receiver: "str|int", message: str) -> None:
        """send message to receiver, if failed, raise Exception

        Args:
            receiver (str|int): receiver ID or username
            message (str): message to send
        """
        try:
            self._client.loop.run_until_complete(
                await self._client.send_message(receiver, message)
            )
        except Exception as e:
            raise Exception(f"Failed to send message: {e}")

    # ========== wait messages ==========#
    def wait_messages(self):
        """start waiting for messages (blocking function)"""
        print("Listening for messages...")
        self._client.run_until_disconnected()
