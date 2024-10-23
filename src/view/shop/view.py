import contextlib

import discord

from control.controller import Controller
from control.types import ControllerType
from events.types import UIEventType
from events.ui_event import UIEvent
from items.item import Item
from items.types import ItemType
from view.shop.embed import ShopEmbed
from view.view_menu import ViewMenu


class ShopView(ViewMenu):

    def __init__(
        self,
        controller: Controller,
        interaction: discord.Interaction,
        items: list[Item],
    ):
        super().__init__(timeout=300)
        self.controller = controller
        items = sorted(items, key=lambda x: (x.shop_category.value, x.cost))
        self.items = items
        self.guild_name = interaction.guild.name
        self.member_id = interaction.user.id
        self.guild_id = interaction.guild_id
        self.current_page = 0
        self.selected: ItemType = None
        self.item_count = len(self.items)
        self.page_count = int(self.item_count / ShopEmbed.ITEMS_PER_PAGE) + (
            self.item_count % ShopEmbed.ITEMS_PER_PAGE > 0
        )

        self.message = None
        self.user_balance = 0
        self.user_items: dict[ItemType, int] = {}
        self.disabled = False

        self.controller_types = [ControllerType.SHOP_VIEW]
        self.controller.register_view(self)
        self.refresh_elements()

    async def listen_for_ui_event(self, event: UIEvent):
        match event.type:
            case UIEventType.SHOP_USER_REFRESH:
                user_id = event.payload[0]
                if user_id != self.member_id:
                    return
                user_balance = event.payload[1]
                user_items = event.payload[2]
                await self.refresh_ui(
                    user_balance=user_balance,
                    user_items=user_items,
                    disabled=self.disabled,
                )

        if event.view_id != self.id:
            return

        match event.type:
            case UIEventType.SHOP_REFRESH:
                user_balance = event.payload[0]
                user_items = event.payload[1]
                await self.refresh_ui(
                    user_balance=user_balance, user_items=user_items, disabled=False
                )
            case UIEventType.SHOP_DISABLE:
                await self.refresh_ui(disabled=event.payload)

    async def buy(self, interaction: discord.Interaction):
        await interaction.response.defer()
        event = UIEvent(
            UIEventType.SHOP_BUY,
            (interaction, self.selected),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def flip_page(self, interaction: discord.Interaction, right: bool = False):
        await interaction.response.defer()
        self.current_page = (self.current_page + (1 if right else -1)) % self.page_count
        self.selected = None
        event = UIEvent(
            UIEventType.SHOP_CHANGED,
            (self.guild_id, self.member_id),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    def refresh_elements(self, user_balance: int = None, disabled: bool = False):
        start = ShopEmbed.ITEMS_PER_PAGE * self.current_page
        end = min((start + ShopEmbed.ITEMS_PER_PAGE), self.item_count)
        page_display = f"Page {self.current_page + 1}/{self.page_count}"

        if user_balance is not None:
            self.user_balance = user_balance

        self.disabled = disabled

        if self.selected is None:
            self.selected = self.items[start].type

        self.clear_items()
        self.add_item(Dropdown(self.items[start:end], self.selected, disabled))
        self.add_item(PageButton("<", False, disabled))
        self.add_item(BuyButton(disabled))
        self.add_item(PageButton(">", True, disabled))
        self.add_item(CurrentPageButton(page_display))
        self.add_item(BalanceButton(self.user_balance))

    async def refresh_ui(
        self, user_balance: int = None, user_items=None, disabled: bool = False
    ):
        self.refresh_elements(user_balance, disabled)
        start = ShopEmbed.ITEMS_PER_PAGE * self.current_page

        if user_items is not None:
            self.user_items = user_items

        embed = ShopEmbed(
            bot=self.controller.bot,
            guild_name=self.guild_name,
            items=self.items,
            user_items=self.user_items,
            start_offset=start,
        )
        if self.message is None:
            return

        try:
            await self.message.edit(embed=embed, view=self)
        except (discord.NotFound, discord.HTTPException):
            self.controller.detach_view(self)

    async def set_selected(self, interaction: discord.Interaction, item_type: ItemType):
        self.selected = item_type
        await interaction.response.defer()

    async def on_timeout(self):
        with contextlib.suppress(discord.HTTPException):
            await self.message.edit(view=None)
        self.controller.detach_view(self)


class BuyButton(discord.ui.Button):

    def __init__(self, disabled: bool = False):
        super().__init__(
            label="Buy", style=discord.ButtonStyle.green, row=1, disabled=disabled
        )

    async def callback(self, interaction: discord.Interaction):
        view: ShopView = self.view

        if await view.interaction_check(interaction):
            await view.buy(interaction)


class PageButton(discord.ui.Button):

    def __init__(self, label: str, right: bool, disabled: bool = False):
        self.right = right
        super().__init__(
            label=label, style=discord.ButtonStyle.grey, row=1, disabled=disabled
        )

    async def callback(self, interaction: discord.Interaction):
        view: ShopView = self.view

        if await view.interaction_check(interaction):
            await view.flip_page(interaction, self.right)


class CurrentPageButton(discord.ui.Button):

    def __init__(self, label: str):
        super().__init__(
            label=label, style=discord.ButtonStyle.grey, row=1, disabled=True
        )


class BalanceButton(discord.ui.Button):

    def __init__(self, balance: int):
        self.balance = balance
        super().__init__(label=f"🅱️{balance}", style=discord.ButtonStyle.blurple, row=1)

    async def callback(self, interaction: discord.Interaction):
        view: ShopView = self.view

        if await view.interaction_check(interaction):
            await interaction.response.defer(ephemeral=True)
            event = UIEvent(UIEventType.SHOW_INVENTORY, interaction, view.id)
            await view.controller.dispatch_ui_event(event)


class Dropdown(discord.ui.Select):

    def __init__(self, items: list[Item], selected: ItemType, disabled: bool = False):

        options = []

        for item in items:
            emoji = item.emoji
            if isinstance(item.emoji, int):
                emoji = str(self.controller.bot.get_emoji(item.emoji))
            option = discord.SelectOption(
                label=item.name,
                description="",
                emoji=emoji,
                value=item.type,
                default=(selected == item.type),
            )

            options.append(option)

        super().__init__(
            placeholder="Select an item.",
            min_values=1,
            max_values=1,
            options=options,
            row=0,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: ShopView = self.view

        if await view.interaction_check(interaction):
            await view.set_selected(interaction, ItemType(self.values[0]))
