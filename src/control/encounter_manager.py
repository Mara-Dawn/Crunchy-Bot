import datetime
import random

import discord
from combat.actors import Character, Opponent
from combat.encounter import Encounter, EncounterContext
from combat.enemies import *  # noqa: F403
from combat.enemies.enemy import Enemy
from combat.enemies.types import EnemyType
from combat.skills import HeavyAttack, NormalAttack
from combat.skills.types import SkillEffect
from datalayer.database import Database
from discord.ext import commands
from events.bot_event import BotEvent
from events.combat_event import CombatEvent
from events.encounter_event import EncounterEvent
from events.types import CombatEventType, EncounterEventType, EventType
from view.combat.combat_turn_view import CombatTurnView
from view.combat.engage_view import EnemyEngageView

from control.controller import Controller
from control.item_manager import ItemManager
from control.logger import BotLogger
from control.service import Service
from control.settings_manager import SettingsManager


class EncounterManager(Service):

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
        self.item_manager: ItemManager = self.controller.get_service(ItemManager)
        self.log_name = "Encounter"

    async def listen_for_event(self, event: BotEvent):
        match event.type:
            case EventType.ENCOUNTER:
                encounter_event: EncounterEvent = event
                match encounter_event.encounter_event_type:
                    case EncounterEventType.MEMBER_ENGAGE:
                        await self.add_member_to_encounter(
                            encounter_event.encounter_id, encounter_event.member_id
                        )

            case EventType.COMBAT:
                combat_event: CombatEvent = event
                if not event.synchronized:
                    return
                await self.refresh_encounter_thread(combat_event.encounter_id)

    def get_enemy(self, enemy_type: EnemyType) -> Enemy:
        enemy = globals()[enemy_type]
        instance = enemy()
        return instance

    async def create_encounter(self, guild_id: int):
        encounter_level = await self.database.get_guild_level(guild_id)

        enemies = [self.get_enemy(enemy_type) for enemy_type in EnemyType]
        possible_enemies = [
            enemy for enemy in enemies if enemy.level <= encounter_level
        ]

        spawn_weights = [enemy.weighting for enemy in possible_enemies]
        spawn_weights = [1.0 / w for w in spawn_weights]
        sum_weights = sum(spawn_weights)
        spawn_weights = [w / sum_weights for w in spawn_weights]

        enemy = random.choices(possible_enemies, weights=spawn_weights)[0]
        enemy_health = random.randint(enemy.min_hp, enemy.max_hp)

        return Encounter(guild_id, enemy.type, enemy_health)

    def get_spawn_embed(
        self, encounter: Encounter, show_info: bool = False
    ) -> discord.Embed:
        enemy = self.get_enemy(encounter.enemy_type)
        title = "A random Enemy appeared!"

        embed = discord.Embed(title=title, color=discord.Colour.blurple())

        enemy_name = f"> ~* {enemy.name} *~"
        content = f'```python\n"{enemy.description}"```'
        embed.add_field(name=enemy_name, value=content, inline=False)

        if show_info:
            enemy_info = f"```ansi\n[37m{enemy.information}```"
            embed.add_field(name="", value=enemy_info, inline=False)
            return embed

        embed.set_image(url=f"attachment://{enemy.image}")

        return embed

    def get_combat_embed(self, context: EncounterContext) -> discord.Embed:
        enemy = context.opponent.enemy

        title = f"> ~* {enemy.name} *~"
        content = f'```python\n"{enemy.description}"```'
        embed = discord.Embed(
            title=title, description=content, color=discord.Colour.blurple()
        )

        health = f"{context.opponent.current_hp}/{context.opponent.max_hp}\n"
        embed.add_field(name="Health", value=health, inline=False)

        initiative_list = context.get_current_initiative()
        initiative_display = ""
        for idx, actor in enumerate(initiative_list):
            number = idx + 1
            if initiative_display == "":
                initiative_display += f"\n{number}. >*{actor.name}*<"
                continue
            initiative_display += f"\n{number}. {actor.name}"
        embed.add_field(name="Turn Order:", value=initiative_display, inline=False)

        embed.set_image(url=f"attachment://{enemy.image}")

        return embed

    def get_character_turn_embed(self, context: EncounterContext) -> discord.Embed:
        actor = context.get_current_actor()

        title = f"Turn of {actor.name}"
        content = f"It is your turn <@{actor.id}>. Please select an action."
        embed = discord.Embed(
            title=title, description=content, color=discord.Colour.blurple()
        )

        health = f"{actor.current_hp}/{actor.max_hp}\n"
        embed.add_field(name="Health:", value=health, inline=False)

        embed.add_field(name="Skills:", value="", inline=False)

        for skill in actor.skills:
            skill.add_to_embed(embed=embed)

        return embed

    async def spawn_encounter(self, guild: discord.Guild, channel_id: int):
        log_message = f"Encounter was spawned in {guild.name}."
        self.logger.log(guild.id, log_message, cog=self.log_name)

        encounter = await self.create_encounter(guild.id)
        embed = self.get_spawn_embed(encounter)

        enemy = self.get_enemy(encounter.enemy_type)

        view = EnemyEngageView(self.controller)
        image = discord.File(f"./img/enemies/{enemy.image}", enemy.image)
        channel = guild.get_channel(channel_id)

        message = await channel.send("", embed=embed, view=view, files=[image])
        encounter.message_id = message.id
        encounter.channel_id = message.channel.id

        encounter_id = await self.database.log_encounter(encounter)

        event = EncounterEvent(
            datetime.datetime.now(),
            guild.id,
            encounter_id,
            self.bot.user.id,
            EncounterEventType.SPAWN,
        )
        await self.controller.dispatch_event(event)

    async def create_encounter_thread(self, encounter: Encounter) -> discord.Thread:
        channel = self.bot.get_channel(encounter.channel_id)
        enemy = self.get_enemy(encounter.enemy_type)
        thread = await channel.create_thread(
            name=f"Encounter: {enemy.name}", type=discord.ChannelType.public_thread
        )

        await self.database.log_encounter_thread(
            encounter.id, thread.id, encounter.guild_id, encounter.channel_id
        )
        return thread

    async def add_member_to_encounter(self, encounter_id: int, member_id: int):
        thread_id = await self.database.get_encounter_thread(encounter_id)

        encounter = await self.database.get_encounter_by_encounter_id(encounter_id)
        thread = None
        new_thread = False

        if thread_id is None:
            thread = await self.create_encounter_thread(encounter)
            new_thread = True
        else:
            thread = self.bot.get_channel(encounter.channel_id).get_thread(thread_id)

        if thread is None:
            return

        user = self.bot.get_user(member_id)
        await thread.add_user(user)

        message = f"<@{member_id}> joined the battle!"
        await thread.send(message)

        if new_thread:
            await self.refresh_encounter_thread(encounter_id)

    async def load_encounter_context(self, encounter_id) -> EncounterContext:
        encounter = await self.database.get_encounter_by_encounter_id(encounter_id)
        enemy = self.get_enemy(encounter.enemy_type)
        opponent = Opponent(enemy, encounter.max_hp)
        encounter_events = await self.database.get_encounter_events_by_encounter_id(
            encounter_id
        )
        combat_events = await self.database.get_combat_events_by_encounter_id(
            encounter_id
        )
        thread_id = await self.database.get_encounter_thread(encounter_id)
        thread = self.bot.get_channel(encounter.channel_id).get_thread(thread_id)

        combatant_ids = await self.database.get_encounter_participants_by_encounter_id(
            encounter_id
        )
        guild = self.bot.get_guild(encounter.guild_id)
        members = [guild.get_member(id) for id in combatant_ids]

        combatants = []

        for member in members:
            combatant = Character(
                member,
                [NormalAttack(), HeavyAttack()],
            )
            combatants.append(combatant)

        return EncounterContext(
            encounter=encounter,
            opponent=opponent,
            encounter_events=encounter_events,
            combat_events=combat_events,
            combatants=combatants,
            thread=thread,
        )

    async def opponent_turn(self, context: EncounterContext):
        opponent = context.opponent

        skill = random.choice(opponent.skills)
        skill_value = opponent.get_skill_value(skill)

        target = random.choice(context.combatants)

        title = f"Turn of *{opponent.name}*"
        content = f"*{opponent.name}* used **{skill.name}**"

        match skill.skill_effect:
            case SkillEffect.PHYSICAL_DAMAGE:
                content += (
                    f" and deals **{skill_value}** physical damage to <@{target.id}>."
                )
            case SkillEffect.MAGICAL_DAMAGE:
                content += (
                    f" and deals **{skill_value}** magical damage to <@{target.id}>."
                )

        embed = discord.Embed(
            title=title, description=content, color=discord.Colour.blurple()
        )

        await context.thread.send("", embed=embed)

        event = CombatEvent(
            datetime.datetime.now(),
            context.encounter.guild_id,
            context.encounter.id,
            opponent.id,
            target.id,
            skill.type,
            skill_value,
            CombatEventType.ENEMY_TURN,
        )
        await self.controller.dispatch_event(event)

    async def refresh_encounter_thread(self, encounter_id: int):
        context = await self.load_encounter_context(encounter_id)
        current_actor = context.get_current_actor()

        async for message in context.thread.history(limit=100):
            if len(message.embeds) == 1 and message.author.id == self.bot.user.id:
                embed = message.embeds[0]
                if embed.image.url is not None:
                    await message.delete()
                    break

        if current_actor.is_enemy:
            await self.opponent_turn(context)
            return

        enemy = context.opponent.enemy
        embed = self.get_combat_embed(context)
        image = discord.File(f"./img/enemies/{enemy.image}", enemy.image)
        await context.thread.send("", embed=embed, files=[image])

        embed = self.get_character_turn_embed(context)
        view = CombatTurnView(self.controller, current_actor, context)
        await context.thread.send("", embed=embed, view=view)
        return
