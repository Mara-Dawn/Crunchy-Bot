import contextlib

import discord
from control.controller import Controller
from control.types import ControllerType
from datalayer.inventory import UserInventory
from events.types import UIEventType
from events.ui_event import UIEvent
from items.item import Item
from items.types import ItemState, ItemType, ShopCategory
from view.elements import CategoryFilter, ImplementsCategoryFilter
from view.inventory.embed import InventoryEmbed
from view.types import ActionType
from view.view_menu import ViewMenu


class InventoryView(ViewMenu, ImplementsCategoryFilter):

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
        self.current_page = 0
        self.selected: ItemType = None

        self.filter: list[ShopCategory] = [category for category in ShopCategory]
        self.filtered_items = []
        self.display_items = []
        self.item_count = 0
        self.page_count = 1
        self.filter_items()
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

    def filter_items(self):
        self.filtered_items = [
            item for item in self.inventory.items if item.shop_category in self.filter
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

    def refresh_elements(self, disabled: bool = False):
        selected_state = self.inventory.get_item_state(self.selected)

        match selected_state:
            case ItemState.ENABLED:
                button_action = ActionType.DISABLE_ACTION
                if self.inventory.get_item_useable(self.selected):
                    button_action = ActionType.USE_ACTION
            case ItemState.DISABLED:
                button_action = ActionType.ENABLE_ACTION

        if self.selected is None:
            button_action = ActionType.DEFAULT_ACTION

        page_display = f"Page {self.current_page + 1}/{self.page_count}"

        controllable_items = [
            item for item in self.display_items if item.controllable or item.useable
        ]

        self.clear_items()
        self.add_item(CategoryFilter(self.filter))
        if len(controllable_items) > 0:
            self.add_item(Dropdown(controllable_items, self.selected))
        self.add_item(PageButton("<", False))
        self.add_item(ActionButton(button_action, disabled))
        self.add_item(PageButton(">", True))
        self.add_item(CurrentPageButton(page_display))
        self.add_item(BalanceButton(self.inventory.balance))
        self.add_item(SellButton(disabled))
        self.add_item(SellAmountButton(disabled))
        self.add_item(SellAllButton(disabled))

    async def refresh_ui(self, inventory: UserInventory = None, disabled: bool = False):
        if inventory is not None:
            self.inventory = inventory
            self.item_count = len(self.inventory.items)
            self.page_count = int(self.item_count / InventoryEmbed.ITEMS_PER_PAGE) + (
                self.item_count % InventoryEmbed.ITEMS_PER_PAGE > 0
            )

            self.current_page = min(self.current_page, (self.page_count - 1))

        self.filter_items()

        if self.selected is None:
            disabled = True

        start_offset = InventoryEmbed.ITEMS_PER_PAGE * self.current_page
        end_offset = min(
            (start_offset + InventoryEmbed.ITEMS_PER_PAGE), len(self.filtered_items)
        )
        self.display_items = self.filtered_items[start_offset:end_offset]

        self.refresh_elements(disabled)

        if self.selected not in [item.type for item in self.display_items]:
            self.selected = None

        embed = InventoryEmbed(self.controller.bot, self.inventory, self.display_items)
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
            case ActionType.USE_ACTION:
                color = discord.ButtonStyle.green
            case _:
                color = discord.ButtonStyle.green

        super().__init__(
            label=action_type.value,
            style=color,
            row=2,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: InventoryView = self.view

        if await view.interaction_check(interaction):
            await view.selected_item_action(interaction, self.action_type)


class SellButton(discord.ui.Button):

    def __init__(self, disabled: bool = False):
        super().__init__(
            label="Sell Single",
            style=discord.ButtonStyle.grey,
            row=3,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: InventoryView = self.view

        if await view.interaction_check(interaction):
            await interaction.response.defer()
            await view.sell_selected_item(interaction)


class SellAmountButton(discord.ui.Button):

    def __init__(self, disabled: bool = False):
        super().__init__(
            label="Sell Amount",
            style=discord.ButtonStyle.grey,
            row=3,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: InventoryView = self.view

        if await view.interaction_check(interaction):
            await interaction.response.send_modal(SellAmountModal(self.view))


class SellAmountModal(discord.ui.Modal):

    def __init__(self, view: InventoryView):
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
            row=3,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: InventoryView = self.view

        if await view.interaction_check(interaction):
            await interaction.response.defer()
            await view.sell_selected_item(interaction, amount=0, sell_until=True)


class BalanceButton(discord.ui.Button):

    def __init__(self, balance: int):
        self.balance = balance
        super().__init__(label=f"🅱️{balance}", style=discord.ButtonStyle.blurple, row=2)

    async def callback(self, interaction: discord.Interaction):
        view: InventoryView = self.view

        if await view.interaction_check(interaction):
            await interaction.response.defer(ephemeral=True)


class Dropdown(discord.ui.Select):

    def __init__(self, items: list[Item], selected: ItemType, disabled: bool = False):

        options = []

        for item in items:
            sell_price = int(
                min((item.cost * UserInventory.SELL_MODIFIER) / item.base_amount, 100)
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
            row=1,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: InventoryView = self.view

        if await view.interaction_check(interaction):
            await view.set_selected(interaction, self.values[0])


class PageButton(discord.ui.Button):

    def __init__(self, label: str, right: bool, disabled: bool = False):
        self.right = right
        super().__init__(
            label=label, style=discord.ButtonStyle.grey, row=2, disabled=disabled
        )

    async def callback(self, interaction: discord.Interaction):
        view: InventoryView = self.view

        if await view.interaction_check(interaction):
            await view.flip_page(interaction, self.right)


class CurrentPageButton(discord.ui.Button):

    def __init__(self, label: str):
        super().__init__(
            label=label, style=discord.ButtonStyle.grey, row=2, disabled=True
        )
