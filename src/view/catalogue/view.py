import contextlib

import discord
from control.controller import Controller
from events.ui_event import UIEvent
from items.item import Item
from items.types import ShopCategory
from view.catalogue.embed import CatalogEmbed
from view.view_menu import ViewMenu


class CatalogView(ViewMenu):

    def __init__(
        self,
        controller: Controller,
        interaction: discord.Interaction,
        items: list[Item],
    ):
        super().__init__(timeout=300)
        self.controller = controller
        self.items = items
        self.guild_name = interaction.guild.name
        self.member_id = interaction.user.id
        self.guild_id = interaction.guild_id
        self.current_page = 0
        self.filter: list[ShopCategory] = []
        self.filtered_items = []
        self.__filter_items()
        self.item_count = len(self.filtered_items)
        self.page_count = int(self.item_count / CatalogEmbed.ITEMS_PER_PAGE) + (
            self.item_count % CatalogEmbed.ITEMS_PER_PAGE > 0
        )
        self.message = None

        self.refresh_elements()

    async def listen_for_ui_event(self, event: UIEvent):
        pass

    def __filter_items(self):
        self.filtered_items = [
            item for item in self.items if item.shop_category in self.filter
        ]
        self.item_count = len(self.filtered_items)
        self.page_count = int(self.item_count / CatalogEmbed.ITEMS_PER_PAGE) + (
            self.item_count % CatalogEmbed.ITEMS_PER_PAGE > 0
        )

    async def flip_page(self, interaction: discord.Interaction, right: bool = False):
        await interaction.response.defer()
        self.current_page = (self.current_page + (1 if right else -1)) % self.page_count
        await self.refresh_ui()

    def refresh_elements(self):
        page_display = f"Page {self.current_page + 1}/{self.page_count}"

        self.clear_items()
        self.add_item(FilterDropdown(self.filter))
        self.add_item(PageButton("<", False))
        self.add_item(CurrentPageButton(page_display))
        self.add_item(PageButton(">", True))

    async def refresh_ui(self):
        self.__filter_items()
        self.refresh_elements()

        start_offset = CatalogEmbed.ITEMS_PER_PAGE * self.current_page
        head_embed = CatalogEmbed(self.controller.bot)
        if self.message is None:
            return

        if len(self.filtered_items) == 0:
            head_embed.add_field(
                name="Please select one or more item categories below.",
                value="",
                inline=False,
            )

        embeds = [head_embed]

        end_offset = min(
            (start_offset + CatalogEmbed.ITEMS_PER_PAGE), len(self.filtered_items)
        )
        display = self.filtered_items[start_offset:end_offset]

        for item in display:
            embeds.append(
                item.get_embed(self.controller.bot, show_price=False, show_info=True)
            )

        with contextlib.suppress(discord.NotFound, discord.HTTPException):
            await self.message.edit(embeds=embeds, view=self)

    async def set_filter(
        self, interaction: discord.Interaction, filter: list[ShopCategory]
    ):
        await interaction.response.defer()
        self.filter = filter
        self.current_page = 0
        await self.refresh_ui()

    async def on_timeout(self):
        with contextlib.suppress(discord.HTTPException):
            await self.message.edit(view=None)


class FilterDropdown(discord.ui.Select):

    CATEGORY_TITLE_MAP = {
        ShopCategory.LOOTBOX: "Lootbox related Items",
        ShopCategory.FUN: "General use items",
        ShopCategory.INTERACTION: "Interaction related Items",
        ShopCategory.SLAP: "Slap Related Items",
        ShopCategory.PET: "Pet Related Items",
        ShopCategory.FART: "Fart Related Items",
        ShopCategory.JAIL: "Jail Related Items",
        ShopCategory.GARDEN: "Garden Related Items",
    }

    def __init__(
        self,
        selected: list[ShopCategory],
    ):

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
            min_values=1,
            max_values=len(ShopCategory),
            options=options,
            row=0,
        )

    async def callback(self, interaction: discord.Interaction):
        view: CatalogView = self.view

        if await view.interaction_check(interaction):
            result = [ShopCategory(int(value)) for value in self.values]
            await view.set_filter(interaction, result)


class PageButton(discord.ui.Button):

    def __init__(self, label: str, right: bool, disabled: bool = False):
        self.right = right
        super().__init__(
            label=label, style=discord.ButtonStyle.grey, row=1, disabled=disabled
        )

    async def callback(self, interaction: discord.Interaction):
        view: CatalogView = self.view

        if await view.interaction_check(interaction):
            await view.flip_page(interaction, self.right)


class CurrentPageButton(discord.ui.Button):

    def __init__(self, label: str):
        super().__init__(
            label=label, style=discord.ButtonStyle.grey, row=1, disabled=True
        )
