import datetime
from typing import Any

from combat.skills.types import SkillType

from events.bot_event import BotEvent
from events.types import CombatEventType, EncounterEventType, EventType


class CombatEvent(BotEvent):

    def __init__(
        self,
        timestamp: datetime.datetime,
        guild_id: int,
        encounter_id: int,
        member_id: int,
        target_id: int,
        skill_type: SkillType,
        skill_value: int,
        skill_id: int,
        combat_event_type: EncounterEventType,
        id: int = None,
    ):
        super().__init__(timestamp, guild_id, EventType.COMBAT, id)
        self.encounter_id = encounter_id
        self.member_id = member_id
        self.target_id = target_id
        self.skill_type = skill_type
        self.skill_value = skill_value
        self.skill_id = skill_id
        self.combat_event_type = combat_event_type
        self.id = id

    def get_causing_user_id(self) -> int:
        return self.member_id

    def get_type_specific_args(self) -> list[Any]:
        return [
            self.encounter_id,
            self.target_id,
            self.skill_type,
            self.skill_value,
            self.skill_id,
            self.combat_event_type,
        ]

    @staticmethod
    def from_db_row(row: dict[str, Any]) -> "CombatEvent":
        from datalayer.database import Database

        if row is None:
            return None

        return CombatEvent(
            timestamp=datetime.datetime.fromtimestamp(
                row[Database.EVENT_TIMESTAMP_COL]
            ),
            guild_id=row[Database.EVENT_GUILD_ID_COL],
            encounter_id=row[Database.COMBAT_EVENT_ENCOUNTER_ID_COL],
            member_id=row[Database.COMBAT_EVENT_MEMBER_ID],
            target_id=row[Database.COMBAT_EVENT_TARGET_ID],
            skill_type=(
                SkillType(row[Database.COMBAT_EVENT_SKILL_TYPE])
                if row[Database.COMBAT_EVENT_SKILL_TYPE] is not None
                else None
            ),
            skill_value=row[Database.COMBAT_EVENT_SKILL_VALUE],
            skill_id=row[Database.COMBAT_EVENT_SKILL_ID],
            combat_event_type=CombatEventType(row[Database.COMBAT_EVENT_TYPE_COL]),
            id=row[Database.EVENT_ID_COL],
        )
