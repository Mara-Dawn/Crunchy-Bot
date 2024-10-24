import datetime
import secrets

from combat.encounter import Encounter, EncounterContext
from combat.enemies.types import EnemyType
from combat.engine.states.state import State
from combat.engine.types import StateType
from control.controller import Controller
from events.bot_event import BotEvent
from events.encounter_event import EncounterEvent
from events.types import EncounterEventType
from view.combat.engage_view import EnemyEngageView


class InitialState(State):

    def __init__(self, controller: Controller, context: EncounterContext):
        super().__init__(controller, context)
        self.state_type: StateType = StateType.INITIAL
        self.next_state: StateType = StateType.WAITING

    async def startup(self):
        encounter = self.context.encounter
        view = EnemyEngageView(self.controller, self.context)
        guild = self.controller.bot.get_guild(encounter.guild_id)
        combat_channels = await self.settings_manager.get_combat_channels(
            self.context.encounter.guild_id
        )
        channel = guild.get_channel(secrets.choice(combat_channels))

        spawn_pings = ""
        ping_role = await self.settings_manager.get_spawn_ping_role(guild.id)
        if ping_role is not None:
            spawn_pings += f"<@&{ping_role}>"

        guild_level = await self.database.get_guild_level(encounter.guild_id)
        if encounter.enemy_level == guild_level:
            max_lvl_ping_role = await self.settings_manager.get_max_lvl_spawn_ping_role(
                guild.id
            )
            if max_lvl_ping_role is not None:
                spawn_pings += f"<@&{max_lvl_ping_role}>"

        message = await self.discord.send_message(
            channel, content=spawn_pings, view=view
        )

        encounter.message_id = message.id
        encounter.channel_id = message.channel.id
        if self.context.owner_id is not None:
            encounter.owner_id = self.context.owner_id

        encounter_id = await self.database.log_encounter(encounter)

        view.set_message(message)
        encounter.id = encounter_id

        custom_img = await self.embed_manager.get_custom_image(encounter)
        if custom_img is not None:
            self.context.opponent.image_url = custom_img.link
            self.context.opponent.name = (
                f"{self.context.opponent.enemy.name} ({custom_img.description})"
            )

        self.context.encounter = encounter
        self.context_loader.context_cache[encounter_id] = self.context

        if encounter.enemy_type == EnemyType.MIMIC:
            mock_enemy = await self.actor_manager.get_random_enemy(
                encounter.enemy_level, exclude=[EnemyType.MIMIC]
            )
            mock_encounter = Encounter(
                guild.id, mock_enemy.type, encounter.enemy_level, encounter.max_hp
            )
            mock_context = await self.context_loader.init_encounter_context(
                mock_encounter
            )
            embed = await self.embed_manager.get_spawn_embed(mock_context)
            await view.refresh_ui(embed=embed, mock_context=mock_context)
        else:
            embed = await self.embed_manager.get_spawn_embed(self.context)
            await view.refresh_ui(embed=embed)

        event = EncounterEvent(
            datetime.datetime.now(),
            guild.id,
            encounter_id,
            self.bot.user.id,
            EncounterEventType.SPAWN,
        )
        await self.controller.dispatch_event(event)

        self.done = True

    async def handle(self, event: BotEvent) -> bool:
        return False

    async def update(self):
        if not self.done:
            await self.startup()
