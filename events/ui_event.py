from typing import Any

from events.types import UIEventType


class UIEvent:

    def __init__(
        self,
        ui_event_type: UIEventType,
        payload: Any,
        view_id: int = None,
    ):
        self.type = ui_event_type
        self.payload = payload
        self.view_id = view_id

    def get_view_id(self) -> int:
        return self.view_id

    def get_type(self) -> UIEventType:
        return self.type

    def get_payload(self) -> Any:
        return self.payload
