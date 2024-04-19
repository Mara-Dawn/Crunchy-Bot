import datetime

import tiktoken


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
        self.backstory = system_message
        self.system_message = ChatMessage(
            ChatMessage.SYSTEM_ROLE, system_message, datetime.datetime.now()
        )
        self.encoding = tiktoken.encoding_for_model("gpt-4-turbo")
        self.summary = ""

    def get_token_count(self) -> int:

        total_tokens = len(self.encoding.encode(self.system_message.message))

        for message in self.chat_log:
            total_tokens += len(self.encoding.encode(message.message))

        return total_tokens

    def add_summary(self, message: str):
        self.summary += " " + message

        system_message = (
            self.backstory
            + "\nThis is a summary of your previous conversation you should keep in mind:\n"
            + self.summary
        )

        self.system_message = ChatMessage(
            ChatMessage.SYSTEM_ROLE, system_message, datetime.datetime.now()
        )

    def add_user_message(self, message: str):
        self.chat_log.append(
            ChatMessage(ChatMessage.USER_ROLE, message, datetime.datetime.now())
        )

    def add_assistant_message(self, message: str):
        self.chat_log.append(
            ChatMessage(ChatMessage.ASSISTANT_ROLE, message, datetime.datetime.now())
        )

    def summarize(self, token_threshold: int) -> list[dict[str, str]]:
        system_message = (
            "You will be provided with a list of messages (delimited with XML tags) "
            "between Mistress Crunch and other users. Provide a concise summary of what was talked about within one paragraph."
        )
        messages = []
        data = {}
        data[self.ROLE_KEY] = ChatMessage.SYSTEM_ROLE
        data[self.CONTENT_KEY] = system_message
        messages.append(data)

        summary_messages = ""

        total_tokens = len(self.encoding.encode(self.system_message.message))

        remaining_messages = []

        for message in self.chat_log:
            if (
                total_tokens >= token_threshold
                and message.role == ChatMessage.USER_ROLE
            ):
                remaining_messages.append(message)
                continue
            total_tokens += len(self.encoding.encode(message.message))
            summary_messages += "<message>" + message.message + "</message>"

        self.chat_log = remaining_messages

        data = {}
        data[self.ROLE_KEY] = ChatMessage.USER_ROLE
        data[self.CONTENT_KEY] = summary_messages
        messages.append(data)

        return messages

    def get_request_data(self) -> list[dict[str, str]]:
        messages = []

        data_entry = {}
        data_entry[self.ROLE_KEY] = self.system_message.role
        data_entry[self.CONTENT_KEY] = self.system_message.message
        messages.append(data_entry)

        for message in self.chat_log:
            data_entry = {}
            data_entry[self.ROLE_KEY] = message.role
            data_entry[self.CONTENT_KEY] = message.message
            messages.append(data_entry)

        return messages

    def get_last_message_timestamp(self) -> datetime.datetime:
        return self.chat_log[-1].timestamp
