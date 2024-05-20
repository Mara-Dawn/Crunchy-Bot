import asyncio

import discord
from combat.actors import Actor
from combat.encounter import Encounter, EncounterContext
from combat.skills.skill import SkillData
from combat.skills.types import SkillEffect
from control.combat.combat_actor_manager import CombatActorManager
from control.combat.combat_enemy_manager import CombatEnemyManager
from control.controller import Controller
from control.logger import BotLogger
from control.service import Service
from datalayer.database import Database
from discord.ext import commands
from events.bot_event import BotEvent


class CombatEmbedManager(Service):

    def __init__(
        self,
        bot: commands.Bot,
        logger: BotLogger,
        database: Database,
        controller: Controller,
    ):
        super().__init__(bot, logger, database)
        self.controller = controller
        self.enemy_manager: CombatEnemyManager = self.controller.get_service(
            CombatEnemyManager
        )
        self.actor_manager: CombatActorManager = self.controller.get_service(
            CombatActorManager
        )
        self.log_name = "Combat Embeds"

    async def listen_for_event(self, event: BotEvent):
        pass

    def get_spawn_embed(
        self, encounter: Encounter, show_info: bool = False
    ) -> discord.Embed:
        enemy = self.enemy_manager.get_enemy(encounter.enemy_type)
        title = "A random Enemy appeared!"

        embed = discord.Embed(title=title, color=discord.Colour.purple())

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

        title = "Encounter Overview"
        content = "Information about the current encounter."
        embed = discord.Embed(
            title=title, description=content, color=discord.Colour.red()
        )
        enemy.add_to_embed(embed)

        current_hp = self.actor_manager.get_actor_current_hp(
            context.opponent, context.combat_events
        )
        health = f"**{current_hp}**/{context.opponent.max_hp}"
        embed.add_field(name="Enemy Health", value=health)

        initiative_list = context.get_current_initiative()
        initiative_display = ""

        for idx, actor in enumerate(initiative_list):
            number = idx + 1
            current_hp = self.actor_manager.get_actor_current_hp(
                actor, context.combat_events
            )
            display_hp = f"[{current_hp}/{actor.max_hp}]" if not actor.is_enemy else ""
            if initiative_display == "":
                initiative_display += f"\n{number}. >> {actor.name} << {display_hp}"
                continue
            initiative_display += f"\n{number}. {actor.name} {display_hp}"
        initiative_display = f"```python\n{initiative_display}```"
        embed.add_field(name="Turn Order:", value=initiative_display, inline=False)
        embed.set_image(url=f"attachment://{enemy.image}")

        return embed

    def get_combat_success_embed(self, context: EncounterContext) -> discord.Embed:
        enemy = context.opponent.enemy

        title = f"> ~* {enemy.name} *~"
        content = f'```python\n"{enemy.description}"```'
        embed = discord.Embed(
            title=title, description=content, color=discord.Colour.green()
        )
        current_hp = self.actor_manager.get_actor_current_hp(
            context.opponent, context.combat_events
        )
        health = f"**{current_hp}**/{context.opponent.max_hp}\n"
        embed.add_field(name="Health", value=health, inline=False)

        defeated_message = f"You successfully defeated *{enemy.name}*."
        embed.add_field(name="Congratulations!", value=defeated_message, inline=False)

        embed.set_image(url=f"attachment://{enemy.image}")

        return embed

    def get_combat_failed_embed(self, context: EncounterContext) -> discord.Embed:
        enemy = context.opponent.enemy

        title = f"> ~* {enemy.name} *~"
        content = f'```python\n"{enemy.description}"```'
        embed = discord.Embed(
            title=title, description=content, color=discord.Colour.red()
        )
        current_hp = self.actor_manager.get_actor_current_hp(
            context.opponent, context.combat_events
        )
        health = f"{current_hp}/{context.opponent.max_hp}\n"
        embed.add_field(name="Health", value=health, inline=False)

        defeated_message = f"You were defeated by *{enemy.name}*."
        embed.add_field(name="Failure!", value=defeated_message, inline=False)

        embed.set_image(url=f"attachment://{enemy.image}")

        return embed

    def get_character_turn_embed(self, context: EncounterContext) -> discord.Embed:
        actor = context.get_current_actor()

        turn_number = context.get_current_turn_number()
        title = f"Turn {turn_number}: {actor.name}"

        content = f"It is your turn <@{actor.id}>. Please select an action."
        embed = discord.Embed(
            title=title, description=content, color=discord.Colour.blurple()
        )

        current_hp = self.actor_manager.get_actor_current_hp(
            actor, context.combat_events
        )
        health = f"**{current_hp}**/{actor.max_hp}"
        embed.add_field(name="Your Health:", value=health, inline=False)

        embed.add_field(name="Your Skills:", value="", inline=False)

        for skill in actor.skill_data:
            skill.add_to_embed(embed=embed)

        return embed

    async def handle_actor_turn_embed(
        self,
        from_actor: Actor,
        to_actor: Actor,
        skill_data: SkillData,
        skill_value: int,
        context: EncounterContext,
        message: discord.Message = None,
    ):
        color = discord.Color.blurple()
        if from_actor.is_enemy:
            color = discord.Color.red()

        from_name = f"<@{from_actor.id}>"
        if from_actor.is_enemy:
            from_name = f"*{from_actor.name}*"

        to_name = f"<@{to_actor.id}>"
        if to_actor.is_enemy:
            to_name = f"*{to_actor.name}*"

        turn_number = context.get_current_turn_number()
        title = f"Turn {turn_number}: {from_actor.name}"

        skill = skill_data.skill

        description = f"{from_name} chose the action"

        embed = discord.Embed(title=title, description=description, color=color)
        skill_data.add_to_embed(embed)

        if message is None:
            message = await context.thread.send(embed=embed)
        else:
            await message.edit(content="", embed=embed, attachments=[], view=None)

        await asyncio.sleep(2.5)

        outcome_title = ""
        damage_info = ""
        content = f"{from_name} used **{skill.name}**"
        current_hp = self.actor_manager.get_actor_current_hp(
            to_actor, context.combat_events
        )

        match skill.skill_effect:
            case SkillEffect.PHYSICAL_DAMAGE:
                outcome_title = "Attack Damage"
                damage_info = f"**{skill_value}** [phys]"
                content += f" and deals **{skill_value}** physical damage to {to_name}."
                current_hp = max(0, current_hp - skill_value)
            case SkillEffect.MAGICAL_DAMAGE:
                outcome_title = "Spell Damage"
                damage_info = f"**{skill_value}** [magic]"
                content += f" and deals **{skill_value}** magical damage to {to_name}."
                current_hp = max(0, current_hp - skill_value)

        embed = discord.Embed(title=title, description=description, color=color)
        skill_data.add_to_embed(embed)
        embed.add_field(name="Target", value=to_name, inline=True)
        embed.add_field(name=outcome_title, value="", inline=True)
        embed.add_field(name="Remaining Health", value="", inline=True)
        await message.edit(embed=embed)

        await asyncio.sleep(1.5)

        loading_icons = [
            "🎲",
            "🎲🎲",
            "🎲🎲🎲",
        ]

        i = 0
        current = i
        while i <= 5:
            current = i % len(loading_icons)
            icon = loading_icons[current]

            embed = discord.Embed(title=title, description=description, color=color)
            skill_data.add_to_embed(embed)
            embed.add_field(name="Target", value=to_name, inline=True)
            embed.add_field(name=outcome_title, value=icon, inline=True)
            embed.add_field(name="Remaining Health", value="", inline=True)

            await message.edit(embed=embed)
            await asyncio.sleep((1 / 10) * (i * 1.5))
            i += 1

        embed = discord.Embed(title=title, description=description, color=color)
        skill_data.add_to_embed(embed)
        embed.add_field(name="Target", value=to_name, inline=True)
        embed.add_field(name=outcome_title, value=damage_info, inline=True)
        embed.add_field(name="Remaining Health", value="", inline=True)
        await message.edit(embed=embed)

        await asyncio.sleep(1)

        display_hp = f"**{current_hp}**/{to_actor.max_hp}"

        embed = discord.Embed(title=title, description=description, color=color)
        skill_data.add_to_embed(embed)
        embed.add_field(name="Target", value=to_name, inline=True)
        embed.add_field(name=outcome_title, value=damage_info, inline=True)
        embed.add_field(name="Remaining Health", value=display_hp, inline=True)
        await message.edit(embed=embed)

        await asyncio.sleep(1)

        embed = discord.Embed(title=title, description=description, color=color)
        skill_data.add_to_embed(embed)
        embed.add_field(name="Target", value=to_name, inline=True)
        embed.add_field(name=outcome_title, value=damage_info, inline=True)
        embed.add_field(name="Remaining Health", value=display_hp, inline=True)
        embed.add_field(name="Outcome", value=content, inline=False)
        await message.edit(embed=embed)

    def get_turn_skip_embed(
        self, actor: Actor, reason: str, context: EncounterContext
    ) -> discord.Embed:
        turn_number = context.get_current_turn_number()
        title = f"Turn {turn_number}: {actor.name}"

        actor_name = f"<@{actor.id}>"
        if actor.is_enemy:
            actor_name = f"*{actor.id}*"

        content = f"{actor_name}'s turn is skipped."

        embed = discord.Embed(
            title=title, description=content, color=discord.Colour.light_grey()
        )
        embed.add_field(name="Reason", value=reason)
        return embed

    def get_notification_embed(self, message: str):
        embed = discord.Embed(title=message, color=discord.Colour.light_grey())
        return embed

    def get_actor_defeated_embed(self, actor: Actor):
        message = f"*{actor.name}* was defeated!"
        return self.get_notification_embed(message)

    def get_actor_join_embed(self, user: discord.Member):
        message = f"*{user.display_name}* joined the battle!"
        return self.get_notification_embed(message)
