from abc import ABC, abstractmethod

import discord


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
        self, interaction: discord.Interaction, scrap_all: bool = False
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


class ScrapAllButton(discord.ui.Button):

    def __init__(self, disabled: bool = False):
        super().__init__(
            label="Scrap All (non locked)",
            style=discord.ButtonStyle.red,
            row=3,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: ImplementsScrapping = self.view

        if await view.interaction_check(interaction):
            await view.scrap_selected(interaction, scrap_all=True)
