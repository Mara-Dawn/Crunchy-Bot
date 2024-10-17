import datetime
import random

import discord
from discord.ext import commands

from combat.actors import Character
from combat.enchantments.enchantment import (
    BaseEnchantment,
    EffectEnchantment,
    Enchantment,
)
from combat.enchantments.enchantments import *  # noqa: F403
from combat.enchantments.types import EnchantmentEffect, EnchantmentType
from combat.encounter import EncounterContext
from combat.enemies.enemy import Enemy
from combat.gear.bases import *  # noqa: F403
from combat.gear.default_gear import (
    DefaultAccessory1,
    DefaultAccessory2,
    DefaultCap,
    DefaultPants,
    DefaultShirt,
    DefaultStick,
    DefaultWand,
)
from combat.gear.droppable import Droppable
from combat.gear.gear import DroppableBase, Gear, GearBase
from combat.gear.types import (
    Base,
    EquipmentSlot,
    GearBaseType,
    GearModifierType,
    Rarity,
)
from combat.gear.uniques import *  # noqa: F403
from combat.gear.uniques import Unique
from combat.skills.skill import BaseSkill, Skill
from combat.skills.skills import *  # noqa: F403
from combat.skills.types import SkillType
from combat.types import UnlockableFeature
from control.combat.combat_skill_manager import CombatSkillManager
from control.combat.object_factory import ObjectFactory
from control.controller import Controller
from control.item_manager import ItemManager
from control.logger import BotLogger
from control.service import Service
from control.settings_manager import SettingsManager
from datalayer.database import Database
from events.bot_event import BotEvent
from events.encounter_event import EncounterEvent
from events.inventory_event import InventoryEvent
from events.types import EncounterEventType
from items import BaseKey
from items.item import Item
from items.types import ItemType


class CombatGearManager(Service):

    GENERATOR_VERSION = "0.0.3"

    ITEM_LEVEL_MIN_DROP = 0.6
    SKILL_DROP_CHANCE = 0.1
    ENCHANTMENT_DROP_CHANCE = 0.05
    GEAR_LEVEL_SCALING = 1
    MOB_LOOT_BONUS_SCALING = 1
    MOB_LOOT_UNIQUE_SCALING = 0.2

    BOSS_PLUS_LEVEL_CHANCE = 0.3

    MIN_RARITY_LVL = {
        Rarity.COMMON: 0,
        Rarity.UNCOMMON: 1,
        Rarity.RARE: 2,
        Rarity.UNIQUE: 2,
        Rarity.LEGENDARY: 4,
    }

    RARITY_WEIGHTS = {
        Rarity.COMMON: 100,
        Rarity.UNCOMMON: 50,
        Rarity.RARE: 10,
        Rarity.LEGENDARY: 3,
        Rarity.UNIQUE: 0.5,
    }
    RARITY_SCALING = {
        Rarity.COMMON: -15,
        Rarity.UNCOMMON: -1,
        Rarity.RARE: 7,
        Rarity.LEGENDARY: 2,
        Rarity.UNIQUE: 0.5,
    }

    MODIFIER_COUNT = {
        Rarity.COMMON: 1,
        Rarity.UNCOMMON: 2,
        Rarity.RARE: 3,
        Rarity.LEGENDARY: 4,
        Rarity.UNIQUE: 0,
    }

    ENCHANTMENT_SCALING = 2.5
    SLOT_SCALING = {
        EquipmentSlot.WEAPON: 3,
        EquipmentSlot.HEAD: 1,
        EquipmentSlot.BODY: 3,
        EquipmentSlot.LEGS: 2,
        EquipmentSlot.ACCESSORY: 1,
        EquipmentSlot.SKILL: 1,
    }

    NON_BASE_SCALING_MODIFIERS = [
        GearModifierType.WEAPON_DAMAGE_MIN,
        GearModifierType.WEAPON_DAMAGE_MAX,
    ]

    MODIFIER_BASE = {
        GearModifierType.WEAPON_DAMAGE_MIN: 9,
        GearModifierType.WEAPON_DAMAGE_MAX: 11,
        GearModifierType.ARMOR: 5,
        GearModifierType.ATTACK: 2,
        GearModifierType.MAGIC: 2,
        GearModifierType.HEALING: 2,
        GearModifierType.CRIT_DAMAGE: 5,
        GearModifierType.CRIT_RATE: 3,
        GearModifierType.DEFENSE: 1,
        GearModifierType.EVASION: 2,
        GearModifierType.CONSTITUTION: 3,
        GearModifierType.DEXTERITY: 1,
    }
    MODIFIER_SCALING = {
        GearModifierType.WEAPON_DAMAGE_MIN: 0.5,
        GearModifierType.WEAPON_DAMAGE_MAX: 0.5,
        GearModifierType.ARMOR: 0.3,
        GearModifierType.ATTACK: 1.5,
        GearModifierType.MAGIC: 1.4,
        GearModifierType.HEALING: 0.2,
        GearModifierType.CRIT_DAMAGE: 0.4,
        GearModifierType.CRIT_RATE: 0.15,
        GearModifierType.DEFENSE: 0.15,
        GearModifierType.EVASION: 0.15,
        GearModifierType.CONSTITUTION: 0.3,
        GearModifierType.DEXTERITY: 0.3,
    }
    MODIFIER_RANGE = {
        GearModifierType.WEAPON_DAMAGE_MIN: 0.07,
        GearModifierType.WEAPON_DAMAGE_MAX: 0.07,
        GearModifierType.ARMOR: 0.08,
        GearModifierType.ATTACK: 0.08,
        GearModifierType.MAGIC: 0.08,
        GearModifierType.HEALING: 0.08,
        GearModifierType.CRIT_DAMAGE: 0.35,
        GearModifierType.CRIT_RATE: 0.08,
        GearModifierType.DEFENSE: 0.08,
        GearModifierType.EVASION: 0.08,
        GearModifierType.CONSTITUTION: 0.08,
        GearModifierType.DEXTERITY: 0.08,
    }
    INT_MODIFIERS = [
        GearModifierType.WEAPON_DAMAGE_MIN,
        GearModifierType.WEAPON_DAMAGE_MAX,
        GearModifierType.ARMOR,
        GearModifierType.CONSTITUTION,
        GearModifierType.DEXTERITY,
    ]

    UNIQE_BASE_UPSCALE = {
        1: Stick_T0(),  # noqa: F405
        2: Stick_T1(),  # noqa: F405
        3: Stick_T2(),  # noqa: F405
        4: Stick_T3(),  # noqa: F405
        5: Stick_T4(),  # noqa: F405
        6: Stick_T5(),  # noqa: F405
        7: Stick_T5(),  # noqa: F405
    }

    def __init__(
        self,
        bot: commands.Bot,
        logger: BotLogger,
        database: Database,
        controller: Controller,
    ):
        super().__init__(bot, logger, database)
        self.controller = controller
        self.log_name = "Combat Loot"
        self.item_manager: ItemManager = self.controller.get_service(ItemManager)
        self.settings_manager: SettingsManager = self.controller.get_service(
            SettingsManager
        )
        self.skill_manager: CombatSkillManager = self.controller.get_service(
            CombatSkillManager
        )
        self.factory: ObjectFactory = self.controller.get_service(ObjectFactory)

    async def listen_for_event(self, event: BotEvent):
        pass

    async def get_bases_by_lvl(
        self,
        guild_id: int,
        item_level: int,
        exclude_skills: bool = False,
        gear_slot: EquipmentSlot = None,
    ) -> list[DroppableBase]:
        matching_bases = []

        gear_base_types = [base_type for base_type in GearBaseType]

        skill_base_types = []
        enchantment_base_types = []

        if not exclude_skills:
            skill_base_types = [base_type for base_type in SkillType]

        unlocked = await self.settings_manager.get_unlocked_features(guild_id)
        crafting_unlocked = UnlockableFeature.CRAFTING in unlocked
        enchantments_unlocked = UnlockableFeature.ENCHANTMENTS in unlocked
        if enchantments_unlocked and crafting_unlocked:
            enchantment_base_types = [base_type for base_type in EnchantmentType]
        elif enchantments_unlocked:
            enchantment_base_types = [
                base_type
                for base_type in EnchantmentType
                if not EnchantmentType.is_crafting(base_type)
            ]
        elif crafting_unlocked:
            enchantment_base_types = [
                base_type
                for base_type in EnchantmentType
                if EnchantmentType.is_crafting(base_type)
            ]

        base_types = gear_base_types + skill_base_types + enchantment_base_types

        for base_type in base_types:
            base_class = globals()[base_type]
            base: DroppableBase = base_class()

            if not base.droppable:
                continue

            if issubclass(base.__class__, Unique):
                continue

            if gear_slot is not None and base.slot != gear_slot:
                continue

            if item_level >= base.min_level and item_level <= base.max_level:
                matching_bases.append(base)

        return matching_bases

    async def get_random_base(
        self,
        guild_id: int,
        item_level: int,
        enemy: Enemy = None,
        exclude_skills: bool = False,
        gear_slot: EquipmentSlot = None,
        random_seed=None,
    ) -> DroppableBase:

        bases = await self.get_bases_by_lvl(
            guild_id=guild_id,
            item_level=item_level,
            exclude_skills=exclude_skills,
            gear_slot=gear_slot,
        )

        if len(bases) <= 0:
            return None

        if enemy is not None:
            skill_base_types = enemy.skill_loot_table
            gear_base_types = enemy.gear_loot_table

            table_base_types = gear_base_types + skill_base_types

            if not enemy.random_loot:
                bases = []

            for base_type in table_base_types:
                base_class = globals()[base_type]
                base: DroppableBase = base_class()
                bases.append(base)

        skill_weight = 0
        gear_weight = 0
        enchantment_weight = 0

        for base in bases:
            match base.base_type:
                case Base.SKILL:
                    skill_weight += base.weight
                case Base.GEAR:
                    gear_weight += base.weight
                case Base.ENCHANTMENT:
                    enchantment_weight += base.weight

        skill_mod = 0
        enchantment_mod = 0
        if not exclude_skills and skill_weight > 0:
            skill_mod = (
                self.SKILL_DROP_CHANCE
                * (skill_weight + gear_weight + enchantment_weight)
                / skill_weight
            )
        if enchantment_weight > 0:
            enchantment_mod = (
                self.ENCHANTMENT_DROP_CHANCE
                * (skill_weight + gear_weight + enchantment_weight)
                / enchantment_weight
            )
        # Forces chance of skill dropping to self.SKILL_DROP_CHANCE while keeping weights

        weights = []
        for base in bases:
            weight = base.weight

            if enemy is not None and (
                base.type in enemy.skill_loot_table
                or base.type in enemy.gear_loot_table
            ):
                scaling = self.MOB_LOOT_BONUS_SCALING
                if issubclass(base.__class__, Unique):
                    scaling *= self.MOB_LOOT_UNIQUE_SCALING
                weight *= scaling

            match base.base_type:
                case Base.SKILL:
                    weight *= skill_mod
                case Base.ENCHANTMENT:
                    weight *= enchantment_mod
                case Base.GEAR:
                    weight *= 1 - (skill_mod + enchantment_mod)
            weights.append(weight)

        sum_weights = sum(weights)
        chances = [v / sum_weights for v in weights]

        if random_seed is not None:
            random.seed(random_seed)

        result = random.choices(bases, weights=chances)[0]

        if random_seed is not None:
            random.seed(None)

        return result

    async def get_random_rarity(self, item_level, random_seed=None) -> Rarity:
        weights = {}

        for rarity, weight in self.RARITY_WEIGHTS.items():
            weight += item_level * self.RARITY_SCALING[rarity]
            weight = max(0, weight)

            if self.MIN_RARITY_LVL[rarity] > item_level:
                weight = 0

            weights[rarity] = weight

        sum_weights = sum(weights.values())
        chances = [v / sum_weights for _, v in weights.items()]
        rarities = [k for k in weights]

        if random_seed is not None:
            random.seed(random_seed)

        result = random.choices(rarities, weights=chances)[0]

        if random_seed is not None:
            random.seed(None)

        return result

    async def get_random_unique_modifiers(
        self, base: GearBase, item_level: int, random_seed=None
    ) -> dict[GearModifierType, float]:
        modifiers = {}
        unique: Unique = base
        for modifier_type, scaling in unique.unique_modifiers.items():

            effective_base = base
            if base.slot == EquipmentSlot.WEAPON and modifier_type in [
                GearModifierType.WEAPON_DAMAGE_MIN,
                GearModifierType.WEAPON_DAMAGE_MAX,
            ]:
                effective_base = self.UNIQE_BASE_UPSCALE[item_level]

            min_roll, max_roll = await self.get_modifier_boundaries(
                effective_base, item_level, modifier_type
            )

            min_roll *= 0.9
            max_roll *= 1.1

            if random_seed is not None:
                random.seed(random_seed)

            value = random.uniform(min_roll, max_roll)
            value *= scaling

            if random_seed is not None:
                random.seed(None)

            if modifier_type in self.INT_MODIFIERS:
                value = int(value)

            modifiers[modifier_type] = value

        return modifiers

    async def get_random_modifiers(
        self, base: GearBase, item_level: int, rarity: Rarity, random_seed=None
    ) -> dict[GearModifierType, float]:
        modifiers = {}

        if rarity == Rarity.UNIQUE:
            return await self.get_random_unique_modifiers(base, item_level, random_seed)

        allowed_modifiers = base.get_allowed_modifiers()
        modifier_count = self.MODIFIER_COUNT[rarity]

        if random_seed is not None:
            random.seed(random_seed)

        modifier_types = random.sample(allowed_modifiers, k=modifier_count)

        if random_seed is not None:
            random.seed(None)

        modifier_types.extend(base.modifiers)

        for modifier_type in modifier_types:
            modifiers[modifier_type] = await self.roll_modifier_value(
                base, item_level, modifier_type, random_seed
            )

        return modifiers

    async def roll_modifier_value(
        self,
        base: GearBase,
        item_level: int,
        modifier_type: GearModifierType,
        random_seed=None,
    ) -> float:
        min_roll, max_roll = await self.get_modifier_boundaries(
            base, item_level, modifier_type
        )

        if random_seed is not None:
            random.seed(random_seed)

        value = random.uniform(min_roll, max_roll)

        if random_seed is not None:
            random.seed(None)

        if modifier_type in self.INT_MODIFIERS:
            value = int(value)

        return value

    async def get_modifier_boundaries(
        self, base: GearBase, item_level: int, modifier_type: GearModifierType
    ):
        slot_scaling = (
            self.SLOT_SCALING[base.slot]
            if modifier_type not in self.NON_BASE_SCALING_MODIFIERS
            else 1
        )

        base_value = (
            (
                self.MODIFIER_BASE[modifier_type]
                + self.MODIFIER_BASE[modifier_type]
                * (self.MODIFIER_SCALING[modifier_type])
                * (item_level - 1)
                * self.GEAR_LEVEL_SCALING
            )
            * slot_scaling
            * base.scaling
        )

        min_roll = max(
            self.MODIFIER_BASE[modifier_type] * slot_scaling,
            base_value * (1 - self.MODIFIER_RANGE[modifier_type]),
        )
        max_roll = base_value * (1 + self.MODIFIER_RANGE[modifier_type])

        return min_roll, max_roll

    async def get_member_daily_items(
        self,
        member_id: int,
        guild_id: int,
    ) -> list[Gear]:
        seed_base = datetime.datetime.now().date().strftime("%Y%m%d") + str(member_id)
        daily_items = []

        def my_hash(text: str):
            hash = 0
            for ch in text:
                hash = (hash * 281 ^ ord(ch) * 997) & 0xFFFFFFFF
            return hash

        level = await self.database.get_forge_level(guild_id)

        already_bought = await self.database.get_already_bought_daily_gear(
            member_id, guild_id
        )

        seed = seed_base + "a"
        item = await self.generate_drop(
            member_id=None,
            guild_id=guild_id,
            item_level=level,
            exclude_skills=True,
            random_seed=seed,
        )
        item.id = my_hash(seed)
        if item.id not in already_bought:
            daily_items.append(item)

        seed = seed_base + "b"
        item = await self.generate_drop(
            member_id=None,
            guild_id=guild_id,
            item_level=level,
            exclude_skills=True,
            random_seed=seed,
        )
        item.id = my_hash(seed)
        if item.id not in already_bought:
            daily_items.append(item)

        seed = seed_base + "c"
        item = await self.generate_drop(
            member_id=None,
            guild_id=guild_id,
            item_level=level,
            gear_slot=EquipmentSlot.SKILL,
            random_seed=seed,
        )
        item.id = my_hash(seed)
        if item.id not in already_bought:
            daily_items.append(item)

        return daily_items

    async def generate_drop(
        self,
        member_id: int,
        guild_id: int,
        item_level: int,
        enemy: Enemy = None,
        exclude_skills: bool = False,
        gear_slot: EquipmentSlot = None,
        random_seed=None,
    ) -> Gear:

        droppable_base = await self.get_random_base(
            guild_id=guild_id,
            item_level=item_level,
            enemy=enemy,
            exclude_skills=exclude_skills,
            gear_slot=gear_slot,
            random_seed=random_seed,
        )

        if droppable_base is None:
            return None

        rarity = await self.get_random_rarity(item_level, random_seed=random_seed)

        return await self.generate_specific_drop(
            member_id=member_id,
            guild_id=guild_id,
            item_level=item_level,
            base=droppable_base,
            rarity=rarity,
            random_seed=random_seed,
        )

    async def generate_specific_drop(
        self,
        member_id: int,
        guild_id: int,
        item_level: int,
        base: DroppableBase,
        rarity: Rarity,
        random_seed=None,
    ) -> Gear:

        if rarity == Rarity.UNIQUE:
            if len(base.uniques) <= 0:
                max_rarity = Rarity.COMMON
                guild_level = await self.database.get_guild_level(guild_id)
                for min_rarity, level in self.MIN_RARITY_LVL.items():
                    if level <= guild_level:
                        max_rarity = min_rarity
                    else:
                        break
                rarity = max_rarity
            else:
                if random_seed is not None:
                    random.seed(random_seed)

                unique_base_type = random.choices(base.uniques)[0]
                base = await self.factory.get_base(unique_base_type)

                if random_seed is not None:
                    random.seed(None)

        if issubclass(base.__class__, Unique):
            rarity = Rarity.UNIQUE

        match base.base_type:
            case Base.SKILL:
                skill_base: BaseSkill = base
                skill = Skill(
                    base_skill=skill_base,
                    rarity=rarity,
                    level=item_level,
                )

                if member_id is not None:
                    skill.id = await self.database.log_user_drop(
                        guild_id=guild_id,
                        member_id=member_id,
                        drop=skill,
                        generator_version=self.GENERATOR_VERSION,
                    )

                return skill

            case Base.ENCHANTMENT:
                base_enchantment: BaseEnchantment = base
                match base_enchantment.enchantment_type:
                    case EnchantmentType.SKILL_STACKS:
                        base_enchantment = SkillStacks(item_level)  # noqa: F405
                if rarity not in base_enchantment.rarities:
                    min_weight = self.RARITY_WEIGHTS[rarity]
                    matched_rarity = None
                    for comparison_rarity, weight in self.RARITY_WEIGHTS.items():
                        if comparison_rarity not in base_enchantment.rarities:
                            continue

                        matched_rarity = comparison_rarity

                        if weight <= min_weight:
                            break

                    rarity = matched_rarity
                if base_enchantment.enchantment_effect == EnchantmentEffect.EFFECT:
                    enchantment = EffectEnchantment(
                        base_enchantment=base_enchantment,
                        rarity=rarity,
                        level=item_level,
                    )
                else:
                    enchantment = Enchantment(
                        base_enchantment=base_enchantment,
                        rarity=rarity,
                        level=item_level,
                    )

                if member_id is not None:
                    enchantment.id = await self.database.log_user_drop(
                        guild_id=guild_id,
                        member_id=member_id,
                        drop=enchantment,
                        generator_version=self.GENERATOR_VERSION,
                    )

                return enchantment

            case Base.GEAR:
                gear_base: GearBase = base
                modifiers = await self.get_random_modifiers(
                    gear_base,
                    item_level,
                    rarity,
                    random_seed=random_seed,
                )

                skills = []
                skills.extend(gear_base.skills)

                # add enchantments

                gear_item = Gear(
                    name="",
                    base=gear_base,
                    rarity=rarity,
                    level=item_level,
                    modifiers=modifiers,
                    skills=skills,
                    enchantments=[],
                )

                if member_id is not None:
                    gear_item.id = await self.database.log_user_drop(
                        guild_id=guild_id,
                        member_id=member_id,
                        drop=gear_item,
                        generator_version=self.GENERATOR_VERSION,
                    )

                return gear_item

    async def generate_encounter_drop(
        self,
        combatant: Character,
        context: EncounterContext,
    ) -> Gear:
        guild_id = combatant.member.guild.id
        member_id = combatant.member.id
        enemy_level = context.opponent.level
        enemy = context.opponent.enemy

        guild_level = await self.database.get_guild_level(guild_id)
        item_level = min(enemy_level, guild_level)

        if enemy.is_boss and random.random() < self.BOSS_PLUS_LEVEL_CHANCE:
            item_level += 1

        return await self.generate_drop(member_id, guild_id, item_level, enemy)

    async def get_combatant_penalty(
        self, character: Character, encounter_events: list[EncounterEvent]
    ) -> float:
        for event in encounter_events:
            if event.member_id == character.member.id:
                match event.encounter_event_type:
                    case EncounterEventType.PENALTY50:
                        return 0.5
                    case EncounterEventType.PENALTY75:
                        return 0.75
        return 0

    async def scrap_gear(
        self, member: discord.Member, guild_id: int, gear_to_scrap: list[Gear]
    ) -> int:
        total_scraps = 0
        for gear in gear_to_scrap:
            total_scraps += await self.get_gear_scrap_value(gear)

            self.logger.log(
                guild_id,
                f"Gear piece was scrapped by {member.display_name}: lvl.{gear.level} {gear.rarity.value} {gear.name}",
                cog="Equipment",
            )

        await self.database.delete_gear_by_ids([gear.id for gear in gear_to_scrap])

        if total_scraps > 0:
            event = InventoryEvent(
                datetime.datetime.now(),
                guild_id,
                member.id,
                ItemType.SCRAP,
                total_scraps,
            )
            await self.controller.dispatch_event(event)
        return total_scraps

    async def roll_enemy_loot(
        self, context: EncounterContext
    ) -> dict[int, tuple[int, list[Droppable], Item]]:
        enemy = context.opponent.enemy
        enemy_level = context.opponent.level
        guild_id = context.encounter.guild_id

        loot = {}

        loot_table = enemy.item_loot_table.copy()
        if enemy_level in BaseKey.TYPE_MAP:
            loot_table.append(BaseKey.TYPE_MAP[enemy_level])

        loot_items = [
            (await self.item_manager.get_item(guild_id, x)) for x in loot_table
        ]

        weights = [item.weight for item in loot_items]
        weights = [1.0 / w for w in weights]
        sum_weights = sum(weights)
        weights = [w / sum_weights for w in weights]

        for combatant in context.combatants:
            if combatant.is_out:
                continue

            penalty = await self.get_combatant_penalty(
                combatant, context.encounter_events
            )

            beans_amount = int(enemy.roll_beans_amount(enemy_level) * (1 - penalty))
            loot_amount = max(
                1, int(enemy.roll_loot_amount(enemy_level) * (1 - penalty))
            )
            bonus_loot_drop = random.random() < (
                enemy.bonus_loot_chance * (1 - penalty)
            )

            drops = []
            for _ in range(loot_amount):
                drop = await self.generate_encounter_drop(combatant, context)
                if drop is not None:
                    drops.append(drop)

            bonus_loot = None
            if bonus_loot_drop:
                bonus_loot = random.choices(loot_items, weights=weights)[0]

            loot[combatant.member] = (beans_amount, drops, bonus_loot)

        return loot

    async def get_default_gear(self) -> list[Gear]:
        return [
            DefaultAccessory1(),
            DefaultAccessory2(),
            DefaultCap(),
            DefaultPants(),
            DefaultShirt(),
            DefaultStick(),
            DefaultWand(),
        ]

    async def get_gear_scrap_value(self, gear: Gear) -> float:
        item_level_weight = 1
        rarity_weight = 1

        rarity_weight = {
            Rarity.COMMON: 1,
            Rarity.UNCOMMON: 3,
            Rarity.RARE: 4,
            Rarity.LEGENDARY: 8,
            Rarity.UNIQUE: 6,
        }
        gear_score = gear.level * item_level_weight
        gear_score *= rarity_weight[gear.rarity]
        if gear.base.base_type == Base.ENCHANTMENT:
            gear_score *= self.ENCHANTMENT_SCALING
        else:
            gear_score *= self.SLOT_SCALING[gear.slot]

        return int(gear_score)

    async def test_generation(self):
        for _ in range(10):
            gear = await self.generate_drop(1197312669179461683, None, 1)
            print("Gear:")
            print(f"{gear.base.name}")
            print(f"{gear.rarity.value}")
            print(f"lvl: {gear.level}")
            print("Modifiers:")

            for mod, value in gear.modifiers.items():
                print(f"  {mod.name}: {value}")

    async def test(self):
        # levels = range(9, 13)

        for base_type in GearBaseType:
            base_class = globals()[base_type]
            base: GearBase = base_class()

            if base.slot != EquipmentSlot.WEAPON:
                continue

            print("#" * 30)
            print(f"Base: {base.type.value}")
            print("#" * 30)
            print("-" * 30)
            print("Levels:")
            print("-" * 30)

            for level in range(base.min_level, base.max_level):
                print(f"  {level}:")
                allowed_modifiers = base.get_allowed_modifiers()

                allowed_modifiers.extend(base.modifiers)

                for modifier_type in allowed_modifiers:
                    min_roll, max_roll = await self.get_modifier_boundaries(
                        base, level, modifier_type
                    )

                    print(f"    {modifier_type.value}: {min_roll:.2f} - {max_roll:.2f}")
