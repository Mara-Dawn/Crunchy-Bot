import asyncio
import contextlib
import datetime

import discord
from discord.ext import commands

from combat.actors import Character
from combat.encounter import Encounter, EncounterContext
from combat.skills.skill import CharacterSkill
from config import Config
from control.combat.combat_embed_manager import CombatEmbedManager
from control.combat.context_loader import ContextLoader
from control.combat.encounter_manager import EncounterManager
from control.combat.object_factory import ObjectFactory
from control.controller import Controller
from control.event_manager import EventManager
from control.item_manager import ItemManager
from control.logger import BotLogger
from control.settings_manager import SettingsManager
from control.view.view_controller import ViewController
from datalayer.database import Database
from events.bot_event import BotEvent
from events.encounter_event import EncounterEvent
from events.types import EncounterEventType, EventType, UIEventType
from events.ui_event import UIEvent
from items.item import Item


class CombatViewController(ViewController):

    def __init__(
        self,
        bot: commands.Bot,
        logger: BotLogger,
        database: Database,
        controller: Controller,
    ):
        super().__init__(bot, logger, database)
        self.controller = controller
        self.settings_manager: SettingsManager = self.controller.get_service(
            SettingsManager
        )
        self.event_manager: EventManager = controller.get_service(EventManager)
        self.item_manager: ItemManager = controller.get_service(ItemManager)
        self.encounter_manager: EncounterManager = controller.get_service(
            EncounterManager
        )
        self.embed_manager: CombatEmbedManager = controller.get_service(
            CombatEmbedManager
        )
        self.context_loader: ContextLoader = self.controller.get_service(ContextLoader)
        self.factory: ObjectFactory = self.controller.get_service(ObjectFactory)
        self.join_queue = asyncio.Queue()
        self.leave_queue = asyncio.Queue()
        self.join_worker = asyncio.create_task(self.join_request_worker())
        self.leave_worker = asyncio.create_task(self.leave_request_worker())

    async def join_request_worker(self):
        while True:
            interaction = await self.join_queue.get()

            guild_id = interaction.guild_id
            member_id = interaction.user.id

            beans_role = await self.settings_manager.get_beans_role(guild_id)
            if beans_role is not None and beans_role not in [
                role.id for role in interaction.user.roles
            ]:
                role_name = interaction.guild.get_role(beans_role).name
                await interaction.followup.send(
                    f"You can only use this feature if you have the role `{role_name}`.",
                    ephemeral=True,
                )
                continue

            message = await interaction.original_response()
            encounter = await self.database.get_encounter_by_message_id(
                guild_id, message.id
            )

            encounters = await self.database.get_encounter_participants(guild_id)
            encounters_filtered = (
                await self.database.get_inactive_encounter_participants(guild_id)
            )

            already_involved = False
            for _, participants in encounters.items():
                if member_id in participants:

                    await interaction.followup.send(
                        "You are already involved in a currently active encounter.",
                        ephemeral=True,
                    )
                    already_involved = True
                    break

            if already_involved:
                continue

            if encounter.id not in encounters:
                await interaction.followup.send(
                    "This encounter has already concluded.",
                    ephemeral=True,
                )
                continue

            enemy = await self.factory.get_enemy(encounter.enemy_type)
            max_encounter_size = enemy.max_players

            active_participants = len(encounters[encounter.id])
            if encounter.id in encounters_filtered:
                active_participants -= len(encounters_filtered[encounter.id])

            if active_participants >= max_encounter_size:
                await interaction.followup.send(
                    "This encounter is already full.",
                    ephemeral=True,
                )
                continue

            event_type = EncounterEventType.MEMBER_ENGAGE
            # event_type = EncounterEventType.MEMBER_REQUEST_JOIN

            if enemy.is_boss:
                event_type = EncounterEventType.MEMBER_REQUEST_JOIN

            event = EncounterEvent(
                datetime.datetime.now(),
                guild_id,
                encounter.id,
                member_id,
                event_type,
            )
            await self.controller.dispatch_event(event)

            self.join_queue.task_done()

    async def leave_request_worker(self):
        while True:
            interaction = await self.leave_queue.get()

            guild_id = interaction.guild_id
            member_id = interaction.user.id
            encounters = await self.database.get_encounter_participants(guild_id)

            is_involved = False
            encounter = None
            for encounter_id, participants in encounters.items():
                if member_id in participants:
                    encounter = await self.database.get_encounter_by_encounter_id(
                        encounter_id
                    )
                    is_involved = True
                    break

            if not is_involved or encounter is None:
                await interaction.followup.send(
                    "You are not involved in any encounter.",
                    ephemeral=True,
                )
                continue

            context = await self.context_loader.load_encounter_context(encounter.id)

            event_type = EncounterEventType.MEMBER_DISENGAGE

            if context.initiated:
                event_type = EncounterEventType.MEMBER_LEAVING
                if member_id == context.current_actor.id:
                    await interaction.followup.send(
                        "Please finish your turn before you leave.",
                        ephemeral=True,
                    )
                    continue

                actor = context.get_actor_by_id(member_id)
                if actor.defeated:
                    await interaction.followup.send(
                        "You are defeated and cannot leave.",
                        ephemeral=True,
                    )
                    continue

            already_left = False

            for event in context.encounter_events:
                if event.member_id == member_id and event.encounter_event_type in [
                    EncounterEventType.MEMBER_LEAVING,
                ]:
                    already_left = True
                    break

            if already_left:
                await interaction.followup.send(
                    "You already left this encounter.",
                    ephemeral=True,
                )
                continue

            character = context.get_actor_by_id(member_id)

            embed = self.embed_manager.get_member_out_embed(character, event_type, "")
            await context.thread.send("", embed=embed)

            event = EncounterEvent(
                datetime.datetime.now(),
                guild_id,
                encounter.id,
                member_id,
                event_type,
            )
            await self.controller.dispatch_event(event)

            self.leave_queue.task_done()

    async def listen_for_event(self, event: BotEvent) -> None:
        encounter_id = None
        match event.type:
            case EventType.ENCOUNTER:
                if not event.synchronized:
                    return
                event: EncounterEvent = event
                encounter_id = event.encounter_id

        if encounter_id is not None and event.encounter_event_type in [
            EncounterEventType.INITIATE,
        ]:
            ui_event = UIEvent(
                UIEventType.ENCOUNTER_INITIATED,
                encounter_id,
            )
            await self.controller.dispatch_ui_event(ui_event)

        if encounter_id is not None and event.encounter_event_type in [
            EncounterEventType.MEMBER_ENGAGE,
            EncounterEventType.MEMBER_OUT,
            EncounterEventType.MEMBER_DISENGAGE,
            EncounterEventType.END,
            EncounterEventType.INITIATE,
        ]:
            done = event.encounter_event_type == EncounterEventType.END
            started = event.encounter_event_type == EncounterEventType.INITIATE
            await self.update_encounter_message(encounter_id, started, done)

    async def listen_for_ui_event(self, event: UIEvent):
        match event.type:
            case UIEventType.COMBAT_ENGAGE:
                interaction = event.payload
                try:
                    exception = self.join_worker.exception()
                    if exception is not None:
                        self.join_worker = asyncio.create_task(
                            self.join_request_worker()
                        )
                        raise exception
                except asyncio.CancelledError:
                    pass
                    self.join_worker = asyncio.create_task(self.join_request_worker())
                except asyncio.InvalidStateError:
                    pass
                await self.join_queue.put(interaction)
            case UIEventType.COMBAT_LEAVE:
                interaction = event.payload
                try:
                    exception = self.leave_worker.exception()
                    if exception is not None:
                        self.leave_worker = asyncio.create_task(
                            self.leave_request_worker()
                        )
                        raise exception
                except asyncio.CancelledError:
                    pass
                    self.leave_worker = asyncio.create_task(self.leave_request_worker())
                except asyncio.InvalidStateError:
                    pass
                await self.leave_queue.put(interaction)
            case UIEventType.COMBAT_APPROVE:
                interaction = event.payload[0]
                encounter = event.payload[1]
                member = event.payload[2]
                await self.approve_player(interaction, encounter, member, event.view_id)
            case UIEventType.COMBAT_USE_SKILL:
                interaction = event.payload[0]
                skill_data = event.payload[1]
                character = event.payload[2]
                context = event.payload[3]
                await self.player_action(
                    interaction, skill_data, character, context, event.view_id
                )
            case UIEventType.COMBAT_TIMEOUT:
                character = event.payload[0]
                context = event.payload[1]
                await self.player_timeout(character, context)
            case UIEventType.COMBAT_INITIATE:
                encounter = event.payload
                await self.initiate_encounter(encounter)
            case UIEventType.CLAIM_SPECIAL_DROP:
                interaction = event.payload[0]
                encounter_id = event.payload[1]
                item = event.payload[2]
                await self.handle_special_drop_claim(
                    interaction, encounter_id, item, event.view_id
                )

    async def initiate_encounter(self, encounter: Encounter):
        context = await self.context_loader.load_encounter_context(encounter.id)
        if context.initiated:
            return
        event = EncounterEvent(
            datetime.datetime.now(),
            encounter.guild_id,
            encounter.id,
            self.bot.user.id,
            EncounterEventType.INITIATE,
        )
        await self.controller.dispatch_event(event)

    async def update_encounter_message(
        self, encounter_id: int, started: bool, done: bool
    ):
        encounter = await self.database.get_encounter_by_encounter_id(encounter_id)
        embed = await self.embed_manager.get_spawn_embed(encounter, done=done)
        event = UIEvent(
            UIEventType.COMBAT_ENGAGE_UPDATE, (encounter_id, embed, started, done)
        )
        await self.controller.dispatch_ui_event(event)

    async def approve_player(
        self,
        interaction: discord.Interaction,
        encounter: Encounter,
        member: discord.Member,
        view_id: int,
    ):
        message = await interaction.original_response()
        guild_id = interaction.guild_id

        encounters = await self.database.get_encounter_participants(guild_id)
        encounters_filtered = await self.database.get_inactive_encounter_participants(
            guild_id
        )

        for _, participants in encounters.items():
            if member.id in participants:

                await interaction.followup.send(
                    "Player is already involved in a currently active encounter.",
                    ephemeral=True,
                )
                return

        if encounter.id not in encounters:
            await interaction.followup.send(
                "This encounter has already concluded.",
                ephemeral=True,
            )
            return

        enemy = await self.factory.get_enemy(encounter.enemy_type)
        max_encounter_size = enemy.max_players

        active_participants = len(encounters[encounter.id])
        if encounter.id in encounters_filtered:
            active_participants -= len(encounters_filtered[encounter.id])

        if active_participants >= max_encounter_size:
            await interaction.followup.send(
                "This encounter is already full.",
                ephemeral=True,
            )
            return

        event = EncounterEvent(
            datetime.datetime.now(),
            guild_id,
            encounter.id,
            member.id,
            EncounterEventType.MEMBER_ENGAGE,
        )
        await self.controller.dispatch_event(event)

        await message.delete()
        self.controller.detach_view_by_id(view_id)

    async def player_action(
        self,
        interaction: discord.Interaction,
        skill_data: CharacterSkill,
        character: Character,
        context: EncounterContext,
        view_id: int,
    ):
        event = UIEvent(UIEventType.STOP_INTERACTIONS, None, view_id)
        await self.controller.dispatch_ui_event(event)

        with contextlib.suppress(discord.NotFound):
            message = await interaction.original_response()
            await message.delete()

            await self.encounter_manager.combatant_turn(context, character, skill_data)

            self.controller.detach_view_by_id(view_id)

    async def player_timeout(
        self,
        character: Character,
        context: EncounterContext,
    ):
        await self.encounter_manager.combatant_timeout(context, character)

    async def handle_special_drop_claim(
        self,
        interaction: discord.Interaction,
        encounter_id: int,
        item: Item,
        view_id: int,
    ):
        event = UIEvent(UIEventType.STOP_INTERACTIONS, None, view_id)
        await self.controller.dispatch_ui_event(event)

        context = await self.context_loader.load_encounter_context(encounter_id)

        guild_id = interaction.guild_id
        member_id = interaction.user.id

        actor = context.get_actor_by_id(member_id)

        if actor is None or actor.is_out:
            await interaction.followup.send(
                "You are not part of this encounter.",
                ephemeral=True,
            )
            event = UIEvent(UIEventType.RESUME_INTERACTIONS, None, view_id)
            await self.controller.dispatch_ui_event(event)
            return

        title = "Special Item"
        description = f"This item was claimed by: \n <@{member_id}>"
        embed = discord.Embed(
            title=title, description=description, color=discord.Colour.purple()
        )

        item.add_to_embed(
            self.bot,
            embed,
            Config.SHOP_ITEM_MAX_WIDTH,
            count=1,
            show_price=False,
        )

        if item.image_url is not None:
            embed.set_image(url=item.image_url)

        await self.item_manager.give_item(guild_id, member_id, item)
        await interaction.edit_original_response(embed=embed, view=None)

        self.controller.detach_view_by_id(view_id)
