import contextlib

import discord

from control.controller import Controller
from control.types import ControllerType
from events.types import UIEventType
from events.ui_event import UIEvent
from items import BaseKey
from items.item import Item
from view.view_menu import ViewMenu


class InventoryConfirmView(ViewMenu):

    def __init__(
        self,
        controller: Controller,
        interaction: discord.Interaction,
        item: Item,
        parent_id: int,
    ):
        super().__init__(timeout=200)

        self.controller = controller
        self.parent_id = parent_id
        self.type = None
        if item is not None:
            self.type = item.type
        self.item = item

        self.member_id = interaction.user.id
        self.guild_id = interaction.guild_id

        self.selected_amount: int = 1

        self.confirm_button: ConfirmButton = None

        self.combine_all_button: CombineAllButton = None
        self.combine_amount_button: CombineAmountButton = None

        self.cancel_button: CancelButton = None

        self.controller_types = [ControllerType.INVENTORY_VIEW]
        self.controller.register_view(self)

        self.refresh_elements()

    async def listen_for_ui_event(self, event: UIEvent):
        if event.view_id != self.id:
            return

        match event.type:
            case UIEventType.SHOP_RESPONSE_REFRESH:
                await self.refresh_ui()
            case UIEventType.SHOP_RESPONSE_DISABLE:
                await self.refresh_ui(disabled=event.payload)
            case UIEventType.SHOP_RESPONSE_EMOJI_UPDATE:
                self.selected_emoji = event.payload[0]
                self.selected_emoji_type = event.payload[1]
                await self.refresh_ui()

    async def submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        event = UIEvent(
            UIEventType.INVENTORY_RESPONSE_CONFIRM_SUBMIT,
            (interaction, self.item),
            self.parent_id,
        )
        await self.controller.dispatch_ui_event(event)

    def refresh_elements(self, disabled: bool = False):
        self.clear_items()
        self.confirm_button = ConfirmButton("Use")
        self.combine_all_button = CombineAllButton(disabled)
        self.combine_amount_button = CombineAmountButton(disabled)
        self.cancel_button = CancelButton()

        self.add_item(self.confirm_button)
        if self.item.type in BaseKey.LVL_MAP:
            self.add_item(self.combine_all_button)
            self.add_item(self.combine_amount_button)
        self.add_item(self.cancel_button)

    async def refresh_ui(
        self, disabled: bool = False, force_embed: discord.Embed = None
    ):
        color = discord.Colour.purple()

        embed = force_embed
        if embed is None:
            embed = self.item.get_embed(
                self.controller.bot, color=color, show_title=False, show_price=True
            )

        emoji = self.item.emoji
        if isinstance(self.item.emoji, int):
            emoji = str(self.controller.bot.get_emoji(self.item.emoji))
        embed.title = f"{emoji} {self.item.name} {emoji}"

        embed.title = f"> {embed.title}"

        self.refresh_elements(disabled)

        try:
            await self.message.edit(embed=embed, view=self)
        except (discord.NotFound, discord.HTTPException):
            self.controller.detach_view(self)

    async def combine_keys(
        self,
        interaction: discord.Interaction,
        amount: int,
        combine_until: bool = False,
    ):

        event = UIEvent(
            UIEventType.INVENTORY_COMBINE,
            (interaction, self.item.type, amount, combine_until),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def on_timeout(self):
        with contextlib.suppress(discord.NotFound):
            await self.message.delete()

        self.controller.detach_view(self)


class CancelButton(discord.ui.Button):

    def __init__(self):

        super().__init__(label="Cancel", style=discord.ButtonStyle.red, row=0)

    async def callback(self, interaction: discord.Interaction):
        view: InventoryConfirmView = self.view

        if await view.interaction_check(interaction):
            await view.on_timeout()


class ConfirmButton(discord.ui.Button):

    def __init__(self, label: str = "Confirm"):
        super().__init__(label=label, style=discord.ButtonStyle.green, row=0)

    async def callback(self, interaction: discord.Interaction):
        view: InventoryConfirmView = self.view

        if await view.interaction_check(interaction):
            await view.submit(interaction)


class CombineAmountButton(discord.ui.Button):

    def __init__(self, disabled: bool = False):
        super().__init__(
            label="Combine Custom Amount",
            style=discord.ButtonStyle.grey,
            row=0,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: InventoryConfirmView = self.view

        if await view.interaction_check(interaction):
            await interaction.response.send_modal(CombineAmountModal(self.view))


class CombineAmountModal(discord.ui.Modal):

    def __init__(self, view: InventoryConfirmView):
        super().__init__(title="Upgrade Keys to the next higher level. (3:1)")
        self.view = view

        self.amount = discord.ui.TextInput(
            label="Specify an amount to combine:",
            placeholder="In multiples of 3",
            required=False,
        )
        self.add_item(self.amount)
        self.amount_left = discord.ui.TextInput(
            label="OR combine until you have this many left:",
            placeholder="Amount left",
            required=False,
        )
        self.add_item(self.amount_left)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        combine_amount_str = self.amount.value
        combine_until_str = self.amount_left.value

        if len(combine_amount_str) == 0 and len(combine_until_str) == 0:
            await interaction.followup.send(
                "Please specify either a combine amount or a combine until value.",
                ephemeral=True,
            )
            return

        if len(combine_amount_str) > 0 and len(combine_until_str) > 0:
            await interaction.followup.send(
                "You can only specify either combine amount or combine until, not both.",
                ephemeral=True,
            )
            return

        combine_until = False

        amount = combine_amount_str
        if len(amount) == 0:
            amount = combine_until_str
            combine_until = True

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

        await self.view.combine_keys(
            interaction, amount=amount, combine_until=combine_until
        )


class CombineAllButton(discord.ui.Button):

    def __init__(self, disabled: bool = False):
        super().__init__(
            label="Combine All (3:1)",
            style=discord.ButtonStyle.grey,
            row=0,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: InventoryConfirmView = self.view

        if await view.interaction_check(interaction):
            await interaction.response.defer()
            await view.combine_keys(interaction, amount=0, combine_until=True)
