import contextlib

import discord

from combat.gear.gear import Gear
from combat.gear.types import Base, GearModifierType
from control.combat.combat_embed_manager import CombatEmbedManager
from control.controller import Controller
from control.types import ControllerType
from events.types import UIEventType
from events.ui_event import UIEvent
from view.combat.elements import (
    ImplementsBack,
    ImplementsBalance,
    MenuState,
)
from view.combat.special_shop_embed import SpecialShopHeadEmbed
from view.view_menu import ViewMenu


class SpecialShopView(ViewMenu, ImplementsBack, ImplementsBalance):

    def __init__(
        self,
        controller: Controller,
        interaction: discord.Interaction,
        items: list[Gear],
        item_values: dict[int, int],
        scrap_balance: int,
    ):
        super().__init__(timeout=300)
        self.controller = controller
        self.guild_name = interaction.guild.name
        self.member_id = interaction.user.id
        self.member = interaction.user
        self.guild_id = interaction.guild_id
        self.scrap_balance = scrap_balance

        self.selected: Gear = items[0] if len(items) > 0 else None
        self.item_values = item_values

        self.display_items = items
        self.item_count = len(items)
        self.message = None
        self.loaded = False

        self.controller_types = [ControllerType.EQUIPMENT]
        self.controller.register_view(self)
        self.refresh_elements()
        self.embed_manager: CombatEmbedManager = controller.get_service(
            CombatEmbedManager
        )

    async def listen_for_ui_event(self, event: UIEvent):
        match event.type:
            case UIEventType.SCRAP_BALANCE_CHANGED:
                guild_id = event.payload[0]
                member_id = event.payload[1]
                balance = event.payload[2]
                if member_id != self.member_id or guild_id != self.guild_id:
                    return
                await self.refresh_ui(scrap_balance=balance)
                return

        if event.view_id != self.id:
            return

    async def buy(self, interaction: discord.Interaction):
        await interaction.response.defer()
        event = UIEvent(
            UIEventType.FORGE_SHOP_BUY,
            (interaction, self.selected),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def open_shop(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

    async def go_back(
        self,
        interaction: discord.Interaction,
    ):
        await interaction.response.defer()
        event = UIEvent(
            UIEventType.MAIN_MENU_STATE_CHANGE,
            (interaction, MenuState.FORGE, False),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    def refresh_elements(self, disabled: bool = False):
        if not self.loaded:
            disabled = True
        self.clear_items()
        disable_buy = True
        if len(self.display_items) > 0:
            disable_buy = disabled
            self.add_item(
                Dropdown(self.display_items, self.selected, disabled=disabled)
            )

        selected_value = None
        if self.selected is not None:
            selected_value = self.item_values[self.selected.id]

        self.add_back_button(disabled=disabled, row=2)
        self.add_item(SelectButton(current_value=selected_value, disabled=disable_buy))
        self.add_scrap_balance_button(self.scrap_balance, row=2)

    async def refresh_ui(
        self,
        items: list[Gear] = None,
        scrap_balance: int = None,
        disabled: bool = False,
    ):
        if self.message is None:
            return

        if scrap_balance is not None:
            self.scrap_balance = scrap_balance

        if items is not None:
            self.display_items = items
            self.selected = (
                None if len(self.display_items) <= 0 else self.display_items[0]
            )

        if self.scrap_balance is not None:
            self.loaded = True

        self.guild_level = await self.controller.database.get_guild_level(self.guild_id)

        self.refresh_elements(disabled)

        embeds = []
        embeds.append(SpecialShopHeadEmbed(self.controller.bot))

        if len(self.display_items) <= 0:
            empty_embed = discord.Embed(
                title="Empty", color=discord.Colour.light_grey()
            )
            self.embed_manager.add_text_bar(
                empty_embed, "", "Seems like there is nothing here. Come back tomorrow."
            )
            empty_embed.set_thumbnail(url=self.controller.bot.user.display_avatar)
            embeds.append(empty_embed)

        for gear in self.display_items:
            embeds.append(gear.get_embed(scrap_value=self.item_values[gear.id]))

        await self.message.edit(embeds=embeds, view=self)

    async def set_selected(self, interaction: discord.Interaction, gear: Gear):
        await interaction.response.defer()
        self.selected = gear
        await self.refresh_ui()

    async def on_timeout(self):
        with contextlib.suppress(discord.HTTPException):
            await self.message.edit(view=None)
        self.controller.detach_view(self)


class SelectButton(discord.ui.Button):

    def __init__(self, current_value: int = None, disabled: bool = True):

        label = "Buy"
        if current_value is not None:
            label = f"Buy for ⚙️{current_value}"

        super().__init__(
            label=label,
            style=discord.ButtonStyle.green,
            row=2,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: SpecialShopView = self.view

        if await view.interaction_check(interaction):
            await view.buy(interaction)


class Dropdown(discord.ui.Select):

    def __init__(
        self,
        gear: list[Gear],
        selected: Gear,
        disabled: bool = False,
    ):
        self.gear = gear

        options = []

        for index, item in enumerate(gear):
            name = item.name
            if name is None or name == "":
                name = item.base.slot.value

            if item.base.base_type == Base.SKILL:
                description = []

                description.append(f"USES: {item.base_skill.stacks}")
                description.append(f"PWR: {item.base_skill.base_value:.1f}")
                description = " | ".join(description)
                description = (
                    (description[:95] + "..") if len(description) > 95 else description
                )
            else:

                description = [f"ILVL: {item.level}"]

                for modifier_type, value in item.modifiers.items():
                    label = GearModifierType.short_label(modifier_type)
                    value = GearModifierType.display_value(modifier_type, value)
                    description.append(f"{label}: {value}")

                description = " | ".join(description)
                description = (
                    (description[:95] + "..") if len(description) > 95 else description
                )

            label = f"[{item.rarity.value}] {name}"

            option = discord.SelectOption(
                label=label,
                description=description,
                value=index,
                default=(item.id == selected.id),
            )
            options.append(option)

        super().__init__(
            placeholder="Select an item you want to buy.",
            min_values=1,
            max_values=1,
            options=options,
            row=1,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: SpecialShopView = self.view

        if await view.interaction_check(interaction):
            await view.set_selected(
                interaction, [self.gear[int(value)] for value in self.values][0]
            )
