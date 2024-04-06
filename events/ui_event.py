from typing import Any
from events.types import UIEventType


class UIEvent:

    def __init__(
        self, guild_id: int, member_id: int, ui_event_type: UIEventType, payload: Any
    ):
        self.guild_id = guild_id
        self.member_id = member_id
        self.type = ui_event_type
        self.payload = payload

    def get_guild_id(self) -> int:
        return self.guild_id

    def get_member_id(self) -> int:
        return self.member_id

    def get_type(self) -> UIEventType:
        return self.type

    def get_payload(self) -> Any:
        return self.payload
