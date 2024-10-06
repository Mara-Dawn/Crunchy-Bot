import importlib
from abc import ABC, abstractmethod
from dataclasses import dataclass

from combat.actors import Actor
from combat.effects.efffect import EffectOutcome
from combat.effects.types import EffectTrigger
from combat.enchantments.enchantment import (
    BaseEnchantment,
    EffectEnchantment,
    Enchantment,
)
from combat.enchantments.types import EnchantmentType
from combat.encounter import EncounterContext
from combat.gear.gear import Gear
from combat.skills.skill import Skill, SkillInstance
from combat.skills.types import SkillEffect
from combat.status_effects.status_handler import StatusEffectHandler
from control.combat.combat_actor_manager import CombatActorManager
from control.combat.object_factory import ObjectFactory
from control.controller import Controller


@dataclass
class HandlerContext:
    trigger: EffectTrigger = None
    context: EncounterContext = None
    source: Actor = None
    target: Actor = None
    skill: Skill = None
    trigger_value: float = None
    damage_instance: SkillInstance = None


class EnchantmentHandler:

    def __init__(self, controller: Controller, base_enchantment: BaseEnchantment):
        self.base_enchantment = base_enchantment
        self.enchantment_type = base_enchantment.enchantment_type
        self.controller = controller

    @staticmethod
    def get_handler(
        controller: Controller, enchantment_type: EnchantmentType
    ) -> "EnchantmentHandler":
        handler_module = f"combat.enchantments.handlers.{enchantment_type.name.lower()}"
        handler_name = f"{enchantment_type.value}Handler"
        handler_class = getattr(
            importlib.import_module(handler_module),
            handler_name,
        )
        return handler_class(controller)

    async def handle(self):
        pass


class EnchantmentCraftHandler(EnchantmentHandler, ABC):

    def __init__(self, controller: Controller, enchantment: Enchantment):
        super().__init__(controller, enchantment)

    @abstractmethod
    async def handle(
        self,
        enchantment: Enchantment,
        gear: Gear,
    ) -> Gear:
        pass


class EnchantmentEffectHandler(EnchantmentHandler, ABC):

    def __init__(self, controller: Controller, enchantment: Enchantment):
        super().__init__(controller, enchantment)
        self.actor_manager: CombatActorManager = self.controller.get_service(
            CombatActorManager
        )
        self.factory: ObjectFactory = self.controller.get_service(ObjectFactory)

    @abstractmethod
    async def handle(
        self,
        enchantment: EffectEnchantment,
        handler_context: HandlerContext,
    ) -> EffectOutcome:
        pass

    @abstractmethod
    async def combine(
        self, outcomes: list[EffectOutcome], handler_context: HandlerContext
    ) -> EffectOutcome:
        pass

    @abstractmethod
    async def is_penalty(
        self,
        skill_effect: SkillEffect,
    ) -> bool:
        pass

    @staticmethod
    def combine_outcomes(
        outcomes: list[EffectOutcome],
    ) -> EffectOutcome:
        return StatusEffectHandler.combine_outcomes(outcomes)
