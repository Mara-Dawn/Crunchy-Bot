import random

import discord
from combat.actors import Actor, Character, Opponent
from combat.encounter import EncounterContext, TurnData
from combat.enemies.enemy import Enemy
from combat.skills.skill import Skill
from combat.skills.types import SkillEffect, SkillInstance, SkillType
from control.combat.combat_skill_manager import CombatSkillManager
from control.controller import Controller
from control.logger import BotLogger
from control.service import Service
from datalayer.database import Database
from discord.ext import commands
from events.bot_event import BotEvent
from events.combat_event import CombatEvent
from events.encounter_event import EncounterEvent
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
        self.skill_manager: CombatSkillManager = self.controller.get_service(
            CombatSkillManager
        )
        self.log_name = "Combat Skills"

    async def listen_for_event(self, event: BotEvent):
        pass

    def get_skill(self, skill_type: SkillType) -> Skill:
        skill = globals()[skill_type]
        instance = skill()
        return instance

    async def get_actor_current_hp(
        self, actor: Actor, combat_events: list[CombatEvent]
    ):
        health = actor.max_hp

        for event in reversed(combat_events):
            if event.target_id != actor.id:
                continue
            if event.skill_type is None:
                continue
            base_skill = await self.skill_manager.get_base_skill(event.skill_type)
            match base_skill.skill_effect:
                case SkillEffect.PHYSICAL_DAMAGE:
                    health -= event.skill_value
                case SkillEffect.MAGICAL_DAMAGE:
                    health -= event.skill_value
                case SkillEffect.HEALING:
                    health += event.skill_value
                    health = min(health, actor.max_hp)

            if health <= 0:
                return 0
        return int(health)

    async def get_opponent(
        self,
        enemy: Enemy,
        enemy_level: int,
        max_hp: int,
        encounter_events: list[EncounterEvent],
        combat_events: list[CombatEvent],
    ) -> Opponent:
        defeated = False
        encounter_id = None
        for event in encounter_events:
            if encounter_id is None:
                encounter_id = event.encounter_id
            if event.encounter_event_type == EncounterEventType.ENEMY_DEFEAT:
                defeated = True
                break

        skills = []
        for skill_type in enemy.skill_types:
            skill = await self.skill_manager.get_enemy_skill(skill_type)
            skills.append(skill)

        skill_cooldowns = self.get_skill_cooldowns(None, skills, combat_events)
        skill_stacks_used = await self.database.get_opponent_skill_stacks_used(
            encounter_id
        )

        return Opponent(
            enemy=enemy,
            level=enemy_level,
            max_hp=max_hp,
            skills=skills,
            skill_cooldowns=skill_cooldowns,
            skill_stacks_used=skill_stacks_used,
            defeated=defeated,
        )

    async def get_character(
        self,
        member: discord.Member,
        encounter_events: list[EncounterEvent] = None,
        combat_events: list[CombatEvent] = None,
    ) -> Character:
        if encounter_events is None:
            encounter_events = []

        if combat_events is None:
            combat_events = []

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
            skill = await self.skill_manager.get_weapon_skill(
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

        character = Character(
            member=member,
            skill_slots=skill_slots,
            skill_cooldowns=skill_cooldowns,
            skill_stacks_used=skill_stacks_used,
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

    async def calculate_aoe_skill(
        self,
        context: EncounterContext,
        skill: Skill,
        available_targets: list[Actor],
        hp_cache: dict[int, int],
    ) -> list[tuple[Actor, SkillInstance, float]]:
        damage_data = []

        for target in available_targets:
            instances = context.opponent.get_skill_effect(
                skill, combatant_count=context.get_combat_scale()
            )
            instance = instances[0]

            if target.id not in hp_cache:
                current_hp = await self.get_actor_current_hp(
                    target, context.combat_events
                )
            else:
                current_hp = hp_cache[target.id]

            total_damage = target.get_damage_after_defense(skill, instance.scaled_value)
            new_target_hp = min(max(0, current_hp - total_damage), target.max_hp)
            hp_cache[target.id] = new_target_hp

            damage_data.append((target, instance, new_target_hp))
        return damage_data

    async def calculate_opponent_turn_data(
        self,
        context: EncounterContext,
        skill: Skill,
        available_targets: list[Actor],
        hp_cache: dict[int, int],
    ):
        damage_data = []

        if skill.base_skill.aoe:
            damage_data = await self.calculate_aoe_skill(
                context, skill, available_targets, hp_cache
            )
            return TurnData(
                actor=context.opponent, skill=skill, damage_data=damage_data
            )

        damage_instances = context.opponent.get_skill_effect(
            skill, combatant_count=context.get_combat_scale()
        )

        for instance in damage_instances:
            if len(available_targets) <= 0:
                break

            target = random.choice(available_targets)

            if target.id not in hp_cache:
                current_hp = await self.get_actor_current_hp(
                    target, context.combat_events
                )
            else:
                current_hp = hp_cache[target.id]

            total_damage = target.get_damage_after_defense(skill, instance.scaled_value)

            new_target_hp = min(max(0, current_hp - total_damage), target.max_hp)

            damage_data.append((target, instance, new_target_hp))

            hp_cache[target.id] = new_target_hp
            available_targets = [
                actor
                for actor in available_targets
                if actor.id not in hp_cache or hp_cache[actor.id] > 0
            ]

        return TurnData(actor=context.opponent, skill=skill, damage_data=damage_data)

    async def calculate_opponent_turn(
        self,
        context: EncounterContext,
    ) -> list[TurnData]:
        opponent = context.opponent

        available_skills = []

        sorted_skills = sorted(
            opponent.skills, key=lambda x: x.base_skill.base_value, reverse=True
        )
        for skill in sorted_skills:
            skill_data = opponent.get_skill_data(skill)
            if not skill_data.on_cooldown():
                available_skills.append(skill)

        skills_to_use = []

        for skill in available_skills:
            skills_to_use.append(skill)
            if len(skills_to_use) >= opponent.enemy.actions_per_turn:
                break

        available_targets = context.get_active_combatants()

        hp_cache = {}
        turn_data = []
        for skill in skills_to_use:
            turn_data.append(
                await self.calculate_opponent_turn_data(
                    context, skill, available_targets, hp_cache
                )
            )

        return turn_data
