from typing import Any

import discord
from discord.ext import commands

from control.combat.combat_actor_manager import CombatActorManager
from control.combat.combat_embed_manager import CombatEmbedManager
from control.controller import Controller
from control.forge_manager import ForgeManager
from control.item_manager import ItemManager
from control.logger import BotLogger
from control.view.view_controller import ViewController
from datalayer.database import Database
from events.bot_event import BotEvent
from events.types import UIEventType
from events.ui_event import UIEvent
from forge.forgable import Forgeable
from items.types import ItemType
from view.combat.elements import MenuState
from view.combat.embed import (
    EquipmentHeadEmbed,
    SelectSkillHeadEmbed,
)
from view.combat.enchantment_view import EnchantmentView
from view.combat.forge_menu_view import ForgeMenuState, ForgeMenuView
from view.combat.gear_menu_view import GearMenuView
from view.combat.skill_menu_view import SkillMenuView
from view.inventory.inventory_menu_view import InventoryMenuView


class MainMenuViewController(ViewController):

    def __init__(
        self,
        bot: commands.Bot,
        logger: BotLogger,
        database: Database,
        controller: Controller,
    ):
        super().__init__(bot, logger, database)
        self.controller = controller
        self.actor_manager: CombatActorManager = controller.get_service(
            CombatActorManager
        )
        self.embed_manager: CombatEmbedManager = controller.get_service(
            CombatEmbedManager
        )
        self.item_manager: ItemManager = controller.get_service(ItemManager)
        self.forge_manager: ForgeManager = self.controller.get_service(ForgeManager)

        self.log_name = "MainMenu"

    async def listen_for_event(self, event: BotEvent) -> None:
        pass

    async def listen_for_ui_event(self, event: UIEvent):
        match event.type:
            case UIEventType.MAIN_MENU_STATE_CHANGE:
                interaction = event.payload[0]
                state = event.payload[1]
                limited = event.payload[2]
                extra = None
                if len(event.payload) == 4:
                    extra = event.payload[3]
                await self.main_menu_select(
                    interaction, state, limited, extra, event.view_id
                )
            case UIEventType.FORGE_ADD_ITEM:
                interaction = event.payload[0]
                forgeable = event.payload[1]
                await self.add_to_forge(interaction, forgeable, event.view_id)

    async def main_menu_select(
        self,
        interaction: discord.Interaction,
        state: MenuState,
        limited: bool,
        extra: Any,
        view_id: int,
    ):
        match state:
            case MenuState.GEAR:
                await self.open_gear_menu(interaction, limited, view_id)
            case MenuState.SKILLS:
                await self.open_skill_menu(interaction, limited, view_id)
            case MenuState.FORGE:
                await self.open_forge_menu(interaction, view_id, extra)
            case MenuState.INVENTORY:
                await self.open_inventory_menu(interaction, view_id)

    async def open_inventory_menu(
        self,
        interaction: discord.Interaction,
        view_id: int,
    ):
        guild_id = interaction.guild_id
        member_id = interaction.user.id

        inventory = await self.item_manager.get_user_inventory(guild_id, member_id)

        view = InventoryMenuView(self.controller, interaction, inventory)

        embeds = []
        loading_embed = discord.Embed(
            title="Loading Inventory", color=discord.Colour.light_grey()
        )
        self.embed_manager.add_text_bar(loading_embed, "", "Please Wait...")
        loading_embed.set_thumbnail(url=self.bot.user.display_avatar)
        embeds.append(loading_embed)

        message = await interaction.original_response()
        await message.edit(embeds=embeds, view=view, attachments=[])
        view.set_message(message)
        await view.refresh_ui()
        self.controller.detach_view_by_id(view_id)

    async def open_skill_menu(
        self,
        interaction: discord.Interaction,
        limited: bool,
        view_id: int,
    ):
        guild_id = interaction.guild_id
        member_id = interaction.user.id

        character = await self.actor_manager.get_character(interaction.user)

        user_items = await self.database.get_item_counts_by_user(
            guild_id, member_id, item_types=[ItemType.SCRAP]
        )
        scrap_balance = 0
        if ItemType.SCRAP in user_items:
            scrap_balance = user_items[ItemType.SCRAP]

        view = SkillMenuView(
            self.controller, interaction, character, scrap_balance, limited
        )

        embeds = []
        embeds.append(SelectSkillHeadEmbed(interaction.user))

        loading_embed = discord.Embed(
            title="Loading Skills", color=discord.Colour.light_grey()
        )
        self.embed_manager.add_text_bar(loading_embed, "", "Please Wait...")
        loading_embed.set_thumbnail(url=self.bot.user.display_avatar)
        embeds.append(loading_embed)

        message = await interaction.original_response()
        await message.edit(embeds=embeds, view=view, attachments=[])
        view.set_message(message)
        await view.refresh_ui()
        self.controller.detach_view_by_id(view_id)

    async def open_gear_menu(
        self,
        interaction: discord.Interaction,
        limited: bool,
        view_id: int,
    ):
        guild_id = interaction.guild_id
        member_id = interaction.user.id

        character = await self.actor_manager.get_character(interaction.user)

        user_items = await self.database.get_item_counts_by_user(
            guild_id, member_id, item_types=[ItemType.SCRAP]
        )
        scrap_balance = 0
        if ItemType.SCRAP in user_items:
            scrap_balance = user_items[ItemType.SCRAP]

        view = GearMenuView(
            self.controller, interaction, character, scrap_balance, limited
        )

        embeds = []
        embeds.append(EquipmentHeadEmbed(interaction.user))

        loading_embed = discord.Embed(
            title="Loading Gear", color=discord.Colour.light_grey()
        )
        self.embed_manager.add_text_bar(loading_embed, "", "Please Wait...")
        loading_embed.set_thumbnail(url=self.bot.user.display_avatar)
        embeds.append(loading_embed)

        message = await interaction.original_response()
        await message.edit(embeds=embeds, view=view, attachments=[])
        view.set_message(message)
        await view.refresh_ui()
        self.controller.detach_view_by_id(view_id)

    async def open_forge_menu(
        self,
        interaction: discord.Interaction,
        view_id: int,
        state: ForgeMenuState = None,
    ):
        guild_id = interaction.guild_id
        member_id = interaction.user.id

        if state is None:
            state = ForgeMenuState.OVERVIEW

        character = await self.actor_manager.get_character(interaction.user)

        user_items = await self.database.get_item_counts_by_user(
            guild_id, member_id, item_types=[ItemType.SCRAP]
        )
        scrap_balance = 0
        if ItemType.SCRAP in user_items:
            scrap_balance = user_items[ItemType.SCRAP]

        forge_level = await self.controller.database.get_forge_level(guild_id)

        view = ForgeMenuView(
            self.controller, interaction, character, scrap_balance, forge_level, state
        )

        message = await interaction.original_response()
        await message.edit(view=view, attachments=[])
        view.set_message(message)
        await view.refresh_ui()
        self.controller.detach_view_by_id(view_id)

    async def add_to_forge(
        self, interaction: discord.Interaction, forgeable: Forgeable, view_id: int
    ):
        await self.forge_manager.add_to_forge(interaction.user, forgeable)

        view: EnchantmentView = self.controller.get_view(view_id)
        await view.refresh_ui()
