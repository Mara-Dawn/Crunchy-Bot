from enum import Enum

import discord

from combat.actors import Character
from combat.gear.types import (
    EquipmentSlot,
    Rarity,
)
from combat.types import UnlockableFeature
from config import Config
from control.combat.combat_embed_manager import CombatEmbedManager
from control.combat.combat_gear_manager import CombatGearManager
from control.controller import Controller
from control.forge_manager import ForgeManager
from control.types import ControllerType
from events.types import UIEventType
from events.ui_event import UIEvent
from forge.forgable import ForgeInventory
from forge.recipe import RecipeHandler
from view.combat.elements import (
    ClearForgeButton,
    ImplementsBack,
    ImplementsBalance,
    ImplementsMainMenu,
    MenuState,
)
from view.combat.embed import (
    ForgeEmbed,
)
from view.view_menu import ViewMenu


class ForgeMenuState(str, Enum):
    OVERVIEW = "Overview"
    SCRAP = "Use Scrap"
    COMBINE = "Combine Items"


class ForgeMenuView(ViewMenu, ImplementsMainMenu, ImplementsBalance, ImplementsBack):

    def __init__(
        self,
        controller: Controller,
        interaction: discord.Interaction,
        character: Character,
        scrap_balance: int,
        forge_level: int,
        state: ForgeMenuState = None,
    ):
        super().__init__(timeout=None)
        self.controller = controller
        self.character = character
        self.member_id = interaction.user.id
        self.guild_id = character.member.guild.id
        self.member = interaction.user
        self.state = MenuState.FORGE
        self.scrap_balance = scrap_balance
        self.loaded = False
        self.forge_inventory: ForgeInventory = None
        self.recipe_handler = RecipeHandler()

        self.forge_manager: ForgeManager = self.controller.get_service(ForgeManager)
        self.embed_manager: CombatEmbedManager = self.controller.get_service(
            CombatEmbedManager
        )

        self.forge_level = forge_level
        self.max_rarity = Rarity.COMMON
        for rarity, level in CombatGearManager.MIN_RARITY_LVL.items():
            if level <= self.forge_level:
                self.max_rarity = rarity
            else:
                break

        self.forge_options = {
            level: scrap
            for level, scrap in ForgeManager.SCRAP_ILVL_MAP.items()
            if level <= self.forge_level
        }
        self.max_forge_level = max(self.forge_options.keys())
        self.selected: int = self.max_forge_level
        self.selected_slot: EquipmentSlot = None

        if state is None:
            self.forge_state: ForgeMenuState = ForgeMenuState.OVERVIEW
        else:
            self.forge_state: ForgeMenuState = state

        self.controller_types = [ControllerType.MAIN_MENU, ControllerType.EQUIPMENT]
        self.controller.register_view(self)
        self.refresh_elements()

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

    def refresh_elements(self, disabled: bool = False):

        if not self.loaded:
            disabled = True

        disable_combine = disabled

        if self.forge_inventory is not None:
            for forgeable in self.forge_inventory.items:
                if forgeable is None:
                    disable_combine = True
        else:
            disable_combine = True

        if not disable_combine:
            disable_combine = not self.recipe_handler.handle(self.forge_inventory)

        self.clear_items()

        self.add_menu(self.state, False, disabled)
        self.add_scrap_balance_button(self.scrap_balance)

        match self.forge_state:
            case ForgeMenuState.OVERVIEW:
                if (
                    self.guild_level
                    >= Config.UNLOCK_LEVELS[UnlockableFeature.FORGE_SCRAP]
                ):
                    self.add_item(ForgeStateButton(ForgeMenuState.SCRAP))
                if (
                    self.guild_level
                    >= Config.UNLOCK_LEVELS[UnlockableFeature.FORGE_RECIPES]
                ):
                    self.add_item(ForgeStateButton(ForgeMenuState.COMBINE))
                if (
                    self.guild_level
                    >= Config.UNLOCK_LEVELS[UnlockableFeature.FORGE_SHOP]
                ):
                    self.add_item(ForgeShopButton(row=2))
            case ForgeMenuState.SCRAP:
                self.add_item(ForgeDropdown(self.forge_options, self.selected))
                self.add_item(SlotDropdown(self.selected_slot, disabled=disabled))
                scaling = 1
                if self.selected_slot is not None:
                    scaling = (
                        CombatGearManager.SLOT_SCALING[self.selected_slot]
                        * Config.SCRAP_FORGE_MULTI
                    )
                total = int(ForgeManager.SCRAP_ILVL_MAP[self.selected] * scaling)
                self.add_item(ForgeUseButton(total))
                if (
                    self.guild_level
                    >= Config.UNLOCK_LEVELS[UnlockableFeature.FORGE_SHOP]
                ):
                    self.add_item(ForgeShopButton())
                self.add_back_button()
            case ForgeMenuState.COMBINE:
                self.add_back_button(row=1)
                self.add_item(ForgeCombineButton(disabled=disable_combine))
                self.add_item(ClearForgeButton(disabled=disabled, row=1))

    async def refresh_ui(
        self,
        character: Character = None,
        scrap_balance: int = None,
        disabled: bool = False,
    ):
        if self.message is None:
            return

        if scrap_balance is not None:
            self.scrap_balance = scrap_balance

        if character is not None:
            self.character = character

        if self.character is not None and self.scrap_balance is not None:
            self.loaded = True

        self.forge_inventory = await self.forge_manager.get_forge_inventory(self.member)

        self.guild_level = await self.controller.database.get_guild_level(self.guild_id)

        self.refresh_elements(disabled=disabled)
        embeds = []
        embed = ForgeEmbed(
            self.member,
            self.forge_level,
            self.max_rarity,
        )
        embeds.append(embed)

        match self.forge_state:
            case ForgeMenuState.COMBINE:
                if self.forge_inventory is not None:
                    for forgeable in self.forge_inventory.items:
                        if forgeable is None:
                            empty_embed = discord.Embed(
                                title="Empty", color=discord.Colour.light_grey()
                            )
                            self.embed_manager.add_text_bar(
                                empty_embed,
                                "",
                                "Please fill out all slots to combine them.",
                            )
                            empty_embed.set_thumbnail(url=self.member.display_avatar)
                            embeds.append(empty_embed)
                        else:
                            embeds.append(forgeable.get_embed())
                else:
                    for _ in range(3):
                        empty_embed = discord.Embed(
                            title="Empty", color=discord.Colour.light_grey()
                        )
                        self.embed_manager.add_text_bar(
                            empty_embed,
                            "",
                            "Please fill out all slots to combine them.",
                        )
                        empty_embed.set_thumbnail(url=self.member.display_avatar)
                        embeds.append(empty_embed)

        try:
            await self.message.edit(embeds=embeds, view=self)
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

    async def set_selected(self, interaction: discord.Interaction, item_level: int):
        await interaction.response.defer()
        self.selected = item_level
        await self.refresh_ui()

    async def go_back(
        self,
        interaction: discord.Interaction,
    ):
        await self.set_forge_state(interaction, ForgeMenuState.OVERVIEW)

    async def set_forge_state(
        self, interaction: discord.Interaction, state: ForgeMenuState
    ):
        await interaction.response.defer()
        self.forge_state = state
        await self.refresh_ui()

    async def set_selected_slot(
        self, interaction: discord.Interaction, slot: EquipmentSlot
    ):
        await interaction.response.defer()
        self.selected_slot = slot
        await self.refresh_ui()

    async def combine_items(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        event = UIEvent(
            UIEventType.FORGE_COMBINE,
            (interaction, self.forge_inventory),
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

    async def use_forge(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        event = UIEvent(
            UIEventType.FORGE_USE,
            (interaction, self.selected, self.selected_slot),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def open_shop(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        event = UIEvent(
            UIEventType.FORGE_OPEN_SHOP,
            interaction,
            self.id,
        )
        await self.controller.dispatch_ui_event(event)


class ForgeDropdown(discord.ui.Select):

    def __init__(
        self,
        scrap_options: dict[int, int],
        selected: int,
        disabled: bool = False,
    ):
        options = []

        for item_level, _ in scrap_options.items():
            label = f"Item Level {item_level}"
            description = f"Gain a random level {item_level} item or skill."

            option = discord.SelectOption(
                label=label,
                description=description,
                value=item_level,
                default=(item_level == selected),
            )
            options.append(option)

        super().__init__(
            placeholder="",
            min_values=1,
            max_values=1,
            options=options,
            row=1,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: ForgeMenuView = self.view

        if await view.interaction_check(interaction):
            await view.set_selected(
                interaction, [int(value) for value in self.values][0]
            )


class SlotDropdown(discord.ui.Select):

    def __init__(
        self,
        selected: EquipmentSlot = None,
        disabled: bool = False,
    ):
        option = discord.SelectOption(
            label="Any",
            description="Drop a completely random item or skill.",
            value="Any",
            default=(selected is None),
        )
        options = [option]

        for slot in EquipmentSlot:
            if slot in [EquipmentSlot.ANY, EquipmentSlot.ARMOR]:
                continue
            label = slot.value
            description = f"Gain a random {slot.value}."

            option = discord.SelectOption(
                label=label,
                description=description,
                value=slot.value,
                default=(slot == selected),
            )
            options.append(option)

        super().__init__(
            placeholder="",
            min_values=1,
            max_values=1,
            options=options,
            row=2,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: ForgeMenuView = self.view

        if await view.interaction_check(interaction):
            selected = self.values[0]
            selected = None if selected == "Any" else EquipmentSlot(selected)

            await view.set_selected_slot(interaction, selected)


class ForgeUseButton(discord.ui.Button):

    def __init__(self, total: int, disabled: bool = False):
        super().__init__(
            label=f"Throw {total}⚙️ Scrap into Forge",
            style=discord.ButtonStyle.green,
            row=3,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: ForgeMenuView = self.view

        if await view.interaction_check(interaction):
            await view.use_forge(interaction)


class ForgeCombineButton(discord.ui.Button):

    def __init__(self, disabled: bool = False):
        super().__init__(
            label="Combine!",
            style=discord.ButtonStyle.green,
            row=1,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: ForgeMenuView = self.view

        if await view.interaction_check(interaction):
            await view.combine_items(interaction)


class ForgeStateButton(discord.ui.Button):

    def __init__(self, state: ForgeMenuState, disabled: bool = False, row: int = 2):
        self.state = state
        super().__init__(
            label=state.value,
            style=discord.ButtonStyle.green,
            row=row,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: ForgeMenuView = self.view

        if await view.interaction_check(interaction):
            await view.set_forge_state(interaction, self.state)


class ForgeShopButton(discord.ui.Button):

    def __init__(self, disabled: bool = False, row: int = 3):
        super().__init__(
            label="Secret Shop",
            style=discord.ButtonStyle.green,
            row=row,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: ForgeMenuView = self.view

        if await view.interaction_check(interaction):
            await view.open_shop(interaction)
