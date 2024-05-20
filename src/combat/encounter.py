from collections import deque
from typing import Any

import discord
from combat.actors import Actor, Character, Opponent
from combat.enemies.types import EnemyType
from events.combat_event import CombatEvent
from events.encounter_event import EncounterEvent
from events.types import EncounterEventType


class Encounter:

    def __init__(
        self,
        guild_id: int,
        enemy_type: EnemyType,
        max_hp: int,
        message_id: int = None,
        channel_id: int = None,
        id: int = None,
    ):
        self.guild_id = guild_id
        self.enemy_type = enemy_type
        self.max_hp = max_hp
        self.message_id = message_id
        self.channel_id = channel_id
        self.id = id

    @staticmethod
    def from_db_row(row: dict[str, Any]) -> "Encounter":
        from datalayer.database import Database

        if row is None:
            return None

        return Encounter(
            guild_id=int(row[Database.ENCOUNTER_GUILD_ID_COL]),
            enemy_type=EnemyType(row[Database.ENCOUNTER_ENEMY_TYPE_COL]),
            max_hp=int(row[Database.ENCOUNTER_ENEMY_HEALTH_COL]),
            message_id=int(row[Database.ENCOUNTER_MESSAGE_ID_COL]),
            channel_id=int(row[Database.ENCOUNTER_CHANNEL_ID_COL]),
            id=int(row[Database.ENCOUNTER_ID_COL]),
        )


class EncounterContext:

    def __init__(
        self,
        encounter: Encounter,
        opponent: Opponent,
        encounter_events: list[EncounterEvent],
        combat_events: list[CombatEvent],
        combatants: list[Character],
        thread: discord.Thread,
    ):
        self.encounter = encounter
        self.opponent = opponent
        self.encounter_events = encounter_events
        self.combat_events = combat_events
        self.combatants = combatants
        self.thread = thread

        self.actors: list[Actor] = []
        self.actors.extend(combatants)
        self.actors.append(opponent)
        self.actors = sorted(
            self.actors, key=lambda item: item.initiative, reverse=True
        )
        self.beginning_actor = self.actors[0]
        self.actors: deque[Actor] = deque(self.actors)

    def get_last_actor(self) -> Actor:
        if len(self.combat_events) <= 0:
            return None
        last_actor = self.combat_events[0].member_id

        for actor in self.actors:
            if actor.id == last_actor:
                return actor

    def get_current_actor(self) -> Actor:
        initiative_list = self.get_current_initiative()
        if len(initiative_list) <= 0:
            return None

        return initiative_list[0]

    def get_current_initiative(self) -> list[Actor]:
        last_actor = self.get_last_actor()
        if last_actor is None:
            return self.actors
        index = self.actors.index(last_actor)
        result = self.actors.copy()
        result.rotate(-(index + 1))
        return result

    def get_current_turn_number(self) -> int:
        return len(self.combat_events) + 1

    def is_concluded(self) -> bool:
        for event in self.encounter_events:
            if event.encounter_event_type == EncounterEventType.END:
                return True
        return False
