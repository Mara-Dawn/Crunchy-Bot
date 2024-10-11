import contextlib
import datetime
from typing import Any

from combat.enchantments.types import EnchantmentType
from combat.skills.types import SkillType
from combat.status_effects.types import StatusEffectType
from events.bot_event import BotEvent
from events.types import CombatEventType, EventType


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
        display_value: int,
        skill_id: int,
        combat_event_type: CombatEventType,
        id: int = None,
    ):
        super().__init__(timestamp, guild_id, EventType.COMBAT, id)
        self.encounter_id = encounter_id
        self.member_id = member_id
        self.target_id = target_id
        self.skill_type = skill_type
        self.skill_value = skill_value
        self.display_value = display_value
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
            self.display_value,
            self.skill_id,
            self.combat_event_type,
        ]

    @staticmethod
    def from_db_row(row: dict[str, Any]) -> "CombatEvent":
        from datalayer.database import Database

        if row is None:
            return None

        skill_type = None

        skill_db_value = row[Database.COMBAT_EVENT_SKILL_TYPE]
        if skill_db_value is not None:
            with contextlib.suppress(Exception):
                skill_type = SkillType(skill_db_value)
            if skill_type is None:
                with contextlib.suppress(Exception):
                    skill_type = StatusEffectType(skill_db_value)
            if skill_type is None:
                with contextlib.suppress(Exception):
                    skill_type = EnchantmentType(skill_db_value)

        return CombatEvent(
            timestamp=datetime.datetime.fromtimestamp(
                row[Database.EVENT_TIMESTAMP_COL]
            ),
            guild_id=row[Database.EVENT_GUILD_ID_COL],
            encounter_id=row[Database.COMBAT_EVENT_ENCOUNTER_ID_COL],
            member_id=row[Database.COMBAT_EVENT_MEMBER_ID],
            target_id=row[Database.COMBAT_EVENT_TARGET_ID],
            skill_type=skill_type,
            skill_value=row[Database.COMBAT_EVENT_SKILL_VALUE],
            display_value=row[Database.COMBAT_EVENT_DISPLAY_VALUE],
            skill_id=row[Database.COMBAT_EVENT_SKILL_ID],
            combat_event_type=CombatEventType(row[Database.COMBAT_EVENT_TYPE_COL]),
            id=row[Database.EVENT_ID_COL],
        )
