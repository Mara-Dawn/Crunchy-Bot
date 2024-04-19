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
