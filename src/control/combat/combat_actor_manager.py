import random

import discord
from combat.actors import Actor, Character, Opponent
from combat.encounter import EncounterContext, TurnData
from combat.enemies.enemy import Enemy
from combat.skills.skill import CharacterSkill, Skill
from combat.skills.types import SkillEffect, SkillType
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

        for event in combat_events:
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
        for event in encounter_events:
            if (
                event.encounter_event_type == EncounterEventType.MEMBER_DEFEAT
                and event.member_id == member.id
            ):
                defeated = True
                break

        equipment = await self.database.get_user_equipment(member.guild.id, member.id)

        skill_types = []

        weapon_skills = equipment.weapon.base.skills
        skill_types.extend(weapon_skills)

        skills = []
        for skill_type in skill_types:
            skill = await self.skill_manager.get_weapon_skill(skill_type)
            skills.append(skill)

        equipped_skills = await self.database.get_user_equipped_skills(
            member.guild.id, member.id
        )

        for skill in equipped_skills:
            if len(skills) >= 4:
                break
            skills.append(skill)

        skill_cooldowns = self.get_skill_cooldowns(member.id, skills, combat_events)
        skill_stacks_used = await self.database.get_user_skill_stacks_used(
            member.guild.id, member.id
        )

        character = Character(
            member=member,
            skills=skills,
            skill_cooldowns=skill_cooldowns,
            skill_stacks_used=skill_stacks_used,
            equipment=equipment,
            defeated=defeated,
        )
        return character

    def get_undefeated_actors(self, actors: list[Actor]):
        return [actor for actor in actors if not actor.defeated]

    def get_skill_cooldowns(
        self, actor_id: int, skills: list[Skill], combat_events: list[CombatEvent]
    ) -> list[CharacterSkill]:
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

        skill_data = {}

        for skill in skills:
            last_used = None
            skill_type = skill.base_skill.skill_type
            if skill_type in cooldowns:
                last_used = cooldowns[skill_type]
            skill_data[skill_type] = last_used
        return skill_data

    async def calculate_opponent_turn_data(
        self,
        context: EncounterContext,
        skill: Skill,
        available_targets: list[Actor],
        hp_cache: dict[int, int],
    ):
        damage_instances = context.opponent.get_skill_damage(
            skill, combatant_count=len(context.combatants)
        )

        damage_data = []

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

            new_target_hp = max(0, current_hp - total_damage)

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

        for skill in opponent.skills:
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
