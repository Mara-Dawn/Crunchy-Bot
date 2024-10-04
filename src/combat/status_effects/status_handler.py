import importlib
from abc import ABC, abstractmethod
from dataclasses import dataclass

from combat.actors import Actor
from combat.encounter import EncounterContext
from combat.skills.skill import Skill, SkillInstance
from combat.status_effects.status_effect import (
    ActiveStatusEffect,
    StatusEffect,
    StatusEffectOutcome,
)
from combat.status_effects.types import (
    StatusEffectTrigger,
    StatusEffectType,
)
from control.combat.combat_actor_manager import CombatActorManager
from control.combat.object_factory import ObjectFactory
from control.controller import Controller


@dataclass
class HandlerContext:
    trigger: StatusEffectTrigger = None
    context: EncounterContext = None
    source: Actor = None
    target: Actor = None
    skill: Skill = None
    triggering_status_effect_type: StatusEffectType = None
    application_value: float = None
    damage_instance: SkillInstance = None


class StatusEffectHandler(ABC):

    def __init__(self, controller: Controller, status_effect: StatusEffect):
        self.status_effect = status_effect
        self.effect_type = status_effect.effect_type

        self.controller = controller
        self.actor_manager: CombatActorManager = self.controller.get_service(
            CombatActorManager
        )
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
    ) -> StatusEffectOutcome:
        pass

    @abstractmethod
    async def combine(
        self, outcomes: list[StatusEffectOutcome], handler_context: HandlerContext
    ) -> StatusEffectOutcome:
        pass

    async def get_application_value(
        self,
        handler_context: HandlerContext,
    ) -> float:
        return handler_context.application_value

    @staticmethod
    def combine_outcomes(
        outcomes: list[StatusEffectOutcome],
    ) -> StatusEffectOutcome:
        combined = StatusEffectOutcome.EMPTY()

        for outcome in outcomes:
            if outcome.value is not None and isinstance(outcome.value, int | float):
                if combined.value is None:
                    combined.value = outcome.value
                else:
                    combined.value += outcome.value

            if outcome.modifier is not None:
                if combined.modifier is None:
                    combined.modifier = outcome.modifier
                else:
                    combined.modifier *= outcome.modifier

            if outcome.crit_chance is not None:  # noqa: SIM102
                if (
                    combined.crit_chance is None
                    or combined.crit_chance < outcome.crit_chance
                ):
                    combined.crit_chance = outcome.crit_chance

            if outcome.crit_chance_modifier is not None:
                if combined.crit_chance_modifier is None:
                    combined.crit_chance_modifier = outcome.crit_chance_modifier
                else:
                    combined.crit_chance_modifier *= outcome.crit_chance_modifier

            if outcome.initiative is not None:
                if combined.initiative is None:
                    combined.initiative = outcome.initiative
                else:
                    combined.initiative += outcome.initiative

            if outcome.applied_effects is not None:
                if combined.applied_effects is None:
                    combined.applied_effects = outcome.applied_effects
                else:
                    combined.applied_effects.extend(outcome.applied_effects)

            if outcome.flags is not None:
                if combined.flags is None:
                    combined.flags = outcome.flags
                else:
                    combined.flags.extend(outcome.flags)

            if outcome.info is not None:
                if combined.info is None:
                    combined.info = outcome.info
                else:
                    combined.info += "\n" + outcome.info

            if outcome.embed_data is not None:
                if combined.embed_data is None:
                    combined.embed_data = outcome.embed_data
                else:
                    combined.embed_data.extend(outcome.embed_data)

        return combined
