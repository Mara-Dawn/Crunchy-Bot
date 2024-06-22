import datetime

from combat.actors import Actor
from combat.encounter import EncounterContext
from combat.skills.types import StatusEffectType
from control.controller import Controller
from control.logger import BotLogger
from control.service import Service
from datalayer.database import Database
from discord.ext import commands
from events.bot_event import BotEvent
from events.status_effect_event import StatusEffectEvent


class StatusEffectManager(Service):

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

    async def apply_status(
        self,
        context: EncounterContext,
        source: Actor,
        target: Actor,
        type: StatusEffectType,
        amount: int = 1,
    ):
        event = StatusEffectEvent(
            datetime.datetime.now(),
            context.encounter.guild_id,
            source.id,
            target.id,
            type,
            amount,
        )
        await self.controller.dispatch_event(event)
