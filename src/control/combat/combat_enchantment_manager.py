import random

from discord.ext import commands

from combat.actors import Character
from combat.enchantments.enchantment import (
    CraftDisplayWrapper,
    EffectEnchantment,
    GearEnchantment,
)
from combat.enchantments.enchantment_handler import (
    EnchantmentEffectHandler,
    EnchantmentHandler,
)
from combat.enchantments.types import EnchantmentEffect
from combat.gear.gear import Enchantment
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

    async def listen_for_event(self, event: BotEvent):
        pass

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
                if base_dmg_type != enchantment.base_skill.skill_effect:
                    modifier *= Config.SKILL_TYPE_PENALTY
            case SkillEffect.MAGICAL_DAMAGE:
                modifier += character.equipment.attributes[
                    CharacterAttribute.MAGIC_DAMAGE_INCREASE
                ]
                if base_dmg_type != enchantment.base_skill.skill_effect:
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
