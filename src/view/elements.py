from abc import ABC, abstractmethod

import discord

from events.ui_event import UIEvent
from items.types import ShopCategory


class ImplementsCategoryFilter(ABC):

    @abstractmethod
    def filter_items(self):
        pass

    @abstractmethod
    async def set_filter(self, event: UIEvent):
        pass


class CategoryFilter(discord.ui.Select):

    CATEGORY_TITLE_MAP = {
        ShopCategory.LOOTBOX: "Lootbox related Items",
        ShopCategory.FUN: "General use items",
        ShopCategory.INTERACTION: "Interaction related Items",
        ShopCategory.SLAP: "Slap Related Items",
        ShopCategory.PET: "Pet Related Items",
        ShopCategory.FART: "Fart Related Items",
        ShopCategory.JAIL: "Jail Related Items",
        ShopCategory.GARDEN: "Garden Related Items",
        ShopCategory.GEAR: "Combat Gear Related Items",
    }

    def __init__(self, selected: list[ShopCategory], row: int = 0):

        options = []

        for category in ShopCategory:

            option = discord.SelectOption(
                label=self.CATEGORY_TITLE_MAP[category],
                description="",
                value=category,
                default=(category in selected),
            )

            options.append(option)

        super().__init__(
            placeholder="Select a Category",
            min_values=0,
            max_values=len(ShopCategory),
            options=options,
            row=row,
        )

    async def callback(self, interaction: discord.Interaction):
        view: ImplementsCategoryFilter = self.view

        if await view.interaction_check(interaction):
            result = [ShopCategory(int(value)) for value in self.values]
            await view.set_filter(interaction, result)
