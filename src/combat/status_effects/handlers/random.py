import random

from combat.effects.effect import EffectOutcome
from combat.effects.effect_handler import HandlerContext
from combat.status_effects.status_effect import ActiveStatusEffect
from combat.status_effects.status_effects import Random
from combat.status_effects.status_handler import StatusEffectHandler
from combat.status_effects.types import StatusEffectType
from config import Config
from control.combat.effect_manager import CombatEffectManager
from control.controller import Controller


class RandomHandler(StatusEffectHandler):

    def __init__(self, controller: Controller):
        StatusEffectHandler.__init__(
            self, controller=controller, status_effect=Random()
        )
        self.effect_manager: CombatEffectManager = self.controller.get_service(
            CombatEffectManager
        )

    async def handle(
        self, status_effect: ActiveStatusEffect, handler_context: HandlerContext
    ) -> EffectOutcome:
        outcome = EffectOutcome.EMPTY()
        effect_type = status_effect.status_effect.effect_type
        if effect_type != self.effect_type:
            return outcome

        random_positive_effect = [
            StatusEffectType.HIGH,
            StatusEffectType.RAGE,
            StatusEffectType.PROTECTION,
        ]
        random_negative_effect = [
            StatusEffectType.BLEED,
            StatusEffectType.BLIND,
            StatusEffectType.POISON,
            StatusEffectType.PARTY_LEECH,
            StatusEffectType.FROST,
        ]

        chance_for_positive = Config.RANDOM_POSITIVE_CHANCE
        if random.random() < chance_for_positive:
            random_type = random.choice(random_positive_effect)
        else:
            random_type = random.choice(random_negative_effect)

        application_value = handler_context.application_value
        match random_type:
            case StatusEffectType.PROTECTION:
                application_value = 15

        application_outcome = await self.effect_manager.apply_status(
            handler_context.context,
            handler_context.source,
            handler_context.target,
            random_type,
            1,
            application_value,
        )

        return application_outcome
