import datetime


class ChatMessage:

    SYSTEM_ROLE = "system"
    USER_ROLE = "user"
    ASSISTANT_ROLE = "assistant"

    def __init__(self, role: str, message: str, timestamp: datetime.datetime):
        self.role = role
        self.message = message
        self.timestamp = timestamp


class ChatLog:

    ROLE_KEY = "role"
    CONTENT_KEY = "content"

    def __init__(self, system_message: str):
        self.chat_log: list[ChatMessage] = []
        self.chat_log.append(
            ChatMessage(
                ChatMessage.SYSTEM_ROLE, system_message, datetime.datetime.now()
            )
        )

    def add_user_message(self, message: str):
        self.chat_log.append(
            ChatMessage(ChatMessage.USER_ROLE, message, datetime.datetime.now())
        )

    def add_assistant_message(self, message: str):
        self.chat_log.append(
            ChatMessage(ChatMessage.ASSISTANT_ROLE, message, datetime.datetime.now())
        )

    def get_request_data(self) -> list[dict[str, str]]:
        messages = []

        for message in self.chat_log:
            data_entry = {}
            data_entry[self.ROLE_KEY] = message.role
            data_entry[self.CONTENT_KEY] = message.message
            messages.append(data_entry)

        return messages

    def get_last_message_timestamp(self) -> datetime.datetime:
        return self.chat_log[-1].timestamp
