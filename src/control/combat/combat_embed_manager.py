import discord
from combat.actors import Actor
from combat.encounter import Encounter, EncounterContext
from combat.skills import Skill
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

        initiative_list = context.get_current_initiative()
        initiative_display = ""

        for idx, actor in enumerate(initiative_list):
            number = idx + 1
            current_hp = self.actor_manager.get_actor_current_hp(
                actor, context.combat_events
            )
            display_hp = f"[{current_hp}/{actor.max_hp}]" if not actor.is_enemy else ""
            if initiative_display == "":
                initiative_display += f"\n{number}. >*{actor.name}*< {display_hp}"
                continue
            initiative_display += f"\n{number}. {actor.name} {display_hp}"

        embed.add_field(name="Turn Order:", value=initiative_display, inline=False)
        embed.set_image(url=f"attachment://{enemy.image}")

        return embed

    def get_combat_concluded_embed(self, context: EncounterContext) -> discord.Embed:
        enemy = context.opponent.enemy

        title = f"> ~* {enemy.name} *~"
        content = f'```python\n"{enemy.description}"```'
        embed = discord.Embed(
            title=title, description=content, color=discord.Colour.green()
        )
        current_hp = self.actor_manager.get_actor_current_hp(
            context.opponent, context.combat_events
        )
        health = f"{current_hp}/{context.opponent.max_hp}\n"
        embed.add_field(name="Health", value=health, inline=False)

        defeated_message = f"You successfully defeated *{enemy.name}*."
        embed.add_field(name="Congratulations!", value=defeated_message, inline=False)

        embed.set_image(url=f"attachment://{enemy.image}")

        return embed

    def get_character_turn_embed(self, context: EncounterContext) -> discord.Embed:
        actor = context.get_current_actor()

        title = f"Turn of {actor.name}"
        content = f"It is your turn <@{actor.id}>. Please select an action."
        embed = discord.Embed(
            title=title, description=content, color=discord.Colour.blurple()
        )

        current_hp = self.actor_manager.get_actor_current_hp(
            actor, context.combat_events
        )
        health = f"{current_hp}/{actor.max_hp}\n"
        embed.add_field(name="Health:", value=health, inline=False)

        embed.add_field(name="Skills:", value="", inline=False)

        for skill in actor.skills:
            skill.add_to_embed(embed=embed)

        return embed

    def get_turn_completed_embed(
        self, from_actor: Actor, to_actor: Actor, skill: Skill
    ) -> discord.Embed:
        skill_value = from_actor.get_skill_value(skill)
        title = f"Turn of *{from_actor.name}*"

        from_name = f"<@{from_actor.id}>"
        if from_actor.is_enemy:
            from_name = f"*{from_actor.name}*"

        to_name = f"<@{to_actor.id}>"
        if to_actor.is_enemy:
            to_name = f"*{to_actor.name}*"

        content = f"{from_name} used **{skill.name}**"
        damage_info = ""

        match skill.skill_effect:
            case SkillEffect.PHYSICAL_DAMAGE:
                content += f" and deals **{skill_value}** physical damage to {to_name}."
                damage_info = f"{skill_value} [phys]"
            case SkillEffect.MAGICAL_DAMAGE:
                content += f" and deals **{skill_value}** magical damage to {to_name}."
                damage_info = f"{skill_value} [magic]"

        color = discord.Color.blurple()
        if from_actor.is_enemy:
            color = discord.Color.red()

        embed = discord.Embed(title=title, description=content, color=color)
        embed.add_field(name="Target", value=to_name)
        embed.add_field(name="Skill", value=skill.name)
        if damage_info != "":
            embed.add_field(name="Damage", value=damage_info)
        return embed

    def get_turn_skip_embed(self, actor: Actor, reason: str) -> discord.Embed:
        title = f"Turn of *{actor.name}*"

        actor_name = f"<@{actor.id}>"
        if actor.is_enemy:
            actor_name = f"*{actor.id}*"

        content = f"{actor_name}'s turn is skipped."

        embed = discord.Embed(
            title=title, description=content, color=discord.Colour.light_grey()
        )
        embed.add_field(name="Reason", value=reason)
        return embed

    def get_actor_defeated_embed(self, actor: Actor):
        title = f"*{actor.name}* was defeated!"
        embed = discord.Embed(title=title, color=discord.Colour.light_grey())
        return embed

    def get_actor_join_embed(self, user: discord.Member):
        title = f"*{user.display_name}* joined the battle!"
        embed = discord.Embed(title=title, color=discord.Colour.light_grey())
        return embed
