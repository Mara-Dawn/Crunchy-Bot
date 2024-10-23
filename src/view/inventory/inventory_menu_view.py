import contextlib

import discord

from control.combat.combat_embed_manager import CombatEmbedManager
from control.controller import Controller
from control.forge_manager import ForgeManager
from control.item_manager import ItemManager
from control.types import ControllerType
from datalayer.inventory import UserInventory
from events.types import UIEventType
from events.ui_event import UIEvent
from forge.forgable import ForgeInventory
from items.item import Item
from items.types import ItemState, ItemType, ShopCategory
from view.combat.elements import (
    ImplementsBalance,
    ImplementsForging,
    ImplementsMainMenu,
    ImplementsPages,
    MenuState,
)
from view.combat.forge_menu_view import ForgeMenuState
from view.elements import CategoryFilter
from view.inventory.embed import InventoryEmbed
from view.types import ActionType
from view.view_menu import ViewMenu


class InventoryMenuView(
    ViewMenu, ImplementsMainMenu, ImplementsPages, ImplementsBalance, ImplementsForging
):

    def __init__(
        self,
        controller: Controller,
        interaction: discord.Interaction,
        inventory: UserInventory,
    ):
        super().__init__(timeout=None)
        self.controller = controller
        self.member_id = interaction.user.id
        self.guild_id = interaction.guild.id
        self.member = interaction.user
        self.state = MenuState.INVENTORY
        self.loaded = False

        self.embed_manager: CombatEmbedManager = self.controller.get_service(
            CombatEmbedManager
        )
        self.forge_manager: ForgeManager = self.controller.get_service(ForgeManager)
        self.item_manager: ItemManager = controller.get_service(ItemManager)

        self.inventory = inventory

        self.current_page = 0
        self.selected: ItemType = None
        self.filter: list[ShopCategory] = []
        self.filtered_items = []
        self.display_items = []
        self.item_count = 0
        self.page_count = 1
        self.forge_inventory: ForgeInventory = None
        self.filter_items()

        self.controller_types = [
            ControllerType.MAIN_MENU,
            ControllerType.EQUIPMENT,
            ControllerType.INVENTORY_VIEW,
        ]
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

    def refresh_elements(self, disabled: bool = False):
        selected_state = self.inventory.get_item_state(self.selected)

        self.clear_items()

        self.add_menu(self.state, False, False)
        self.add_beans_balance_button(self.inventory.balance)
        disable_forge = disabled

        match selected_state:
            case ItemState.ENABLED:
                button_action = ActionType.DISABLE_ACTION
                if self.inventory.get_item_useable(self.selected):
                    button_action = ActionType.USE_ACTION
            case ItemState.DISABLED:
                button_action = ActionType.ENABLE_ACTION

        if self.selected is None:
            button_action = ActionType.DEFAULT_ACTION
            disable_forge = True

        page_display = f"Page {self.current_page + 1}/{self.page_count}"

        controllable_items = [
            item for item in self.display_items if item.controllable or item.useable
        ]

        self.add_item(CategoryFilter(self.filter, row=1))
        if len(controllable_items) > 0:
            self.add_item(Dropdown(controllable_items, self.selected))
        self.add_page_button("<", False, row=3)
        self.add_item(ActionButton(button_action, disabled))
        self.add_page_button(">", False, row=3)
        self.add_current_page_button(page_display, row=3)
        self.add_item(SellButton(disabled))
        self.add_item(SellAmountButton(disabled))
        self.add_item(SellAllButton(disabled))
        self.add_add_to_forge_button(disabled=disable_forge, row=4)
        if self.forge_inventory is not None and not self.forge_inventory.empty:
            self.add_forge_status_button(
                current=self.forge_inventory, row=3, disabled=False
            )
            self.add_clear_forge_button(disabled=False)

    async def refresh_ui(
        self,
        inventory: UserInventory = None,
        disabled: bool = False,
    ):
        if self.message is None:
            return

        if inventory is not None:
            self.inventory = inventory
            self.item_count = len(self.inventory.items)
            self.page_count = int(self.item_count / InventoryEmbed.ITEMS_PER_PAGE) + (
                self.item_count % InventoryEmbed.ITEMS_PER_PAGE > 0
            )

            self.current_page = min(self.current_page, (self.page_count - 1))

        self.guild_level = await self.controller.database.get_guild_level(self.guild_id)

        self.filter_items()

        if self.selected is None:
            disabled = True

        start_offset = InventoryEmbed.ITEMS_PER_PAGE * self.current_page
        end_offset = min(
            (start_offset + InventoryEmbed.ITEMS_PER_PAGE), len(self.filtered_items)
        )
        self.display_items = self.filtered_items[start_offset:end_offset]

        self.forge_inventory = await self.forge_manager.get_forge_inventory(self.member)

        if self.selected not in [item.type for item in self.display_items]:
            self.selected = None

        self.refresh_elements(disabled)

        embed = InventoryEmbed(self.controller.bot, self.inventory, self.display_items)
        if self.message is None:
            return

        try:
            await self.message.edit(embed=embed, view=self)
        except (discord.NotFound, discord.HTTPException):
            self.controller.detach_view(self)

    async def set_state(self, state: MenuState, interaction: discord.Interaction):
        await interaction.response.defer()
        event = UIEvent(
            UIEventType.MAIN_MENU_STATE_CHANGE,
            (interaction, state, False),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    def filter_items(self):
        category_filer = self.filter
        if len(category_filer) == 0:
            category_filer = [category for category in ShopCategory]
        self.filtered_items = [
            item
            for item in self.inventory.items
            if item.shop_category in category_filer
        ]
        self.item_count = len(self.filtered_items)
        self.page_count = int(self.item_count / InventoryEmbed.ITEMS_PER_PAGE) + (
            self.item_count % InventoryEmbed.ITEMS_PER_PAGE > 0
        )

    async def set_filter(
        self, interaction: discord.Interaction, filter: list[ShopCategory]
    ):
        await interaction.response.defer()
        self.filter = filter
        self.current_page = 0
        await self.refresh_ui()

    async def flip_page(self, interaction: discord.Interaction, right: bool = False):
        await interaction.response.defer()
        self.current_page = (self.current_page + (1 if right else -1)) % self.page_count
        self.selected = None
        await self.refresh_ui()

    async def open_shop(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        event = UIEvent(UIEventType.SHOW_SHOP, interaction, self.id)
        await self.controller.dispatch_ui_event(event)

    async def selected_item_action(
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
        self,
        interaction: discord.Interaction,
        amount: int = 1,
        sell_until: bool = False,
    ):
        event = UIEvent(
            UIEventType.INVENTORY_SELL,
            (interaction, self.selected, amount, sell_until),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def set_selected(self, interaction: discord.Interaction, item_type: ItemType):
        if item_type is not None:
            item_type = ItemType(item_type)
        self.selected = item_type
        await interaction.response.defer()
        await self.refresh_ui()

    async def add_to_forge(
        self,
        interaction: discord.Interaction,
    ):
        await interaction.response.defer(ephemeral=True)
        if self.selected is None:
            return
        selected = self.selected
        item = await self.item_manager.get_item(self.guild_id, selected)
        amount = self.inventory.get_item_count(selected)

        if item.id <= 0:
            return

        if item.permanent:
            return

        for id in range(amount):
            item.id = item.id + id
            if self.forge_inventory is None or item.id not in [
                x.id for x in self.forge_inventory.items if x is not None
            ]:
                event = UIEvent(
                    UIEventType.FORGE_ADD_ITEM,
                    (interaction, item),
                    self.id,
                )
                await self.controller.dispatch_ui_event(event)
                return

    async def open_forge(
        self,
        interaction: discord.Interaction,
    ):
        await interaction.response.defer()
        event = UIEvent(
            UIEventType.MAIN_MENU_STATE_CHANGE,
            (interaction, MenuState.FORGE, False, ForgeMenuState.COMBINE),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def clear_forge(
        self,
        interaction: discord.Interaction,
    ):
        await interaction.response.defer()
        event = UIEvent(
            UIEventType.FORGE_CLEAR,
            interaction,
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

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
            case ActionType.USE_ACTION:
                color = discord.ButtonStyle.green
            case _:
                color = discord.ButtonStyle.green

        super().__init__(
            label=action_type.value,
            style=color,
            row=3,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: InventoryMenuView = self.view

        if await view.interaction_check(interaction):
            await view.selected_item_action(interaction, self.action_type)


class SellButton(discord.ui.Button):

    def __init__(self, disabled: bool = False):
        super().__init__(
            label="Sell Single",
            style=discord.ButtonStyle.grey,
            row=4,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: InventoryMenuView = self.view

        if await view.interaction_check(interaction):
            await interaction.response.defer()
            await view.sell_selected_item(interaction)


class SellAmountButton(discord.ui.Button):

    def __init__(self, disabled: bool = False):
        super().__init__(
            label="Sell Amount",
            style=discord.ButtonStyle.grey,
            row=4,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: InventoryMenuView = self.view

        if await view.interaction_check(interaction):
            await interaction.response.send_modal(SellAmountModal(self.view))


class SellAmountModal(discord.ui.Modal):

    def __init__(self, view: InventoryMenuView):
        super().__init__(title="Specify how much you want to sell.")
        self.view = view

        self.amount = discord.ui.TextInput(
            label="Specify an amount to sell:",
            placeholder="Sell amount",
            required=False,
        )
        self.add_item(self.amount)
        self.amount_left = discord.ui.TextInput(
            label="OR sell all until you have this many left:",
            placeholder="Sell until amount left",
            required=False,
        )
        self.add_item(self.amount_left)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        sell_amount_str = self.amount.value
        sell_until_str = self.amount_left.value

        if len(sell_amount_str) == 0 and len(sell_until_str) == 0:
            await interaction.followup.send(
                "Please specify either a sell amount or a sell until value.",
                ephemeral=True,
            )
            return

        if len(sell_amount_str) > 0 and len(sell_until_str) > 0:
            await interaction.followup.send(
                "You can only specify either sell amount or sell until, not both.",
                ephemeral=True,
            )
            return

        sell_until = False

        amount = sell_amount_str
        if len(amount) == 0:
            amount = sell_until_str
            sell_until = True

        error = False
        try:
            amount = int(amount)
            error = amount < 0
        except ValueError:
            error = True

        if error:
            await interaction.followup.send(
                "Please enter a valid amount above 0.", ephemeral=True
            )
            return

        await self.view.sell_selected_item(
            interaction, amount=amount, sell_until=sell_until
        )


class SellAllButton(discord.ui.Button):

    def __init__(self, disabled: bool = False):
        super().__init__(
            label="Sell All",
            style=discord.ButtonStyle.grey,
            row=4,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: InventoryMenuView = self.view

        if await view.interaction_check(interaction):
            await interaction.response.defer()
            await view.sell_selected_item(interaction, amount=0, sell_until=True)


class Dropdown(discord.ui.Select):

    def __init__(self, items: list[Item], selected: ItemType, disabled: bool = False):

        options = []

        for item in items:
            sell_price = int(
                min((item.cost * UserInventory.SELL_MODIFIER) / item.base_amount, 100)
            )

            emoji = item.emoji
            if isinstance(item.emoji, int):
                emoji = str(self.bot.get_emoji(item.emoji))

            option = discord.SelectOption(
                label=item.name,
                description=f"Sells for 🅱️{sell_price} a piece",
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
            row=2,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: InventoryMenuView = self.view

        if await view.interaction_check(interaction):
            await view.set_selected(interaction, self.values[0])
