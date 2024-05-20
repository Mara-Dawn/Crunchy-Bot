import discord
from combat.actors import Actor, Character, Opponent
from combat.enemies.enemy import Enemy
from combat.equipment import CharacterEquipment
from combat.skills import HeavyAttack, NormalAttack, Skill
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
from events.types import EncounterEventType


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

    def get_actor_current_hp(self, actor: Actor, combat_events: list[CombatEvent]):
        health = actor.max_hp

        for event in combat_events:
            if event.target_id != actor.id:
                continue
            skill = self.skill_manager.get_skill(event.skill_type)
            match skill.skill_effect:
                case SkillEffect.PHYSICAL_DAMAGE:
                    health -= event.skill_value
                case SkillEffect.MAGICAL_DAMAGE:
                    health -= event.skill_value
                case SkillEffect.HEALING:
                    health += event.skill_value

            if health <= 0:
                return 0
        return health

    def get_opponent(
        self,
        enemy: Enemy,
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
        skill_data = self.get_skill_data(None, skills, combat_events)

        return Opponent(
            enemy=enemy, max_hp=max_hp, skill_data=skill_data, defeated=defeated
        )

    def get_character(
        self,
        member: discord.Member,
        encounter_events: list[EncounterEvent],
        combat_events: list[CombatEvent],
    ) -> Character:
        defeated = False
        for event in encounter_events:
            if (
                event.encounter_event_type == EncounterEventType.MEMBER_DEFEAT
                and event.member_id == member.id
            ):
                defeated = True
                break

        skills = [NormalAttack(), HeavyAttack()]
        skill_data = self.get_skill_data(member.id, skills, combat_events)
        equipment = CharacterEquipment(member.id)

        character = Character(
            member=member,
            skill_data=skill_data,
            equipment=equipment,
            defeated=defeated,
        )
        return character

    def get_undefeated_actors(self, actors: list[Actor]):
        return [actor for actor in actors if not actor.defeated]

    def get_skill_data(
        self, actor_id: int, skills: list[Skill], combat_events: list[CombatEvent]
    ) -> list[SkillData]:
        cooldowns = {}
        last_used = 0
        for event in combat_events:
            if event.member_id == actor_id:
                if event.skill_type is not None:
                    skill_type = event.skill_type
                    if skill_type not in cooldowns:
                        cooldowns[skill_type] = last_used
                last_used += 1
        skill_data = []

        for skill in skills:
            last_used = None
            if skill.type in cooldowns:
                last_used = cooldowns[skill.type]
            data = SkillData(skill=skill, last_used=last_used)
            skill_data.append(data)
        return skill_data
