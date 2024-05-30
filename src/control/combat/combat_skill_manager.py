from combat.skills.skill import Skill
from combat.skills.skills import *  # noqa: F403
from combat.skills.types import SkillType
from control.controller import Controller
from control.logger import BotLogger
from control.service import Service
from datalayer.database import Database
from discord.ext import commands
from events.bot_event import BotEvent


class CombatSkillManager(Service):

    def __init__(
        self,
        bot: commands.Bot,
        logger: BotLogger,
        database: Database,
        controller: Controller,
    ):
        super().__init__(bot, logger, database)
        self.controller = controller
        self.log_name = "Combat Skills"

    async def listen_for_event(self, event: BotEvent):
        pass

    async def get_skill(self, skill_type: SkillType) -> Skill:
        skill = globals()[skill_type]
        instance = skill()
        return instance
