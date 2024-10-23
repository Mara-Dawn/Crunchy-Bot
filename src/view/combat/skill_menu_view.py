import discord

from combat.actors import Character
from control.combat.combat_skill_manager import CombatSkillManager
from control.controller import Controller
from control.types import ControllerType
from events.types import UIEventType
from events.ui_event import UIEvent
from view.combat.elements import (
    ImplementsBalance,
    ImplementsMainMenu,
    MenuState,
)
from view.combat.embed import (
    SkillsHeadEmbed,
)
from view.view_menu import ViewMenu


class SkillMenuView(ViewMenu, ImplementsMainMenu, ImplementsBalance):

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
        self.state = MenuState.SKILLS
        self.limited = limited
        self.scrap_balance = scrap_balance
        self.loaded = False
        self.skill_manager: CombatSkillManager = self.controller.get_service(
            CombatSkillManager
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

        self.add_menu(self.state, self.limited, disabled)

        if self.limited:
            return

        self.add_scrap_balance_button(self.scrap_balance)
        self.add_item(SkillManageButton(disabled=disabled))
        self.add_item(SkillEquipButton(disabled=disabled))

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
        embed = SkillsHeadEmbed(self.character.member, is_owner=(not self.limited))
        embeds.append(embed)
        for skill in self.character.skills:
            skill_embed = (
                await self.skill_manager.get_skill_data(self.character, skill)
            ).get_embed()
            embeds.append(skill_embed)

        try:
            await self.message.edit(embeds=embeds, view=self)
        except (discord.NotFound, discord.HTTPException):
            self.controller.detach_view(self)

    async def set_state(self, state: MenuState, interaction: discord.Interaction):
        await interaction.response.defer()
        event = UIEvent(
            UIEventType.MAIN_MENU_STATE_CHANGE,
            (interaction, state, self.limited),
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

    async def open_skill_equip_view(self, interaction: discord.Interaction):
        await interaction.response.defer()
        event = UIEvent(
            UIEventType.SKILL_EQUIP_VIEW,
            interaction,
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def open_skill_manage_view(self, interaction: discord.Interaction):
        await interaction.response.defer()
        event = UIEvent(
            UIEventType.SKILL_MANAGE_VIEW,
            interaction,
            self.id,
        )
        await self.controller.dispatch_ui_event(event)


class SkillManageButton(discord.ui.Button):

    def __init__(self, disabled: bool = False):
        super().__init__(
            label="Manage Skill Inventory",
            style=discord.ButtonStyle.green,
            row=1,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: SkillMenuView = self.view

        if await view.interaction_check(interaction):
            await view.open_skill_manage_view(interaction)


class SkillEquipButton(discord.ui.Button):

    def __init__(self, disabled: bool = False):
        super().__init__(
            label="Quick Select",
            style=discord.ButtonStyle.green,
            row=1,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: SkillMenuView = self.view

        if await view.interaction_check(interaction):
            await view.open_skill_equip_view(interaction)
