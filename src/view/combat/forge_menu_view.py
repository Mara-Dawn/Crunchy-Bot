import discord

from combat.actors import Character
from combat.gear.types import (
    EquipmentSlot,
    Rarity,
)
from config import Config
from control.combat.combat_gear_manager import CombatGearManager
from control.controller import Controller
from control.types import ControllerType
from events.types import UIEventType
from events.ui_event import UIEvent
from view.combat.elements import (
    ImplementsBalance,
    ImplementsMainMenu,
    MenuState,
    ScrapBalanceButton,
)
from view.combat.embed import (
    ForgeEmbed,
)
from view.view_menu import ViewMenu


class ForgeMenuView(ViewMenu, ImplementsMainMenu, ImplementsBalance):

    SCRAP_ILVL_MAP = {
        1: 15,
        2: 30,
        3: 60,
        4: 100,
        5: 150,
        6: 200,
        7: 250,
    }

    def __init__(
        self,
        controller: Controller,
        interaction: discord.Interaction,
        character: Character,
        scrap_balance: int,
        forge_level: int,
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

        self.forge_level = forge_level
        self.max_rarity = Rarity.COMMON
        for rarity, level in CombatGearManager.MIN_RARITY_LVL.items():
            if level <= self.forge_level:
                self.max_rarity = rarity
            else:
                break

        self.forge_options = {
            level: scrap
            for level, scrap in self.SCRAP_ILVL_MAP.items()
            if level <= self.forge_level
        }
        self.max_forge_level = max(self.forge_options.keys())
        self.selected: int = self.max_forge_level
        self.selected_slot: EquipmentSlot = None

        self.controller_type = ControllerType.EQUIPMENT
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

        self.add_menu(self.state, False, disabled)
        self.add_item(ScrapBalanceButton(self.scrap_balance))

        self.add_item(ForgeDropdown(self.forge_options, self.selected))
        self.add_item(SlotDropdown(self.selected_slot, disabled=disabled))
        scaling = 1
        if self.selected_slot is not None:
            scaling = (
                CombatGearManager.SLOT_SCALING[self.selected_slot]
                * Config.SCRAP_FORGE_MULTI
            )
        total = int(self.SCRAP_ILVL_MAP[self.selected] * scaling)
        self.add_item(ForgeUseButton(total))
        self.add_item(ForgeShopButton())

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

        self.refresh_elements(disabled=disabled)
        embeds = []
        embed = ForgeEmbed(
            self.member,
            self.forge_level,
            self.max_rarity,
        )
        embeds.append(embed)

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

    async def set_selected_slot(
        self, interaction: discord.Interaction, slot: EquipmentSlot
    ):
        await interaction.response.defer()
        self.selected_slot = slot
        await self.refresh_ui()

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


class ForgeShopButton(discord.ui.Button):

    def __init__(self, disabled: bool = False):
        super().__init__(
            label="Secret Shop",
            style=discord.ButtonStyle.green,
            row=3,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: ForgeMenuView = self.view

        if await view.interaction_check(interaction):
            await view.open_shop(interaction)
