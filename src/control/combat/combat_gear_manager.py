import random
import secrets

from combat.encounter import EncounterContext
from combat.gear.bases import *  # noqa: F403
from combat.gear.gear import Gear, GearBase
from combat.gear.types import GearBaseType, GearModifierType, GearRarity, GearSlot
from control.controller import Controller
from control.item_manager import ItemManager
from control.logger import BotLogger
from control.service import Service
from datalayer.database import Database
from discord.ext import commands
from events.bot_event import BotEvent


class CombatGearManager(Service):

    GENERATOR_VERSION = "0.0.1"

    ITEM_LEVEL_MIN_DROP = 0.6

    MIN_RARITY_LVL = {
        GearRarity.NORMAL: 0,
        GearRarity.MAGIC: 1,
        GearRarity.RARE: 3,
        GearRarity.LEGENDARY: 6,
        GearRarity.UNIQUE: 4,
    }
    RARITY_WEIGHTS = {
        GearRarity.NORMAL: 100,
        GearRarity.MAGIC: 50,
        GearRarity.RARE: 10,
        GearRarity.LEGENDARY: 1,
        GearRarity.UNIQUE: 5,
    }
    RARITY_SCALING = {
        GearRarity.NORMAL: -15,
        GearRarity.MAGIC: 1,
        GearRarity.RARE: 6,
        GearRarity.LEGENDARY: 1,
        GearRarity.UNIQUE: 1.5,
    }

    MODIFIER_COUNT = {
        GearRarity.NORMAL: 1,
        GearRarity.MAGIC: 2,
        GearRarity.RARE: 3,
        GearRarity.LEGENDARY: 4,
        GearRarity.UNIQUE: 0,
    }

    SLOT_SCALING = {
        GearSlot.WEAPON: 3,
        GearSlot.HEAD: 1,
        GearSlot.BODY: 3,
        GearSlot.LEGS: 2,
        GearSlot.ACCESSORY: 1,
    }

    MODIFIER_BASE = {
        GearModifierType.WEAPON_DAMAGE_MIN: 1,
        GearModifierType.WEAPON_DAMAGE_MAX: 3,
        GearModifierType.ARMOR: 5,
        GearModifierType.ATTACK: 1,
        GearModifierType.MAGIC: 1,
        GearModifierType.HEALING: 1,
        GearModifierType.CRIT_DAMAGE: 1,
        GearModifierType.CRIT_RATE: 1,
        GearModifierType.DEFENSE: 1,
        GearModifierType.CONSTITUTION: 5,
        GearModifierType.DEXTERITY: 1,
    }
    MODIFIER_SCALING = {
        GearModifierType.WEAPON_DAMAGE_MIN: 0.3,
        GearModifierType.WEAPON_DAMAGE_MAX: 0.3,
        GearModifierType.ARMOR: 0.3,
        GearModifierType.ATTACK: 0.5,
        GearModifierType.MAGIC: 0.5,
        GearModifierType.HEALING: 0.5,
        GearModifierType.CRIT_DAMAGE: 0.5,
        GearModifierType.CRIT_RATE: 0.5,
        GearModifierType.DEFENSE: 0.5,
        GearModifierType.CONSTITUTION: 0.3,
        GearModifierType.DEXTERITY: 0.3,
    }
    MODIFIER_RANGE = {
        GearModifierType.WEAPON_DAMAGE_MIN: 0.15,
        GearModifierType.WEAPON_DAMAGE_MAX: 0.15,
        GearModifierType.ARMOR: 0.15,
        GearModifierType.ATTACK: 0.15,
        GearModifierType.MAGIC: 0.15,
        GearModifierType.HEALING: 0.15,
        GearModifierType.CRIT_DAMAGE: 0.15,
        GearModifierType.CRIT_RATE: 0.15,
        GearModifierType.DEFENSE: 0.15,
        GearModifierType.CONSTITUTION: 0.15,
        GearModifierType.DEXTERITY: 0.15,
    }
    INT_MODIFIERS = [
        GearModifierType.WEAPON_DAMAGE_MIN,
        GearModifierType.WEAPON_DAMAGE_MAX,
        GearModifierType.ARMOR,
        GearModifierType.CONSTITUTION,
        GearModifierType.DEXTERITY,
    ]

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

    async def listen_for_event(self, event: BotEvent):
        pass

    async def get_bases_by_lvl(self, item_level: int) -> list[GearBase]:
        matching_bases = []
        for base_type in GearBaseType:
            base_class = globals()[base_type]
            base: GearBase = base_class()
            if item_level >= base.min_level and item_level <= base.max_level:
                matching_bases.append(base)

        return matching_bases

    async def get_random_base(self, item_level: int) -> GearBase:
        max_level = item_level
        min_level = max(1, int(item_level * self.ITEM_LEVEL_MIN_DROP))

        drop_item_level = random.randint(min_level, max_level)

        bases = await self.get_bases_by_lvl(drop_item_level)
        base = secrets.choice(bases)
        return base

    async def get_random_rarity(self, item_level) -> GearRarity:
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

        return random.choices(rarities, weights=chances)[0]

    async def get_random_modifiers(
        self, base: GearBase, item_level: int, rarity: GearRarity
    ) -> dict[GearModifierType, float]:
        modifiers = {}
        allowed_modifiers = base.get_allowed_modifiers()
        modifier_count = self.MODIFIER_COUNT[rarity]

        modifier_types = random.sample(allowed_modifiers, k=modifier_count)
        modifier_types.extend(base.modifiers)

        for modifier_type in modifier_types:
            base_value = (
                self.MODIFIER_BASE[modifier_type]
                + self.SLOT_SCALING[base.slot]
                * self.MODIFIER_SCALING[modifier_type]
                * base.scaling
                * item_level
            )

            min_roll = base_value * (1 - self.MODIFIER_RANGE[modifier_type])
            max_roll = base_value * (1 + self.MODIFIER_RANGE[modifier_type])
            value = random.uniform(min_roll, max_roll)

            if modifier_type in self.INT_MODIFIERS:
                value = int(value)

            modifiers[modifier_type] = value

        return modifiers

    async def generate_gear_piece(
        self,
        guild_id: int,
        member_id: int,
        enemy_level: int,
    ) -> Gear:
        guild_level = await self.database.get_guild_level(guild_id)
        item_level = min(enemy_level, guild_level)

        gear_base = await self.get_random_base(item_level)
        rarity = await self.get_random_rarity(item_level)
        modifiers = await self.get_random_modifiers(gear_base, item_level, rarity)

        # add skills
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
            gear_item.id = await self.database.log_user_gear(
                guild_id=guild_id, member_id=member_id, gear=gear_item
            )

        return gear_item

    async def roll_enemy_loot(self, context: EncounterContext):
        enemy = context.opponent.enemy

        loot = {}

        for combatant in context.combatants:

            guild_id = combatant.member.guild.id
            member_id = combatant.member.id

            beans_amount = random.randint(
                enemy.min_beans_reward, enemy.max_beans_reward
            )
            gear_amount = random.randint(
                enemy.min_gear_drop_count, enemy.max_gear_drop_count
            )
            bonus_loot_drop = random.random() < enemy.bonus_loot_chance

            gear = []
            for _ in range(gear_amount):
                gear_piece = await self.generate_gear_piece(
                    guild_id, member_id, enemy.min_level
                )
                gear.append(gear_piece)

            bonus_loot = None
            if bonus_loot_drop and len(enemy.loot_table) > 0:
                loot_items = [
                    (await self.item_manager.get_item(guild_id, x))
                    for x in enemy.loot_table
                ]
                weights = [item.weight for item in loot_items]
                weights = [1.0 / w for w in weights]
                sum_weights = sum(weights)
                weights = [w / sum_weights for w in weights]
                bonus_loot = random.choices(loot_items, weights=weights)[0]

            loot[combatant.member] = (beans_amount, gear, bonus_loot)

        return loot

    async def test_generation(self):
        for _ in range(10):
            gear = await self.generate_gear_piece(1197312669179461683, None, 1)
            print("Gear:")
            print(f"{gear.base.name}")
            print(f"{gear.rarity.value}")
            print(f"lvl: {gear.level}")
            print("Modifiers:")

            for mod, value in gear.modifiers.items():
                print(f"  {mod.name}: {value}")

    async def test(self):
        # levels = range(1, 13)
        levels = range(9, 13)

        for level in levels:
            print("#" * 30)
            print("#" * 30)
            print(f"\nLevel: {level}")
            print("-" * 30)
            print("Rarities:")
            print("-" * 30)
            weights = {}

            for rarity, weight in self.RARITY_WEIGHTS.items():
                weight += level * self.RARITY_SCALING[rarity]

                weight = max(0, weight)

                if self.MIN_RARITY_LVL[rarity] > level:
                    weight = 0

                weights[rarity] = weight

            sum_weights = sum(weights.values())
            # weights = {k: v / sum_weights for k, v in weights.items()}

            for rarity, weight in weights.items():
                percent = weight / sum_weights * 100
                print(f"{rarity.value}: {percent:.02f}%")

            print("-" * 30)
            print("Bases:")
            print("-" * 30)
            bases = await self.get_bases_by_lvl(level, level)

            for base in bases:
                print(f"  {base.type.value}:")
                allowed_modifiers = base.get_allowed_modifiers()

                allowed_modifiers.extend(base.modifiers)

                for modifier_type in allowed_modifiers:
                    base_value = (
                        self.MODIFIER_BASE[modifier_type]
                        + self.SLOT_SCALING[base.slot]
                        * self.MODIFIER_SCALING[modifier_type]
                        * base.scaling
                        * level
                    )

                    min_roll = base_value * (1 - self.MODIFIER_RANGE[modifier_type])
                    max_roll = base_value * (1 + self.MODIFIER_RANGE[modifier_type])

                    if modifier_type in self.INT_MODIFIERS:
                        min_roll = int(min_roll)
                        max_roll = int(max_roll)

                    print(f"    {modifier_type.value}: {min_roll:.2f} - {max_roll:.2f}")
