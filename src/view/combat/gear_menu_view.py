from enum import Enum

import discord

from combat.actors import Character
from combat.gear.types import (
    EquipmentSlot,
)
from combat.types import UnlockableFeature
from config import Config
from control.combat.combat_embed_manager import CombatEmbedManager
from control.controller import Controller
from control.types import ControllerType
from events.types import UIEventType
from events.ui_event import UIEvent
from view.combat.elements import (
    ImplementsBack,
    ImplementsBalance,
    ImplementsMainMenu,
    MenuState,
)
from view.combat.embed import (
    AttributesHeadEmbed,
    EquipmentHeadEmbed,
)
from view.view_menu import ViewMenu


class GearMenuState(Enum):
    GEAR = 0
    STATS = 1


class GearMenuView(ViewMenu, ImplementsMainMenu, ImplementsBack, ImplementsBalance):

    def __init__(
        self,
        controller: Controller,
        interaction: discord.Interaction,
        character: Character,
        scrap_balance: int,
        limited: bool = True,
    ):
        super().__init__(timeout=None)
        self.controller = controller
        self.character = character
        self.member_id = interaction.user.id
        self.guild_id = character.member.guild.id
        self.member = interaction.user
        self.menu_state = MenuState.GEAR
        self.view_state = GearMenuState.GEAR
        self.limited = limited
        self.scrap_balance = scrap_balance
        self.loaded = False
        self.embed_manager: CombatEmbedManager = self.controller.get_service(
            CombatEmbedManager
        )

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

        self.clear_items()

        self.add_menu(self.menu_state, self.limited, disabled)

        if self.limited:
            match self.view_state:
                case GearMenuState.GEAR:
                    self.add_item(StatsButton(disabled=disabled))
                case GearMenuState.STATS:
                    self.add_back_button(disabled=disabled)
            return

        self.add_scrap_balance_button(self.scrap_balance)

        match self.view_state:
            case GearMenuState.GEAR:
                self.add_item(SelectGearSlot(EquipmentSlot.WEAPON, disabled=disabled))
                self.add_item(SelectGearSlot(EquipmentSlot.HEAD, disabled=disabled))
                self.add_item(SelectGearSlot(EquipmentSlot.BODY, disabled=disabled))
                self.add_item(SelectGearSlot(EquipmentSlot.LEGS, disabled=disabled))
                self.add_item(
                    SelectGearSlot(EquipmentSlot.ACCESSORY, disabled=disabled)
                )
                self.add_item(StatsButton(disabled=disabled))
                if (
                    self.guild_level
                    >= Config.UNLOCK_LEVELS[UnlockableFeature.ENCHANTMENTS]
                ):
                    self.add_item(EnchantmentsButton(disabled=disabled))
                self.add_item(ScrapAllButton(disabled=disabled))
            case GearMenuState.STATS:
                self.add_back_button(disabled=disabled)

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

        self.guild_level = await self.controller.database.get_guild_level(self.guild_id)

        self.refresh_elements(disabled=disabled)
        embeds = []
        match self.view_state:
            case GearMenuState.GEAR:
                embeds.append(
                    EquipmentHeadEmbed(
                        self.character.member, is_owner=(not self.limited)
                    )
                )
                embeds.append(
                    await self.embed_manager.get_gear_embed(
                        self.character.equipment.weapon, self.character
                    )
                )
                embeds.append(
                    await self.embed_manager.get_gear_embed(
                        self.character.equipment.head_gear, self.character
                    )
                )
                embeds.append(
                    await self.embed_manager.get_gear_embed(
                        self.character.equipment.body_gear, self.character
                    )
                )
                embeds.append(
                    await self.embed_manager.get_gear_embed(
                        self.character.equipment.leg_gear, self.character
                    )
                )
                embeds.append(
                    await self.embed_manager.get_gear_embed(
                        self.character.equipment.accessory_1, self.character
                    )
                )
                embeds.append(
                    await self.embed_manager.get_gear_embed(
                        self.character.equipment.accessory_2, self.character
                    )
                )
            case GearMenuState.STATS:
                embeds.append(
                    AttributesHeadEmbed(
                        self.character.member, is_owner=(not self.limited)
                    )
                )
                title = f"{self.character.member.display_name}'s Attributes"
                embeds.append(self.character.equipment.get_embed(title=title))

        await self.message.edit(embeds=embeds, view=self)
        # try:
        #     await self.message.edit(embeds=embeds, view=self)
        # except (discord.NotFound, discord.HTTPException):
        #     self.controller.detach_view(self)

    async def set_state(self, state: MenuState, interaction: discord.Interaction):
        await interaction.response.defer()
        event = UIEvent(
            UIEventType.MAIN_MENU_STATE_CHANGE,
            (interaction, state, self.limited),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def toggle_stats(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.view_state = GearMenuState.STATS
        await self.refresh_ui()

    async def go_back(
        self,
        interaction: discord.Interaction,
    ):
        await interaction.response.defer()
        self.view_state = GearMenuState.GEAR
        await self.refresh_ui()

    async def change_gear(self, interaction: discord.Interaction, slot: EquipmentSlot):
        await interaction.response.defer()
        event = UIEvent(
            UIEventType.GEAR_OPEN_SELECT,
            (interaction, slot),
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

    async def open_enchantments_view(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        event = UIEvent(
            UIEventType.ENCHANTMENTS_OPEN,
            (interaction, None),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def dismantle_gear(self, interaction: discord.Interaction):
        await interaction.response.defer()
        event = UIEvent(
            UIEventType.GEAR_DISMANTLE,
            (interaction, [], True, None),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)


class StatsButton(discord.ui.Button):

    def __init__(self, selected: bool = False, disabled: bool = True, row: int = 2):
        color = discord.ButtonStyle.grey

        label = "Attributes"

        super().__init__(
            label=label,
            style=color,
            disabled=disabled,
            row=row,
        )

    async def callback(self, interaction: discord.Interaction):
        view: GearMenuView = self.view
        await view.toggle_stats(interaction)


class SelectGearSlot(discord.ui.Button):

    def __init__(
        self,
        slot: EquipmentSlot,
        selected: bool = False,
        disabled: bool = False,
        row: int = 1,
    ):

        label = slot.value
        if selected:
            label = f">{label}<"
            disabled = True

        super().__init__(
            label=label,
            style=discord.ButtonStyle.green,
            disabled=disabled,
            row=row,
        )
        self.slot = slot

    async def callback(self, interaction: discord.Interaction):
        view: GearMenuView = self.view
        await view.change_gear(interaction, self.slot)


class ScrapAllButton(discord.ui.Button):

    def __init__(self, disabled: bool = False):

        label = "Scrap non locked Gear"
        super().__init__(
            label=label,
            style=discord.ButtonStyle.red,
            row=2,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: GearMenuView = self.view

        if await view.interaction_check(interaction):
            await view.dismantle_gear(interaction)


class EnchantmentsButton(discord.ui.Button):

    def __init__(self, disabled: bool = False):

        label = "Enchantments"

        super().__init__(
            label=label,
            style=discord.ButtonStyle.grey,
            row=2,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: GearMenuView = self.view

        if await view.interaction_check(interaction):
            await view.open_enchantments_view(interaction)
