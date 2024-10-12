import datetime
import random

from discord.ext import commands

from combat.actors import Character
from combat.effects.effect import EffectOutcome, OutcomeFlag
from combat.effects.effect_handler import HandlerContext
from combat.effects.types import EffectTrigger
from combat.enchantments.enchantment import (
    CraftDisplayWrapper,
    EffectEnchantment,
    Enchantment,
    GearEnchantment,
)
from combat.enchantments.enchantment_handler import (
    EnchantmentEffectHandler,
    EnchantmentHandler,
)
from combat.enchantments.types import EnchantmentEffect, EnchantmentType
from combat.encounter import EncounterContext
from combat.gear.types import CharacterAttribute, GearModifierType
from combat.skills.skill import SkillInstance
from combat.skills.skills import *  # noqa: F403
from combat.skills.types import SkillEffect
from config import Config
from control.ai_manager import AIManager
from control.controller import Controller
from control.logger import BotLogger
from control.service import Service
from datalayer.database import Database
from events.bot_event import BotEvent
from events.combat_event import CombatEvent
from events.types import CombatEventType


class CombatEnchantmentManager(Service):

    def __init__(
        self,
        bot: commands.Bot,
        logger: BotLogger,
        database: Database,
        controller: Controller,
    ):
        super().__init__(bot, logger, database)
        self.controller = controller
        self.ai_manager: AIManager = self.controller.get_service(AIManager)
        self.log_name = "Combat Enchantments"

        self.handler_cache: dict[EnchantmentType, EnchantmentEffectHandler] = {}

    async def listen_for_event(self, event: BotEvent):
        pass

    async def get_handler(
        self, enchantment_type: EnchantmentType
    ) -> EnchantmentEffectHandler:
        if enchantment_type not in self.handler_cache:
            handler = EnchantmentEffectHandler.get_handler(
                self.controller, enchantment_type
            )
            self.handler_cache[enchantment_type] = handler
        return self.handler_cache[enchantment_type]

    async def get_gear_enchantment(
        self, character: Character, enchantment: Enchantment
    ) -> GearEnchantment:

        if (
            enchantment.base_enchantment.enchantment_effect
            == EnchantmentEffect.CRAFTING
        ):
            return CraftDisplayWrapper(enchantment)

        enchantment: EffectEnchantment = enchantment
        enchantment_id = enchantment.id
        stacks_used = 0
        last_used = None

        if enchantment_id in character.enchantment_stacks_used:
            stacks_used = character.enchantment_stacks_used[enchantment_id]
        if enchantment_id in character.enchantment_cooldowns:
            last_used = character.enchantment_cooldowns[enchantment.id]

        character_type = character.skill_slots[0].base_skill.skill_effect

        penalty = await self.get_enchantment_penalty(enchantment, character_type)

        return GearEnchantment(
            enchantment=enchantment,
            last_used=last_used,
            stacks_used=stacks_used,
            min_roll=(
                await self.get_enchantment_effect(
                    character, enchantment, force_min=True
                )
            )[0].raw_value,
            max_roll=(
                await self.get_enchantment_effect(
                    character, enchantment, force_max=True
                )
            )[0].raw_value,
            penalty=penalty,
        )

    async def get_enchantment_penalty(
        self, enchantment: Enchantment, effect_type: SkillEffect
    ) -> bool:
        if enchantment.base_enchantment.enchantment_effect != EnchantmentEffect.EFFECT:
            return False

        handler: EnchantmentEffectHandler = EnchantmentHandler.get_handler(
            self.controller, enchantment.base_enchantment.enchantment_type
        )
        return await handler.is_penalty(effect_type)

    async def get_enchantment_effect(
        self,
        character: Character,
        enchantment: EffectEnchantment,
        combatant_count: int = 1,
        force_min: bool = False,
        force_max: bool = False,
    ) -> list[SkillInstance]:
        base_value = enchantment.base_enchantment.value
        weapon_min_roll = character.equipment.weapon.modifiers[
            GearModifierType.WEAPON_DAMAGE_MIN
        ]
        weapon_max_roll = character.equipment.weapon.modifiers[
            GearModifierType.WEAPON_DAMAGE_MAX
        ]

        modifier = 1
        base_dmg_type = character.skill_slots[0].base_skill.skill_effect

        encounter_scaling = 1
        if combatant_count > 1:
            encounter_scaling = (
                1 / combatant_count * Config.CHARACTER_ENCOUNTER_SCALING_FACOTR
            )

        critical_modifier = character.equipment.attributes[
            CharacterAttribute.CRIT_DAMAGE
        ]

        match enchantment.base_enchantment.skill_effect:
            case SkillEffect.PHYSICAL_DAMAGE:
                modifier += character.equipment.attributes[
                    CharacterAttribute.PHYS_DAMAGE_INCREASE
                ]
                if base_dmg_type != enchantment.base_enchantment.skill_effect:
                    modifier *= Config.SKILL_TYPE_PENALTY
            case SkillEffect.MAGICAL_DAMAGE:
                modifier += character.equipment.attributes[
                    CharacterAttribute.MAGIC_DAMAGE_INCREASE
                ]
                if base_dmg_type != enchantment.base_enchantment.skill_effect:
                    modifier *= Config.SKILL_TYPE_PENALTY
            case SkillEffect.HEALING:
                encounter_scaling = 1
                weapon_lvl = character.equipment.weapon.level
                base_roll = Config.OPPONENT_DAMAGE_BASE[weapon_lvl]
                weapon_min_roll = base_roll * (1 - Config.OPPONENT_DAMAGE_VARIANCE)
                weapon_max_roll = base_roll * (1 + Config.OPPONENT_DAMAGE_VARIANCE)
                modifier += character.equipment.attributes[
                    CharacterAttribute.HEALING_BONUS
                ]
                critical_modifier = Config.HEAL_CRIT_MODIFIER
            case SkillEffect.NOTHING | SkillEffect.BUFF:
                modifier = 0

        attack_count = enchantment.base_enchantment.hits
        skill_instances = []
        for _ in range(attack_count):

            if force_min:
                weapon_roll = weapon_min_roll
            elif force_max:
                weapon_roll = weapon_max_roll
            else:
                weapon_roll = random.randint(int(weapon_min_roll), int(weapon_max_roll))

            crit_rate = character.equipment.attributes[CharacterAttribute.CRIT_RATE]

            skill_instance = SkillInstance(
                weapon_roll=weapon_roll,
                skill_base=base_value,
                modifier=modifier,
                critical_modifier=critical_modifier,
                encounter_scaling=encounter_scaling,
                crit_chance=crit_rate,
            )
            skill_instances.append(skill_instance)

        return skill_instances

    async def on_status_self_application(
        self,
        handler_context: HandlerContext,
    ) -> EffectOutcome:
        return EffectOutcome.EMPTY()

    async def on_status_application(
        self,
        handler_context: HandlerContext,
    ) -> EffectOutcome:

        triggered_source_enchantments = await self.enchantment_trigger(
            handler_context.context,
            handler_context.source,
            EffectTrigger.ON_STATUS_APPLICATION,
        )

        triggered_target_enchantments = await self.enchantment_trigger(
            handler_context.context,
            handler_context.target,
            EffectTrigger.ON_STATUS_APPLICATION,
        )
        triggered_enchantments = (
            triggered_source_enchantments + triggered_target_enchantments
        )

        if len(triggered_enchantments) <= 0:
            return EffectOutcome.EMPTY()

        outcome = await self.get_outcome(triggered_enchantments, handler_context)

        return outcome

    async def on_attribute(
        self,
        handler_context: HandlerContext,
    ) -> EffectOutcome:

        triggered_enchantments = await self.enchantment_trigger(
            handler_context.context, handler_context.source, EffectTrigger.ATTRIBUTE
        )

        if len(triggered_enchantments) <= 0:
            return EffectOutcome.EMPTY()

        return await self.get_outcome(triggered_enchantments, handler_context)

    async def on_attack(
        self,
        handler_context: HandlerContext,
    ) -> EffectOutcome:

        skill_effect = handler_context.skill.base_skill.skill_effect

        triggered_enchantments = await self.enchantment_trigger(
            handler_context.context, handler_context.source, EffectTrigger.ON_ATTACK
        )

        if len(triggered_enchantments) <= 0 or skill_effect in [
            SkillEffect.NOTHING,
            SkillEffect.BUFF,
        ]:
            return EffectOutcome.EMPTY()

        outcome = await self.get_outcome(triggered_enchantments, handler_context)

        if not handler_context.skill.base_skill.modifiable:
            if outcome.modifier is not None:
                outcome.modifier = max(1, outcome.modifier)
            outcome.crit_chance = None
            outcome.crit_chance_modifier = None

        return outcome

    async def on_damage_taken(
        self,
        handler_context: HandlerContext,
    ) -> EffectOutcome:

        skill_effect = handler_context.skill.base_skill.skill_effect

        if skill_effect in [
            SkillEffect.NOTHING,
            SkillEffect.HEALING,
            SkillEffect.BUFF,
        ]:
            return EffectOutcome.EMPTY()

        triggered_enchantments = await self.enchantment_trigger(
            handler_context.context,
            handler_context.source,
            EffectTrigger.ON_DAMAGE_TAKEN,
        )

        if len(triggered_enchantments) <= 0:
            return EffectOutcome.EMPTY()

        outcome = await self.get_outcome(triggered_enchantments, handler_context)

        if not handler_context.skill.base_skill.modifiable:
            if outcome.modifier is not None:
                outcome.modifier = max(1, outcome.modifier)
            outcome.crit_chance = None
            outcome.crit_chance_modifier = None

        return outcome

    async def on_death(
        self,
        handler_context: HandlerContext,
    ) -> EffectOutcome:

        triggered_enchantments = await self.enchantment_trigger(
            handler_context.context, handler_context.source, EffectTrigger.ON_DEATH
        )

        if len(triggered_enchantments) <= 0:
            return EffectOutcome.EMPTY()

        return await self.get_outcome(triggered_enchantments, handler_context)

    async def on_post_attack(
        self,
        handler_context: HandlerContext,
    ) -> EffectOutcome:

        triggered_enchantments = await self.enchantment_trigger(
            handler_context.context, handler_context.source, EffectTrigger.POST_ATTACK
        )

        return await self.get_outcome(triggered_enchantments, handler_context)

    async def on_post_skill(
        self,
        handler_context: HandlerContext,
    ) -> EffectOutcome:

        triggered_enchantments = await self.enchantment_trigger(
            handler_context.context, handler_context.source, EffectTrigger.POST_SKILL
        )

        return await self.get_outcome(triggered_enchantments, handler_context)

    async def on_round_start(
        self,
        handler_context: HandlerContext,
    ) -> dict[int, EffectOutcome]:

        triggered_enchantments = await self.enchantment_trigger(
            handler_context.context,
            handler_context.source,
            EffectTrigger.START_OF_ROUND,
        )

        if len(triggered_enchantments) <= 0:
            return EffectOutcome.EMPTY()

        return await self.get_outcome(triggered_enchantments, handler_context)

    async def on_round_end(
        self,
        handler_context: HandlerContext,
    ) -> dict[int, EffectOutcome]:

        triggered_enchantments = await self.enchantment_trigger(
            handler_context.context,
            handler_context.source,
            EffectTrigger.END_OF_ROUND,
        )

        if len(triggered_enchantments) <= 0:
            return EffectOutcome.EMPTY()

        return await self.get_outcome(triggered_enchantments, handler_context)

    async def on_turn_start(
        self,
        handler_context: HandlerContext,
    ) -> dict[int, EffectOutcome]:
        triggered_enchantments = await self.enchantment_trigger(
            handler_context.context,
            handler_context.source,
            EffectTrigger.START_OF_TURN,
        )

        if len(triggered_enchantments) <= 0:
            return EffectOutcome.EMPTY()

        return await self.get_outcome(triggered_enchantments, handler_context)

    async def on_turn_end(
        self,
        handler_context: HandlerContext,
    ) -> dict[int, EffectOutcome]:
        triggered_enchantments = await self.enchantment_trigger(
            handler_context.context,
            handler_context.source,
            EffectTrigger.END_OF_TURN,
        )

        if len(triggered_enchantments) <= 0:
            return EffectOutcome.EMPTY()

        return await self.get_outcome(triggered_enchantments, handler_context)

    async def on_applicant_turn_end(
        self,
        handler_context: HandlerContext,
    ) -> EffectOutcome:
        return EffectOutcome.EMPTY()

    async def on_skill_charges(
        self,
        handler_context: HandlerContext,
    ) -> EffectOutcome:
        triggered_enchantments = await self.enchantment_trigger(
            handler_context.context, handler_context.source, EffectTrigger.SKILL_CHARGE
        )

        if len(triggered_enchantments) <= 0:
            return EffectOutcome.EMPTY()

        return await self.get_outcome(triggered_enchantments, handler_context)

    async def on_skill_hits(
        self,
        handler_context: HandlerContext,
    ) -> EffectOutcome:
        triggered_enchantments = await self.enchantment_trigger(
            handler_context.context, handler_context.source, EffectTrigger.SKILL_HITS
        )

        if len(triggered_enchantments) <= 0:
            return EffectOutcome.EMPTY()

        return await self.get_outcome(triggered_enchantments, handler_context)

    async def get_outcome(
        self,
        gear_enchantments: list[GearEnchantment],
        handler_context: HandlerContext,
    ) -> EffectOutcome:
        outcome_data: dict[EnchantmentType, EffectOutcome] = {}

        for gear_enchantment in gear_enchantments:
            enchantment_type = (
                gear_enchantment.enchantment.base_enchantment.enchantment_type
            )
            handler = await self.get_handler(enchantment_type)
            outcome = await handler.handle(
                gear_enchantment.enchantment, handler_context
            )

            if enchantment_type not in outcome_data:
                outcome_data[enchantment_type] = [outcome]
            else:
                outcome_data[enchantment_type].append(outcome)

            if (
                EffectTrigger.ON_TRIGGER_SUCCESS
                in gear_enchantment.enchantment.base_enchantment.consumed
                and (
                    outcome.flags is None or OutcomeFlag.NO_CONSUME not in outcome.flags
                )
            ):
                await self.consume_enchantment_stack(
                    handler_context.context,
                    handler_context.source,
                    gear_enchantment.enchantment,
                )

        combined_outcomes = []
        for enchantment_type, outcomes in outcome_data.items():
            handler = await self.get_handler(enchantment_type)
            combined = await handler.combine(outcomes, handler_context)
            combined_outcomes.append(combined)

        return EnchantmentEffectHandler.combine_outcomes(combined_outcomes)

    async def consume_enchantment_stack(
        self,
        context: EncounterContext,
        character: Character,
        enchantment: EffectEnchantment,
        amount: int = 1,
    ):
        event = CombatEvent(
            datetime.datetime.now(),
            context.encounter.guild_id,
            context.encounter.id,
            character.id,
            character.id,
            enchantment.base_enchantment.enchantment_type,
            -amount,
            -amount,
            enchantment.id,
            CombatEventType.ENCHANTMENT_EFFECT,
        )
        await self.controller.dispatch_event(event)

    async def enchantment_trigger(
        self,
        context: EncounterContext,
        character: Character,
        trigger: EffectTrigger,
        multi: bool = False,
    ) -> list[GearEnchantment]:
        triggered: list[GearEnchantment] = []
        triggered_types: list[EnchantmentType] = []

        if character.is_enemy:
            return []

        for enchantment in character.active_enchantments:

            is_triggered = trigger in enchantment.base_enchantment.trigger
            is_consumed = trigger in enchantment.base_enchantment.consumed

            if not (is_triggered or is_consumed):
                continue

            gear_enchantment = await self.get_gear_enchantment(character, enchantment)

            enchantment_type = enchantment.base_enchantment.enchantment_type

            if not multi and enchantment_type in triggered_types:
                continue

            stacks_left = gear_enchantment.stacks_left()

            if stacks_left is not None and stacks_left <= 0:
                continue

            if gear_enchantment.on_cooldown():
                continue

            if not gear_enchantment.proc():
                continue

            if is_consumed:
                await self.consume_enchantment_stack(context, character, enchantment)

            if is_triggered:
                triggered.append(gear_enchantment)
                triggered_types.append(enchantment_type)

        triggered = sorted(
            triggered, key=lambda item: item.enchantment.priority, reverse=True
        )
        return triggered
