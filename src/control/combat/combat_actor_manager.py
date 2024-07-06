import discord
from combat.actors import Actor, Character, Opponent
from combat.enemies.enemy import Enemy
from combat.gear.types import CharacterAttribute, GearModifierType
from combat.skills.skill import Skill
from combat.skills.status_effect import ActiveStatusEffect
from combat.skills.types import SkillEffect, SkillType, StatusEffectType
from config import Config
from control.combat.object_factory import ObjectFactory
from control.controller import Controller
from control.logger import BotLogger
from control.service import Service
from datalayer.database import Database
from discord.ext import commands
from events.bot_event import BotEvent
from events.combat_event import CombatEvent
from events.encounter_event import EncounterEvent
from events.status_effect_event import StatusEffectEvent
from events.types import CombatEventType, EncounterEventType


class CombatActorManager(Service):

    def __init__(
        self,
        bot: commands.Bot,
        logger: BotLogger,
        database: Database,
        controller: Controller,
    ):
        super().__init__(bot, logger, database)
        self.controller = controller
        self.factory: ObjectFactory = self.controller.get_service(ObjectFactory)
        self.log_name = "Combat Skills"

    async def listen_for_event(self, event: BotEvent):
        pass

    async def get_actor_current_hp(
        self, actor: Actor, combat_events: list[CombatEvent]
    ):
        health = actor.max_hp

        for event in reversed(combat_events):
            if event.target_id != actor.id:
                continue
            if event.skill_type is None:
                continue
            if event.combat_event_type == CombatEventType.STATUS_EFFECT:
                continue
            if event.combat_event_type == CombatEventType.STATUS_EFFECT_OUTCOME:
                status_effect = await self.factory.get_status_effect(event.skill_type)
                skill_effect = status_effect.damage_type
            else:
                base_skill = await self.factory.get_base_skill(event.skill_type)
                skill_effect = base_skill.skill_effect

            match skill_effect:
                case SkillEffect.PHYSICAL_DAMAGE:
                    health -= event.skill_value
                case SkillEffect.MAGICAL_DAMAGE:
                    health -= event.skill_value
                case SkillEffect.STATUS_EFFECT_DAMAGE:
                    health -= event.skill_value
                case SkillEffect.HEALING:
                    health += event.skill_value
            health = min(health, actor.max_hp)

            if health <= 0:
                return 0
        return int(health)

    async def get_active_status_effects(
        self,
        id: int,
        status_effects: dict[int, list[StatusEffectEvent]],
        combat_events: list[CombatEvent],
    ) -> list[ActiveStatusEffect]:
        active_status_effects: dict[StatusEffectType, list[ActiveStatusEffect]] = {}
        active_status_effects = []

        if id not in status_effects:
            return active_status_effects

        actor_status_effects = status_effects[id]
        stacks = {event.id: event.stacks for event in actor_status_effects}

        for combat_event in combat_events:
            if combat_event.combat_event_type != CombatEventType.STATUS_EFFECT:
                continue

            status_id = combat_event.skill_id
            if status_id not in stacks:
                continue

            stacks[status_id] += combat_event.skill_value

        for event in actor_status_effects:
            status_effect = await self.factory.get_status_effect(event.status_type)
            active_status_effect = ActiveStatusEffect(
                status_effect, event, stacks[event.id]
            )
            # if event.status_type not in active_status_effects:
            #     active_status_effects = [active_status_effect]
            # else:
            #     if status_effect.override and stacks[event.id] > 0:
            #         continue
            #
            #     users_with_active_status = [
            #         element.event.get_causing_user_id
            #         for element in active_status_effects[event.status_type]
            #     ]
            #     if (
            #         status_effect.override_by_actor
            #         and event.get_causing_user_id in users_with_active_status
            #     ):
            #         continue

            active_status_effects.append(active_status_effect)

        # active_status_effects = [x for v in active_status_effects.values() for x in v]

        return active_status_effects

    async def get_opponent(
        self,
        enemy: Enemy,
        enemy_level: int,
        max_hp: int,
        encounter_events: list[EncounterEvent],
        combat_events: list[CombatEvent],
        status_effects: dict[int, list[StatusEffectEvent]],
    ) -> Opponent:
        defeated = False
        encounter_id = None
        id = -1
        for event in encounter_events:
            if encounter_id is None:
                encounter_id = event.encounter_id
            if event.encounter_event_type == EncounterEventType.ENEMY_DEFEAT:
                defeated = True
                break

        skills = []
        for skill_type in enemy.skill_types:
            skill = await self.factory.get_enemy_skill(skill_type)
            skills.append(skill)

        skill_cooldowns = self.get_skill_cooldowns(id, skills, combat_events)
        skill_stacks_used = await self.database.get_opponent_skill_stacks_used(
            encounter_id
        )
        active_status_effects = await self.get_active_status_effects(
            id, status_effects, combat_events
        )

        return Opponent(
            id=id,
            enemy=enemy,
            level=enemy_level,
            max_hp=max_hp,
            skills=skills,
            skill_cooldowns=skill_cooldowns,
            skill_stacks_used=skill_stacks_used,
            status_effects=active_status_effects,
            defeated=defeated,
        )

    async def get_character(
        self,
        member: discord.Member,
        encounter_events: list[EncounterEvent] = None,
        combat_events: list[CombatEvent] = None,
        status_effects: dict[int, StatusEffectEvent] = None,
    ) -> Character:
        if encounter_events is None:
            encounter_events = []

        if combat_events is None:
            combat_events = []

        if status_effects is None:
            status_effects = {}

        defeated = False
        timed_out = False
        for event in encounter_events:
            if (
                event.encounter_event_type == EncounterEventType.MEMBER_DEFEAT
                and event.member_id == member.id
            ):
                defeated = True
            if (
                event.encounter_event_type == EncounterEventType.MEMBER_TIMEOUT
                and event.member_id == member.id
            ):
                timed_out = True

        equipment = await self.database.get_user_equipment(member.guild.id, member.id)

        weapon_skills = equipment.weapon.base.skills

        skill_slots = {}

        for slot, skill_type in enumerate(weapon_skills):
            skill = await self.factory.get_weapon_skill(
                skill_type, equipment.weapon.rarity, equipment.weapon.level
            )
            skill_slots[slot] = skill

        equipped_skills = await self.database.get_user_equipped_skills(
            member.guild.id, member.id
        )

        for index in range(4):
            if index not in skill_slots:
                skill_slots[index] = equipped_skills[index]

        skills = [skill for skill in skill_slots.values() if skill is not None]

        skill_cooldowns = self.get_skill_cooldowns(member.id, skills, combat_events)
        skill_stacks_used = await self.database.get_user_skill_stacks_used(
            member.guild.id, member.id
        )

        active_status_effects = await self.get_active_status_effects(
            member.id, status_effects, combat_events
        )

        character = Character(
            member=member,
            skill_slots=skill_slots,
            skill_cooldowns=skill_cooldowns,
            skill_stacks_used=skill_stacks_used,
            status_effects=active_status_effects,
            equipment=equipment,
            defeated=defeated,
            timed_out=timed_out,
        )
        return character

    def get_undefeated_actors(self, actors: list[Actor]):
        return [actor for actor in actors if not actor.defeated]

    def get_skill_cooldowns(
        self, actor_id: int, skills: list[Skill], combat_events: list[CombatEvent]
    ) -> dict[SkillType, int]:
        cooldowns = {}
        last_used = 0
        for event in combat_events:
            if event.member_id == actor_id:
                if event.skill_type is not None:
                    skill_type = event.skill_type
                    if skill_type not in cooldowns:
                        cooldowns[skill_type] = max(0, last_used - 1)
                if event.combat_event_type in [
                    CombatEventType.ENEMY_END_TURN,
                    CombatEventType.MEMBER_END_TURN,
                ]:
                    last_used += 1

        round_count = last_used

        skill_data = {}

        for skill in skills:
            last_used = None
            skill_type = skill.base_skill.skill_type
            if skill_type in cooldowns:
                last_used = cooldowns[skill_type]
            elif (
                skill.base_skill.initial_cooldown is not None
                and skill.base_skill.initial_cooldown > 0
            ):
                last_used = (
                    -skill.base_skill.initial_cooldown
                    + round_count
                    + skill.base_skill.cooldown
                )

            skill_data[skill_type] = last_used
        return skill_data

    def get_encounter_scaling(self, actor: Actor, combatant_count: int = 1) -> float:
        encounter_scaling = 1
        if actor.is_enemy:
            return encounter_scaling

        if combatant_count > 1:
            encounter_scaling = (
                1 / combatant_count * Config.CHARACTER_ENCOUNTER_SCALING_FACOTR
            )
        return encounter_scaling

    async def get_skill_damage_after_defense(
        self, actor: Actor, skill: Skill, incoming_damage: int
    ) -> float:
        return await self.get_damage_after_defense(
            actor, skill.base_skill.skill_effect, incoming_damage
        )

    async def get_damage_after_defense(
        self, actor: Actor, skill_effect: SkillEffect, incoming_damage: int
    ) -> float:
        if actor.is_enemy:
            return await self.get_opponent_damage_after_defense(
                actor, skill_effect, incoming_damage
            )
        else:
            return await self.get_character_damage_after_defense(
                actor, skill_effect, incoming_damage
            )

    async def get_character_damage_after_defense(
        self, character: Character, skill_effect: SkillEffect, incoming_damage: int
    ) -> float:
        modifier = 1
        flat_reduction = 0

        match skill_effect:
            case SkillEffect.PHYSICAL_DAMAGE:
                modifier -= character.equipment.attributes[
                    CharacterAttribute.DAMAGE_REDUCTION
                ]
                flat_reduction = int(
                    character.equipment.gear_modifiers[GearModifierType.ARMOR] / 4
                )
            case SkillEffect.NEUTRAL_DAMAGE:
                modifier -= character.equipment.attributes[
                    CharacterAttribute.DAMAGE_REDUCTION
                ]
            case SkillEffect.MAGICAL_DAMAGE:
                modifier -= character.equipment.attributes[
                    CharacterAttribute.DAMAGE_REDUCTION
                ]
            case SkillEffect.STATUS_EFFECT_DAMAGE:
                modifier -= character.equipment.attributes[
                    CharacterAttribute.DAMAGE_REDUCTION
                ]
            case SkillEffect.HEALING:
                pass

        return int(max(0, ((incoming_damage * modifier) - flat_reduction)))

    async def get_opponent_damage_after_defense(
        self, opponent: Opponent, skill_effect: SkillEffect, incoming_damage: int
    ) -> float:
        modifier = 1
        flat_reduction = 0

        match skill_effect:
            case SkillEffect.PHYSICAL_DAMAGE:
                modifier -= opponent.enemy.attributes[
                    CharacterAttribute.DAMAGE_REDUCTION
                ]
            case SkillEffect.NEUTRAL_DAMAGE:
                modifier -= opponent.enemy.attributes[
                    CharacterAttribute.DAMAGE_REDUCTION
                ]
            case SkillEffect.MAGICAL_DAMAGE:
                modifier -= opponent.enemy.attributes[
                    CharacterAttribute.DAMAGE_REDUCTION
                ]
            case SkillEffect.STATUS_EFFECT_DAMAGE:
                modifier -= opponent.enemy.attributes[
                    CharacterAttribute.DAMAGE_REDUCTION
                ]
            case SkillEffect.HEALING:
                pass

        return int(max(0, ((incoming_damage - flat_reduction) * modifier)))
