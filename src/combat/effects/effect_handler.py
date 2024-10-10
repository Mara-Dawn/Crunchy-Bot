from abc import ABC, abstractmethod
from dataclasses import dataclass

from combat.actors import Actor
from combat.effects.effect import EffectOutcome
from combat.effects.types import EffectTrigger
from combat.encounter import EncounterContext
from combat.skills.skill import Skill, SkillInstance
from combat.status_effects.types import StatusEffectType
from control.controller import Controller


@dataclass
class HandlerContext:
    trigger: EffectTrigger = None
    context: EncounterContext = None
    source: Actor = None
    target: Actor = None
    skill: Skill = None
    application_value: float = None
    damage_instance: SkillInstance = None
    status_effect_type: StatusEffectType = None


class EffectHandler(ABC):

    def __init__(self, controller: Controller):
        self.controller = controller

    @abstractmethod
    async def handle(self) -> EffectOutcome:
        pass

    async def combine(
        self, outcomes: list[EffectOutcome], handler_context: HandlerContext
    ) -> EffectOutcome:
        return self.combine_outcomes(outcomes)

    @staticmethod
    def combine_outcomes(
        outcomes: list[EffectOutcome],
    ) -> EffectOutcome:
        combined = EffectOutcome.EMPTY()

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

            if outcome.bonus_damage is not None:
                if combined.bonus_damage is None:
                    combined.bonus_damage = outcome.bonus_damage
                else:
                    combined.bonus_damage += outcome.bonus_damage

            if outcome.embed_data is not None:
                if combined.embed_data is None:
                    combined.embed_data = outcome.embed_data
                else:
                    combined.embed_data.extend(outcome.embed_data)

        return combined
