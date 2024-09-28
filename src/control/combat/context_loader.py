from discord.ext import commands

from combat.encounter import Encounter, EncounterContext
from control.combat.combat_actor_manager import CombatActorManager
from control.combat.combat_embed_manager import CombatEmbedManager
from control.combat.object_factory import ObjectFactory
from control.combat.status_effect_manager import CombatStatusEffectManager
from control.controller import Controller
from control.logger import BotLogger
from control.service import Service
from datalayer.database import Database
from events.bot_event import BotEvent
from events.combat_event import CombatEvent
from events.encounter_event import EncounterEvent
from events.status_effect_event import StatusEffectEvent
from events.types import EncounterEventType, EventType


class ContextLoader(Service):

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
        self.status_effect_manager: CombatStatusEffectManager = (
            self.controller.get_service(CombatStatusEffectManager)
        )
        self.factory: ObjectFactory = self.controller.get_service(ObjectFactory)
        self.log_name = "ContextLoader"

        self.context_cache: dict[int, EncounterContext] = {}

    async def listen_for_event(self, event: BotEvent):
        if not event.synchronized:
            return
        match event.type:
            case EventType.ENCOUNTER:
                encounter_event: EncounterEvent = event
                encounter_id = encounter_event.encounter_id

                context = await self.load_encounter_context(encounter_id)
                context = self.context_cache[encounter_id]
                context.add_event(event)
                for actor in context.actors:
                    await self.actor_manager.apply_event(actor, event)

                match encounter_event.encounter_event_type:
                    case EncounterEventType.END:
                        del self.context_cache[encounter_id]
                        return

            case EventType.COMBAT:
                event: CombatEvent = event
                encounter_id = event.encounter_id
                context = await self.load_encounter_context(encounter_id)
                context = self.context_cache[encounter_id]
                context.add_event(event)
                for actor in context.actors:
                    await self.actor_manager.apply_event(actor, event)

            case EventType.STATUS_EFFECT:
                event: StatusEffectEvent = event
                encounter_id = event.encounter_id
                context = await self.load_encounter_context(encounter_id)
                context = self.context_cache[encounter_id]
                context.add_event(event)
                for actor in context.actors:
                    await self.actor_manager.apply_event(actor, event)

    async def init_encounter_context(self, encounter: Encounter) -> EncounterContext:
        enemy = await self.factory.get_enemy(encounter.enemy_type)
        opponent = await self.actor_manager.get_opponent(
            enemy,
            encounter,
            [],
            [],
            {},
        )
        context = EncounterContext(
            encounter=encounter,
            opponent=opponent,
            encounter_events=[],
            combat_events=[],
            status_effects={},
            combatants=[],
            thread=None,
        )

        return context

    async def load_encounter_context(self, encounter_id) -> EncounterContext:
        if encounter_id in self.context_cache:
            return self.context_cache[encounter_id]

        encounter = await self.database.get_encounter_by_encounter_id(encounter_id)
        encounter_events = await self.database.get_encounter_events_by_encounter_id(
            encounter_id
        )
        combat_events = await self.database.get_combat_events_by_encounter_id(
            encounter_id
        )
        status_effects = await self.database.get_status_effects_by_encounter(
            encounter_id
        )
        thread_id = await self.database.get_encounter_thread(encounter_id)
        thread = self.bot.get_channel(encounter.channel_id).get_thread(thread_id)

        enemy = await self.factory.get_enemy(encounter.enemy_type)

        opponent = await self.actor_manager.get_opponent(
            enemy,
            encounter,
            encounter_events,
            combat_events,
            status_effects,
        )

        combatant_ids = await self.database.get_encounter_participants_by_encounter_id(
            encounter_id
        )

        guild = self.bot.get_guild(encounter.guild_id)
        members = [guild.get_member(id) for id in combatant_ids]

        combatants = []

        for member in members:

            combatant = await self.actor_manager.get_character(
                member, encounter_events, combat_events, status_effects
            )

            combatants.append(combatant)

        context = EncounterContext(
            encounter=encounter,
            opponent=opponent,
            encounter_events=encounter_events,
            combat_events=combat_events,
            status_effects=status_effects,
            combatants=combatants,
            thread=thread,
        )

        outcome = await self.status_effect_manager.handle_attribute_status_effects(
            context, context.opponent
        )
        context.opponent.round_modifier = outcome

        for combatant in context.combatants:
            outcome = await self.status_effect_manager.handle_attribute_status_effects(
                context, combatant
            )
            combatant.round_modifier = outcome

        self.context_cache[encounter_id] = context
        return self.context_cache[encounter_id]
