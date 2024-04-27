from typing import Any  # noqa: UP035

from items.item import Item
from items.types import ItemType


class InteractionModifiers:

    def __init__(
        self,
        item_modifier: int = 1,
        auto_crit: bool = False,
        stabilized: bool = False,
        advantage: bool = False,
        bonus_attempt: Item = None,
        satan_boost: bool = False,
    ):
        self.item_modifier = item_modifier
        self.auto_crit = auto_crit
        self.stabilized = stabilized
        self.advantage = advantage
        self.bonus_attempt = bonus_attempt
        self.satan_boost = satan_boost
        self.major_jail_actions: list[ItemType] = []
