import datetime

from combat.actors import Opponent
from combat.encounter import EncounterContext
from control.combat.enemy.enemy_controller import EnemyController
from events.bot_event import BotEvent
from events.encounter_event import EncounterEvent
from events.types import (
    EncounterEventType,
)


class BasicEnemyController(EnemyController):

    async def listen_for_event(self, event: BotEvent):
        pass

    async def on_defeat(self, context: EncounterContext, opponent: Opponent):
        encounter_event_type = EncounterEventType.ENEMY_DEFEAT
        embed = self.embed_manager.get_actor_defeated_embed(opponent)
        await self.discord.append_embed_to_round(context, embed)

        event = EncounterEvent(
            datetime.datetime.now(),
            context.encounter.guild_id,
            context.encounter.id,
            opponent.id,
            encounter_event_type,
        )
        await self.controller.dispatch_event(event)

    async def intro(self, encounter_id: int):
        pass
