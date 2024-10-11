from abc import ABC, abstractmethod

from discord.ext import commands

from combat.effects.effect import EffectOutcome
from combat.effects.effect_handler import HandlerContext
from combat.status_effects.status_handler import StatusEffectHandler
from combat.status_effects.types import StatusEffectType
from control.combat.object_factory import ObjectFactory
from control.controller import Controller
from control.logger import BotLogger
from control.service import Service
from datalayer.database import Database
from events.bot_event import BotEvent


class EffectManager(Service, ABC):

    def __init__(
        self,
        bot: commands.Bot,
        logger: BotLogger,
        database: Database,
        controller: Controller,
    ):
        Service.__init__(self, bot, logger, database)
        self.controller = controller
        self.log_name = "StatusEffects"
        self.factory: ObjectFactory = self.controller.get_service(ObjectFactory)

        self.handler_cache: dict[StatusEffectType, StatusEffectHandler] = {}

    async def listen_for_event(self, event: BotEvent):
        pass

    @abstractmethod
    async def on_status_self_application(
        self,
        handler_context: HandlerContext,
    ) -> EffectOutcome:
        pass

    @abstractmethod
    async def on_status_application(
        self,
        handler_context: HandlerContext,
    ) -> EffectOutcome:
        pass

    @abstractmethod
    async def on_attribute(
        self,
        handler_context: HandlerContext,
    ) -> EffectOutcome:
        pass

    @abstractmethod
    async def on_attack(
        self,
        handler_context: HandlerContext,
    ) -> EffectOutcome:
        pass

    @abstractmethod
    async def on_damage_taken(
        self,
        handler_context: HandlerContext,
    ) -> EffectOutcome:
        pass

    @abstractmethod
    async def on_death(
        self,
        handler_context: HandlerContext,
    ) -> EffectOutcome:
        pass

    @abstractmethod
    async def on_post_attack(
        self,
        handler_context: HandlerContext,
    ) -> EffectOutcome:
        pass

    @abstractmethod
    async def on_post_skill(
        self,
        handler_context: HandlerContext,
    ) -> EffectOutcome:
        pass

    @abstractmethod
    async def on_round_start(
        self,
        handler_context: HandlerContext,
    ) -> EffectOutcome:
        pass

    @abstractmethod
    async def on_round_end(
        self,
        handler_context: HandlerContext,
    ) -> EffectOutcome:
        pass

    @abstractmethod
    async def on_turn_start(
        self,
        handler_context: HandlerContext,
    ) -> EffectOutcome:
        pass

    @abstractmethod
    async def on_turn_end(
        self,
        handler_context: HandlerContext,
    ) -> EffectOutcome:
        pass

    @abstractmethod
    async def on_applicant_turn_end(
        self,
        handler_context: HandlerContext,
    ) -> EffectOutcome:
        pass

    @abstractmethod
    async def on_skill_charges(
        self,
        handler_context: HandlerContext,
    ) -> EffectOutcome:
        pass

    @abstractmethod
    async def on_skill_hits(
        self,
        handler_context: HandlerContext,
    ) -> EffectOutcome:
        pass
