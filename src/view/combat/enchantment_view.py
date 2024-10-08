import contextlib
from dataclasses import dataclass

import discord

from combat.actors import Character
from combat.enchantments.enchantment import Enchantment, GearEnchantment
from combat.enchantments.types import EnchantmentEffect, EnchantmentType
from combat.gear.gear import Gear
from combat.gear.types import EquipmentSlot, Rarity
from control.combat.combat_embed_manager import CombatEmbedManager
from control.combat.combat_enchantment_manager import CombatEnchantmentManager
from control.controller import Controller
from control.types import ControllerType
from events.types import UIEventType
from events.ui_event import UIEvent
from view.combat.elements import (
    BackButton,
    CurrentPageButton,
    ImplementsBack,
    ImplementsLocking,
    ImplementsPages,
    ImplementsScrapping,
    PageButton,
    ScrapAllButton,
    ScrapAmountButton,
    ScrapBalanceButton,
)
from view.combat.embed import (
    EnchantmentHeadEmbed,
    EnchantmentSpacerEmbed,
)
from view.combat.equipment_view import EquipmentViewState
from view.view_menu import ViewMenu


@dataclass
class EnchantmentGroup:
    enchantment_type: EnchantmentType
    rarity: Rarity
    enchantments: list[Enchantment]
    enchantment_data: GearEnchantment = None

    @property
    def amount(self) -> int:
        return len(self.enchantments)

    @property
    def enchantment(self) -> Enchantment:
        return self.enchantments[0]

    @property
    def id(self) -> int:
        return self.enchantments[0].id

    def add_enchantment_data(self, data: GearEnchantment):
        self.enchantment_data = data


class EnchantmentView(
    ViewMenu, ImplementsPages, ImplementsBack, ImplementsLocking, ImplementsScrapping
):

    def __init__(
        self,
        controller: Controller,
        interaction: discord.Interaction,
        character: Character,
        enchantment_inventory: list[Enchantment],
        scrap_balance: int,
        gear: Gear | None,
    ):
        super().__init__(timeout=300)
        self.controller = controller
        self.guild_name = interaction.guild.name
        self.member_id = interaction.user.id
        self.member = interaction.user
        self.guild_id = interaction.guild_id
        self.enchantments = enchantment_inventory
        self.character = character
        self.scrap_balance = scrap_balance
        self.enchantment_info: dict[EnchantmentType, str] = {}
        self.gear = gear

        self.current_page = 0
        self.selected: list[EnchantmentGroup] = []
        self.selected_filter_type: EnchantmentType = None

        self.enchantment_manager: CombatEnchantmentManager = (
            self.controller.get_service(CombatEnchantmentManager)
        )

        self.filter = EquipmentSlot.ANY
        self.filtered_items: list[EnchantmentGroup] = []
        self.display_items = []
        self.display_enchantments = []
        self.item_count = 0
        self.page_count = 1
        self.filter_items()
        self.message = None
        self.loaded = False

        self.controller_type = ControllerType.EQUIPMENT
        self.controller.register_view(self)
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

    def group_enchantments(self):
        enchantment_stock: dict[EnchantmentType, dict[Rarity, list[Enchantment]]] = {}
        sorted_enchantments: list[Enchantment] = sorted(
            self.enchantments, key=lambda x: x.id
        )

        enchantment_info = {}

        for enchantment in sorted_enchantments:
            enchantment_type = enchantment.base_enchantment.enchantment_type
            rarity = enchantment.rarity

            if (
                enchantment.base_enchantment.base_enchantment_type
                not in enchantment_info
                and enchantment.base_enchantment.enchantment_effect
                == EnchantmentEffect.EFFECT
            ):
                enchantment_info[enchantment.base_enchantment.base_enchantment_type] = (
                    enchantment.name
                )

            if (
                EnchantmentType.CRAFTING not in enchantment_info
                and enchantment.base_enchantment.enchantment_effect
                == EnchantmentEffect.CRAFTING
            ):
                enchantment_info[EnchantmentType.CRAFTING] = "Crafting"

            if enchantment_type not in enchantment_stock:
                enchantment_stock[enchantment_type] = {}

            if rarity not in enchantment_stock[enchantment_type]:
                enchantment_stock[enchantment_type][rarity] = []

            enchantment_stock[enchantment_type][rarity].append(enchantment)

        self.enchantment_info = enchantment_info

        enchantment_groups = []
        for enchantment_type, stock in enchantment_stock.items():
            for rarity, enchantments in stock.items():
                enchantment_groups.append(
                    EnchantmentGroup(enchantment_type, rarity, enchantments)
                )

        self.filtered_items = enchantment_groups

    def filter_items(self):
        self.group_enchantments()

        if self.gear is not None:
            self.filtered_items = [
                x
                for x in self.filtered_items
                if x.enchantment.slot in [EquipmentSlot.ANY, self.gear.slot]
            ]

        if self.selected_filter_type is not None:
            filtered = []
            for enchantment_group in self.filtered_items:
                if self.selected_filter_type == EnchantmentType.CRAFTING:
                    if (
                        enchantment_group.enchantment.base_enchantment.enchantment_effect
                        == EnchantmentEffect.CRAFTING
                    ):
                        filtered.append(enchantment_group)
                else:
                    if (
                        enchantment_group.enchantment.base_enchantment.base_enchantment_type
                        == self.selected_filter_type
                    ):
                        filtered.append(enchantment_group)

            self.filtered_items = filtered

        self.item_count = len(self.filtered_items)
        self.page_count = int(self.item_count / EnchantmentHeadEmbed.ITEMS_PER_PAGE) + (
            self.item_count % EnchantmentHeadEmbed.ITEMS_PER_PAGE > 0
        )
        self.page_count = max(self.page_count, 1)

        self.filtered_items = sorted(
            self.filtered_items,
            key=lambda x: (
                Enchantment.EFFECT_SORT_MAP[
                    x.enchantment.base_enchantment.enchantment_effect
                ],
                x.enchantment.base_enchantment.base_enchantment_type.value,
                Enchantment.RARITY_SORT_MAP[x.rarity],
            ),
            reverse=True,
        )

    async def flip_page(self, interaction: discord.Interaction, right: bool = False):
        await interaction.response.defer()
        self.current_page = (self.current_page + (1 if right else -1)) % self.page_count
        self.selected = []
        await self.refresh_ui()

    async def open_shop(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        event = UIEvent(
            UIEventType.FORGE_OPEN_SHOP,
            interaction,
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def apply_enchantment(self, interaction: discord.Interaction):
        await interaction.response.defer()

        selected = [group.enchantment for group in self.selected]

        event = UIEvent(
            UIEventType.ENCHANTMENTS_APPLY,
            (interaction, self.gear, selected),
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

        if len(self.selected) != 1:
            return

        selected = self.selected[0]

        scrappable = selected.enchantments

        if amount is not None:
            if not scrap_until:
                scrappable = scrappable[:amount]
            else:
                total = len(scrappable) - amount
                scrappable = scrappable[:total]

        self.selected = []

        event = UIEvent(
            UIEventType.GEAR_DISMANTLE,
            (interaction, scrappable, False, self.filter),
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
        selected = [item for item in self.selected]
        self.selected = []
        event = UIEvent(
            UIEventType.GEAR_UNLOCK,
            (interaction, selected),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def go_back(
        self,
        interaction: discord.Interaction,
    ):
        await interaction.response.defer()
        event = UIEvent(
            UIEventType.GEAR_OPEN_OVERVIEW,
            (interaction, EquipmentViewState.GEAR),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def refresh_elements(self, disabled: bool = False):
        page_display = f"Page {self.current_page + 1}/{self.page_count}"

        if not self.loaded:
            disabled = True

        disable_apply = disabled
        disable_dismantle = disabled
        for enchantment_group in self.selected:
            if enchantment_group is None:
                continue
            if (
                enchantment_group.enchantment.id is None
                or enchantment_group.enchantment.id < 0
            ):
                # Default Gear
                disable_dismantle = True
                break

        if self.gear is None:
            disable_apply = True

        if len(self.selected) <= 0:
            disable_apply = True
            disable_dismantle = True

        self.clear_items()

        if len(self.selected) > 1:
            disable_apply = True
        if len(self.enchantment_info) > 0:
            self.add_item(
                EnchantmentTypeDropdown(
                    self.enchantment_info,
                    self.selected_filter_type,
                )
            )
        if len(self.display_enchantments) > 0:
            self.add_item(
                Dropdown(
                    self.display_enchantments,
                    self.selected,
                    row=1,
                    min_values=0,
                    max_values=1,
                )
            )

        self.add_item(PageButton("<", False))
        self.add_item(ApplyButton(disabled=disable_apply))
        self.add_item(PageButton(">", True))
        self.add_item(CurrentPageButton(page_display))
        self.add_item(ScrapBalanceButton(self.scrap_balance))
        self.add_item(ScrapAllButton(disabled=disable_dismantle))
        self.add_item(ScrapAmountButton(disabled=disable_dismantle))
        self.add_item(BackButton())

    async def refresh_ui(
        self,
        character: Character = None,
        enchantment_inventory: list[Enchantment] = None,
        scrap_balance: int = None,
        disabled: bool = False,
        no_embeds: bool = False,
    ):
        if self.message is None:
            return

        if character is not None:
            self.character = character

        if enchantment_inventory is not None:
            self.enchantments = enchantment_inventory
            self.filter_items()
            self.current_page = min(self.current_page, (self.page_count - 1))

        if scrap_balance is not None:
            self.scrap_balance = scrap_balance

        if self.selected is None or len(self.selected) <= 0:
            disabled = True

        if no_embeds:
            await self.refresh_elements(disabled)
            await self.message.edit(view=self)
            return

        start_offset = EnchantmentHeadEmbed.ITEMS_PER_PAGE * self.current_page
        end_offset = min(
            (start_offset + EnchantmentHeadEmbed.ITEMS_PER_PAGE),
            len(self.filtered_items),
        )
        self.display_items = self.filtered_items[start_offset:end_offset]

        if None not in [self.scrap_balance, self.enchantments]:
            self.loaded = True

        self.display_enchantments = []
        embeds = []

        embeds.append(EnchantmentHeadEmbed(self.member))

        if self.gear is not None:
            gear_embed = await self.embed_manager.get_gear_embed(
                self.gear, self.character
            )
            embeds.append(gear_embed)

        embeds.append(EnchantmentSpacerEmbed(self.member, self.gear))

        for enchantment_group in self.display_items:

            enchantment_data = await self.enchantment_manager.get_gear_enchantment(
                self.character, enchantment_group.enchantment
            )

            enchantment_group.add_enchantment_data(enchantment_data)
            self.display_enchantments.append(enchantment_group)

            enchantment_embed = enchantment_data.get_embed(
                show_full_data=True,
                amount=enchantment_group.amount,
            )
            embeds.append(enchantment_embed)

        for enchantment_group in self.selected:
            if enchantment_group.enchantment_data is None:
                enchantment_data = await self.enchantment_manager.get_gear_enchantment(
                    self.character, enchantment_group.skill
                )

                enchantment_group.add_enchantment_data(enchantment_data)

        await self.refresh_elements(disabled)

        if len(self.display_items) <= 0:
            empty_embed = discord.Embed(
                title="Empty", color=discord.Colour.light_grey()
            )
            self.embed_manager.add_text_bar(
                empty_embed, "", "Seems like there is nothing here."
            )
            empty_embed.set_thumbnail(url=self.controller.bot.user.display_avatar)
            embeds.append(empty_embed)

        await self.message.edit(embeds=embeds, view=self)

    async def set_filter_type(
        self,
        interaction: discord.Interaction,
        selected_type: EnchantmentType,
    ):
        await interaction.response.defer()
        self.selected_filter_type = selected_type
        self.filter_items()
        self.current_page = min(self.current_page, (self.page_count - 1))
        await self.refresh_ui()

    async def set_selected(
        self,
        interaction: discord.Interaction,
        enchantment_ids: list[int],
    ):
        await interaction.response.defer()

        self.selected = [
            group for group in self.filtered_items if group.id in enchantment_ids
        ]

        await self.refresh_ui()

    async def on_timeout(self):
        with contextlib.suppress(discord.HTTPException):
            await self.message.edit(view=None)
        self.controller.detach_view(self)


class ApplyButton(discord.ui.Button):

    def __init__(self, disabled: bool = True, row: int = 2):

        super().__init__(
            label="Apply",
            style=discord.ButtonStyle.green,
            row=row,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: EnchantmentView = self.view

        if await view.interaction_check(interaction):
            await view.apply_enchantment(interaction)


class EnchantmentTypeDropdown(discord.ui.Select):

    def __init__(
        self,
        enchantment_selection: dict[EnchantmentType, str],
        selected: EnchantmentType,
        disabled: bool = False,
        row: int = 0,
    ):
        self.row = row
        options = []

        sorted_enchantment_types = sorted(
            enchantment_selection, key=lambda x: enchantment_selection[x]
        )

        for enchantment_type in sorted_enchantment_types:

            option = discord.SelectOption(
                label=enchantment_selection[enchantment_type],
                value=enchantment_type.value,
                default=enchantment_type == selected,
            )
            options.append(option)

        placeholder = "Filter Enchantments"

        super().__init__(
            placeholder=placeholder,
            min_values=0,
            max_values=1,
            options=options,
            row=row,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: EnchantmentView = self.view

        if await view.interaction_check(interaction):
            value = EnchantmentType(self.values[0]) if len(self.values) > 0 else None
            await view.set_filter_type(interaction, value)


class Dropdown(discord.ui.Select):

    def __init__(
        self,
        enchantment_data: list[EnchantmentGroup],
        selected_data: list[EnchantmentGroup],
        disabled: bool = False,
        row: int = 0,
        min_values: int = 1,
        max_values: int = 1,
    ):
        self.row = row
        options = []
        default = False

        available = enchantment_data

        if (
            len(selected_data) == 1
            and selected_data[0] is not None
            and selected_data[0].id not in [x.id for x in available]
        ):
            available.append(selected_data[0])

        max_values = min(max_values, len(available))

        for group in available:
            data = group.enchantment_data
            enchantment = group.enchantment

            name = enchantment.name
            name_prefix = f"[{enchantment.rarity.value}] "
            name_suffix = ""

            if name is None or name == "":
                name = enchantment.base.slot.value

            label = f"{name_prefix}{name}{name_suffix}"
            description = []
            if (
                enchantment.base_enchantment.enchantment_effect
                == EnchantmentEffect.EFFECT
            ):
                description.append(f"MIN: {data.min_roll}")
                description.append(f"MAX: {data.max_roll}")
            description.append(f"CNT: {group.amount}")
            description = " | ".join(description)
            description = (
                (description[:95] + "..") if len(description) > 95 else description
            )

            if enchantment.id is not None and enchantment.id < 0:
                label = enchantment.name
                description = ""

            default = group.id in [x.id for x in selected_data if x is not None]

            option = discord.SelectOption(
                label=label,
                description=description,
                value=(
                    enchantment.id
                    if enchantment is not None and enchantment.id is not None
                    else 0
                ),
                default=default,
            )
            options.append(option)

        placeholder = "Select an Enchantment."

        super().__init__(
            placeholder=placeholder,
            min_values=min_values,
            max_values=max_values,
            options=options,
            row=row,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: EnchantmentView = self.view

        if await view.interaction_check(interaction):
            await view.set_selected(interaction, [int(value) for value in self.values])
