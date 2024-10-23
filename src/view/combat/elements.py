from abc import ABC, abstractmethod
from enum import Enum

import discord

from combat.types import UnlockableFeature
from config import Config
from forge.forgable import ForgeInventory
from view.view_menu import ViewMenu


class MenuState(str, Enum):
    GEAR = "Gear"
    SKILLS = "Skills"
    FORGE = "Forge"
    INVENTORY = "Inventory"


# MAIN MENU


class ImplementsMainMenu(ABC):

    @abstractmethod
    async def set_state(self, state: MenuState, interaction: discord.Interaction):
        pass

    def add_menu(
        self, current: MenuState, limited: bool = False, disabled: bool = False
    ):
        for state in MenuState:
            if limited and state in [MenuState.FORGE, MenuState.INVENTORY]:
                continue
            selected = current == state
            self.add_item(MenuButton(state=state, selected=selected, disabled=disabled))


class MenuButton(discord.ui.Button):

    def __init__(self, state: MenuState, selected: bool, disabled: bool = True):
        color = discord.ButtonStyle.grey

        label = state.value
        self.state = state
        if selected:
            label = f">{label}<"
            disabled = True

        super().__init__(label=label, style=color, disabled=disabled, row=0)

    async def callback(self, interaction: discord.Interaction):
        view: ImplementsMainMenu = self.view
        await view.set_state(self.state, interaction)


# PAGE NAVIGATION


class ImplementsPages(ABC):

    @abstractmethod
    async def flip_page(self, interaction: discord.Interaction, right: bool = False):
        pass

    def add_page_button(
        self, label: str, right: bool, disabled: bool = False, row: int = 2
    ):
        self.add_item(PageButton(label=label, right=right, disabled=disabled, row=row))

    def add_current_page_button(self, label: str, row: int = 2):
        self.add_item(CurrentPageButton(label=label, row=row))


class PageButton(discord.ui.Button):

    def __init__(self, label: str, right: bool, disabled: bool = False, row: int = 2):
        self.right = right
        super().__init__(
            label=label, style=discord.ButtonStyle.grey, row=row, disabled=disabled
        )

    async def callback(self, interaction: discord.Interaction):
        view: ImplementsPages = self.view

        if await view.interaction_check(interaction):
            await view.flip_page(interaction, self.right)


class CurrentPageButton(discord.ui.Button):

    def __init__(self, label: str, row: int = 2):
        super().__init__(
            label=label, style=discord.ButtonStyle.grey, row=row, disabled=True
        )


# BALANCE DISPLAY


class ImplementsBalance(ABC):

    def __init__(self):
        self.guild_level: int = None

    @abstractmethod
    async def open_shop(self, interaction: discord.Interaction):
        pass

    def add_scrap_balance_button(self, balance: int, row: int = 0):
        shop_unlocked = (
            self.guild_level >= Config.UNLOCK_LEVELS[UnlockableFeature.FORGE_SHOP]
        )
        self.add_item(
            ScrapBalanceButton(balance=balance, row=row, link_shop=shop_unlocked)
        )

    def add_beans_balance_button(self, balance: int, row: int = 0):
        shop_unlocked = self.guild_level >= Config.UNLOCK_LEVELS[UnlockableFeature.SHOP]
        self.add_item(
            BeansBalanceButton(balance=balance, row=row, link_shop=shop_unlocked)
        )


class ScrapBalanceButton(discord.ui.Button):

    def __init__(self, balance: int, row: int = 0, link_shop: bool = False):
        self.balance = balance
        self.link_shop = link_shop
        super().__init__(
            label=f"⚙️{balance}", style=discord.ButtonStyle.blurple, row=row
        )

    async def callback(self, interaction: discord.Interaction):
        view: ImplementsBalance = self.view

        if await view.interaction_check(interaction):
            if not self.link_shop:
                await interaction.response.defer()
                return
            await view.open_shop(interaction)


class BeansBalanceButton(discord.ui.Button):

    def __init__(self, balance: int, row: int = 0, link_shop: bool = False):
        self.balance = balance
        self.link_shop = link_shop
        super().__init__(
            label=f"🅱️{balance}", style=discord.ButtonStyle.blurple, row=row
        )

    async def callback(self, interaction: discord.Interaction):
        view: ImplementsBalance = self.view

        if await view.interaction_check(interaction):
            if not self.link_shop:
                await interaction.response.defer()
                return
            await view.open_shop(interaction)


# BACK BUTTON


class ImplementsBack(ABC):

    @abstractmethod
    async def go_back(
        self,
        interaction: discord.Interaction,
    ):
        pass

    def add_back_button(self, disabled: bool = False, row: int = 4):
        self.add_item(BackButton(disabled=disabled, row=row))


class BackButton(discord.ui.Button):

    def __init__(self, disabled: bool = False, row: int = 4):
        super().__init__(
            label="Back",
            style=discord.ButtonStyle.gray,
            row=row,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: ImplementsBack = self.view

        if await view.interaction_check(interaction):
            await view.go_back(interaction)


# GEAR LOCKING


class ImplementsLocking(ABC):

    @abstractmethod
    async def lock_selected(
        self,
        interaction: discord.Interaction,
    ):
        pass

    @abstractmethod
    async def unlock_selected(
        self,
        interaction: discord.Interaction,
    ):
        pass

    def add_lock_button(self, row: int = 3, disabled: bool = False):
        self.add_item(LockButton(disabled=disabled, row=row))

    def add_unlock_button(self, row: int = 3, disabled: bool = False):
        self.add_item(UnlockButton(disabled=disabled, row=row))


class LockButton(discord.ui.Button):

    def __init__(self, row: int = 3, disabled: bool = False):
        super().__init__(
            label="Lock",
            style=discord.ButtonStyle.gray,
            row=row,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: ImplementsLocking = self.view

        if await view.interaction_check(interaction):
            await view.lock_selected(interaction)


class UnlockButton(discord.ui.Button):

    def __init__(self, row: int = 3, disabled: bool = False):
        super().__init__(
            label="Unlock",
            style=discord.ButtonStyle.gray,
            row=row,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: ImplementsLocking = self.view

        if await view.interaction_check(interaction):
            await view.unlock_selected(interaction)


# SCRAPPING


class ImplementsScrapping(ABC):

    @abstractmethod
    async def scrap_selected(
        self,
        interaction: discord.Interaction,
        scrap_all: bool = False,
        amount: int | None = None,
        scrap_until: bool = False,
    ):
        pass

    def add_scrap_selected_button(self, row: int = 3, disabled: bool = False):
        self.add_item(ScrapSelectedButton(disabled=disabled, row=row))

    def add_scrap_amount_button(self, row: int = 3, disabled: bool = False):
        self.add_item(ScrapAmountButton(disabled=disabled, row=row))

    def add_scrap_all_button(self, row: int = 3, disabled: bool = False):
        self.add_item(ScrapAllButton(disabled=disabled, row=row))


class ScrapSelectedButton(discord.ui.Button):

    def __init__(self, row: int = 3, disabled: bool = False):
        super().__init__(
            label="Scrap",
            style=discord.ButtonStyle.red,
            row=row,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: ImplementsScrapping = self.view

        if await view.interaction_check(interaction):
            await view.scrap_selected(interaction)


class ScrapAmountButton(discord.ui.Button):

    def __init__(self, row: int = 3, disabled: bool = False):
        super().__init__(
            label="Scrap Amount",
            style=discord.ButtonStyle.red,
            row=row,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: ImplementsScrapping = self.view

        if await view.interaction_check(interaction):
            await interaction.response.send_modal(ScrapAmountModal(self.view))


class ScrapAmountModal(discord.ui.Modal):

    def __init__(self, view: ViewMenu):
        super().__init__(title="Specify how much you want to scrap.")
        self.view = view

        self.amount = discord.ui.TextInput(
            label="Specify an amount to Scrap:",
            placeholder="Scrap amount",
            required=False,
        )
        self.add_item(self.amount)
        self.amount_left = discord.ui.TextInput(
            label="OR scrap all until you have this many left:",
            placeholder="scrap until amount left",
            required=False,
        )
        self.add_item(self.amount_left)

    async def on_submit(self, interaction: discord.Interaction):
        scrap_amount_str = self.amount.value
        scrap_until_str = self.amount_left.value

        if len(scrap_amount_str) == 0 and len(scrap_until_str) == 0:
            await interaction.followup.send(
                "Please specify either a scrap amount or a scrap until value.",
                ephemeral=True,
            )
            return

        if len(scrap_amount_str) > 0 and len(scrap_until_str) > 0:
            await interaction.followup.send(
                "You can only specify either scrap amount or scrap until, not both.",
                ephemeral=True,
            )
            return

        scrap_until = False

        amount = scrap_amount_str
        if len(amount) == 0:
            amount = scrap_until_str
            scrap_until = True

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

        await self.view.scrap_selected(
            interaction, amount=amount, scrap_until=scrap_until
        )


class ScrapAllButton(discord.ui.Button):

    def __init__(self, row: int = 3, disabled: bool = False):
        super().__init__(
            label="Scrap All",
            style=discord.ButtonStyle.red,
            row=row,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: ImplementsScrapping = self.view

        if await view.interaction_check(interaction):
            await view.scrap_selected(interaction, scrap_all=True)


# CRAFTING


class ImplementsCrafting(ABC):

    def __init__(self):
        self.guild_level: int = None

    @abstractmethod
    async def craft_selected(
        self,
        interaction: discord.Interaction,
    ):
        pass

    def add_craft_button(self, row: int = 3, disabled: bool = True):
        if (
            self.guild_level >= Config.UNLOCK_LEVELS[UnlockableFeature.ENCHANTMENTS]
            or self.guild_level >= Config.UNLOCK_LEVELS[UnlockableFeature.CRAFTING]
        ):
            self.add_item(CraftSelectedButton(disabled=disabled, row=row))


class CraftSelectedButton(discord.ui.Button):

    def __init__(self, row: int = 3, disabled: bool = True):

        super().__init__(
            label="Enchant",
            style=discord.ButtonStyle.gray,
            row=row,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: ImplementsCrafting = self.view

        if await view.interaction_check(interaction):
            await view.craft_selected(interaction)


# FORGE


class ImplementsForging(ABC):

    def __init__(self):
        self.guild_level: int = None

    @abstractmethod
    async def add_to_forge(
        self,
        interaction: discord.Interaction,
    ):
        pass

    @abstractmethod
    async def open_forge(
        self,
        interaction: discord.Interaction,
    ):
        pass

    @abstractmethod
    async def clear_forge(
        self,
        interaction: discord.Interaction,
    ):
        pass

    def add_add_to_forge_button(self, disabled: bool = False, row: int = 4):
        if self.guild_level >= Config.UNLOCK_LEVELS[UnlockableFeature.FORGE_RECIPES]:
            self.add_item(AddToForgeButton(disabled=disabled, row=row))

    def add_clear_forge_button(self, disabled: bool = False, row: int = 4):
        if self.guild_level >= Config.UNLOCK_LEVELS[UnlockableFeature.FORGE_RECIPES]:
            self.add_item(ClearForgeButton(disabled=disabled, row=row))

    def add_forge_status_button(
        self,
        current: ForgeInventory,
        row: int = 4,
        disabled: bool = False,
    ):
        if self.guild_level >= Config.UNLOCK_LEVELS[UnlockableFeature.FORGE_RECIPES]:
            self.add_item(
                ForgeStatusButton(current=current, disabled=disabled, row=row)
            )


class AddToForgeButton(discord.ui.Button):

    def __init__(self, disabled: bool = False, row: int = 4):
        super().__init__(
            label="Add to Forge",
            style=discord.ButtonStyle.green,
            row=row,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: ImplementsBack = self.view

        if await view.interaction_check(interaction):
            await view.add_to_forge(interaction)


class ClearForgeButton(discord.ui.Button):

    def __init__(self, disabled: bool = False, row: int = 4):
        super().__init__(
            label="Clear Forge",
            style=discord.ButtonStyle.red,
            row=row,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: ImplementsBack = self.view

        if await view.interaction_check(interaction):
            await view.clear_forge(interaction)


class ForgeStatusButton(discord.ui.Button):

    def __init__(
        self,
        current: ForgeInventory,
        row: int = 4,
        disabled: bool = False,
    ):
        forgeables = []
        for forgeable in current.items:
            if forgeable is not None:
                forgeables.append(forgeable.name)

        label = "/".join(forgeables)

        super().__init__(
            label=f"Forge: {label}",
            style=discord.ButtonStyle.blurple,
            row=row,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: ImplementsBalance = self.view

        if await view.interaction_check(interaction):
            await view.open_forge(interaction)
