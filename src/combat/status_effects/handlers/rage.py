from combat.effects.effect import EffectOutcome
from combat.effects.effect_handler import HandlerContext
from combat.skills.types import SkillEffect
from combat.status_effects.status_effect import ActiveStatusEffect
from combat.status_effects.status_effects import Rage
from combat.status_effects.status_handler import StatusEffectHandler
from combat.status_effects.types import StatusEffectType
from control.combat.effect_manager import CombatEffectManager
from control.controller import Controller


class RageHandler(StatusEffectHandler):

    def __init__(self, controller: Controller):
        StatusEffectHandler.__init__(self, controller=controller, status_effect=Rage())
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

        skill_effect = handler_context.skill.base_skill.skill_effect

        if skill_effect in [
            SkillEffect.NOTHING,
            SkillEffect.HEALING,
            SkillEffect.BUFF,
        ]:
            return outcome

        damage = handler_context.damage_instance.value

        application_outcome = await self.effect_manager.apply_status(
            handler_context.context,
            handler_context.source,
            handler_context.target,
            StatusEffectType.BLEED,
            3,
            damage,
        )

        return application_outcome
