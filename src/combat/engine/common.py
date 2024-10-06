import datetime
import importlib

from discord.ext import commands

from combat.encounter import EncounterContext
from control.combat.combat_actor_manager import CombatActorManager
from control.combat.combat_embed_manager import CombatEmbedManager
from control.combat.discord_manager import DiscordManager
from control.combat.effect_manager import CombatEffectManager
from control.combat.object_factory import ObjectFactory
from control.controller import Controller
from control.logger import BotLogger
from control.service import Service
from control.types import ControllerModuleMap
from datalayer.database import Database
from events.bot_event import BotEvent
from events.encounter_event import EncounterEvent
from events.types import EncounterEventType, UIEventType
from events.ui_event import UIEvent
from view.combat.approve_view import ApproveMemberView


class CommonService(Service):

    def __init__(
        self,
        bot: commands.Bot,
        logger: BotLogger,
        database: Database,
        controller: Controller,
    ):
        super().__init__(bot, logger, database)
        self.controller = controller
        self.actor_manager: CombatActorManager = self.controller.get_service(
            CombatActorManager
        )
        self.embed_manager: CombatEmbedManager = self.controller.get_service(
            CombatEmbedManager
        )
        self.effect_manager: CombatEffectManager = self.controller.get_service(
            CombatEffectManager
        )
        self.discord: DiscordManager = self.controller.get_service(DiscordManager)
        self.factory: ObjectFactory = self.controller.get_service(ObjectFactory)
        self.log_name = "Combat Engine"

    async def listen_for_event(self, event: BotEvent):
        pass

    async def check_actor_defeat(self, context: EncounterContext):
        for actor in context.initiative:
            if actor.defeated:
                continue

            health = actor.current_hp

            if health <= 0:
                if actor.is_enemy:
                    controller_type = actor.enemy.controller
                    controller_class = getattr(
                        importlib.import_module(
                            "control.combat.enemy."
                            + ControllerModuleMap.get_module(controller_type)
                        ),
                        controller_type,
                    )
                    enemy_controller = self.controller.get_service(controller_class)

                    await enemy_controller.on_defeat(context, actor)
                    continue

                outcome = await self.effect_manager.on_death(context, actor)
                if outcome.embed_data is not None:
                    await self.discord.append_embeds_to_round(
                        context, actor, outcome.embed_data
                    )
                if outcome.value == 1:
                    continue

                encounter_event_type = EncounterEventType.MEMBER_DEFEAT
                embed = self.embed_manager.get_actor_defeated_embed(actor)
                await self.discord.append_embed_to_round(context, embed)

                event = EncounterEvent(
                    datetime.datetime.now(),
                    context.encounter.guild_id,
                    context.encounter.id,
                    actor.id,
                    encounter_event_type,
                )
                await self.controller.dispatch_event(event)

                if actor in context.active_combatants:
                    context.active_combatants.remove(actor)
                if actor not in context.defeated_combatants:
                    context.defeated_combatants.append(actor)
        return False

    async def add_member_to_encounter(self, member_id: int, context: EncounterContext):
        encounter = context.encounter
        thread = context.thread
        additional_message = await self.apply_late_join_penalty(member_id, context)

        enemy = await self.factory.get_enemy(encounter.enemy_type)

        user = self.bot.get_guild(encounter.guild_id).get_member(member_id)
        await thread.add_user(user)

        embed = self.embed_manager.get_actor_join_embed(
            user, additional_message=additional_message
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        await self.discord.send_message(thread, content="", embed=embed)

        combatant = await self.actor_manager.get_character(
            user,
            context.encounter_events,
            context.combat_events,
            context.status_effects,
        )
        context.combatants.append(combatant)

        encounters = await self.database.get_encounter_participants(encounter.guild_id)
        enemy = await self.factory.get_enemy(encounter.enemy_type)
        max_encounter_size = enemy.max_players
        if encounter.id not in encounters:
            # TODO why does this happen
            return
        if len(encounters[encounter.id]) >= max_encounter_size and not enemy.is_boss:
            event = UIEvent(UIEventType.COMBAT_FULL, encounter.id)
            await self.controller.dispatch_ui_event(event)

        # context.refresh_initiative()

    async def add_member_join_request(self, member_id: int, context: EncounterContext):
        encounter = context.encounter
        thread = context.thread

        user = self.bot.get_guild(encounter.guild_id).get_member(member_id)
        owner = self.bot.get_guild(encounter.guild_id).get_member(encounter.owner_id)
        await thread.add_user(user)

        embed = self.embed_manager.get_actor_join_request_embed(user, owner)
        embed.set_thumbnail(url=user.display_avatar.url)

        view = ApproveMemberView(self.controller, encounter, user, owner)
        message = await self.discord.send_message(
            thread, content="", embed=embed, view=view
        )
        view.set_message(message)

    async def apply_late_join_penalty(
        self, member_id: int, context: EncounterContext
    ) -> str:
        encounter = context.encounter

        combat_progress = context.opponent.current_hp / context.opponent.max_hp

        if combat_progress >= 0.5:
            return ""

        if combat_progress < 0.5 and combat_progress > 0.25:
            additional_message = (
                "You joined late, so you will only get 50% of the loot."
            )
            event = EncounterEvent(
                datetime.datetime.now(),
                encounter.guild_id,
                encounter.id,
                member_id,
                EncounterEventType.PENALTY50,
            )
            await self.controller.dispatch_event(event)
        elif combat_progress <= 0.25:
            additional_message = (
                "You joined late, so you will only get 25% of the loot."
            )
            event = EncounterEvent(
                datetime.datetime.now(),
                encounter.guild_id,
                encounter.id,
                member_id,
                EncounterEventType.PENALTY75,
            )
            await self.controller.dispatch_event(event)

        return additional_message

    async def force_end(self, context: EncounterContext):
        await self.discord.delete_previous_combat_info(context.thread)
        embed = await self.embed_manager.get_combat_failed_embed(context)
        await self.discord.send_message(context.thread, content="", embed=embed)
