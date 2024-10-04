import datetime
from typing import Any

from combat.status_effects.types import StatusEffectType
from events.bot_event import BotEvent
from events.types import EventType


class StatusEffectEvent(BotEvent):

    def __init__(
        self,
        timestamp: datetime.datetime,
        guild_id: int,
        encounter_id: int,
        source_id: int,
        actor_id: int,
        status_type: StatusEffectType,
        stacks: int,
        value: float,
        id: int = None,
    ):
        super().__init__(timestamp, guild_id, EventType.STATUS_EFFECT, id)
        self.encounter_id = encounter_id
        self.source_id = source_id
        self.actor_id = actor_id
        self.status_type = status_type
        self.stacks = stacks
        self.value = value

    def get_causing_user_id(self) -> int:
        return self.actor_id

    def get_type_specific_args(self) -> list[Any]:
        return [self.source_id, self.status_type, self.stacks, self.value]

    @staticmethod
    def from_db_row(row: dict[str, Any]) -> "StatusEffectEvent":
        from datalayer.database import Database

        if row is None:
            return None
        return StatusEffectEvent(
            timestamp=datetime.datetime.fromtimestamp(
                row[Database.EVENT_TIMESTAMP_COL]
            ),
            guild_id=row[Database.EVENT_GUILD_ID_COL],
            encounter_id=row[Database.STATUS_EFFECT_EVENT_ENCOUNTER_ID_COL],
            source_id=row[Database.STATUS_EFFECT_EVENT_SOURCE_ID_COL],
            actor_id=row[Database.STATUS_EFFECT_EVENT_ACTOR_ID_COL],
            status_type=StatusEffectType(
                row[Database.STATUS_EFFECT_EVENT_STATUS_TYPE_COL]
            ),
            stacks=row[Database.STATUS_EFFECT_EVENT_STACKS_COL],
            value=row[Database.STATUS_EFFECT_EVENT_VALUE_COL],
            id=row[Database.EVENT_ID_COL],
        )
