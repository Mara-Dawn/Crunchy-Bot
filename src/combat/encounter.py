from collections import deque
from typing import Any

import discord

from combat.actors import Actor, Character, Opponent
from combat.enemies.types import EnemyType
from combat.skills.skill import Skill
from combat.skills.types import SkillInstance, StatusEffectType
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
    ):
        self.encounter = encounter
        self.opponent = opponent
        self.encounter_events = encounter_events
        self.combat_events = combat_events
        self.status_effects = status_effects
        self.combatants = combatants
        self.thread = thread

        self.initiative: list[Actor] = None
        self.beginning_actor = None

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
        self._new_round: bool = None
        self._new_turn: bool = None
        self._round_event_id_cutoff: int = None
        self._initialized: bool = None
        self._concluded: bool = None

        self.refresh_initiative()

    def add_combatant(self, character: Character):
        self.combatants.append(character)
        self.refresh_initiative()

    def apply_event(self, event: BotEvent):
        match event.type:
            case EventType.ENCOUNTER:
                event: EncounterEvent = event
                self.encounter_events.insert(0, event)
                self.apply_encounter_event(event)
            case EventType.COMBAT:
                event: CombatEvent = event
                self.combat_events.insert(0, event)
                self.apply_combat_event(event)
            case EventType.STATUS_EFFECT:
                event: StatusEffectEvent = event
                member_id = event.actor_id
                if member_id not in self.status_effects:
                    self.status_effects[member_id] = [event]
                else:
                    self.status_effects[member_id].insert(0, event)
                self.apply_status_event(event)

    def apply_encounter_event(self, event: EncounterEvent):
        match event.encounter_event_type:
            case EncounterEventType.INITIATE:
                self._initialized = True
            case EncounterEventType.NEW_ROUND | EncounterEventType.ENEMY_PHASE_CHANGE:
                self._new_round = True
                self.round_number += 1
                self._round_event_id_cutoff = event.id
                self._current_actor = None
                for actor in self.combatants:
                    if (
                        not actor.defeated
                        and not actor.leaving
                        and not actor.is_out
                        and actor not in self.active_combatants
                    ):
                        self.active_combatants.append(actor)
            case EncounterEventType.MEMBER_REQUEST_JOIN:
                pass
            case EncounterEventType.MEMBER_ENGAGE:
                pass
            case EncounterEventType.MEMBER_DEFEAT:
                actor = self.get_actor_by_id(event.member_id)
                if actor in self.active_combatants:
                    self.active_combatants.remove(actor)
                if actor not in self.defeated_combatants:
                    self.defeated_combatants.append(actor)
            case EncounterEventType.MEMBER_REVIVE:
                actor = self.get_actor_by_id(event.member_id)
                if actor in self.defeated_combatants:
                    self.defeated_combatants.remove(actor)
                if actor not in self.active_combatants:
                    self.active_combatants.append(actor)
            case EncounterEventType.FORCE_SKIP:
                pass
            case EncounterEventType.MEMBER_LEAVING:
                pass
            case EncounterEventType.MEMBER_OUT:
                actor = self.get_actor_by_id(event.member_id)
                if actor in self.active_combatants:
                    self.active_combatants.remove(actor)
            case EncounterEventType.MEMBER_DISENGAGE:
                actor = self.get_actor_by_id(event.member_id)
                if actor is not None:
                    self.combatants.remove(actor)
            case EncounterEventType.ENEMY_DEFEAT:
                pass
            case EncounterEventType.END:
                self._concluded = True
            case EncounterEventType.PENALTY50:
                pass
            case EncounterEventType.PENALTY75:
                pass

    def apply_combat_event(self, event: CombatEvent):
        self._new_round = False

        match event.combat_event_type:
            case CombatEventType.STATUS_EFFECT:
                pass
            case CombatEventType.STATUS_EFFECT_OUTCOME:
                pass
            case CombatEventType.MEMBER_TURN_SKIP:
                self._new_turn = False
            case CombatEventType.MEMBER_TURN:
                self._new_turn = False
            case CombatEventType.MEMBER_TURN_STEP:
                self._new_turn = False
            case CombatEventType.ENEMY_TURN:
                self._new_turn = False
            case CombatEventType.ENEMY_TURN_STEP:
                self._new_turn = False
            case CombatEventType.MEMBER_END_TURN | CombatEventType.ENEMY_END_TURN:
                self._last_actor = self._current_actor
                self._current_initiative.rotate(-1)
                self._current_actor = self._current_initiative[0]
                self._new_turn = True

    def apply_status_event(self, event: StatusEffectEvent):
        pass

    def refresh_initiative(self):
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

        if self._current_actor is None:
            self._current_actor = self.beginning_actor
        index = self.initiative.index(self._current_actor)
        self._current_initiative.rotate(-(index))

    def get_actor_by_id(self, actor_id: int) -> Actor:
        for actor in self.initiative:
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

            if self.new_round:
                self._current_actor = self.beginning_actor

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
    def new_round(self) -> bool:
        if self._new_round is not None:
            return self._new_round

        round_event_id = None
        for event in self.encounter_events:
            if event.encounter_event_type in [
                EncounterEventType.NEW_ROUND,
                EncounterEventType.ENEMY_PHASE_CHANGE,
            ]:
                round_event_id = event.id
                break

        if round_event_id is None:
            self._new_round = False
            return self._new_round

        if len(self.combat_events) == 0:
            self._new_round = True
            return self._new_round

        last_event = self.combat_events[0]
        self._new_round = last_event.id < round_event_id

        return self._new_round

    @property
    def new_turn(self) -> bool:
        if self._new_turn is not None:
            return self._new_turn

        if len(self.combat_events) == 0:
            self._new_turn = True
            return self._new_turn

        for event in self.combat_events:
            if event.combat_event_type in [
                CombatEventType.ENEMY_END_TURN,
                CombatEventType.MEMBER_END_TURN,
            ]:
                self._new_turn = True
                return self._new_turn
            elif event.combat_event_type not in [
                CombatEventType.STATUS_EFFECT,
                CombatEventType.STATUS_EFFECT_OUTCOME,
            ]:
                break

        self._new_turn = False

        return self._new_turn

    @property
    def round_event_id_cutoff(self) -> int:
        if self._round_event_id_cutoff is None:
            for event in self.encounter_events:
                if event.encounter_event_type in [
                    EncounterEventType.NEW_ROUND,
                ]:
                    self._round_event_id_cutoff = event.id
            self._round_event_id_cutoff = 0

        return self._round_event_id_cutoff

    @property
    def initiated(self) -> bool:
        if self._initialized is None:
            for event in self.encounter_events:
                if event.encounter_event_type == EncounterEventType.INITIATE:
                    self._initialized = True
            self._initialized = False
        return self._initialized

    @property
    def concluded(self) -> bool:
        if self._concluded is None:
            for event in self.encounter_events:
                if event.encounter_event_type == EncounterEventType.END:
                    self._concluded = True
                self._concluded = False
        return self._concluded


class TurnData:

    def __init__(
        self,
        actor: Actor,
        skill: Skill,
        damage_data: list[tuple[Actor, SkillInstance, int]],
        post_embed_data: dict[str, str] = None,
        description_override: str = None,
    ):
        self.actor = actor
        self.skill = skill
        self.damage_data = damage_data
        self.post_embed_data = post_embed_data
        self.description_override = description_override
