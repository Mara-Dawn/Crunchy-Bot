from combat.enemies.types import EnemyType
from combat.skills.skill import Skill
from items.item import Item


class Enemy:

    LOOT_MIN_AMOUNT_BY_LVL = {
        1: 1,
        2: 1,
        3: 1,
        4: 1,
        5: 2,
        6: 2,
        7: 2,
        8: 2,
        9: 3,
        10: 3,
        11: 3,
        12: 3,
    }

    LOOT_MAX_AMOUNT_BY_LVL = {
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

    def __init__(
        self,
        name: str,
        type: EnemyType,
        description: str,
        information: str,
        image: str,
        level: int,
        min_hp: int,
        max_hp: int,
        skills: list[Skill],
        loot_table: list[Item],
        min_drop_count: int = None,
        max_drop_count: int = None,
        min_beans_reward: int = None,
        max_beans_reward: int = None,
        weighting: int = 100,
    ):
        self.name = name
        self.type = type
        self.description = description
        self.information = information
        self.image = image
        self.level = level
        self.min_hp = min_hp
        self.max_hp = max_hp
        self.skills = skills
        self.loot_table = loot_table
        self.min_drop_count = min_drop_count
        self.max_drop_count = max_drop_count
        self.min_beans_reward = min_beans_reward
        self.max_beans_reward = max_beans_reward
        self.weighting = weighting

        if self.min_drop_count is None:
            self.min_drop_count = self.LOOT_MIN_AMOUNT_BY_LVL[self.level]
        if self.max_drop_count is None:
            self.max_drop_count = self.LOOT_MAX_AMOUNT_BY_LVL[self.level]

        if self.min_beans_reward is None:
            self.min_beans_reward = 95 * self.level
        if self.max_beans_reward is None:
            self.max_beans_reward = 105 * self.level
