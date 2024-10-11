import datetime

import discord
from discord.ext import commands

from combat.gear.droppable import Droppable
from combat.gear.types import EquipmentSlot
from config import Config
from control.combat.combat_gear_manager import CombatGearManager
from control.controller import Controller
from control.logger import BotLogger
from control.service import Service
from datalayer.database import Database
from events.bot_event import BotEvent
from events.inventory_event import InventoryEvent
from forge.forgable import Forgeable, ForgeInventory
from items.types import ItemType
from view.combat.forge_menu_view import ForgeMenuView


class ForgeManager(Service):

    def __init__(
        self,
        bot: commands.Bot,
        logger: BotLogger,
        database: Database,
        controller: Controller,
    ):
        super().__init__(bot, logger, database)
        self.controller = controller
        self.log_name = "Forge"

        self.gear_manager: CombatGearManager = self.controller.get_service(
            CombatGearManager
        )
        self.forge_cache: dict[discord.Member, ForgeInventory] = {}

    async def listen_for_event(self, event: BotEvent) -> str:
        pass

    async def get_forge_inventory(self, member: discord.Member) -> ForgeInventory:
        if member in self.forge_cache:
            return self.forge_cache[member]
        else:
            return None

    async def add_to_forge(
        self, member: discord.Member, item: Forgeable
    ) -> ForgeInventory:
        if member not in self.forge_cache:
            self.forge_cache[member] = ForgeInventory()

        if self.forge_cache[member].add(item):
            message = (
                f"{member.display_name} added {item.name} ({item.id}) to the forge."
            )
            self.logger.log(member.guild.id, message, self.log_name)

    async def remove_from_forge(
        self, member: discord.Member, item: Forgeable
    ) -> ForgeInventory:
        if member not in self.forge_cache:
            self.forge_cache[member] = ForgeInventory()

        if self.forge_cache[member].remove(item):
            message = (
                f"{member.display_name} removed {item.name} ({item.id}) from the forge."
            )
            self.logger.log(member.guild.id, message, self.log_name)

    async def clear_forge_inventory(self, member: discord.Member) -> ForgeInventory:
        if member not in self.forge_cache:
            return

        self.forge_cache[member].clear()
        message = f"{member.display_name} cleared the forge."
        self.logger.log(member.guild.id, message, self.log_name)

    async def use_scrap(
        self, member: discord.Member, slot: EquipmentSlot | None, level: int
    ) -> Droppable:
        guild_id = member.guild.id
        member_id = member.id

        scaling = 1
        if slot is not None:
            scaling = CombatGearManager.SLOT_SCALING[slot] * Config.SCRAP_FORGE_MULTI
        scrap_value = int(ForgeMenuView.SCRAP_ILVL_MAP[level] * scaling)

        user_items = await self.database.get_item_counts_by_user(
            guild_id, member_id, item_types=[ItemType.SCRAP]
        )
        scrap_balance = 0
        if ItemType.SCRAP in user_items:
            scrap_balance = user_items[ItemType.SCRAP]

        if scrap_balance < scrap_value:
            return None

        drop = await self.gear_manager.generate_drop(
            member_id, guild_id, level, gear_slot=slot
        )

        event = InventoryEvent(
            datetime.datetime.now(),
            guild_id,
            member_id,
            ItemType.SCRAP,
            -scrap_value,
        )
        await self.controller.dispatch_event(event)

        message = f"{member.display_name} Forge: [level {level}, slot {slot}] -> {drop.rarity.value} {drop.name} ({drop.id})"
        self.logger.log(guild_id, message, self.log_name)

        return drop
