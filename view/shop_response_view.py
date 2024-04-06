import re
from typing import List
import discord
from control.view.shop_response_view_controller import ShopResponseViewController
from events.ui_event import UIEvent
from events.types import UIEventType
from items.item import Item
from view.types import EmojiType
from view.view_menu import ViewMenu


class ShopResponseView(ViewMenu):

    def __init__(
        self,
        controller: ShopResponseViewController,
        interaction: discord.Interaction,
        item: Item,
    ):
        super().__init__(timeout=200)

        self.controller = controller
        self.type = None
        if item is not None:
            self.type = item.get_type()
        self.item = item

        self.message = None
        self.member_id = interaction.user.id
        self.guild_id = interaction.guild_id

        self.selected_user: discord.Member = None
        self.selected_amount: int = 1
        self.selected_color: str = None
        self.selected_emoji: discord.Emoji | str = None
        self.selected_emoji_type: EmojiType = None

        self.confirm_button: ConfirmButton = None
        self.cancel_button: CancelButton = None
        self.user_select: UserPicker = None
        self.color_input_button: ColorInputButton = None
        self.amount_select: AmountInput = None
        self.reaction_input_button: ReactionInputButton = None

        self.controller.register_view(self)

    async def listen_for_ui_event(self, event: UIEvent):
        if (
            event.get_guild_id() != self.guild_id
            or event.get_member_id() != self.member_id
        ):
            return

        match event.get_type():
            case UIEventType.REFRESH_SHOP_RESPONSE:
                await self.refresh_ui()
            case UIEventType.DISABLE_SHOP_RESPONSE:
                await self.refresh_ui(disabled=event.get_payload())
            case UIEventType.UPDATE_SHOP_RESPONSE_EMOJI:
                self.selected_emoji = event.get_payload()[0]
                self.selected_emoji_type = event.get_payload()[1]
                await self.refresh_ui()

    async def submit(self, interaction: discord.Interaction):
        pass

    def refresh_elements(self, disabled: bool = False):
        elements: List[discord.ui.Item] = [
            self.user_select,
            self.amount_select,
            self.color_input_button,
            self.reaction_input_button,
            self.confirm_button,
            self.cancel_button,
        ]

        self.clear_items()
        for element in elements:
            if element is self.amount_select and not self.item.get_allow_amount():
                continue
            if element is not None:
                element.disabled = disabled
                self.add_item(element)

    async def refresh_ui(self, disabled: bool = False):
        color = discord.Colour.purple()
        if self.selected_color is not None:
            hex_value = int(self.selected_color, 16)
            color = discord.Color(hex_value)

        embed = self.item.get_embed(color=color, amount_in_cart=self.selected_amount)

        embed.title = (
            f"{self.item.get_emoji()} {self.item.get_name()} {self.item.get_emoji()}"
        )

        if self.selected_amount > 1:
            embed.title = f"{self.selected_amount}x {embed.title}"
        if self.selected_color is not None:
            embed.title = f"{embed.title} [#{self.selected_color}]"
        if self.selected_emoji is not None:
            embed.title = f"{embed.title} - Selected: {str(self.selected_emoji)}"

        embed.title = f"> {embed.title}"

        if self.amount_select is not None:
            self.amount_select.options[self.selected_amount - 1].default = True

        self.refresh_elements(disabled)

        await self.message.edit(embed=embed, view=self)

    async def set_amount(self, amount: int):
        self.amount_select.options[self.selected_amount - 1].default = False
        self.selected_amount = amount
        await self.refresh_ui()

    async def set_selected(self, member: discord.Member):
        self.selected_user = member
        await self.refresh_ui()

    async def set_color(self, color: str):
        self.selected_color = color.lstrip("#")
        await self.refresh_ui()

    async def set_emoji(self, emoji: discord.Emoji | str, emoji_type: EmojiType):
        self.selected_emoji = emoji
        self.selected_emoji_type = emoji_type
        await self.refresh_ui()

    async def set_message(self, message: discord.Message):
        self.message = message
        await self.refresh_ui()

    # pylint: disable-next=arguments-differ
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return await self.controller.interaction_check(interaction, self.member_id)

    async def on_timeout(self):
        try:
            await self.message.delete()
        except discord.NotFound:
            pass

        self.controller.refresh_shop_view(self.guild_id, self.member_id)
        self.controller.detach_view(self)


class UserPicker(discord.ui.UserSelect):

    def __init__(self):
        super().__init__(
            placeholder="Select a user.", min_values=1, max_values=1, row=0
        )

    async def callback(self, interaction: discord.Interaction):
        view: ShopResponseView = self.view
        await interaction.response.defer()

        if await view.interaction_check(interaction):
            await view.set_selected(self.values[0])


class CancelButton(discord.ui.Button):

    def __init__(self):
        super().__init__(label="Cancel", style=discord.ButtonStyle.red, row=2)

    async def callback(self, interaction: discord.Interaction):
        view: ShopResponseView = self.view

        if await view.interaction_check(interaction):
            await view.on_timeout()


class ConfirmButton(discord.ui.Button):

    def __init__(self, label: str = "Confirm and Buy"):
        super().__init__(label=label, style=discord.ButtonStyle.green, row=2)

    async def callback(self, interaction: discord.Interaction):
        view: ShopResponseView = self.view

        if await view.interaction_check(interaction):
            await view.submit(interaction)


class AmountInput(discord.ui.Select):

    def __init__(self, suffix: str = ""):
        options = []

        for i in range(1, 20):
            options.append(
                discord.SelectOption(label=f"{i}{suffix}", value=i, default=(i == 1))
            )

        super().__init__(
            placeholder="Choose the amount.",
            min_values=1,
            max_values=1,
            options=options,
            row=1,
        )

    async def callback(self, interaction: discord.Interaction):
        view: ShopResponseView = self.view
        await interaction.response.defer()
        if await view.interaction_check(interaction):
            await view.set_amount(int(self.values[0]))


class ColorInputButton(discord.ui.Button):

    def __init__(self, default_color: str):
        super().__init__(label="Pick a Color", style=discord.ButtonStyle.green, row=2)
        self.default_color = default_color

    async def callback(self, interaction: discord.Interaction):
        view: ShopResponseView = self.view
        if await view.interaction_check(interaction):
            await interaction.response.send_modal(
                ColorInputModal(self.view, self.default_color)
            )


class ColorInputModal(discord.ui.Modal):

    def __init__(self, view: ShopResponseView, default_color: str):
        super().__init__(title="Choose a Color")
        self.view = view
        if default_color is not None:
            default_color = f"#{default_color}"
        self.hex_color = discord.ui.TextInput(
            label="Hex Color Code", placeholder="#FFFFFF", default=default_color
        )
        self.add_item(self.hex_color)

    # pylint: disable-next=arguments-differ
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        hex_string = self.hex_color.value
        match = re.search(r"^#(?:[0-9a-fA-F]{3}){1,2}$", hex_string)
        if not match:
            await interaction.followup.send(
                "Please enter a valid hex color value.", ephemeral=True
            )
            return

        await self.view.set_color(hex_string)


class ReactionInputButton(discord.ui.Button):

    def __init__(self):
        super().__init__(label="Select Emoji", style=discord.ButtonStyle.green, row=2)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        parent: ShopResponseView = self.view
        if await parent.interaction_check(interaction):
            await parent.refresh_ui(disabled=True)

            content = f"<@{interaction.user.id}> please react to this message with the emoji of your choice."
            view = ReactionInputView(parent.controller, interaction, parent.item)
            message = await interaction.followup.send(content, view=view)
            await view.set_message(message)


class ReactionInputView(ShopResponseView):

    def __init__(
        self,
        controller: ShopResponseViewController,
        interaction: discord.Interaction,
        item: Item,
    ):
        super().__init__(controller, interaction, item)
        self.controller = controller

        self.confirm_button = ConfirmButton("Confirm")
        self.cancel_button = CancelButton()

        self.refresh_elements()

    async def listen_for_ui_event(self, event: UIEvent):
        pass

    async def submit(self, interaction: discord.Interaction):
        self.controller.submit_reaction_selection(interaction, self.message)

    async def on_timeout(self):
        try:
            await self.message.delete()
        except discord.NotFound:
            pass

        self.controller.refresh_shop_response_view(self.guild_id, self.member_id)
        self.controller.detach_view(self)
