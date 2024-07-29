import asyncio
import copy
import datetime

import discord
from combat.actors import Actor
from combat.encounter import Encounter, EncounterContext, TurnData
from combat.skills.skill import Skill
from combat.skills.types import SkillEffect, SkillInstance
from config import Config
from control.combat.combat_actor_manager import CombatActorManager
from control.combat.combat_skill_manager import CombatSkillManager
from control.combat.object_factory import ObjectFactory
from control.controller import Controller
from control.logger import BotLogger
from control.service import Service
from datalayer.database import Database
from discord.ext import commands
from events.bot_event import BotEvent
from items.item import Item


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
        self.actor_manager: CombatActorManager = self.controller.get_service(
            CombatActorManager
        )
        self.skill_manager: CombatSkillManager = self.controller.get_service(
            CombatSkillManager
        )
        self.factory: ObjectFactory = self.controller.get_service(ObjectFactory)
        self.log_name = "Combat Embeds"

    async def listen_for_event(self, event: BotEvent):
        pass

    async def get_spawn_embed(
        self, encounter: Encounter, done: bool = False, show_info: bool = False
    ) -> discord.Embed:
        enemy = await self.factory.get_enemy(encounter.enemy_type)

        if enemy.is_boss:
            title = "A Boss Challenge Has Appeared!"
            enemy_name = f"> ~* {enemy.name} *~"
            color = discord.Colour.red()
        else:
            title = "A random Enemy appeared!"
            enemy_name = f"> ~* {enemy.name} - Lvl. {encounter.enemy_level} *~"
            color = discord.Colour.purple()

        embed = discord.Embed(title=title, color=color)

        content = f'```python\n"{enemy.description}"```'
        embed.add_field(name=enemy_name, value=content, inline=False)

        if show_info or enemy.is_boss:
            enemy_info = f"```ansi\n[33m{enemy.information}```"
            embed.add_field(name="", value=enemy_info, inline=False)

        min_encounter_size = enemy.min_encounter_scale
        max_encounter_size = enemy.max_players
        participants = await self.database.get_encounter_participants_by_encounter_id(
            encounter.id
        )
        out_participants = (
            await self.database.get_encounter_out_participants_by_encounter_id(
                encounter.id
            )
        )
        active_participants = len(participants) - len(out_participants)
        if not done:
            if min_encounter_size > 1 and active_participants < min_encounter_size:
                participant_info = f"\nCombatants Needed to Start: {active_participants}/{min_encounter_size}"
            else:
                participant_info = (
                    f"\nActive Combatants: {active_participants}/{max_encounter_size}"
                )
        else:
            participant_info = "This Encounter Has Concluded."
        embed.add_field(name=participant_info, value="", inline=False)
        embed.set_image(url=enemy.image_url)
        if enemy.author is not None:
            embed.set_footer(text=f"by {enemy.author}")

        return embed

    def add_health_bar(
        self,
        embed: discord.Embed,
        current_hp: int,
        max_hp: int,
        hide_hp: bool = True,
        max_width: int = None,
    ):
        if max_width is None:
            max_width = Config.COMBAT_EMBED_MAX_WIDTH

        health = f"{current_hp}/{max_hp}"
        fraction = current_hp / max_hp
        percentage = f"{round(fraction * 100, 1)}".rstrip("0").rstrip(".")

        bar_start = "|"
        bar_end = f"| {percentage}%"

        bar_length = max_width - len(bar_start) - len(bar_end)

        missing_health_length = int(bar_length * (1 - fraction))
        health_length = bar_length - missing_health_length

        missing_health_bar = " " * missing_health_length
        health_bar = "█" * health_length

        content = "```" + bar_start + health_bar + missing_health_bar + bar_end + "```"

        title = "Health:"
        if not hide_hp:
            title += f" {health}"

        embed.add_field(name=title, value=content)

    def add_text_bar(
        self,
        embed: discord.Embed,
        name: str,
        value: str,
        max_width: int = None,
    ):
        if max_width is None:
            max_width = Config.COMBAT_EMBED_MAX_WIDTH

        spacing = ""
        content_length = len(value)
        if content_length < (max_width + 20):
            spacing = " " + "\u00a0" * max_width

        embed_content = "```\n" + value + spacing + "```"
        embed.add_field(name=name, value=embed_content, inline=False)

    def add_active_status_effect_bar(
        self,
        embed: discord.Embed,
        actor: Actor,
        max_width: int = None,
    ):
        if len(actor.status_effects) <= 0:
            return

        if max_width is None:
            max_width = Config.COMBAT_EMBED_MAX_WIDTH

        name = "Status Effects"
        value = ""

        for effect in actor.status_effects:
            if effect.status_effect.display_status and effect.remaining_stacks > 0:
                value += f"{effect.status_effect.emoji}{effect.remaining_stacks}"

        if value == "":
            return

        embed_content = "```\n" + value + "```"
        embed.add_field(name=name, value=embed_content, inline=False)

    async def get_combat_embed(self, context: EncounterContext) -> discord.Embed:
        enemy = context.opponent.enemy

        title = f"> ~* {enemy.name} - Lvl. {context.opponent.level} *~"
        if enemy.is_boss:
            title = f"> ~* {enemy.name} *~"

        content = f'```python\n"{enemy.description}"```'
        embed = discord.Embed(
            title=title, description=content, color=discord.Colour.red()
        )

        current_hp = await self.actor_manager.get_actor_current_hp(
            context.opponent, context.combat_events
        )
        max_hp = context.opponent.max_hp
        self.add_health_bar(embed, current_hp, max_hp, max_width=Config.ENEMY_MAX_WIDTH)

        self.add_active_status_effect_bar(
            embed, context.opponent, max_width=Config.ENEMY_MAX_WIDTH
        )

        skill_list = []
        for skill_type in enemy.skill_types:
            skill = await self.factory.get_enemy_skill(skill_type)
            skill_list.append(skill.name)

        self.add_text_bar(
            embed,
            name="Skills:",
            value=", ".join(skill_list),
            max_width=Config.ENEMY_MAX_WIDTH,
        )

        if enemy.information != "":
            self.add_text_bar(
                embed,
                name="Additional Information:",
                value=enemy.information,
                max_width=Config.ENEMY_MAX_WIDTH,
            )

        embed.set_image(url=enemy.image_url)
        if enemy.author is not None:
            embed.set_footer(text=f"by {enemy.author}")

        return embed

    async def get_combat_success_embed(
        self, context: EncounterContext
    ) -> discord.Embed:
        enemy = context.opponent.enemy

        title = f"> ~* {enemy.name} - Lvl. {context.opponent.level} *~"
        if enemy.is_boss:
            title = f"> ~* {enemy.name} *~"

        content = f'```python\n"{enemy.description}"```'
        embed = discord.Embed(
            title=title, description=content, color=discord.Colour.green()
        )

        current_hp = await self.actor_manager.get_actor_current_hp(
            context.opponent, context.combat_events
        )
        max_hp = context.opponent.max_hp
        self.add_health_bar(embed, current_hp, max_hp, max_width=Config.ENEMY_MAX_WIDTH)

        defeated_message = f"You successfully defeated *{enemy.name}*."
        embed.add_field(name="Congratulations!", value=defeated_message, inline=False)

        embed.set_image(url=enemy.image_url)
        if enemy.author is not None:
            embed.set_footer(text=f"by {enemy.author}")

        return embed

    async def get_combat_failed_embed(self, context: EncounterContext) -> discord.Embed:
        enemy = context.opponent.enemy

        title = f"> ~* {enemy.name} - Lvl. {context.opponent.level} *~"
        if enemy.is_boss:
            title = f"> ~* {enemy.name} *~"

        content = f'```python\n"{enemy.description}"```'
        embed = discord.Embed(
            title=title, description=content, color=discord.Colour.red()
        )

        current_hp = await self.actor_manager.get_actor_current_hp(
            context.opponent, context.combat_events
        )
        max_hp = context.opponent.max_hp
        self.add_health_bar(embed, current_hp, max_hp, max_width=Config.ENEMY_MAX_WIDTH)

        defeated_message = f"You were defeated by *{enemy.name}*."
        embed.add_field(name="Failure!", value=defeated_message, inline=False)

        embed.set_image(url=enemy.image_url)
        if enemy.author is not None:
            embed.set_footer(text=f"by {enemy.author}")

        return embed

    async def get_character_turn_embeds(
        self, context: EncounterContext
    ) -> list[discord.Embed]:
        actor = context.get_current_actor()
        embeds = []

        title = f"It's your turn {actor.name}!"

        content = "Please select an action. Otherwise your turn will be skipped."

        now = datetime.datetime.now().timestamp()
        turn_duration = context.get_turn_timeout(actor.id)
        timeout = int(now + turn_duration)

        if len(content) < Config.COMBAT_EMBED_MAX_WIDTH:
            content += " " + "\u00a0" * Config.COMBAT_EMBED_MAX_WIDTH

        content = f"```python\n{content}```"

        content += f"Skipping <t:{timeout}:R>."

        head_embed = discord.Embed(
            title=title, description=content, color=discord.Colour.blurple()
        )

        current_hp = await self.actor_manager.get_actor_current_hp(
            actor, context.combat_events
        )
        max_hp = int(actor.max_hp)
        self.add_health_bar(
            head_embed,
            current_hp,
            max_hp,
            hide_hp=False,
            max_width=Config.COMBAT_EMBED_MAX_WIDTH,
        )

        self.add_active_status_effect_bar(
            head_embed, actor, max_width=Config.COMBAT_EMBED_MAX_WIDTH
        )

        if actor.image_url is not None:
            head_embed.set_thumbnail(url=actor.image_url)

        head_embed.add_field(name="Your Skills:", value="", inline=False)
        embeds.append(head_embed)

        for skill in actor.skills:
            embeds.append(
                (await self.skill_manager.get_skill_data(actor, skill)).get_embed(
                    show_data=True
                )
            )

        return embeds

    async def get_loot_embed(self, member: discord.Member, beans: int):
        title = f"{member.display_name}'s Loot"
        embed = discord.Embed(title=title, color=discord.Colour.green())
        message = f"You gain 🅱️{beans} beans and the following items:"
        self.add_text_bar(embed, "", message)
        embed.set_thumbnail(url=member.display_avatar.url)
        return embed

    async def get_embed_attack_data(
        self,
        current_actor: Actor,
        target: Actor,
        skill: Skill,
        damage_instance: SkillInstance,
    ):
        outcome_title = ""
        damage_info = ""

        total_damage = await self.actor_manager.get_skill_damage_after_defense(
            target, skill, damage_instance.scaled_value
        )

        display_dmg = damage_instance.value
        if current_actor.is_enemy:
            display_dmg = total_damage

        match skill.base_skill.skill_effect:
            case SkillEffect.NEUTRAL_DAMAGE:
                outcome_title = "Damage"
                damage_info = f"**{display_dmg}**"
            case SkillEffect.PHYSICAL_DAMAGE:
                outcome_title = "Attack Damage"
                damage_info = f"**{display_dmg}** [phys]"
            case SkillEffect.MAGICAL_DAMAGE:
                outcome_title = "Spell Damage"
                damage_info = f"**{display_dmg}** [magic]"
            case SkillEffect.HEALING:
                outcome_title = "Healing"
                damage_info = f"**{display_dmg}**"

        if damage_instance.is_crit:
            damage_info = "CRIT! " + damage_info

        return outcome_title, damage_info

    async def display_aoe_skill(
        self,
        turn_data: TurnData,
        skill: Skill,
        full_embed: discord.Embed,
    ):
        actor = turn_data.actor

        embed = copy.deepcopy(full_embed)
        await asyncio.sleep(0.5)

        content_map = {}

        for target, damage_instance, _ in turn_data.damage_data:
            to_name = f"<@{target.id}>"
            if target.is_enemy:
                to_name = f"*{target.name}*"

            outcome_title, damage_info = await self.get_embed_attack_data(
                current_actor=actor,
                target=target,
                skill=skill,
                damage_instance=damage_instance,
            )
            content_map[target.id] = (to_name, outcome_title, damage_info)

            embed.add_field(name="Target", value=to_name, inline=True)
            embed.add_field(name=outcome_title, value="", inline=True)
            embed.add_field(name="Target Health", value="", inline=True)

        yield embed
        await asyncio.sleep(0.2)

        loading_icons = [
            "🎲",
            "🎲🎲",
            "🎲🎲🎲",
        ]

        i = 0
        current = i
        while i <= 2:
            current = i % len(loading_icons)
            icon = loading_icons[current]

            embed = copy.deepcopy(full_embed)
            for to_name, outcome_title, _ in content_map.values():
                embed.add_field(name="Target", value=to_name, inline=True)
                embed.add_field(name=outcome_title, value=icon, inline=True)
                embed.add_field(name="Target Health", value="", inline=True)

            yield embed

            await asyncio.sleep((1 / 5) * (i * 2))
            i += 1

        embed = copy.deepcopy(full_embed)

        embed = copy.deepcopy(full_embed)
        for target, _, remaiming_hp in turn_data.damage_data:
            percentage = f"{round(remaiming_hp/target.max_hp * 100, 1)}".rstrip(
                "0"
            ).rstrip(".")
            display_hp = f"{percentage}%"

            to_name, outcome_title, damage_info = content_map[target.id]

            full_embed.add_field(name="Target", value=to_name, inline=True)
            full_embed.add_field(name=outcome_title, value=damage_info, inline=True)
            full_embed.add_field(name="Target Health", value=display_hp, inline=True)

        yield full_embed

    async def display_regular_skill(
        self,
        turn_data: TurnData,
        skill: Skill,
        full_embed: discord.Embed,
    ):
        actor = turn_data.actor

        fast_mode = len(turn_data.damage_data) > 3

        for target, damage_instance, remaiming_hp in turn_data.damage_data:
            await asyncio.sleep(0.5)

            to_name = f"<@{target.id}>"
            if target.is_enemy:
                to_name = f"*{target.name}*"

            outcome_title, damage_info = await self.get_embed_attack_data(
                current_actor=actor,
                target=target,
                skill=skill,
                damage_instance=damage_instance,
            )

            embed = copy.deepcopy(full_embed)
            embed.add_field(name="Target", value=to_name, inline=True)
            embed.add_field(name=outcome_title, value="", inline=True)
            embed.add_field(name="Target Health", value="", inline=True)

            yield embed

            if not fast_mode:
                await asyncio.sleep(0.2)

                loading_icons = [
                    "🎲",
                    "🎲🎲",
                    "🎲🎲🎲",
                ]

                i = 0
                current = i
                while i <= 2:
                    current = i % len(loading_icons)
                    icon = loading_icons[current]

                    embed = copy.deepcopy(full_embed)
                    embed.add_field(name="Target", value=to_name, inline=True)
                    embed.add_field(name=outcome_title, value=icon, inline=True)
                    embed.add_field(name="Target Health", value="", inline=True)
                    yield embed

                    await asyncio.sleep((1 / 5) * (i * 2))
                    i += 1
            else:
                await asyncio.sleep(0.5)

            percentage = f"{round(remaiming_hp/target.max_hp * 100, 1)}".rstrip(
                "0"
            ).rstrip(".")
            display_hp = f"{percentage}%"

            full_embed.add_field(name="Target", value=to_name, inline=True)
            full_embed.add_field(name=outcome_title, value=damage_info, inline=True)
            full_embed.add_field(name="Target Health", value=display_hp, inline=True)
            yield full_embed

    async def handle_actor_turn_embed(
        self,
        turn_data: TurnData,
        context: EncounterContext,
    ):
        actor = turn_data.actor
        color = discord.Color.blurple()
        if actor.is_enemy:
            color = discord.Color.red()

        # turn_number = context.get_current_turn_number()
        title = f"{actor.name}"

        full_embed = None

        skill_data = await self.skill_manager.get_skill_data(actor, turn_data.skill)

        skill = skill_data.skill

        full_embed = discord.Embed(title="", description="", color=color)
        full_embed.set_author(name=title, icon_url=actor.image_url)
        full_embed.set_thumbnail(url=skill.base_skill.image_url)
        skill_data.add_to_embed(
            full_embed, description_override=turn_data.description_override
        )

        yield full_embed

        if (
            actor.is_enemy
            # and actor.enemy.is_boss
            and skill.type
            not in self.actor_manager.get_used_skills(actor.id, context.combat_events)
        ):
            wait = max(len(skill.description) * 0.06, 3)
            await asyncio.sleep(wait)

        if (
            not skill.base_skill.base_value <= 0
            and skill.base_skill.skill_effect
            not in [
                SkillEffect.NOTHING,
                SkillEffect.BUFF,
            ]
        ):
            if skill.base_skill.aoe:
                async for embed in self.display_aoe_skill(turn_data, skill, full_embed):
                    yield embed
            else:
                async for embed in self.display_regular_skill(
                    turn_data, skill, full_embed
                ):
                    yield embed

    def get_status_effect_embed(
        self, actor: Actor, effect_data: dict[str, str]
    ) -> discord.Embed:
        actor_name = f"{actor.name}"

        color = discord.Color.blurple()
        if actor.is_enemy:
            color = discord.Color.red()

        embed = discord.Embed(title="", description="", color=color)
        embed.set_author(name=actor_name, icon_url=actor.image_url)
        embed.set_thumbnail(url=actor.image_url)

        for title, description in effect_data.items():
            # embed.add_field(name=title, value=description)
            self.add_text_bar(embed, title, description)

        return embed

    def get_member_out_embed(self, actor: Actor, reason: str) -> discord.Embed:
        actor_name = f"{actor.name}"

        content = f"{actor_name} left the encounter. They will be removed at the start of the next round."

        embed = discord.Embed(
            title="", description="", color=discord.Colour.light_grey()
        )
        embed.set_author(name=actor_name, icon_url=actor.image_url)
        self.add_text_bar(embed, "", content)

        if actor.image_url is not None:
            embed.set_thumbnail(url=actor.image_url)
        if reason is not None and len(reason) > 0:
            embed.add_field(name="Reason", value=reason)
        return embed

    def get_turn_skip_embed(
        self, actor: Actor, reason: str, context: EncounterContext
    ) -> discord.Embed:
        actor_name = f"{actor.name}"

        content = f"{actor_name}'s turn is skipped."

        embed = discord.Embed(
            title="", description="", color=discord.Colour.light_grey()
        )
        embed.set_author(name=actor_name, icon_url=actor.image_url)
        self.add_text_bar(embed, "", content)

        if actor.image_url is not None:
            embed.set_thumbnail(url=actor.image_url)
        if reason is not None and len(reason) > 0:
            embed.add_field(name="Reason", value=reason)
        return embed

    async def get_waiting_for_party_embed(self, party_size: int):
        embed = discord.Embed(
            title="Waiting for players to arrive.", color=discord.Colour.green()
        )

        message = f"Combat will start as soon as {party_size} players join."
        self.add_text_bar(embed, "", message)

        embed.set_thumbnail(url=self.bot.user.display_avatar)
        return embed

    async def get_initiation_embed(self, wait_time: float):
        embed = discord.Embed(title="Get Ready to Fight!", color=discord.Colour.green())

        now = datetime.datetime.now().timestamp()
        timer = int(now + wait_time)

        message = f"Combat will start <t:{timer}:R>."
        embed.add_field(name=message, value="", inline=False)

        text = "Waiting for players to join."
        self.add_text_bar(embed, "", text)

        embed.set_thumbnail(url=self.bot.user.display_avatar)
        return embed

    async def get_round_embed(self, context: EncounterContext, cont: bool = False):
        title = "New Round"
        if cont:
            title = "Round Continued.."
        embed = discord.Embed(title=title, color=discord.Colour.green())
        initiative_list = context.actors
        current_actor = context.get_current_actor()
        initiative_display = ""

        for idx, actor in enumerate(initiative_list):
            if actor.is_out:
                continue
            number = idx + 1
            current_hp = await self.actor_manager.get_actor_current_hp(
                actor, context.combat_events
            )
            fraction = current_hp / actor.max_hp
            percentage = f"{round(fraction * 100, 1)}".rstrip("0").rstrip(".")
            name = actor.name[:13]
            display_hp = f"[{percentage}%]" if not actor.is_enemy else ""
            status_effects = ""
            for effect in actor.status_effects:
                if effect.status_effect.display_status and effect.remaining_stacks > 0:
                    status_effects += (
                        f"{effect.status_effect.emoji}{effect.remaining_stacks}"
                    )
            if actor.id == current_actor.id:
                width = 45
                text = f"{number}. >> {name} << {status_effects} {display_hp}"
                spacing = " " * max(0, width - len(text))
                initiative_display += f"\n{text}{spacing}"
                continue
            initiative_display += (
                f"\n{number}. {actor.name} {status_effects} {display_hp}"
            )
        initiative_display = f"```python\n{initiative_display}```"
        embed.add_field(name="Turn Order:", value=initiative_display, inline=False)

        embed.set_thumbnail(url=self.bot.user.display_avatar)
        return embed

    def get_notification_embed(
        self, title: str, message: str, actor: Actor = None
    ) -> discord.Embed:
        embed = discord.Embed(title=title, color=discord.Colour.light_grey())
        self.add_text_bar(embed, "", message)
        if actor is not None:
            embed.set_thumbnail(url=actor.image_url)
        return embed

    def get_actor_defeated_embed(self, actor: Actor) -> discord.Embed:
        title = f"*{actor.name}* was defeated!"
        message = ""
        if not actor.is_enemy:
            message = "Their future turns will be skipped."
        return self.get_notification_embed(title, message, actor)

    def get_actor_join_embed(
        self, user: discord.Member, additional_message: str = None
    ) -> discord.Embed:
        title = "A new player joined the battle!"
        message = f"Good luck {user.display_name}!"
        if additional_message is not None and additional_message != "":
            message += f"\n{additional_message}"
        return self.get_notification_embed(title, message)

    def get_special_item_embed(self, item: Item, delay_claim: int = None):
        title = "Special Item"
        embed = discord.Embed(title=title, description="", color=discord.Colour.gold())
        message = (
            "A boss key dropped! Only one of you may claim this item. "
            "The one who takes up the responsibility may spawn the boss encounter at any time. "
        )

        self.add_text_bar(embed, "", message)

        item.add_to_embed(
            self.bot,
            embed,
            Config.SHOP_ITEM_MAX_WIDTH,
            count=1,
            show_price=False,
        )

        if item.image_url is not None:
            embed.set_image(url=item.image_url)

        if delay_claim is not None:
            now = datetime.datetime.now().timestamp()
            timer = int(now + delay_claim)
            embed.add_field(name="", value=f"Able to claim <t:{timer}:R>.")

        return embed
