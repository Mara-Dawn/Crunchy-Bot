import contextlib

import discord
from control.controller import Controller
from control.types import ControllerType
from datalayer.inventory import UserInventory
from events.types import UIEventType
from events.ui_event import UIEvent
from items.item import Item
from items.types import ItemState, ItemType

from view.inventory_embed import InventoryEmbed
from view.types import ActionType
from view.view_menu import ViewMenu


class InventoryView(ViewMenu):

    def __init__(
        self,
        controller: Controller,
        interaction: discord.Interaction,
        inventory: UserInventory,
    ):
        super().__init__(timeout=300)
        self.controller = controller
        self.inventory = inventory
        self.guild_name = interaction.guild.name
        self.member_id = interaction.user.id
        self.guild_id = interaction.guild_id
        self.selected: ItemType = None

        self.message = None

        self.controller_type = ControllerType.INVENTORY_VIEW
        self.controller.register_view(self)
        self.refresh_elements()

    async def listen_for_ui_event(self, event: UIEvent):
        match event.type:
            case UIEventType.INVENTORY_USER_REFRESH:
                inventory: UserInventory = event.payload
                if (
                    inventory.member != self.member_id
                    or inventory.guild_id != self.guild_id
                ):
                    return
                await self.refresh_ui(inventory=inventory, disabled=False)
                return

        if event.view_id != self.id:
            return

        match event.type:
            case UIEventType.INVENTORY_REFRESH:
                inventory = event.payload
                await self.refresh_ui(inventory=inventory)

    async def toggle_selected_item(
        self, interaction: discord.Interaction, action_type: ActionType
    ):
        await interaction.response.defer()
        event = UIEvent(
            UIEventType.INVENTORY_ITEM_ACTION,
            (interaction, self.selected, action_type),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def sell_selected_item(
        self, interaction: discord.Interaction, all: bool = False
    ):
        await interaction.response.defer()
        sell_amount = 1
        if all:
            sell_amount = self.inventory.get_item_count(self.selected)
        event = UIEvent(
            UIEventType.INVENTORY_SELL,
            (interaction, self.selected, sell_amount),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    def refresh_elements(self, disabled: bool = False):
        selected_state = self.inventory.get_item_state(self.selected)

        button_action = ActionType.DEFAULT_ACTION

        match selected_state:
            case ItemState.ENABLED:
                button_action = ActionType.DISABLE_ACTION
            case ItemState.DISABLED:
                button_action = ActionType.ENABLE_ACTION

        sellable_items = [item for item in self.inventory.items if item.sellable]

        self.clear_items()
        self.add_item(Dropdown(sellable_items, self.selected))
        self.add_item(ActionButton(button_action, disabled))
        self.add_item(SellButton(disabled))
        self.add_item(SellAllButton(disabled))
        self.add_item(BalanceButton(self.inventory.balance))

    async def refresh_ui(self, inventory: UserInventory = None, disabled: bool = False):
        if inventory is not None:
            self.inventory = inventory

        if self.selected not in self.inventory.inventory:
            self.selected = None

        if self.selected is None:
            disabled = True

        self.refresh_elements(disabled)

        embed = InventoryEmbed(inventory=self.inventory)
        if self.message is None:
            return

        try:
            await self.message.edit(embed=embed, view=self)
        except (discord.NotFound, discord.HTTPException):
            self.controller.detach_view(self)

    async def set_selected(self, interaction: discord.Interaction, item_type: ItemType):
        if item_type is not None:
            item_type = ItemType(item_type)
        self.selected = item_type
        await interaction.response.defer()
        await self.refresh_ui()

    async def on_timeout(self):
        with contextlib.suppress(discord.HTTPException):
            await self.message.edit(view=None)
        self.controller.detach_view(self)


class ActionButton(discord.ui.Button):

    def __init__(
        self, action_type: ActionType = ActionType.DEFAULT_ACTION, disabled: bool = True
    ):
        self.action_type = action_type

        match action_type:
            case ActionType.ENABLE_ACTION:
                color = discord.ButtonStyle.green
            case ActionType.DISABLE_ACTION:
                color = discord.ButtonStyle.red
            case _:
                color = discord.ButtonStyle.grey

        super().__init__(
            label=action_type.value,
            style=color,
            row=1,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: InventoryView = self.view

        if await view.interaction_check(interaction):
            await view.toggle_selected_item(interaction, self.action_type)


class SellButton(discord.ui.Button):

    def __init__(self, disabled: bool = False):
        super().__init__(
            label="Sell Single",
            style=discord.ButtonStyle.green,
            row=1,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: InventoryView = self.view

        if await view.interaction_check(interaction):
            await view.sell_selected_item(interaction)


class SellAllButton(discord.ui.Button):

    def __init__(self, disabled: bool = False):
        super().__init__(
            label="Sell All", style=discord.ButtonStyle.green, row=1, disabled=disabled
        )

    async def callback(self, interaction: discord.Interaction):
        view: InventoryView = self.view

        if await view.interaction_check(interaction):
            await view.sell_selected_item(interaction, all=True)


class BalanceButton(discord.ui.Button):

    def __init__(self, balance: int):
        self.balance = balance
        super().__init__(label=f"🅱️{balance}", style=discord.ButtonStyle.blurple, row=1)

    async def callback(self, interaction: discord.Interaction):
        view: InventoryView = self.view

        if await view.interaction_check(interaction):
            await interaction.response.defer(ephemeral=True)


class Dropdown(discord.ui.Select):

    def __init__(self, items: list[Item], selected: ItemType, disabled: bool = False):

        options = []

        for item in items:
            sell_price = int(
                (item.cost * UserInventory.SELL_MODIFIER) / item.base_amount
            )

            option = discord.SelectOption(
                label=item.name,
                description=f"Sells for 🅱️{sell_price} a piece",
                emoji=item.emoji,
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
        view: InventoryView = self.view

        if await view.interaction_check(interaction):
            await view.set_selected(interaction, self.values[0])
