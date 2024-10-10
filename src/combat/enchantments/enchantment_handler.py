import importlib
from abc import ABC, abstractmethod

from combat.effects.effect import EffectOutcome
from combat.effects.effect_handler import EffectHandler, HandlerContext
from combat.enchantments.enchantment import (
    BaseEnchantment,
    EffectEnchantment,
    Enchantment,
)
from combat.enchantments.types import EnchantmentType
from combat.gear.gear import Gear
from combat.skills.types import SkillEffect
from control.combat.combat_actor_manager import CombatActorManager
from control.combat.object_factory import ObjectFactory
from control.controller import Controller


class EnchantmentHandler(EffectHandler):

    def __init__(self, controller: Controller, base_enchantment: BaseEnchantment):
        super().__init__(controller)
        self.base_enchantment = base_enchantment
        self.enchantment_type = base_enchantment.enchantment_type

    @staticmethod
    def get_handler(
        controller: Controller, enchantment_type: EnchantmentType
    ) -> "EnchantmentHandler":
        handler_module = f"combat.enchantments.handlers.{enchantment_type.name.lower()}"
        match enchantment_type:
            case EnchantmentType.SKILL_STACKS:
                handler_name = "SkillStacksHandler"
            case _:
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
    async def is_penalty(
        self,
        skill_effect: SkillEffect,
    ) -> bool:
        pass
