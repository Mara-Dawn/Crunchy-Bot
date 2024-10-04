from combat.status_effects.status_effect import (
    ActiveStatusEffect,
    EmbedDataCollection,
    StatusEffectEmbedData,
    StatusEffectOutcome,
)
from combat.status_effects.status_effects import FullCleanse
from combat.status_effects.status_handler import HandlerContext, StatusEffectHandler
from combat.status_effects.types import StatusEffectType
from control.combat.status_effect_manager import CombatStatusEffectManager
from control.controller import Controller


class FullCleanseHandler(StatusEffectHandler):

    def __init__(self, controller: Controller):
        StatusEffectHandler.__init__(
            self, controller=controller, status_effect=FullCleanse()
        )
        self.status_effect_manager: CombatStatusEffectManager = (
            self.controller.get_service(CombatStatusEffectManager)
        )

    async def handle(
        self, status_effect: ActiveStatusEffect, handler_context: HandlerContext
    ) -> StatusEffectOutcome:
        outcome = StatusEffectOutcome.EMPTY()

        effect_type = status_effect.status_effect.effect_type
        if effect_type != self.effect_type:
            return outcome

        info = []
        for status in handler_context.target.status_effects:
            if status.remaining_stacks <= 0:
                continue
            message = ""
            if StatusEffectType.is_negative(status.status_effect.effect_type):
                await self.status_effect_manager.consume_status_stack(
                    handler_context.context,
                    status,
                    status.remaining_stacks,
                )
                message = f"{status.status_effect.name} was cleansed from {handler_context.target.name}."
                if message != "" and message not in info:
                    info.append(message)
        info = "\n".join(info) if len(info) > 0 else None

        if info is not None:
            embed_data_collection = EmbedDataCollection()
            description = info
            embed_data = StatusEffectEmbedData(
                self.status_effect, self.status_effect.title, description
            )
            embed_data_collection.append(embed_data)
            outcome.embed_data = embed_data_collection

        return outcome

    async def combine(
        self, outcomes: list[StatusEffectOutcome], handler_context: HandlerContext
    ) -> StatusEffectOutcome:
        return self.combine_outcomes(outcomes)
