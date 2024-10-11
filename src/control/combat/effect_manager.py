from discord.ext import commands

from combat.actors import Actor
from combat.effects.effect import EffectOutcome, OutcomeFlag
from combat.effects.effect_handler import EffectHandler, HandlerContext
from combat.effects.types import EffectTrigger
from combat.encounter import EncounterContext
from combat.skills.skill import Skill, SkillInstance
from combat.status_effects.status_effects import *  # noqa: F403
from combat.status_effects.status_handler import StatusEffectHandler
from combat.status_effects.types import StatusEffectType
from control.combat.combat_enchantment_manager import CombatEnchantmentManager
from control.combat.effect_manager_interface import EffectManager
from control.combat.status_effect_manager import CombatStatusEffectManager
from control.controller import Controller
from control.logger import BotLogger
from control.service import Service
from datalayer.database import Database
from events.bot_event import BotEvent


class CombatEffectManager(Service):

    def __init__(
        self,
        bot: commands.Bot,
        logger: BotLogger,
        database: Database,
        controller: Controller,
    ):
        super().__init__(bot, logger, database)
        self.controller = controller
        self.log_name = "StatusEffects"
        self.handler_cache: dict[StatusEffectType, StatusEffectHandler] = {}
        self.status_effect_manager: CombatStatusEffectManager = (
            self.controller.get_service(CombatStatusEffectManager)
        )
        self.enchantment_manager: CombatEnchantmentManager = (
            self.controller.get_service(CombatEnchantmentManager)
        )

        self.managers: list[EffectManager] = [
            self.status_effect_manager,
            self.enchantment_manager,
        ]

    async def listen_for_event(self, event: BotEvent):
        pass

    async def apply_status(
        self,
        context: EncounterContext,
        source: Actor,
        target: Actor,
        type: StatusEffectType,
        stacks: int,
        application_value: float = None,
    ) -> EffectOutcome:
        outcome = await self.on_status_application(
            source, target, context, type, application_value
        )

        if outcome.flags is not None:
            for flag in outcome.flags:
                match flag:
                    case OutcomeFlag.PREVENT_STATUS_APPLICATION:
                        return outcome
                    case OutcomeFlag.ADDITIONAL_STACK_VALUE:
                        stacks = stacks + outcome.value

        status_outcome = await self.status_effect_manager.apply_status(
            context, source, target, type, stacks, application_value
        )

        self_application_outcome = await self.on_status_self_application(
            source, target, context, type, status_outcome.value
        )

        outcome = EffectHandler.combine_outcomes(
            [self_application_outcome, status_outcome, outcome]
        )

        return outcome

    async def on_status_self_application(
        self,
        source: Actor,
        target: Actor,
        context: EncounterContext,
        effect_type: StatusEffectType,
        application_value: float = None,
    ) -> EffectOutcome:

        handler_context = HandlerContext(
            trigger=EffectTrigger.ON_STATUS_APPLICATION,
            context=context,
            source=source,
            target=target,
            skill=None,
            status_effect_type=effect_type,
            application_value=application_value,
            damage_instance=None,
        )

        outcomes: list[EffectOutcome] = []
        for manager in self.managers:
            outcomes.append(await manager.on_status_self_application(handler_context))
        return EffectHandler.combine_outcomes(outcomes)

    async def on_status_application(
        self,
        source: Actor,
        target: Actor,
        context: EncounterContext,
        applied_effect_type: StatusEffectType,
        application_value: float = None,
    ) -> EffectOutcome:

        handler_context = HandlerContext(
            trigger=EffectTrigger.ON_STATUS_APPLICATION,
            context=context,
            source=source,
            target=target,
            skill=None,
            status_effect_type=applied_effect_type,
            application_value=application_value,
            damage_instance=None,
        )

        outcomes: list[EffectOutcome] = []
        for manager in self.managers:
            outcome = await manager.on_status_application(handler_context)
            outcomes.append(outcome)
            if (
                outcome.flags is not None
                and OutcomeFlag.PREVENT_STATUS_APPLICATION in outcome.flags
            ):
                break
        return EffectHandler.combine_outcomes(outcomes)

    async def on_attribute(
        self,
        context: EncounterContext,
        actor: Actor,
    ) -> EffectOutcome:

        handler_context = HandlerContext(
            trigger=EffectTrigger.ATTRIBUTE,
            context=context,
            source=actor,
            target=actor,
            skill=None,
            status_effect_type=None,
            application_value=None,
            damage_instance=None,
        )

        outcomes: list[EffectOutcome] = []
        for manager in self.managers:
            outcomes.append(await manager.on_attribute(handler_context))
        return EffectHandler.combine_outcomes(outcomes)

    async def on_attack(
        self,
        context: EncounterContext,
        source: Actor,
        target: Actor,
        skill: Skill,
    ) -> EffectOutcome:

        handler_context = HandlerContext(
            trigger=EffectTrigger.ON_ATTACK,
            context=context,
            source=source,
            target=target,
            skill=skill,
            status_effect_type=None,
            application_value=None,
            damage_instance=None,
        )

        outcomes: list[EffectOutcome] = []
        for manager in self.managers:
            outcomes.append(await manager.on_attack(handler_context))
        return EffectHandler.combine_outcomes(outcomes)

    async def on_damage_taken(
        self,
        context: EncounterContext,
        actor: Actor,
        skill: Skill,
    ) -> EffectOutcome:
        handler_context = HandlerContext(
            trigger=EffectTrigger.ON_DAMAGE_TAKEN,
            context=context,
            source=actor,
            target=actor,
            skill=skill,
            status_effect_type=None,
            application_value=None,
            damage_instance=None,
        )

        outcomes: list[EffectOutcome] = []
        for manager in self.managers:
            outcomes.append(await manager.on_damage_taken(handler_context))
        return EffectHandler.combine_outcomes(outcomes)

    async def on_death(
        self,
        context: EncounterContext,
        actor: Actor,
    ) -> EffectOutcome:
        handler_context = HandlerContext(
            trigger=EffectTrigger.ON_DEATH,
            context=context,
            source=actor,
            target=actor,
            skill=None,
            status_effect_type=None,
            application_value=None,
            damage_instance=None,
        )

        outcomes: list[EffectOutcome] = []
        for manager in self.managers:
            outcome = await manager.on_death(handler_context)
            outcomes.append(outcome)
            if outcome.flags is not None and OutcomeFlag.PREVENT_DEATH in outcome.flags:
                break
        return EffectHandler.combine_outcomes(outcomes)

    async def on_post_attack(
        self,
        context: EncounterContext,
        actor: Actor,
        target: Actor,
        skill: Skill,
        damage_instance: SkillInstance,
    ) -> EffectOutcome:
        handler_context = HandlerContext(
            trigger=EffectTrigger.POST_ATTACK,
            context=context,
            source=actor,
            target=target,
            skill=skill,
            status_effect_type=None,
            application_value=None,
            damage_instance=damage_instance,
        )

        outcomes: list[EffectOutcome] = []
        for manager in self.managers:
            outcomes.append(await manager.on_post_attack(handler_context))
        return EffectHandler.combine_outcomes(outcomes)

    async def on_post_skill(
        self,
        context: EncounterContext,
        actor: Actor,
        target: Actor,
        skill: Skill,
    ) -> EffectOutcome:
        handler_context = HandlerContext(
            trigger=EffectTrigger.POST_SKILL,
            context=context,
            source=actor,
            target=target,
            skill=skill,
            status_effect_type=None,
            application_value=None,
            damage_instance=None,
        )

        outcomes: list[EffectOutcome] = []
        for manager in self.managers:
            outcomes.append(await manager.on_post_skill(handler_context))
        return EffectHandler.combine_outcomes(outcomes)

    async def on_round_start(
        self,
        context: EncounterContext,
    ) -> dict[int, EffectOutcome]:
        actor_outcomes = {}
        for active_actor in context.current_initiative:

            handler_context = HandlerContext(
                trigger=EffectTrigger.START_OF_ROUND,
                context=context,
                source=active_actor,
                target=active_actor,
                skill=None,
                status_effect_type=None,
                application_value=None,
                damage_instance=None,
            )

            outcomes: list[EffectOutcome] = []
            for manager in self.managers:
                outcomes.append(await manager.on_round_start(handler_context))
            actor_outcomes[active_actor.id] = EffectHandler.combine_outcomes(outcomes)

        return actor_outcomes

    async def on_round_end(
        self,
        context: EncounterContext,
    ) -> dict[int, EffectOutcome]:
        actor_outcomes = {}
        for active_actor in context.current_initiative:

            handler_context = HandlerContext(
                trigger=EffectTrigger.END_OF_ROUND,
                context=context,
                source=active_actor,
                target=active_actor,
                skill=None,
                status_effect_type=None,
                application_value=None,
                damage_instance=None,
            )

            outcomes: list[EffectOutcome] = []
            for manager in self.managers:
                outcomes.append(await manager.on_round_end(handler_context))
            actor_outcomes[active_actor.id] = EffectHandler.combine_outcomes(outcomes)

        return actor_outcomes

    async def on_turn_start(
        self,
        context: EncounterContext,
        actor: Actor,
    ) -> EffectOutcome:

        handler_context = HandlerContext(
            trigger=EffectTrigger.START_OF_TURN,
            context=context,
            source=actor,
            target=actor,
            skill=None,
            status_effect_type=None,
            application_value=None,
            damage_instance=None,
        )

        outcomes: list[EffectOutcome] = []
        for manager in self.managers:
            outcomes.append(await manager.on_turn_start(handler_context))
        return EffectHandler.combine_outcomes(outcomes)

    async def on_turn_end(
        self,
        context: EncounterContext,
        actor: Actor,
    ) -> EffectOutcome:

        handler_context = HandlerContext(
            trigger=EffectTrigger.END_OF_TURN,
            context=context,
            source=actor,
            target=actor,
            skill=None,
            status_effect_type=None,
            application_value=None,
            damage_instance=None,
        )

        outcomes: list[EffectOutcome] = []
        for manager in self.managers:
            outcomes.append(await manager.on_turn_end(handler_context))
        return EffectHandler.combine_outcomes(outcomes)

    async def on_applicant_turn_end(
        self,
        context: EncounterContext,
        actor: Actor,
    ) -> dict[int, EffectOutcome]:
        actor_outcomes = {}

        for active_actor in context.current_initiative:

            handler_context = HandlerContext(
                trigger=EffectTrigger.END_OF_APPLICANT_TURN,
                context=context,
                source=actor,
                target=active_actor,
                skill=None,
                status_effect_type=None,
                application_value=None,
                damage_instance=None,
            )

            outcomes: list[EffectOutcome] = []
            for manager in self.managers:
                outcomes.append(await manager.on_applicant_turn_end(handler_context))
            actor_outcomes[active_actor.id] = EffectHandler.combine_outcomes(outcomes)

        return actor_outcomes

    async def on_skill_charges(
        self,
        actor: Actor,
        skill: Skill,
    ) -> EffectOutcome:

        handler_context = HandlerContext(
            trigger=EffectTrigger.SKILL_CHARGE,
            context=None,
            source=actor,
            target=None,
            skill=skill,
            status_effect_type=None,
            application_value=None,
            damage_instance=None,
        )

        outcomes: list[EffectOutcome] = []
        for manager in self.managers:
            outcomes.append(await manager.on_skill_charges(handler_context))
        return EffectHandler.combine_outcomes(outcomes)

    async def on_skill_hits(
        self,
        actor: Actor,
        skill: Skill,
    ) -> EffectOutcome:

        handler_context = HandlerContext(
            trigger=EffectTrigger.SKILL_HITS,
            context=None,
            source=actor,
            target=None,
            skill=skill,
            status_effect_type=None,
            application_value=None,
            damage_instance=None,
        )

        outcomes: list[EffectOutcome] = []
        for manager in self.managers:
            outcomes.append(await manager.on_skill_hits(handler_context))
        return EffectHandler.combine_outcomes(outcomes)
