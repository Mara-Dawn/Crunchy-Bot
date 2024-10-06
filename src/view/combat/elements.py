from abc import ABC, abstractmethod

import discord

from view.view_menu import ViewMenu


class ImplementsPages(ABC):

    @abstractmethod
    async def flip_page(self, interaction: discord.Interaction, right: bool = False):
        pass

    @abstractmethod
    async def open_shop(self, interaction: discord.Interaction):
        pass


class ImplementsBack(ABC):

    @abstractmethod
    async def go_back(
        self,
        interaction: discord.Interaction,
    ):
        pass


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


class ImplementsCrafting(ABC):

    @abstractmethod
    async def craft_selected(
        self,
        interaction: discord.Interaction,
    ):
        pass


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


class ScrapBalanceButton(discord.ui.Button):

    def __init__(self, balance: int, row: int = 2):
        self.balance = balance
        super().__init__(
            label=f"⚙️{balance}", style=discord.ButtonStyle.blurple, row=row
        )

    async def callback(self, interaction: discord.Interaction):
        view: ImplementsPages = self.view

        if await view.interaction_check(interaction):
            await view.open_shop(interaction)


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


class LockButton(discord.ui.Button):

    def __init__(self, row: int = 3, disabled: bool = False):
        super().__init__(
            label="Lock Selected",
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
            label="Unlock Selected",
            style=discord.ButtonStyle.gray,
            row=row,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: ImplementsLocking = self.view

        if await view.interaction_check(interaction):
            await view.unlock_selected(interaction)


class ScrapSelectedButton(discord.ui.Button):

    def __init__(self, row: int = 3, disabled: bool = False):
        super().__init__(
            label="Scrap Selected",
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
            label="Scrap Selected Amount",
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

    def __init__(self, disabled: bool = False):
        super().__init__(
            label="Scrap All Selected",
            style=discord.ButtonStyle.red,
            row=3,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: ImplementsScrapping = self.view

        if await view.interaction_check(interaction):
            await view.scrap_selected(interaction, scrap_all=True)


class CraftSelectedButton(discord.ui.Button):

    def __init__(self, disabled: bool = True):

        super().__init__(
            label="Craft",
            style=discord.ButtonStyle.blurple,
            row=3,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: ImplementsCrafting = self.view

        if await view.interaction_check(interaction):
            await view.craft_selected(interaction)
