import discord
from combat.gear.gear import Gear
from combat.gear.types import GearSlot
from datalayer.database import Database
from discord.ext import commands
from events.types import UIEventType
from events.ui_event import UIEvent
from view.combat.equipment_select_view import EquipmentSelectView
from view.combat.equipment_view import EquipmentView

from control.combat.combat_actor_manager import CombatActorManager
from control.combat.combat_embed_manager import CombatEmbedManager
from control.combat.encounter_manager import EncounterManager
from control.controller import Controller
from control.event_manager import EventManager
from control.logger import BotLogger
from control.view.view_controller import ViewController


class EquipmentViewController(ViewController):

    def __init__(
        self,
        bot: commands.Bot,
        logger: BotLogger,
        database: Database,
        controller: Controller,
    ):
        super().__init__(bot, logger, database)
        self.controller = controller
        self.event_manager: EventManager = controller.get_service(EventManager)
        self.actor_manager: CombatActorManager = controller.get_service(
            CombatActorManager
        )
        self.encounter_manager: EncounterManager = controller.get_service(
            EncounterManager
        )
        self.embed_manager: CombatEmbedManager = controller.get_service(
            CombatEmbedManager
        )

    async def listen_for_ui_event(self, event: UIEvent):
        match event.type:
            case UIEventType.GEAR_OPEN_SECELT:
                interaction = event.payload[0]
                slot = event.payload[1]
                await self.open_gear_select(interaction, slot, event.view_id)
            case UIEventType.GEAR_OPEN_OVERVIEW:
                interaction = event.payload
                await self.open_gear_overview(interaction, event.view_id)
            case UIEventType.GEAR_EQUIP:
                interaction = event.payload[0]
                selected = event.payload[1]
                await self.equip_gear(interaction, selected, event.view_id)
            case UIEventType.GEAR_DISMANTLE:
                pass

    async def open_gear_select(
        self, interaction: discord.Interaction, slot: GearSlot, view_id: int
    ):
        guild_id = interaction.guild.id
        member_id = interaction.user.id
        gear_inventory = await self.database.get_user_armory(guild_id, member_id)

        view = EquipmentSelectView(self.controller, interaction, gear_inventory, slot)

        message = await interaction.original_response()
        await message.edit(view=view)
        view.set_message(message)
        await view.refresh_ui()
        self.controller.detach_view_by_id(view_id)

    async def open_gear_overview(self, interaction: discord.Interaction, view_id: int):
        character = await self.actor_manager.get_character(interaction.user)
        view = EquipmentView(self.controller, interaction, character)

        message = await interaction.original_response()
        await message.edit(view=view)
        view.set_message(message)
        await view.refresh_ui()
        self.controller.detach_view_by_id(view_id)

    async def equip_gear(
        self, interaction: discord.Interaction, selected: list[Gear], view_id: int
    ):
        guild_id = interaction.guild_id
        member_id = interaction.user.id

        if selected is None or len(selected) <= 0:
            return

        if len(selected) > 2:
            return

        if len(selected) >= 1:
            await self.database.update_user_equipment(guild_id, member_id, selected[0])

        if len(selected) == 2:
            # Accessory
            await self.database.update_user_equipment(
                guild_id, member_id, selected[1], acc_slot_2=True
            )

        await self.open_gear_overview(interaction, view_id)
