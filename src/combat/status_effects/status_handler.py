import importlib
from abc import ABC, abstractmethod

from combat.effects.effect import EffectOutcome
from combat.effects.effect_handler import EffectHandler, HandlerContext
from combat.status_effects.status_effect import (
    ActiveStatusEffect,
    StatusEffect,
)
from combat.status_effects.types import (
    StatusEffectType,
)
from control.combat.combat_actor_manager import CombatActorManager
from control.combat.object_factory import ObjectFactory
from control.controller import Controller


class StatusEffectHandler(EffectHandler, ABC):

    def __init__(self, controller: Controller, status_effect: StatusEffect):
        super().__init__(controller)
        self.status_effect = status_effect
        self.effect_type = status_effect.effect_type

        self.actor_manager: CombatActorManager = self.controller.get_service(
            CombatActorManager
        )
        self.factory: ObjectFactory = self.controller.get_service(ObjectFactory)

    @staticmethod
    def get_handler(
        controller: Controller, status_type: StatusEffectType
    ) -> "StatusEffectHandler":
        handler_module = f"combat.status_effects.handlers.{status_type.name.lower()}"
        handler_name = f"{status_type.value}Handler"
        handler_class = getattr(
            importlib.import_module(handler_module),
            handler_name,
        )
        return handler_class(controller)

    @abstractmethod
    async def handle(
        self, status_effect: ActiveStatusEffect, handler_context: HandlerContext
    ) -> EffectOutcome:
        pass

    async def get_application_value(
        self,
        handler_context: HandlerContext,
    ) -> float:
        return handler_context.application_value
