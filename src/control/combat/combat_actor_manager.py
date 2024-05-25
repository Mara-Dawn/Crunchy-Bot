import discord
from combat.actors import Actor, Character, Opponent
from combat.enemies.enemy import Enemy
from combat.skills import Skill
from combat.skills.skill import SkillData
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
            skill = await self.skill_manager.get_skill(event.skill_type)
            match skill.skill_effect:
                case SkillEffect.PHYSICAL_DAMAGE:
                    health -= event.skill_value
                case SkillEffect.MAGICAL_DAMAGE:
                    health -= event.skill_value
                case SkillEffect.HEALING:
                    health += event.skill_value

            if health <= 0:
                return 0
        return int(health)

    def get_opponent(
        self,
        enemy: Enemy,
        enemy_level: int,
        max_hp: int,
        encounter_events: list[EncounterEvent],
        combat_events: list[CombatEvent],
    ) -> Opponent:
        defeated = False
        for event in encounter_events:
            if event.encounter_event_type == EncounterEventType.ENEMY_DEFEAT:
                defeated = True
                break

        skills = enemy.skills
        skill_cooldowns = self.get_skill_cooldowns(None, skills, combat_events)

        return Opponent(
            enemy=enemy,
            level=enemy_level,
            max_hp=max_hp,
            skills=skills,
            skill_cooldowns=skill_cooldowns,
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

        skill_types.extend(
            await self.database.get_user_equipped_skills(member.guild.id, member.id)
        )
        skills = []
        for skill_type in skill_types:
            skill = await self.skill_manager.get_skill(skill_type)
            skills.append(skill)
            if len(skills) >= 4:
                break

        skill_cooldowns = self.get_skill_cooldowns(member.id, skills, combat_events)

        character = Character(
            member=member,
            skills=skills,
            skill_cooldowns=skill_cooldowns,
            equipment=equipment,
            defeated=defeated,
        )
        return character

    def get_undefeated_actors(self, actors: list[Actor]):
        return [actor for actor in actors if not actor.defeated]

    def get_skill_cooldowns(
        self, actor_id: int, skills: list[Skill], combat_events: list[CombatEvent]
    ) -> list[SkillData]:
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
            if skill.type in cooldowns:
                last_used = cooldowns[skill.type]
            skill_data[skill.type] = last_used
        return skill_data
