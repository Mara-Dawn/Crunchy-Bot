import random

from combat.actors import Character
from combat.encounter import EncounterContext
from combat.enemies.enemy import Enemy
from combat.gear import (
    DefaultAccessory1,
    DefaultAccessory2,
    DefaultCap,
    DefaultPants,
    DefaultShirt,
    DefaultStick,
    DefaultWand,
)
from combat.gear.bases import *  # noqa: F403
from combat.gear.gear import DroppableBase, Gear, GearBase
from combat.gear.types import (
    Base,
    EquipmentSlot,
    GearBaseType,
    GearModifierType,
    Rarity,
)
from combat.skills.skill import BaseSkill, Skill
from combat.skills.skills import *  # noqa: F403
from combat.skills.types import SkillType
from control.combat.combat_skill_manager import CombatSkillManager
from control.controller import Controller
from control.item_manager import ItemManager
from control.logger import BotLogger
from control.service import Service
from datalayer.database import Database
from discord.ext import commands
from events.bot_event import BotEvent
from events.encounter_event import EncounterEvent
from events.types import EncounterEventType


class CombatGearManager(Service):

    GENERATOR_VERSION = "0.0.1"

    ITEM_LEVEL_MIN_DROP = 0.6

    SKILL_DROP_CHANCE = 0.1

    MIN_RARITY_LVL = {
        Rarity.NORMAL: 0,
        Rarity.MAGIC: 1,
        Rarity.RARE: 2,
        Rarity.LEGENDARY: 5,
        Rarity.UNIQUE: 3,
    }
    RARITY_WEIGHTS = {
        Rarity.NORMAL: 100,
        Rarity.MAGIC: 50,
        Rarity.RARE: 10,
        Rarity.LEGENDARY: 1,
        Rarity.UNIQUE: 5,
    }
    RARITY_SCALING = {
        Rarity.NORMAL: -15,
        Rarity.MAGIC: 1,
        Rarity.RARE: 6,
        Rarity.LEGENDARY: 1,
        Rarity.UNIQUE: 1.5,
    }

    MODIFIER_COUNT = {
        Rarity.NORMAL: 1,
        Rarity.MAGIC: 2,
        Rarity.RARE: 3,
        Rarity.LEGENDARY: 4,
        Rarity.UNIQUE: 0,
    }

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
        GearModifierType.WEAPON_DAMAGE_MIN: 7,
        GearModifierType.WEAPON_DAMAGE_MAX: 10,
        GearModifierType.ARMOR: 5,
        GearModifierType.ATTACK: 2,
        GearModifierType.MAGIC: 2,
        GearModifierType.HEALING: 2,
        GearModifierType.CRIT_DAMAGE: 4,
        GearModifierType.CRIT_RATE: 2,
        GearModifierType.DEFENSE: 1,
        GearModifierType.CONSTITUTION: 3,
        GearModifierType.DEXTERITY: 1,
    }
    MODIFIER_SCALING = {
        GearModifierType.WEAPON_DAMAGE_MIN: 0.5,
        GearModifierType.WEAPON_DAMAGE_MAX: 0.5,
        GearModifierType.ARMOR: 0.3,
        GearModifierType.ATTACK: 0.6,
        GearModifierType.MAGIC: 0.55,
        GearModifierType.HEALING: 0.6,
        GearModifierType.CRIT_DAMAGE: 0.15,
        GearModifierType.CRIT_RATE: 0.03,
        GearModifierType.DEFENSE: 0.15,
        GearModifierType.CONSTITUTION: 0.3,
        GearModifierType.DEXTERITY: 0.3,
    }
    MODIFIER_RANGE = {
        GearModifierType.WEAPON_DAMAGE_MIN: 0.05,
        GearModifierType.WEAPON_DAMAGE_MAX: 0.05,
        GearModifierType.ARMOR: 0.05,
        GearModifierType.ATTACK: 0.05,
        GearModifierType.MAGIC: 0.05,
        GearModifierType.HEALING: 0.05,
        GearModifierType.CRIT_DAMAGE: 0.05,
        GearModifierType.CRIT_RATE: 0.05,
        GearModifierType.DEFENSE: 0.05,
        GearModifierType.CONSTITUTION: 0.05,
        GearModifierType.DEXTERITY: 0.05,
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
        self.skill_manager: CombatSkillManager = self.controller.get_service(
            CombatSkillManager
        )

    async def listen_for_event(self, event: BotEvent):
        pass

    async def get_bases_by_lvl(self, item_level: int) -> list[DroppableBase]:
        matching_bases = []

        gear_base_types = [base_type for base_type in GearBaseType]
        skill_base_types = [base_type for base_type in SkillType]

        base_types = gear_base_types + skill_base_types

        for base_type in base_types:
            base_class = globals()[base_type]
            base: DroppableBase = base_class()

            if not base.droppable:
                continue

            if item_level >= base.min_level and item_level <= base.max_level:
                matching_bases.append(base)

        return matching_bases

    async def get_random_base(self, item_level: int, enemy: Enemy) -> DroppableBase:
        max_level = item_level
        min_level = max(1, int(item_level * self.ITEM_LEVEL_MIN_DROP))

        drop_item_level = random.randint(min_level, max_level)

        bases = await self.get_bases_by_lvl(drop_item_level)

        if len(bases) <= 0:
            return None

        gear_base_types = enemy.gear_loot_table
        skill_base_types = enemy.skill_loot_table

        table_base_types = gear_base_types + skill_base_types

        for base_type in table_base_types:
            base_class = globals()[base_type]
            base: DroppableBase = base_class()
            bases.append(base)

        skill_weight = 0
        gear_weight = 0

        for base in bases:
            match base.base_type:
                case Base.SKILL:
                    skill_weight += base.weight
                case Base.GEAR:
                    gear_weight += base.weight

        skill_mod = self.SKILL_DROP_CHANCE * (skill_weight + gear_weight) / skill_weight
        # Forces chance of skill dropping to self.SKILL_DROP_CHANCE while keeping weights

        weights = []
        for base in bases:
            weight = base.weight
            match base.base_type:
                case Base.SKILL:
                    weight *= skill_mod
                case Base.GEAR:
                    weight *= 1 - skill_mod
            weights.append(weight)

        sum_weights = sum(weights)
        chances = [v / sum_weights for v in weights]
        return random.choices(bases, weights=chances)[0]

    async def get_random_rarity(self, item_level) -> Rarity:
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
        self, base: GearBase, item_level: int, rarity: Rarity
    ) -> dict[GearModifierType, float]:
        modifiers = {}
        allowed_modifiers = base.get_allowed_modifiers()
        modifier_count = self.MODIFIER_COUNT[rarity]

        modifier_types = random.sample(allowed_modifiers, k=modifier_count)
        modifier_types.extend(base.modifiers)

        for modifier_type in modifier_types:
            min_roll, max_roll = await self.get_modifier_boundaries(
                base, item_level, modifier_type
            )
            value = random.uniform(min_roll, max_roll)

            if modifier_type in self.INT_MODIFIERS:
                value = int(value)

            modifiers[modifier_type] = value

        return modifiers

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

    async def generate_drop(
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

        droppable_base = await self.get_random_base(item_level, enemy)

        if droppable_base is None:
            return None

        rarity = await self.get_random_rarity(item_level)

        match droppable_base.base_type:
            case Base.SKILL:
                skill_base: BaseSkill = droppable_base
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

            case Base.GEAR:
                gear_base: GearBase = droppable_base
                modifiers = await self.get_random_modifiers(
                    gear_base, item_level, rarity
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

    async def roll_enemy_loot(self, context: EncounterContext):
        enemy = context.opponent.enemy

        loot = {}

        for combatant in context.combatants:

            guild_id = combatant.member.guild.id

            penalty = await self.get_combatant_penalty(
                combatant, context.encounter_events
            )

            beans_amount = int(
                enemy.roll_beans_amount(context.opponent.level) * (1 - penalty)
            )
            loot_amount = int(
                enemy.roll_loot_amount(context.opponent.level) * (1 - penalty)
            )
            bonus_loot_drop = random.random() < (
                enemy.bonus_loot_chance * (1 - penalty)
            )

            drops = []
            for _ in range(loot_amount):
                drop = await self.generate_drop(combatant, context)
                if drop is not None:
                    drops.append(drop)

            bonus_loot = None
            if bonus_loot_drop and len(enemy.item_loot_table) > 0:
                loot_items = [
                    (await self.item_manager.get_item(guild_id, x))
                    for x in enemy.item_loot_table
                ]
                weights = [item.weight for item in loot_items]
                weights = [1.0 / w for w in weights]
                sum_weights = sum(weights)
                weights = [w / sum_weights for w in weights]
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

    async def get_gear_score(self, gear: Gear) -> float:
        item_level_weight = 1
        rarity_weight = 1

        rarity_weight = {
            Rarity.NORMAL: 1,
            Rarity.MAGIC: 3,
            Rarity.RARE: 5,
            Rarity.LEGENDARY: 10,
            Rarity.UNIQUE: 8,
        }

        gear_score = gear.level * item_level_weight
        gear_score *= rarity_weight[gear.rarity]

        return gear_score

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
