import contextlib

import discord
from combat.gear.gear import Gear
from combat.gear.types import GearModifierType, GearSlot
from control.combat.combat_embed_manager import CombatEmbedManager
from control.controller import Controller
from control.types import ControllerType
from events.types import UIEventType
from events.ui_event import UIEvent
from view.combat.embed import SelectGearHeadEmbed
from view.view_menu import ViewMenu


class EquipmentSelectView(ViewMenu):

    def __init__(
        self,
        controller: Controller,
        interaction: discord.Interaction,
        gear_inventory: list[Gear],
        currently_equipped: list[Gear],
        scrap_balance: int,
        slot: GearSlot,
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

        self.selected = [
            gear
            for gear in self.filtered_items
            if gear.id in [gear.id for gear in self.current]
        ]

        self.controller_type = ControllerType.EQUIPMENT
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
                not x.locked,
                x.level,
                Gear.RARITY_SORT_MAP[x.rarity],
            ),
            reverse=True,
        )

    async def flip_page(self, interaction: discord.Interaction, right: bool = False):
        await interaction.response.defer()
        self.current_page = (self.current_page + (1 if right else -1)) % self.page_count
        self.selected = []
        await self.refresh_ui()

    async def select_gear(self, interaction: discord.Interaction):
        await interaction.response.defer()
        event = UIEvent(
            UIEventType.GEAR_EQUIP,
            (interaction, self.selected),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def dismantle_gear(
        self, interaction: discord.Interaction, scrap_all: bool = False
    ):
        await interaction.response.defer()
        event = UIEvent(
            UIEventType.GEAR_DISMANTLE,
            (interaction, self.selected, scrap_all),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def lock_selected(
        self,
        interaction: discord.Interaction,
    ):
        await interaction.response.defer()
        event = UIEvent(
            UIEventType.GEAR_LOCK,
            (interaction, self.selected),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def unlock_selected(
        self,
        interaction: discord.Interaction,
    ):
        await interaction.response.defer()
        event = UIEvent(
            UIEventType.GEAR_UNLOCK,
            (interaction, self.selected),
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
            interaction,
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    def refresh_elements(self, disabled: bool = False):
        page_display = f"Page {self.current_page + 1}/{self.page_count}"

        max_values = 1
        if self.filter == GearSlot.ACCESSORY:
            max_values = 2

        disable_equip = disabled
        if len(self.selected) > max_values:
            disable_equip = True

        disable_dismantle = disabled
        for selected_gear in self.selected:
            if selected_gear.id in [gear.id for gear in self.current]:
                disable_dismantle = True

            if selected_gear.id < 0:
                # Default Gear
                disable_dismantle = True

        self.clear_items()
        if len(self.display_items) > 0:
            self.add_item(Dropdown(self.display_items, self.selected))
        self.add_item(PageButton("<", False))
        self.add_item(SelectButton(disable_equip))
        self.add_item(PageButton(">", True))
        self.add_item(CurrentPageButton(page_display))
        self.add_item(ScrapBalanceButton(self.scrap_balance))
        self.add_item(ScrapSelectedButton(disable_dismantle))
        self.add_item(LockButton(disabled))
        self.add_item(UnlockButton(disabled))
        self.add_item(BackButton())

    async def refresh_ui(
        self,
        gear_inventory: list[Gear] = None,
        scrap_balance: int = None,
        disabled: bool = False,
    ):
        if self.message is None:
            return

        if scrap_balance is not None:
            self.scrap_balance = scrap_balance

        if gear_inventory is not None:
            self.gear = gear_inventory
            self.filter_items()
            self.current_page = min(self.current_page, (self.page_count - 1))

        if self.selected is None or len(self.selected) <= 0:
            disabled = True

        start_offset = SelectGearHeadEmbed.ITEMS_PER_PAGE * self.current_page
        end_offset = min(
            (start_offset + SelectGearHeadEmbed.ITEMS_PER_PAGE),
            len(self.filtered_items),
        )
        self.display_items = self.filtered_items[start_offset:end_offset]

        self.refresh_elements(disabled)

        refresh_selected = []
        for selected in self.selected:
            if selected in self.display_items:
                refresh_selected.append(selected)
        self.selected = refresh_selected

        embeds = []
        files = {}
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

            embeds.append(gear.get_embed(equipped=equipped, show_locked_state=True))
            file_path = f"./{gear.base.image_path}{gear.base.image}"
            if file_path not in files:
                file = discord.File(
                    file_path,
                    gear.base.image,
                )
                files[file_path] = file

        files = list(files.values())

        await self.message.edit(embeds=embeds, attachments=files, view=self)
        # try:
        #     await self.message.edit(embeds=embeds, attachments=files, view=self)
        # except (discord.NotFound, discord.HTTPException):
        #     self.controller.detach_view(self)

    async def set_selected(self, interaction: discord.Interaction, gear_ids: list[int]):
        await interaction.response.defer()
        self.selected = [gear for gear in self.gear if gear.id in gear_ids]
        await self.refresh_ui()

    async def on_timeout(self):
        with contextlib.suppress(discord.HTTPException):
            await self.message.edit(view=None)
        self.controller.detach_view(self)


class SelectButton(discord.ui.Button):

    def __init__(self, disabled: bool = True):

        super().__init__(
            label="Equip",
            style=discord.ButtonStyle.green,
            row=1,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: EquipmentSelectView = self.view

        if await view.interaction_check(interaction):
            await view.select_gear(interaction)


class ScrapSelectedButton(discord.ui.Button):

    def __init__(self, disabled: bool = False):
        super().__init__(
            label="Scrap Selected",
            style=discord.ButtonStyle.red,
            row=2,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: EquipmentSelectView = self.view

        if await view.interaction_check(interaction):
            await view.dismantle_gear(interaction)


class ScrapAllButton(discord.ui.Button):

    def __init__(self, disabled: bool = False):
        super().__init__(
            label="Scrap All (non locked)",
            style=discord.ButtonStyle.red,
            row=2,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: EquipmentSelectView = self.view

        if await view.interaction_check(interaction):
            await view.dismantle_gear(interaction, scrap_all=True)


class LockButton(discord.ui.Button):

    def __init__(self, disabled: bool = False):
        super().__init__(
            label="Lock Selected",
            style=discord.ButtonStyle.gray,
            row=2,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: EquipmentSelectView = self.view

        if await view.interaction_check(interaction):
            await view.lock_selected(interaction)


class UnlockButton(discord.ui.Button):

    def __init__(self, disabled: bool = False):
        super().__init__(
            label="Unlock Selected",
            style=discord.ButtonStyle.gray,
            row=2,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: EquipmentSelectView = self.view

        if await view.interaction_check(interaction):
            await view.unlock_selected(interaction)


class BackButton(discord.ui.Button):

    def __init__(self, disabled: bool = False):
        super().__init__(
            label="Back",
            style=discord.ButtonStyle.gray,
            row=2,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: EquipmentSelectView = self.view

        if await view.interaction_check(interaction):
            await view.go_back(interaction)


class Dropdown(discord.ui.Select):

    def __init__(
        self,
        gear: list[Gear],
        selected: list[Gear],
        disabled: bool = False,
    ):

        options = []

        for item in gear:
            name = item.name
            if name is None or name == "":
                name = item.base.slot.value

            description = [f"ILVL: {item.level}"]
            for modifier_type, value in item.modifiers.items():
                label = GearModifierType.short_label(modifier_type)
                value = GearModifierType.display_value(modifier_type, value)
                description.append(f"{label}: {value}")

            description = " | ".join(description)
            description = (
                (description[:95] + "..") if len(description) > 95 else description
            )
            label = f"{name} [{item.rarity.value}] "

            option = discord.SelectOption(
                label=label,
                description=description,
                value=item.id,
                default=(item in selected),
            )
            options.append(option)

        max_values = min(SelectGearHeadEmbed.ITEMS_PER_PAGE, len(gear))

        super().__init__(
            placeholder="Select a piece of equipment.",
            min_values=1,
            max_values=max_values,
            options=options,
            row=0,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: EquipmentSelectView = self.view

        if await view.interaction_check(interaction):
            await view.set_selected(interaction, [int(value) for value in self.values])


class PageButton(discord.ui.Button):

    def __init__(self, label: str, right: bool, disabled: bool = False):
        self.right = right
        super().__init__(
            label=label, style=discord.ButtonStyle.grey, row=1, disabled=disabled
        )

    async def callback(self, interaction: discord.Interaction):
        view: EquipmentSelectView = self.view

        if await view.interaction_check(interaction):
            await view.flip_page(interaction, self.right)


class CurrentPageButton(discord.ui.Button):

    def __init__(self, label: str):
        super().__init__(
            label=label, style=discord.ButtonStyle.grey, row=1, disabled=True
        )


class ScrapBalanceButton(discord.ui.Button):

    def __init__(self, balance: int):
        self.balance = balance
        super().__init__(label=f"⚙️{balance}", style=discord.ButtonStyle.blurple, row=1)

    async def callback(self, interaction: discord.Interaction):
        view: EquipmentSelectView = self.view

        if await view.interaction_check(interaction):
            await interaction.response.defer(ephemeral=True)
