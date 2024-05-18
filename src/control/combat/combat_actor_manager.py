import discord
from combat.actors import Actor, Character, Opponent
from combat.enemies.enemy import Enemy
from combat.skills import HeavyAttack, NormalAttack, Skill
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
        self, enemy: Enemy, max_hp: int, encounter_events: list[EncounterEvent]
    ) -> Opponent:
        defeated = False
        for event in encounter_events:
            if event.encounter_event_type == EncounterEventType.ENEMY_DEFEAT:
                defeated = True
                break

        return Opponent(enemy=enemy, max_hp=max_hp, defeated=defeated)

    def get_character(
        self, member: discord.Member, encounter_events: list[EncounterEvent]
    ) -> Character:
        defeated = False
        for event in encounter_events:
            if (
                event.encounter_event_type == EncounterEventType.MEMBER_DEFEAT
                and event.member_id == member.id
            ):
                defeated = True
                break

        character = Character(
            member=member, skills=[NormalAttack(), HeavyAttack()], defeated=defeated
        )
        return character
