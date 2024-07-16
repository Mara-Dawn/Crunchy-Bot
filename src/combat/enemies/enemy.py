import random

import discord
from combat.enemies.types import EnemyType
from combat.gear.types import CharacterAttribute, GearBaseType
from combat.skills.types import SkillType
from items.types import ItemType


class Enemy:

    LOOT_MIN_AMOUNT_BY_LVL = {
        1: 2,
        2: 2,
        3: 2,
        4: 2,
        5: 3,
        6: 3,
        7: 3,
        8: 3,
        9: 4,
        10: 4,
        11: 4,
        12: 4,
    }

    LOOT_MAX_AMOUNT_BY_LVL = {
        1: 3,
        2: 3,
        3: 4,
        4: 4,
        5: 4,
        6: 4,
        7: 5,
        8: 5,
        9: 5,
        10: 5,
        11: 6,
        12: 6,
    }

    LOOT_BONUS_CHANCE_BY_LVL = {
        1: 0.1,
        2: 0.2,
        3: 0.3,
        4: 0.4,
        5: 0.5,
        6: 0.6,
        7: 0.7,
        8: 0.8,
        9: 0.9,
        10: 1,
        11: 1,
        12: 1,
    }

    def __init__(
        self,
        name: str,
        type: EnemyType,
        description: str,
        information: str,
        image_url: str,
        min_level: int,
        max_level: int,
        health: float,
        damage_scaling: float,
        max_players: int,
        skill_types: list[SkillType],
        item_loot_table: list[ItemType],
        gear_loot_table: list[GearBaseType],
        skill_loot_table: list[SkillType],
        min_gear_drop_count: int = None,
        max_gear_drop_count: int = None,
        min_beans_reward: int = None,
        max_beans_reward: int = None,
        bonus_loot_chance: float = None,
        weighting: int = 100,
        initiative: int = 10,
        attribute_overrides: dict[CharacterAttribute, float] = None,
        actions_per_turn: int = 1,
        min_encounter_scale: int = 1,
        is_boss: bool = False,
        phases: list[EnemyType] = None,
        controller: str = "BasicEnemyController",
        author: str = None,
    ):
        self.name = name
        self.type = type
        self.description = description
        self.information = information
        self.image_url = image_url
        self.min_level = min_level
        self.max_level = max_level
        self.health = health
        self.damage_scaling = damage_scaling
        self.max_players = max_players
        self.skill_types = skill_types
        self.item_loot_table = item_loot_table
        self.gear_loot_table = gear_loot_table
        self.skill_loot_table = skill_loot_table
        self.min_gear_drop_count = min_gear_drop_count
        self.max_gear_drop_count = max_gear_drop_count
        self.min_beans_reward = min_beans_reward
        self.max_beans_reward = max_beans_reward
        self.bonus_loot_chance = bonus_loot_chance
        self.weighting = weighting
        self.initiative = initiative
        self.actions_per_turn = actions_per_turn
        self.min_encounter_scale = min_encounter_scale
        self.controller = controller
        self.is_boss = is_boss
        self.phases = phases

        self.attribute_overrides = attribute_overrides

        self.attributes: dict[CharacterAttribute, float] = {
            CharacterAttribute.PHYS_DAMAGE_INCREASE: 0,
            CharacterAttribute.MAGIC_DAMAGE_INCREASE: 0,
            CharacterAttribute.HEALING_BONUS: 0,
            CharacterAttribute.CRIT_RATE: 0.1,
            CharacterAttribute.CRIT_DAMAGE: 1.5,
            CharacterAttribute.DAMAGE_REDUCTION: 0,
            CharacterAttribute.MAX_HEALTH: 50,
        }

        if attribute_overrides is not None:
            for attribute_type, value in attribute_overrides:
                self.attributes[attribute_type] = value

        if self.bonus_loot_chance is None:
            self.bonus_loot_chance = self.LOOT_BONUS_CHANCE_BY_LVL[self.min_level]

        self.author = author
        if self.author is None:
            self.author = "Mara"

    def roll_beans_amount(self, level: int):
        if self.min_beans_reward is None:
            self.min_beans_reward = 95 * level
        if self.max_beans_reward is None:
            self.max_beans_reward = 105 * level

        return random.randint(self.min_beans_reward, self.max_beans_reward)

    def roll_loot_amount(self, level: int):
        if self.min_gear_drop_count is None:
            self.min_gear_drop_count = self.LOOT_MIN_AMOUNT_BY_LVL[level]
        if self.max_gear_drop_count is None:
            self.max_gear_drop_count = self.LOOT_MAX_AMOUNT_BY_LVL[level]

        return random.randint(self.min_gear_drop_count, self.max_gear_drop_count)

    def add_to_embed(
        self, embed: discord.Embed, show_info: bool = False, max_width: int = 56
    ) -> None:
        title = f"> ~* {self.name} - Lvl. {self.min_level} *~"
        description = f'"{self.description}"'

        if len(description) < max_width:
            spacing = max_width - len(description)
            description += " " * spacing

        info_block = f"```python\n{description}```"
        if show_info:
            info_block += f"```ansi\n[37m{self.information}```"

        embed.add_field(name=title, value=info_block, inline=False)
