from combat.enemies import *  # noqa: F403
from combat.enemies.enemy import Enemy
from combat.enemies.types import EnemyType
from combat.gear.bases import *  # noqa: F403
from combat.gear.droppable import DroppableBase
from combat.gear.types import Rarity
from combat.gear.uniques import *  # noqa: F403
from combat.skills.skill import Skill
from combat.skills.skills import *  # noqa: F403
from combat.skills.status_effect import (
    StatusEffect,
)
from combat.skills.status_effects import *  # noqa: F403
from combat.skills.types import SkillType, StatusEffectType
from control.controller import Controller
from control.logger import BotLogger
from control.service import Service
from datalayer.database import Database
from discord.ext import commands
from events.bot_event import BotEvent


class ObjectFactory(Service):

    def __init__(
        self,
        bot: commands.Bot,
        logger: BotLogger,
        database: Database,
        controller: Controller,
    ):
        super().__init__(bot, logger, database)
        self.controller = controller
        self.log_name = "Factory"

    async def listen_for_event(self, event: BotEvent):
        pass

    async def get_status_effect(self, status_type: StatusEffectType) -> StatusEffect:
        status_effect = globals()[status_type]
        return status_effect()

    async def get_enemy(self, enemy_type: EnemyType) -> Enemy:
        enemy = globals()[enemy_type]
        instance = enemy()
        return instance

    async def get_base(self, base_type) -> DroppableBase:
        base_class = globals()[base_type]
        instance = base_class()
        return instance

    async def get_weapon_skill(
        self, skill_type: SkillType, rarity: Rarity, level: int
    ) -> Skill:
        skill = globals()[skill_type]
        instance = skill()
        weapon_skill = Skill(base_skill=instance, rarity=rarity, level=level)
        return weapon_skill

    async def get_enemy_skill(self, skill_type: SkillType) -> Skill:
        skill = globals()[skill_type]
        instance = skill()
        enemy_skill = Skill(base_skill=instance, rarity=Rarity.COMMON, level=1)
        return enemy_skill

    async def get_base_skill(self, skill_type: SkillType) -> Skill:
        skill = globals()[skill_type]
        instance = skill()
        return instance
