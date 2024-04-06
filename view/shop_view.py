from typing import List
import discord
from control.view.shop_view_controller import ShopViewController
from events.ui_event import UIEvent
from events.types import UIEventType
from items.item import Item
from items.types import ItemType
from view.shop_embed import ShopEmbed
from view.view_menu import ViewMenu


class ShopView(ViewMenu):

    def __init__(
        self,
        controller: ShopViewController,
        interaction: discord.Interaction,
        items: List[Item],
        user_balance: int,
    ):
        super().__init__(timeout=300)
        self.controller = controller
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
        self.user_balance = user_balance
        self.controller.register_view(self)
        self.controller.refresh_ui(interaction)

    async def listen_for_ui_event(self, event: UIEvent):
        if (
            event.get_guild_id() != self.guild_id
            or event.get_member_id() != self.member_id
        ):
            return

        match event.get_type():
            case UIEventType.REFRESH_SHOP:
                await self.refresh_ui(user_balance=event.get_payload(), disabled=False)
            case UIEventType.DISABLE_SHOP:
                await self.refresh_ui(disabled=event.get_payload())

    def set_message(self, message: discord.Message):
        self.message = message

    async def buy(self, interaction: discord.Interaction):
        if not await self.controller.interaction_check(interaction, self.member_id):
            return
        await self.controller.buy(interaction, self.selected)

    async def flip_page(self, interaction: discord.Interaction, right: bool = False):
        self.current_page = (self.current_page + (1 if right else -1)) % self.page_count
        self.selected = None
        self.controller.refresh_ui(interaction)
        await interaction.response.defer()

    def refresh_elements(self, user_balance: int = None, disabled: bool = False):
        start = ShopEmbed.ITEMS_PER_PAGE * self.current_page
        end = min((start + ShopEmbed.ITEMS_PER_PAGE), self.item_count)
        page_display = f"Page {self.current_page + 1}/{self.page_count}"

        if user_balance is not None:
            self.user_balance = user_balance

        self.clear_items()
        self.add_item(Dropdown(self.items[start:end], self.selected, disabled))
        self.add_item(PageButton("<", False, disabled))
        self.add_item(BuyButton(disabled))
        self.add_item(PageButton(">", True, disabled))
        self.add_item(CurrentPageButton(page_display))
        self.add_item(BalanceButton(self.controller, self.user_balance))

    async def refresh_ui(self, user_balance: int = None, disabled: bool = False):
        self.refresh_elements(user_balance, disabled)
        start = ShopEmbed.ITEMS_PER_PAGE * self.current_page
        embed = ShopEmbed(self.guild_name, self.member_id, self.items, start)
        await self.message(embed=embed, view=self)

    async def set_selected(self, interaction: discord.Interaction, item_type: ItemType):
        self.selected = item_type
        await interaction.response.defer()

    # pylint: disable-next=arguments-differ
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return await self.controller.interaction_check(interaction, self.member_id)

    async def on_timeout(self):
        try:
            await self.message.edit(view=None)
        except discord.HTTPException:
            pass
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

    def __init__(self, controller: ShopViewController, balance: int):
        self.controller = controller
        self.balance = balance
        super().__init__(label=f"🅱️{balance}", style=discord.ButtonStyle.blurple, row=1)

    async def callback(self, interaction: discord.Interaction):
        view: ShopView = self.view

        if await view.interaction_check(interaction):
            await interaction.response.defer(ephemeral=True)

            police_img = discord.File("./img/police.png", "police.png")
            embed = self.controller.get_inventory_embed(interaction)

            await interaction.followup.send(
                "", embed=embed, files=[police_img], ephemeral=True
            )


class Dropdown(discord.ui.Select):

    def __init__(self, items: List[Item], selected: ItemType, disabled: bool = False):

        options = []

        for item in items:
            option = discord.SelectOption(
                label=item.get_name(),
                description="",
                emoji=item.get_emoji(),
                value=item.get_type(),
                default=(selected == item.get_type()),
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
            await view.set_selected(interaction, self.values[0])
