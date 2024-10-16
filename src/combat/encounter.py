from collections import deque
from dataclasses import dataclass
from typing import Any

import discord

from combat.actors import Actor, Character, Opponent
from combat.effects.effect import EmbedDataCollection
from combat.enemies.types import EnemyType
from combat.skills.skill import Skill, SkillInstance
from combat.status_effects.status_effect import StatusEffect
from combat.status_effects.types import StatusEffectType
from events.bot_event import BotEvent
from events.combat_event import CombatEvent
from events.encounter_event import EncounterEvent
from events.status_effect_event import StatusEffectEvent
from events.types import CombatEventType, EncounterEventType, EventType


class Encounter:

    def __init__(
        self,
        guild_id: int,
        enemy_type: EnemyType,
        enemy_level: int,
        max_hp: int,
        message_id: int = None,
        channel_id: int = None,
        owner_id: int = None,
        id: int = None,
    ):
        self.guild_id = guild_id
        self.enemy_type = enemy_type
        self.enemy_level = enemy_level
        self.max_hp = max_hp
        self.message_id = message_id
        self.channel_id = channel_id
        self.owner_id = owner_id
        self.id = id

    @staticmethod
    def from_db_row(row: dict[str, Any] | None) -> "Encounter":
        from datalayer.database import Database

        if row is None:
            return None

        return Encounter(
            guild_id=int(row[Database.ENCOUNTER_GUILD_ID_COL]),
            enemy_type=EnemyType(row[Database.ENCOUNTER_ENEMY_TYPE_COL]),
            enemy_level=int(row[Database.ENCOUNTER_ENEMY_LEVEL_COL]),
            max_hp=int(row[Database.ENCOUNTER_ENEMY_HEALTH_COL]),
            message_id=int(row[Database.ENCOUNTER_MESSAGE_ID_COL]),
            channel_id=int(row[Database.ENCOUNTER_CHANNEL_ID_COL]),
            owner_id=row[Database.ENCOUNTER_OWNER_ID_COL],
            id=int(row[Database.ENCOUNTER_ID_COL]),
        )


class EncounterContext:

    def __init__(
        self,
        encounter: Encounter,
        opponent: Opponent,
        encounter_events: list[EncounterEvent],
        combat_events: list[CombatEvent],
        status_effects: dict[int, list[StatusEffectEvent]],
        combatants: list[Character],
        thread: discord.Thread,
        owner_id: int | None = None,
    ):
        self.encounter = encounter
        self.opponent = opponent
        self.encounter_events = encounter_events
        self.combat_events = combat_events
        self.status_effects = status_effects
        self.combatants = combatants
        self.thread = thread
        self.owner_id = owner_id

        self.initiative: list[Actor] = None
        self.beginning_actor = None
        self.reset_initiative: bool = False

        self.active_combatants: list[Actor] = [
            actor
            for actor in self.combatants
            if not actor.defeated and not actor.is_out and actor.ready
        ]
        self.defeated_combatants: list[Actor] = [
            actor
            for actor in self.combatants
            if actor.defeated and not actor.is_out and actor.ready
        ]
        self.round_number: int = 0
        for event in self.encounter_events:
            if event.encounter_event_type in [
                EncounterEventType.NEW_ROUND,
            ]:
                self.round_number += 1

        self._current_actor: Actor = None
        self._last_actor: Actor = None
        self._combat_scale: int = None
        self._current_initiative: deque[Actor] = None
        self.round_event_id_cutoff: int = 0
        self.turn_event_id_cutoff: int = 0
        self._initiated: bool = None
        self._concluded: bool = None

        self.reset_initiative: bool = False

        self.current_turn_embed: discord.Embed = None

        self.min_participants: int = 1
        self.max_lvl: bool = False

        self.refresh_initiative()

    def add_event(self, event: BotEvent):
        match event.type:
            case EventType.ENCOUNTER:
                event: EncounterEvent = event
                self.encounter_events.insert(0, event)
            case EventType.COMBAT:
                event: CombatEvent = event
                self.combat_events.insert(0, event)
            case EventType.STATUS_EFFECT:
                event: StatusEffectEvent = event
                member_id = event.actor_id
                if member_id not in self.status_effects:
                    self.status_effects[member_id] = [event]
                else:
                    self.status_effects[member_id].insert(0, event)

    def refresh_initiative(self, reset: bool = False):
        self.initiative = []
        self.initiative.append(self.opponent)

        self._combat_scale = 0
        for actor in self.combatants:
            if actor.ready and not actor.is_out:
                self._combat_scale += 1
                self.initiative.append(actor)

        self.initiative = sorted(
            self.initiative, key=lambda item: item.initiative, reverse=True
        )
        self.beginning_actor = self.initiative[0]

        self._current_initiative = deque(self.initiative)

        if self.initiated:
            if self._current_actor is None or reset:
                self._current_actor = self.beginning_actor
            index = self.initiative.index(self._current_actor)
            self._current_initiative.rotate(-(index))

    def get_actor_by_id(self, actor_id: int) -> Actor:
        for actor in self.actors:
            if actor.id == actor_id:
                return actor
        return None

    def get_applied_status_count(
        self, actor_id: int, status_type: StatusEffectType, count_stacks: bool = False
    ) -> int:
        count = 0

        if actor_id not in self.status_effects:
            return count

        for event in self.status_effects[actor_id]:
            if event.status_type == status_type and event.stacks > 0:
                if count_stacks:
                    count = +event.stacks
                else:
                    count += 1
        return count

    @property
    def last_actor(self) -> Actor:
        if self._last_actor is not None:
            return self._last_actor

        new_round_event_id = None
        # Reset initiative after boss phase change
        for event in self.encounter_events:
            if event.encounter_event_type in [
                EncounterEventType.NEW_ROUND,
            ]:
                new_round_event_id = event.id
                break
            if event.encounter_event_type in [
                EncounterEventType.ENEMY_PHASE_CHANGE,
            ]:
                return None

        relevant_combat_events = self.combat_events
        if new_round_event_id is not None:
            relevant_combat_events = [
                event for event in self.combat_events if event.id > new_round_event_id
            ]

        if len(relevant_combat_events) <= 0:
            return None

        last_actor = None

        for event in relevant_combat_events:
            if event.combat_event_type in [
                CombatEventType.ENEMY_END_TURN,
                CombatEventType.MEMBER_END_TURN,
            ]:
                last_actor = event.member_id
                break

        if last_actor is None:
            return None

        for actor in self.initiative:
            if actor.id == last_actor:
                self._last_actor = actor
                return actor

    @property
    def actors(self) -> list[Actor]:
        return self.combatants + [self.opponent]

    @property
    def combat_scale(self) -> int:
        if self._combat_scale is None:
            self._combat_scale = len(
                [actor for actor in self.combatants if not actor.is_out and actor.ready]
            )
        return self._combat_scale

    @property
    def current_actor(self) -> Actor:
        if self._current_actor is None:

            initiative_list = self.current_initiative
            if len(initiative_list) <= 0:
                return None

            self._current_actor = initiative_list[0]

        return self._current_actor

    @property
    def current_initiative(self) -> list[Actor]:
        if self._current_initiative is None:
            self.refresh_initiative()

        return self._current_initiative

    @property
    def initiated(self) -> bool:
        if self._initiated is None:
            for event in self.encounter_events:
                if event.encounter_event_type == EncounterEventType.INITIATE:
                    self._initiated = True
                    return self._initiated
            self._initiated = False
        return self._initiated

    @property
    def concluded(self) -> bool:
        if self._concluded is None:
            for event in self.encounter_events:
                if event.encounter_event_type == EncounterEventType.END:
                    self._concluded = True
                    return self._concluded
                self._concluded = False
        return self._concluded


@dataclass
class TurnDamageData:
    target: Actor
    instance: SkillInstance
    hp: int
    _applied_status_effects: list[tuple[StatusEffect, int]] | None = None

    @property
    def applied_status_effects(self) -> list[tuple[StatusEffect, int]]:
        if self._applied_status_effects is None:
            self._applied_status_effects = []

        return self._applied_status_effects


@dataclass
class TurnData:
    actor: Actor
    skill: Skill
    damage_data: list[TurnDamageData]
    post_embed_data: EmbedDataCollection | None = None
    description_override: str | None = None
