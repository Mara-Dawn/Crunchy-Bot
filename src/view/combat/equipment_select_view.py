import contextlib
import copy

import discord

from combat.gear.gear import Gear
from combat.gear.types import EquipmentSlot, GearModifierType, Rarity
from control.combat.combat_actor_manager import CombatActorManager
from control.combat.combat_embed_manager import CombatEmbedManager
from control.controller import Controller
from control.forge_manager import ForgeManager
from control.types import ControllerType
from events.types import UIEventType
from events.ui_event import UIEvent
from forge.forgable import ForgeInventory
from view.combat.elements import (
    ImplementsBack,
    ImplementsBalance,
    ImplementsCrafting,
    ImplementsForging,
    ImplementsLocking,
    ImplementsPages,
    ImplementsScrapping,
    MenuState,
)
from view.combat.embed import SelectGearHeadEmbed
from view.combat.forge_menu_view import ForgeMenuState
from view.combat.gear_menu_view import SelectGearSlot
from view.view_menu import ViewMenu


class EquipmentSelectView(
    ViewMenu,
    ImplementsPages,
    ImplementsBack,
    ImplementsLocking,
    ImplementsScrapping,
    ImplementsCrafting,
    ImplementsForging,
    ImplementsBalance,
):

    def __init__(
        self,
        controller: Controller,
        interaction: discord.Interaction,
        gear_inventory: list[Gear],
        currently_equipped: list[Gear],
        scrap_balance: int,
        slot: EquipmentSlot,
    ):
        super().__init__(timeout=300)
        self.controller = controller
        self.guild_name = interaction.guild.name
        self.member_id = interaction.user.id
        self.member = interaction.user
        self.guild_id = interaction.guild_id
        self.gear = gear_inventory
        self.current = currently_equipped
        self.scrap_balance = scrap_balance

        self.current_page = 0
        self.selected: list[Gear] = []

        self.filter = slot
        self.filtered_items = []
        self.display_items = []
        self.item_count = 0
        self.page_count = 1
        self.filter_items()
        self.message = None
        self.loaded = False
        self.forge_inventory: ForgeInventory = None

        self.controller_types = [ControllerType.MAIN_MENU, ControllerType.EQUIPMENT]
        self.controller.register_view(self)
        self.refresh_elements()
        self.embed_manager: CombatEmbedManager = controller.get_service(
            CombatEmbedManager
        )
        self.actor_manager: CombatActorManager = self.controller.get_service(
            CombatActorManager
        )
        self.forge_manager: ForgeManager = self.controller.get_service(ForgeManager)

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

    def filter_items(self):
        self.filtered_items = [
            gear for gear in self.gear if gear.base.slot == self.filter
        ]
        self.item_count = len(self.filtered_items)
        self.page_count = int(self.item_count / SelectGearHeadEmbed.ITEMS_PER_PAGE) + (
            self.item_count % SelectGearHeadEmbed.ITEMS_PER_PAGE > 0
        )
        self.page_count = max(self.page_count, 1)

        self.filtered_items = sorted(
            self.filtered_items,
            key=lambda x: (
                (x.id in [gear.id for gear in self.current]),
                # x.locked,
                x.level,
                Gear.RARITY_SORT_MAP[x.rarity],
            ),
            reverse=True,
        )

    async def flip_page(self, interaction: discord.Interaction, right: bool = False):
        await interaction.response.defer()
        self.current_page = (self.current_page + (1 if right else -1)) % self.page_count
        # self.selected = []
        await self.refresh_ui()

    async def select_gear(self, interaction: discord.Interaction):
        await interaction.response.defer()
        selected = [item for item in self.selected]
        self.selected = []
        event = UIEvent(
            UIEventType.GEAR_EQUIP,
            (interaction, selected),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def scrap_selected(
        self,
        interaction: discord.Interaction,
        scrap_all: bool = False,
        amount: int | None = None,
        scrap_until: bool = False,
    ):
        await interaction.response.defer()

        scrappable = [item for item in self.selected if not item.locked]
        self.selected = []

        event = UIEvent(
            UIEventType.GEAR_DISMANTLE,
            (interaction, scrappable, scrap_all, self.filter),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def lock_selected(
        self,
        interaction: discord.Interaction,
    ):
        await interaction.response.defer()
        selected = [item for item in self.selected]
        self.selected = []
        event = UIEvent(
            UIEventType.GEAR_LOCK,
            (interaction, selected),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def unlock_selected(
        self,
        interaction: discord.Interaction,
    ):
        await interaction.response.defer()
        items = [
            item
            for item in self.selected
            if item.id not in [item.id for item in self.current]
        ]
        self.selected = []
        event = UIEvent(
            UIEventType.GEAR_UNLOCK,
            (interaction, items),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def go_back(
        self,
        interaction: discord.Interaction,
    ):
        await interaction.response.defer()
        event = UIEvent(
            UIEventType.MAIN_MENU_STATE_CHANGE,
            (interaction, MenuState.GEAR, False),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

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

    async def craft_selected(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        if len(self.selected) != 1:
            return

        selected_piece = self.selected[0]

        event = UIEvent(
            UIEventType.ENCHANTMENTS_OPEN,
            (interaction, selected_piece),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    def refresh_elements(self, disabled: bool = False):
        page_display = f"Page {self.current_page + 1}/{self.page_count}"

        if not self.loaded:
            disabled = True

        max_values = 1
        if self.filter == EquipmentSlot.ACCESSORY:
            max_values = 2

        disable_equip = disabled
        disable_dismantle = disabled
        disable_lock = disabled
        disable_craft = disabled
        disable_forge = disabled

        if len(self.selected) <= 0:
            disable_equip = True
            disable_dismantle = True
            disable_lock = True
        elif len(self.selected) > max_values:
            disable_equip = True

        if len(self.selected) != 1:
            disable_craft = True
            disable_forge = True

        for selected_gear in self.selected:
            if selected_gear.id in [gear.id for gear in self.current]:
                disable_dismantle = True

            if (
                selected_gear.rarity == Rarity.UNIQUE
                or GearModifierType.CRANGLED in selected_gear.modifiers
            ):
                disable_craft = True

            if selected_gear.id < 0:
                # Default Gear
                disable_dismantle = True
                disable_craft = True
                disable_forge = True

        equipped = [gear.id for gear in self.current if gear.base.slot == self.filter]

        self.clear_items()
        if len(self.display_items) > 0:
            self.add_item(
                Dropdown(self.display_items, self.selected, equipped, disabled=disabled)
            )
        self.add_page_button("<", False, disabled=disabled)
        self.add_item(SelectButton(disabled=disable_equip))
        self.add_page_button(">", True, disabled=disabled)
        self.add_current_page_button(page_display)
        self.add_scrap_balance_button(self.scrap_balance, row=2)
        self.add_scrap_selected_button(disabled=disable_dismantle)
        self.add_craft_button(disabled=disable_craft)
        self.add_lock_button(disabled=disable_lock)
        self.add_unlock_button(disabled=disable_lock)
        self.add_add_to_forge_button(disabled=disable_forge, row=3)
        self.add_back_button(disabled=disabled)
        if self.forge_inventory is not None and not self.forge_inventory.empty:
            self.add_forge_status_button(current=self.forge_inventory, disabled=False)
            self.add_clear_forge_button(disabled=False)
        self.add_item(
            SelectGearSlot(
                EquipmentSlot.WEAPON,
                row=0,
                selected=(self.filter == EquipmentSlot.WEAPON),
                disabled=disabled,
            )
        )
        self.add_item(
            SelectGearSlot(
                EquipmentSlot.HEAD,
                row=0,
                selected=(self.filter == EquipmentSlot.HEAD),
                disabled=disabled,
            )
        )
        self.add_item(
            SelectGearSlot(
                EquipmentSlot.BODY,
                row=0,
                selected=(self.filter == EquipmentSlot.BODY),
                disabled=disabled,
            )
        )
        self.add_item(
            SelectGearSlot(
                EquipmentSlot.LEGS,
                row=0,
                selected=(self.filter == EquipmentSlot.LEGS),
                disabled=disabled,
            )
        )
        self.add_item(
            SelectGearSlot(
                EquipmentSlot.ACCESSORY,
                row=0,
                selected=(self.filter == EquipmentSlot.ACCESSORY),
                disabled=disabled,
            )
        )

    async def refresh_ui(
        self,
        gear_inventory: list[Gear] = None,
        currently_equipped: list[Gear] = None,
        scrap_balance: int = None,
        disabled: bool = False,
    ):
        if self.message is None:
            return

        if scrap_balance is not None:
            self.scrap_balance = scrap_balance

        if gear_inventory is not None:
            self.gear = gear_inventory

        if currently_equipped is not None:
            self.current = currently_equipped

        if None not in [self.scrap_balance, self.gear, self.current]:
            self.loaded = True

        self.guild_level = await self.controller.database.get_guild_level(self.guild_id)

        self.filter_items()
        self.current_page = min(self.current_page, (self.page_count - 1))

        start_offset = SelectGearHeadEmbed.ITEMS_PER_PAGE * self.current_page
        end_offset = min(
            (start_offset + SelectGearHeadEmbed.ITEMS_PER_PAGE),
            len(self.filtered_items),
        )
        self.display_items = self.filtered_items[start_offset:end_offset]

        self.selected = [
            gear for gear in self.gear if gear.id in [x.id for x in self.selected]
        ]

        self.forge_inventory = await self.forge_manager.get_forge_inventory(self.member)

        self.refresh_elements(disabled)

        embeds = []
        embeds.append(SelectGearHeadEmbed(self.member))

        if len(self.display_items) <= 0:
            empty_embed = discord.Embed(
                title="Empty", color=discord.Colour.light_grey()
            )
            self.embed_manager.add_text_bar(
                empty_embed, "", "Seems like there is nothing here."
            )
            empty_embed.set_thumbnail(url=self.controller.bot.user.display_avatar)
            embeds.append(empty_embed)

        for gear in self.display_items:
            equipped = False
            if gear.id in [gear.id for gear in self.current]:
                equipped = True

            character = await self.actor_manager.get_character(self.member)
            embed = await self.embed_manager.get_gear_embed(
                gear, character, equipped=equipped, show_locked_state=True
            )
            embeds.append(embed)

        await self.message.edit(embeds=embeds, view=self)

    async def set_selected(self, interaction: discord.Interaction, gear_ids: list[int]):
        await interaction.response.defer()
        self.selected = [gear for gear in self.gear if gear.id in gear_ids]
        await self.refresh_ui()

    async def add_to_forge(
        self,
        interaction: discord.Interaction,
    ):
        await interaction.response.defer(ephemeral=True)
        if len(self.selected) != 1:
            return
        selected = self.selected[0]
        event = UIEvent(
            UIEventType.FORGE_ADD_ITEM,
            (interaction, selected),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

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


class SelectButton(discord.ui.Button):

    def __init__(self, disabled: bool = True):

        super().__init__(
            label="Equip",
            style=discord.ButtonStyle.green,
            row=2,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: EquipmentSelectView = self.view

        if await view.interaction_check(interaction):
            await view.select_gear(interaction)


class Dropdown(discord.ui.Select):

    def __init__(
        self,
        gear: list[Gear],
        selected: list[Gear],
        equipped: list[Gear],
        disabled: bool = False,
    ):

        options = []
        available = copy.copy(gear)

        for piece in selected:
            if piece.id not in [item.id for item in gear]:
                available.append(piece)

        for item in available:
            name = item.name
            if name is None or name == "":
                name = item.base.slot.value
            else:
                if item.id in equipped:
                    name += " [EQ]"
                if item.locked:
                    name += " [🔒]"

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
                value=item.id,
                default=(item.id in [item.id for item in selected]),
            )
            options.append(option)

        max_values = len(available)

        super().__init__(
            placeholder="Select one or more pieces of equipment.",
            min_values=0,
            max_values=max_values,
            options=options,
            row=1,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: EquipmentSelectView = self.view

        if await view.interaction_check(interaction):
            await view.set_selected(interaction, [int(value) for value in self.values])
