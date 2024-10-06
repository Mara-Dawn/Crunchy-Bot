import datetime

from discord.ext import commands

from combat.actors import Actor
from combat.effects.effect import EffectOutcome, OutcomeFlag
from combat.effects.effect_handler import HandlerContext
from combat.effects.types import EffectTrigger
from combat.encounter import EncounterContext
from combat.skills.skill import Skill, SkillInstance
from combat.skills.types import SkillEffect
from combat.status_effects.status_effect import ActiveStatusEffect
from combat.status_effects.status_effects import *  # noqa: F403
from combat.status_effects.status_handler import StatusEffectHandler
from combat.status_effects.types import StatusEffectType
from control.combat.combat_actor_manager import CombatActorManager
from control.combat.combat_embed_manager import CombatEmbedManager
from control.combat.object_factory import ObjectFactory
from control.controller import Controller
from control.logger import BotLogger
from control.service import Service
from datalayer.database import Database
from events.bot_event import BotEvent
from events.combat_event import CombatEvent
from events.status_effect_event import StatusEffectEvent
from events.types import CombatEventType


class CombatStatusEffectManager(Service):

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
        self.actor_manager: CombatActorManager = self.controller.get_service(
            CombatActorManager
        )
        self.embed_manager: CombatEmbedManager = self.controller.get_service(
            CombatEmbedManager
        )
        self.factory: ObjectFactory = self.controller.get_service(ObjectFactory)

        self.handler_cache: dict[StatusEffectType, StatusEffectHandler] = {}

    async def listen_for_event(self, event: BotEvent):
        pass

    async def get_handler(self, effect_type: StatusEffectType):
        if effect_type not in self.handler_cache:
            handler = StatusEffectHandler.get_handler(self.controller, effect_type)
            self.handler_cache[effect_type] = handler
        return self.handler_cache[effect_type]

    async def apply_status(
        self,
        context: EncounterContext,
        source: Actor,
        target: Actor,
        type: StatusEffectType,
        stacks: int,
        application_value: float = None,
    ) -> EffectOutcome:

        status_effect = await self.factory.get_status_effect(type)

        outcome = await self.handle_on_status_application_status_effects(
            target, context, type
        )

        if (
            outcome.flags is not None
            and OutcomeFlag.PREVENT_STATUS_APPLICATION in outcome.flags
        ):
            return outcome

        if (
            application_value is not None
            and application_value == 0
            and not status_effect.apply_on_miss
        ):
            return outcome

        handler = await self.get_handler(type)
        handler_context = HandlerContext(
            context=context,
            source=source,
            target=target,
            application_value=application_value,
        )
        value = await handler.get_application_value(handler_context)
        initial_stacks = stacks
        if (
            status_effect.override
            or status_effect.override_by_actor
            or status_effect.stack
        ):
            for active_effect in target.status_effects:
                override = False
                if active_effect.status_effect.effect_type != type:
                    continue
                if status_effect.override and active_effect.remaining_stacks > 0:
                    override = True
                if (
                    status_effect.override_by_actor
                    and active_effect.event.get_causing_user_id == source.id
                ):
                    override = True
                if status_effect.stack and active_effect.remaining_stacks > 0:
                    override = True
                    stacks += active_effect.remaining_stacks
                if override:
                    await self.consume_status_stack(
                        context,
                        active_effect,
                        active_effect.remaining_stacks,
                    )

        stacks = min(stacks, status_effect.max_stacks)

        event = StatusEffectEvent(
            datetime.datetime.now(),
            context.encounter.guild_id,
            context.encounter.id,
            source.id,
            target.id,
            type,
            stacks,
            value,
        )
        await self.controller.dispatch_event(event)

        if outcome.applied_effects is None:
            outcome.applied_effects = [(type, initial_stacks)]
        else:
            outcome.applied_effects.append((type, initial_stacks))

        self_application_outcome = await self.handle_on_self_application_status_effects(
            source, target, context, type, value
        )

        outcome = StatusEffectHandler.combine_outcomes(
            [self_application_outcome, outcome]
        )

        return outcome

    async def handle_on_self_application_status_effects(
        self,
        source: Actor,
        target: Actor,
        context: EncounterContext,
        effect_type: StatusEffectType,
        application_value: float = None,
    ) -> EffectOutcome:
        triggered_status_effects = await self.actor_trigger(
            context, target, EffectTrigger.ON_SELF_APPLICATION
        )

        if len(triggered_status_effects) <= 0:
            return EffectOutcome.EMPTY()

        filtered = []
        for effect in triggered_status_effects:
            if effect.status_effect.effect_type == effect_type:
                filtered.append(effect)

        if len(filtered) <= 0:
            return EffectOutcome.EMPTY()

        handler_context = HandlerContext(
            trigger=EffectTrigger.ON_STATUS_APPLICATION,
            context=context,
            source=source,
            target=target,
            skill=None,
            triggering_status_effect_type=effect_type,
            application_value=application_value,
            damage_instance=None,
        )

        return await self.get_status_effects_outcome(
            triggered_status_effects, handler_context
        )

    async def handle_on_status_application_status_effects(
        self,
        actor: Actor,
        context: EncounterContext,
        applied_effect_type: StatusEffectType,
    ) -> EffectOutcome:
        triggered_status_effects = await self.actor_trigger(
            context, actor, EffectTrigger.ON_STATUS_APPLICATION
        )

        if len(triggered_status_effects) <= 0:
            return EffectOutcome.EMPTY()

        handler_context = HandlerContext(
            trigger=EffectTrigger.ON_STATUS_APPLICATION,
            context=context,
            source=actor,
            target=actor,
            skill=None,
            triggering_status_effect_type=applied_effect_type,
            application_value=None,
            damage_instance=None,
        )

        outcome = await self.get_status_effects_outcome(
            triggered_status_effects, handler_context
        )

        return outcome

    async def consume_status_stack(
        self,
        context: EncounterContext,
        status_effect: ActiveStatusEffect,
        amount: int = 1,
    ):
        status_effect_event = status_effect.event
        event = CombatEvent(
            datetime.datetime.now(),
            context.encounter.guild_id,
            context.encounter.id,
            status_effect_event.actor_id,
            status_effect_event.actor_id,
            status_effect_event.status_type,
            -amount,
            -amount,
            status_effect_event.id,
            CombatEventType.STATUS_EFFECT,
        )
        await self.controller.dispatch_event(event)

    async def handle_attribute_status_effects(
        self,
        context: EncounterContext,
        actor: Actor,
    ) -> EffectOutcome:

        triggered_status_effects = await self.actor_trigger(
            context, actor, EffectTrigger.ATTRIBUTE
        )

        if len(triggered_status_effects) <= 0:
            return EffectOutcome.EMPTY()

        handler_context = HandlerContext(
            trigger=EffectTrigger.ATTRIBUTE,
            context=context,
            source=actor,
            target=actor,
            skill=None,
            triggering_status_effect_type=None,
            application_value=None,
            damage_instance=None,
        )

        return await self.get_status_effects_outcome(
            triggered_status_effects, handler_context
        )

    async def get_status_effects_outcome(
        self,
        status_effects: list[ActiveStatusEffect],
        handler_context: HandlerContext,
    ) -> EffectOutcome:
        outcome_data: dict[StatusEffectType, EffectOutcome] = {}

        for status_effect in status_effects:
            effect_type = status_effect.status_effect.effect_type
            handler = await self.get_handler(effect_type)
            outcome = await handler.handle(status_effect, handler_context)

            if effect_type not in outcome_data:
                outcome_data[effect_type] = [outcome]
            else:
                outcome_data[effect_type].append(outcome)

        combined_outcomes = []
        for effect_type, outcomes in outcome_data.items():
            handler = await self.get_handler(effect_type)
            combined = await handler.combine(outcomes, handler_context)
            combined_outcomes.append(combined)

        return StatusEffectHandler.combine_outcomes(combined_outcomes)

    async def handle_attack_status_effects(
        self,
        context: EncounterContext,
        actor: Actor,
        skill: Skill,
    ) -> EffectOutcome:
        skill_effect = skill.base_skill.skill_effect

        triggered_status_effects = await self.actor_trigger(
            context, actor, EffectTrigger.ON_ATTACK
        )

        if len(triggered_status_effects) <= 0 or skill_effect in [
            SkillEffect.NOTHING,
            SkillEffect.BUFF,
        ]:
            return EffectOutcome.EMPTY()

        handler_context = HandlerContext(
            trigger=EffectTrigger.ON_ATTACK,
            context=context,
            source=actor,
            target=actor,
            skill=skill,
            triggering_status_effect_type=None,
            application_value=None,
            damage_instance=None,
        )

        outcome = await self.get_status_effects_outcome(
            triggered_status_effects, handler_context
        )

        if not skill.base_skill.modifiable:
            if outcome.modifier is not None:
                outcome.modifier = max(1, outcome.modifier)
            outcome.crit_chance = None
            outcome.crit_chance_modifier = None

        return outcome

    async def handle_on_damage_taken_status_effects(
        self,
        context: EncounterContext,
        actor: Actor,
        skill: Skill,
    ) -> EffectOutcome:
        skill_effect = skill.base_skill.skill_effect

        if skill_effect in [
            SkillEffect.NOTHING,
            SkillEffect.HEALING,
            SkillEffect.BUFF,
        ]:
            return EffectOutcome.EMPTY()

        triggered_status_effects = await self.actor_trigger(
            context, actor, EffectTrigger.ON_DAMAGE_TAKEN
        )

        if len(triggered_status_effects) <= 0:
            return EffectOutcome.EMPTY()

        handler_context = HandlerContext(
            trigger=EffectTrigger.ON_DAMAGE_TAKEN,
            context=context,
            source=actor,
            target=actor,
            skill=skill,
            triggering_status_effect_type=None,
            application_value=None,
            damage_instance=None,
        )

        outcome = await self.get_status_effects_outcome(
            triggered_status_effects, handler_context
        )

        if not skill.base_skill.modifiable:
            if outcome.modifier is not None:
                outcome.modifier = max(1, outcome.modifier)
            outcome.crit_chance = None
            outcome.crit_chance_modifier = None

        return outcome

    async def handle_on_death_status_effects(
        self,
        context: EncounterContext,
        actor: Actor,
    ) -> EffectOutcome:
        for active_actor in context.current_initiative:
            if active_actor.id == actor.id:
                actor = active_actor

        triggered_status_effects = await self.actor_trigger(
            context, actor, EffectTrigger.ON_DEATH
        )

        if len(triggered_status_effects) <= 0:
            return EffectOutcome.EMPTY()

        handler_context = HandlerContext(
            trigger=EffectTrigger.ON_DEATH,
            context=context,
            source=actor,
            target=actor,
            skill=None,
            triggering_status_effect_type=None,
            application_value=None,
            damage_instance=None,
        )

        return await self.get_status_effects_outcome(
            triggered_status_effects, handler_context
        )

    async def handle_post_attack_status_effects(
        self,
        context: EncounterContext,
        actor: Actor,
        target: Actor,
        skill: Skill,
        damage_instance: SkillInstance,
    ) -> EffectOutcome:

        triggered_status_effects = await self.actor_trigger(
            context, actor, EffectTrigger.POST_ATTACK
        )

        handler_context = HandlerContext(
            trigger=EffectTrigger.POST_ATTACK,
            context=context,
            source=actor,
            target=target,
            skill=skill,
            triggering_status_effect_type=None,
            application_value=None,
            damage_instance=damage_instance,
        )

        return await self.get_status_effects_outcome(
            triggered_status_effects, handler_context
        )

    async def handle_round_status_effects(
        self,
        context: EncounterContext,
        trigger: EffectTrigger,
    ) -> dict[int, EffectOutcome]:
        actor_outcomes = {}
        for active_actor in context.current_initiative:

            triggered_status_effects = await self.actor_trigger(
                context, active_actor, trigger
            )

            if len(triggered_status_effects) <= 0:
                continue

            handler_context = HandlerContext(
                trigger=trigger,
                context=context,
                source=active_actor,
                target=active_actor,
                skill=None,
                triggering_status_effect_type=None,
                application_value=None,
                damage_instance=None,
            )

            actor_outcomes[active_actor.id] = await self.get_status_effects_outcome(
                triggered_status_effects, handler_context
            )

        return actor_outcomes

    async def handle_turn_status_effects(
        self,
        context: EncounterContext,
        actor: Actor,
        trigger: EffectTrigger,
    ) -> EffectOutcome:
        if actor.defeated or actor.leaving or actor.is_out:
            return EffectOutcome.EMPTY()

        triggered_status_effects = await self.actor_trigger(context, actor, trigger)

        if len(triggered_status_effects) <= 0:
            return EffectOutcome.EMPTY()

        handler_context = HandlerContext(
            trigger=trigger,
            context=context,
            source=actor,
            target=actor,
            skill=None,
            triggering_status_effect_type=None,
            application_value=None,
            damage_instance=None,
        )

        return await self.get_status_effects_outcome(
            triggered_status_effects, handler_context
        )

    async def handle_applicant_turn_status_effects(
        self,
        context: EncounterContext,
        actor: Actor,
    ) -> dict[int, EffectOutcome]:
        actor_outcomes = {}

        for active_actor in context.current_initiative:

            triggered_status_effects = await self.actor_trigger(
                context,
                active_actor,
                EffectTrigger.END_OF_APPLICANT_TURN,
                match_source_id=actor.id,
            )

            filtered = []

            for effect in triggered_status_effects:
                if effect.event.source_id == actor.id:
                    filtered.append(effect)

            if len(filtered) <= 0:
                continue

            handler_context = HandlerContext(
                trigger=EffectTrigger.END_OF_APPLICANT_TURN,
                context=context,
                source=actor,
                target=active_actor,
                skill=None,
                triggering_status_effect_type=None,
                application_value=None,
                damage_instance=None,
            )

            actor_outcomes[active_actor.id] = await self.get_status_effects_outcome(
                triggered_status_effects, handler_context
            )

        return actor_outcomes

    async def actor_trigger(
        self,
        context: EncounterContext,
        actor: Actor,
        trigger: EffectTrigger,
        match_source_id: int | None = None,
    ) -> list[ActiveStatusEffect]:
        triggered = []

        for active_status_effect in actor.status_effects:
            if active_status_effect.remaining_stacks <= 0:
                continue

            status_effect = active_status_effect.status_effect
            status_effect_event = active_status_effect.event

            next_round = status_effect_event.id <= context.round_event_id_cutoff

            delay_consume = status_effect.delay_consume and not next_round
            delay_trigger = status_effect.delay_trigger and not next_round

            actor_is_source = status_effect_event.source_id == actor.id

            if status_effect.delay_for_source_only and not actor_is_source:
                delay_consume = False
                delay_trigger = False

            if not delay_consume and trigger in status_effect.consumed:  # noqa: SIM102
                if match_source_id is None or (
                    status_effect_event.source_id == match_source_id
                ):
                    await self.consume_status_stack(context, active_status_effect)

            if not delay_trigger and trigger in status_effect.trigger:
                triggered.append(active_status_effect)

        triggered = sorted(
            triggered, key=lambda item: item.status_effect.priority, reverse=True
        )
        return triggered
