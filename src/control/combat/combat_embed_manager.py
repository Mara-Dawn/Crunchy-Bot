import asyncio
import copy
import datetime

import discord
from discord.ext import commands

from combat.actors import Actor, Character, Opponent
from combat.effects.effect import EmbedDataCollection
from combat.encounter import Encounter, EncounterContext, TurnDamageData, TurnData
from combat.gear.gear import Gear
from combat.gear.types import GearModifierType
from combat.skills.skill import Skill
from combat.skills.types import SkillEffect
from config import Config
from control.combat.combat_actor_manager import CombatActorManager
from control.combat.combat_enchantment_manager import CombatEnchantmentManager
from control.combat.combat_gear_manager import CombatGearManager
from control.combat.combat_skill_manager import CombatSkillManager
from control.combat.encounter_statistics import EncounterStatistics
from control.combat.object_factory import ObjectFactory
from control.controller import Controller
from control.imgur_manager import ImgurManager
from control.logger import BotLogger
from control.service import Service
from control.types import FieldData
from datalayer.database import Database
from events.bot_event import BotEvent
from events.types import EncounterEventType
from items.item import Item


class CombatEmbedManager(Service):

    SYSTEM_MESSAGE_COLOR = discord.Colour.purple()

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
        self.imgur_manager: ImgurManager = self.controller.get_service(ImgurManager)
        self.skill_manager: CombatSkillManager = self.controller.get_service(
            CombatSkillManager
        )
        self.encounter_statistics: EncounterStatistics = self.controller.get_service(
            EncounterStatistics
        )
        self.gear_manager: CombatGearManager = self.controller.get_service(
            CombatGearManager
        )
        self.enchantment_manager: CombatEnchantmentManager = (
            self.controller.get_service(CombatEnchantmentManager)
        )
        self.factory: ObjectFactory = self.controller.get_service(ObjectFactory)
        self.log_name = "Combat Embeds"

    async def listen_for_event(self, event: BotEvent):
        pass

    async def get_spawn_embed(
        self, context: EncounterContext, show_info: bool = False
    ) -> discord.Embed:
        encounter = context.encounter
        enemy = await self.factory.get_enemy(encounter.enemy_type)
        enemy_name = enemy.name
        image_url = enemy.image_url
        image = await self.get_custom_image(encounter)
        if image is not None:
            image_url = image.link
            enemy_name += f" ({image.description})"

        if enemy.is_boss:
            title = "A Boss Challenge Has Appeared!"
            enemy_name = f"> ~* {enemy_name} *~"
            color = discord.Colour.red()
        else:
            title = "A random Enemy appeared!"
            enemy_name = f"> ~* {enemy_name} - Lvl. {encounter.enemy_level} *~"
            color = self.SYSTEM_MESSAGE_COLOR

        embed = discord.Embed(title=title, color=color)

        content = f'```python\n"{enemy.description}"```'
        embed.add_field(name=enemy_name, value=content, inline=False)

        if show_info or enemy.is_boss:
            enemy_info = f"```ansi\n[33m{enemy.information}```"
            embed.add_field(name="", value=enemy_info, inline=False)

        min_encounter_size = context.min_participants

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
        if not context.concluded:
            if min_encounter_size > 1 and active_participants < min_encounter_size:
                participant_info = f"\nCombatants Needed to Start: {active_participants}/{min_encounter_size}"
            else:
                participant_info = (
                    f"\nActive Combatants: {active_participants}/{max_encounter_size}"
                )
        else:
            participant_info = "This Encounter Has Concluded."
        embed.add_field(name=participant_info, value="", inline=False)

        embed.set_image(url=image_url)

        if enemy.author is not None:
            embed.set_footer(text=f"by {enemy.author}")

        return embed

    async def get_custom_image(self, encounter: Encounter):
        image = await self.imgur_manager.get_random_encounter_image(encounter)
        return image

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
        if content_length < max_width:
            spacing = " " + "\u00a0" * (max_width - content_length)

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

    async def add_active_enchantments(
        self,
        embed: discord.Embed,
        character: Character,
        max_width: int = None,
    ) -> str:
        if len(character.active_enchantments) <= 0:
            return ""

        if max_width is None:
            max_width = Config.COMBAT_EMBED_MAX_WIDTH

        info_block = "```ansi\n"
        info_data = []
        for enchantment in character.active_enchantments:
            cooldown_remaining = None
            if (
                enchantment.base_enchantment.cooldown is not None
                and enchantment.id in character.enchantment_cooldowns
                and character.enchantment_cooldowns[enchantment.id] is not None
            ):
                cooldown_remaining = (
                    enchantment.base_enchantment.cooldown
                    - character.enchantment_cooldowns[enchantment.id]
                )

            uses = None
            if enchantment.base_enchantment.stacks is not None:
                total = enchantment.base_enchantment.stacks
                remaining = total
                if enchantment.id in character.enchantment_stacks_used:
                    remaining = (
                        total - character.enchantment_stacks_used[enchantment.id]
                    )
                uses = (remaining, total)
            info_data.append(
                enchantment.get_info_text(cooldown=cooldown_remaining, uses=uses)
            )
        info_block += "\n".join(info_data)
        info_block += "```"

        embed.add_field(name="Active Enchantments", value=info_block, inline=False)

    async def get_combat_embed(self, context: EncounterContext) -> discord.Embed:
        enemy = context.opponent.enemy

        title = f"> ~* {context.opponent.name} - Lvl. {context.opponent.level} *~"
        if enemy.is_boss:
            title = f"> ~* {enemy.name} *~"

        content = f'```python\n"{enemy.description}"```'
        embed = discord.Embed(
            title=title, description=content, color=discord.Color.red()
        )

        current_hp = context.opponent.current_hp
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
            if enemy.is_boss:
                enemy_info = f"```ansi\n[33m{enemy.information}```"
                embed.add_field(name="", value=enemy_info, inline=False)
            else:
                self.add_text_bar(
                    embed,
                    name="Additional Information:",
                    value=enemy.information,
                    max_width=Config.ENEMY_MAX_WIDTH,
                )

        image_url = context.opponent.image_url
        if image_url is None:
            image_url = enemy.image_url
        embed.set_image(url=image_url)
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

        current_hp = context.opponent.current_hp
        max_hp = context.opponent.max_hp
        self.add_health_bar(embed, current_hp, max_hp, max_width=Config.ENEMY_MAX_WIDTH)

        defeated_message = f"You successfully defeated *{enemy.name}*."
        embed.add_field(name="Congratulations!", value=defeated_message, inline=False)

        await self.encounter_statistics.add_to_embed(context, embed)

        image_url = context.opponent.image_url
        if image_url is None:
            image_url = enemy.image_url
        embed.set_image(url=image_url)
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

        current_hp = context.opponent.current_hp
        max_hp = context.opponent.max_hp
        self.add_health_bar(embed, current_hp, max_hp, max_width=Config.ENEMY_MAX_WIDTH)

        defeated_message = f"You were defeated by *{enemy.name}*."
        embed.add_field(name="Failure!", value=defeated_message, inline=False)

        image_url = context.opponent.image_url
        embed.set_image(url=image_url)
        if enemy.author is not None:
            embed.set_footer(text=f"by {enemy.author}")

        return embed

    async def get_character_turn_embeds(
        self, context: EncounterContext
    ) -> list[discord.Embed]:
        actor = context.current_actor
        embeds = []

        title = f"It's your turn {actor.name}!"

        content = "Please select an action. Otherwise your turn will be skipped."

        now = datetime.datetime.now().timestamp()

        if actor.timeout_count == 0:
            turn_duration = Config.DEFAULT_TIMEOUT
        else:
            turn_duration = Config.SHORT_TIMEOUT

        timeout = int(now + turn_duration)

        if len(content) < Config.COMBAT_EMBED_MAX_WIDTH:
            content += " " + "\u00a0" * Config.COMBAT_EMBED_MAX_WIDTH

        content = f"```python\n{content}```"

        content += f"Skipping <t:{timeout}:R>."

        head_embed = discord.Embed(
            title=title, description=content, color=self.SYSTEM_MESSAGE_COLOR
        )

        max_hp = int(actor.max_hp)
        self.add_health_bar(
            head_embed,
            actor.current_hp,
            max_hp,
            hide_hp=False,
            max_width=Config.COMBAT_EMBED_MAX_WIDTH,
        )

        self.add_active_status_effect_bar(
            head_embed, actor, max_width=Config.COMBAT_EMBED_MAX_WIDTH
        )

        await self.add_active_enchantments(head_embed, actor)

        if actor.image_url is not None:
            head_embed.set_thumbnail(url=actor.image_url)

        head_embed.add_field(name="Your Skills:", value="", inline=False)
        embeds.append(head_embed)

        for skill in actor.skills:
            embeds.append(
                (await self.skill_manager.get_skill_data(actor, skill)).get_embed()
            )

        return embeds

    async def get_loot_embed(self, member: discord.Member, beans: int):
        title = f"{member.display_name}'s Loot"
        embed = discord.Embed(title=title, color=self.SYSTEM_MESSAGE_COLOR)
        message = f"You gain 🅱️{beans} beans and the following items:"
        self.add_text_bar(embed, "", message)
        embed.set_thumbnail(url=member.display_avatar.url)
        return embed

    async def get_loot_scrap_embed(
        self, member: discord.Member, scrap: int, level: int
    ):
        title = f"{member.display_name}'s Auto Scrap Results"
        content = f"You gain ⚙️{scrap} Scrap from scrapping all items up to and including level {level}."
        embed = discord.Embed(
            title=title, description=content, color=self.SYSTEM_MESSAGE_COLOR
        )
        message = "To change this and other things, please use the command /personal_settings."
        self.add_text_bar(embed, "", message)
        embed.set_thumbnail(url=member.display_avatar.url)
        return embed

    async def get_embed_attack_data(
        self,
        current_actor: Actor,
        skill: Skill,
        damage_data: TurnDamageData,
    ):
        outcome_title = ""
        damage_info = ""
        target = damage_data.target
        damage_instance = damage_data.instance

        total_damage = await self.actor_manager.get_skill_damage_after_defense(
            target, skill, damage_instance.scaled_value
        )
        display_dmg = await self.actor_manager.get_skill_damage_after_defense(
            target, skill, damage_instance.value
        )
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
                if current_actor.is_enemy:
                    damage_info = f"**{int(display_dmg/current_actor.max_hp*100)}%**"
                else:
                    damage_info = f"**{display_dmg}**"

        if damage_instance.is_crit:
            damage_info = "CRIT! " + damage_info
        if damage_instance.bonus_damage is not None:
            damage_info = damage_info + f"\n+ **{damage_instance.bonus_damage}**"

        return outcome_title, damage_info

    async def display_aoe_skill(
        self,
        turn_data: TurnData,
        full_embed: discord.Embed,
    ):
        actor = turn_data.actor

        embed = copy.deepcopy(full_embed)
        await asyncio.sleep(0.5)

        content_map = {}

        for damage_data in turn_data.damage_data:
            target = damage_data.target
            to_name = f"<@{target.id}>"
            if target.is_enemy:
                to_name = f"*{target.name}*"

            outcome_title, damage_info = await self.get_embed_attack_data(
                current_actor=actor,
                skill=turn_data.skill,
                damage_data=damage_data,
            )

            content_map[target.id] = (to_name, outcome_title, damage_info)

            embed.add_field(name="Target", value=to_name, inline=True)
            embed.add_field(name=outcome_title, value="", inline=True)
            embed.add_field(name="Target Health", value="", inline=True)

        yield embed

        await asyncio.sleep(0.5)

        embed = copy.deepcopy(full_embed)
        for damage_data in turn_data.damage_data:
            target = damage_data.target

            to_name, outcome_title, damage_info = content_map[target.id]

            embed.add_field(name="Target", value=to_name, inline=True)
            embed.add_field(name=outcome_title, value=damage_info, inline=True)
            embed.add_field(name="Target Health", value="", inline=True)

        yield embed

        await asyncio.sleep(0.5)

        for damage_data in turn_data.damage_data:
            target = damage_data.target
            to_name, outcome_title, damage_info = content_map[target.id]

            remaiming_hp = damage_data.hp
            percentage = f"{round(remaiming_hp/target.max_hp * 100, 1)}".rstrip(
                "0"
            ).rstrip(".")
            display_hp = f"{percentage}%"

            applied_effect_display = ""
            for status_effect_type, stacks in damage_data.applied_status_effects:
                status_effect = await self.factory.get_status_effect(status_effect_type)
                if status_effect.display_status:
                    applied_effect_display += f"{status_effect.emoji}{stacks}"

            full_isplay_hp = display_hp
            if applied_effect_display != "":
                full_isplay_hp += f" | `{applied_effect_display}`"

            full_embed.add_field(name="Target", value=to_name, inline=True)
            full_embed.add_field(name=outcome_title, value=damage_info, inline=True)
            full_embed.add_field(
                name="Target Health", value=full_isplay_hp, inline=True
            )

        yield full_embed

    async def display_regular_skill(
        self,
        turn_data: TurnData,
        full_embed: discord.Embed,
    ):
        actor = turn_data.actor

        fast_mode = len(turn_data.damage_data) > 1

        for damage_data in turn_data.damage_data:
            target = damage_data.target
            remaiming_hp = damage_data.hp
            await asyncio.sleep(1)

            to_name = f"<@{target.id}>"
            if target.is_enemy:
                to_name = f"*{target.name}*"

            outcome_title, damage_info = await self.get_embed_attack_data(
                current_actor=actor,
                skill=turn_data.skill,
                damage_data=damage_data,
            )

            if not fast_mode:
                embed = copy.deepcopy(full_embed)
                embed.add_field(name="Target", value=to_name, inline=True)
                embed.add_field(name=outcome_title, value="", inline=True)
                embed.add_field(name="Target Health", value="", inline=True)
                yield embed
                await asyncio.sleep(0.5)

                embed = copy.deepcopy(full_embed)
                embed.add_field(name="Target", value=to_name, inline=True)
                embed.add_field(name=outcome_title, value=damage_info, inline=True)
                embed.add_field(name="Target Health", value="", inline=True)
                yield embed
                await asyncio.sleep(0.5)

            percentage = f"{round(remaiming_hp/target.max_hp * 100, 1)}".rstrip(
                "0"
            ).rstrip(".")
            display_hp = f"{percentage}%"

            applied_effect_display = ""
            for status_effect_type, stacks in damage_data.applied_status_effects:
                status_effect = await self.factory.get_status_effect(status_effect_type)
                if status_effect.display_status:
                    applied_effect_display += f"{status_effect.emoji}{stacks}"

            if applied_effect_display != "":
                display_hp = f"{display_hp} | `{applied_effect_display}`"

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

        title = f"{actor.name}"

        full_embed = None

        skill_data = await self.skill_manager.get_skill_data(actor, turn_data.skill)

        skill = skill_data.skill

        if actor.is_enemy:
            color = discord.Color.red()
        else:
            color = Skill.RARITY_COLOR_HEX_MAP[skill.rarity]

        full_embed = discord.Embed(title="", description="", color=color)
        full_embed.set_author(name=title, icon_url=actor.image_url)
        full_embed.set_thumbnail(url=skill.base_skill.image_url)
        skill_data.add_to_embed(
            full_embed, description_override=turn_data.description_override
        )

        yield full_embed

        if actor.is_enemy and skill.type not in self.actor_manager.get_used_skills(
            actor.id, context.combat_events
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
                async for embed in self.display_aoe_skill(turn_data, full_embed):
                    yield embed
            else:
                async for embed in self.display_regular_skill(turn_data, full_embed):
                    yield embed

    async def apply_attack_data_to_embed(
        self, embed: discord.Embed, turn_data: TurnData
    ):
        actor = turn_data.actor
        skill_data = await self.skill_manager.get_skill_data(actor, turn_data.skill)
        skill = skill_data.skill

        if actor.is_enemy:
            color = discord.Color.red()
        else:
            color = Skill.RARITY_COLOR_HEX_MAP[skill.rarity]

        embed.set_thumbnail(url=skill.base_skill.image_url)
        embed.color = color

    async def get_actor_turn_embed_data(
        self,
        turn_data: TurnData,
        context: EncounterContext,
    ):

        actor = turn_data.actor
        skill_data = await self.skill_manager.get_skill_data(actor, turn_data.skill)
        skill = skill_data.skill

        field = skill_data.get_embed_field(
            description_override=turn_data.description_override
        )
        fields = [field]
        yield fields

        if actor.is_enemy and skill.type not in self.actor_manager.get_used_skills(
            actor.id, context
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
                async for field_data in self.get_aoe_skill_data(turn_data):
                    yield field_data
            else:
                async for field_data in self.get_regular_skill_data(turn_data):
                    yield field_data

    async def get_regular_skill_data(
        self,
        turn_data: TurnData,
    ):
        actor = turn_data.actor

        fast_mode = len(turn_data.damage_data) > 1

        fields = []

        for damage_data in turn_data.damage_data:
            target = damage_data.target
            remaiming_hp = damage_data.hp
            await asyncio.sleep(1)

            to_name = f"<@{target.id}>"
            if target.is_enemy:
                to_name = f"*{target.name}*"

            outcome_title, damage_info = await self.get_embed_attack_data(
                current_actor=actor,
                skill=turn_data.skill,
                damage_data=damage_data,
            )

            if not fast_mode:
                fields = []
                fields.append(FieldData(name="Target", value=to_name, inline=True))
                fields.append(FieldData(name=outcome_title, value="", inline=True))
                fields.append(FieldData(name="Target Health", value="", inline=True))
                yield fields
                await asyncio.sleep(0.5)

                fields = []
                fields.append(FieldData(name="Target", value=to_name, inline=True))
                fields.append(
                    FieldData(name=outcome_title, value=damage_info, inline=True)
                )
                fields.append(FieldData(name="Target Health", value="", inline=True))
                yield fields
                await asyncio.sleep(0.5)
                fields = []

            percentage = f"{round(remaiming_hp/target.max_hp * 100, 1)}".rstrip(
                "0"
            ).rstrip(".")
            display_hp = f"{percentage}%"

            applied_effect_display = ""
            for status_effect_type, stacks in damage_data.applied_status_effects:
                status_effect = await self.factory.get_status_effect(status_effect_type)
                if status_effect.display_status:
                    applied_effect_display += f"{status_effect.emoji}{stacks}"

            if applied_effect_display != "":
                display_hp = f"{display_hp} | `{applied_effect_display}`"

            fields.append(FieldData(name="Target", value=to_name, inline=True))
            fields.append(FieldData(name=outcome_title, value=damage_info, inline=True))
            fields.append(
                FieldData(name="Target Health", value=display_hp, inline=True)
            )
            yield fields

    async def get_aoe_skill_data(
        self,
        turn_data: TurnData,
    ):
        actor = turn_data.actor

        fields = []
        await asyncio.sleep(0.5)

        content_map = {}

        for damage_data in turn_data.damage_data:
            target = damage_data.target
            to_name = f"<@{target.id}>"
            if target.is_enemy:
                to_name = f"*{target.name}*"

            outcome_title, damage_info = await self.get_embed_attack_data(
                current_actor=actor,
                skill=turn_data.skill,
                damage_data=damage_data,
            )

            content_map[target.id] = (to_name, outcome_title, damage_info)

            fields.append(FieldData(name="Target", value=to_name, inline=True))
            fields.append(FieldData(name=outcome_title, value="", inline=True))
            fields.append(FieldData(name="Target Health", value="", inline=True))

        yield fields

        await asyncio.sleep(0.5)

        fields = []
        for damage_data in turn_data.damage_data:
            target = damage_data.target

            to_name, outcome_title, damage_info = content_map[target.id]

            fields.append(FieldData(name="Target", value=to_name, inline=True))
            fields.append(FieldData(name=outcome_title, value=damage_info, inline=True))
            fields.append(FieldData(name="Target Health", value="", inline=True))

        yield fields

        await asyncio.sleep(0.5)

        fields = []
        for damage_data in turn_data.damage_data:
            target = damage_data.target
            to_name, outcome_title, damage_info = content_map[target.id]

            remaiming_hp = damage_data.hp
            percentage = f"{round(remaiming_hp/target.max_hp * 100, 1)}".rstrip(
                "0"
            ).rstrip(".")
            display_hp = f"{percentage}%"

            applied_effect_display = ""
            for status_effect_type, stacks in damage_data.applied_status_effects:
                status_effect = await self.factory.get_status_effect(status_effect_type)
                if status_effect.display_status:
                    applied_effect_display += f"{status_effect.emoji}{stacks}"

            full_isplay_hp = display_hp
            if applied_effect_display != "":
                full_isplay_hp += f" | `{applied_effect_display}`"

            fields.append(FieldData(name="Target", value=to_name, inline=True))
            fields.append(FieldData(name=outcome_title, value=damage_info, inline=True))
            fields.append(
                FieldData(name="Target Health", value=full_isplay_hp, inline=True)
            )

        yield fields

    def get_turn_embed(self, actor: Actor) -> discord.Embed:
        actor_name = f"{actor.name}"

        color = self.SYSTEM_MESSAGE_COLOR
        if actor.is_enemy:
            color = discord.Color.red()

        embed = discord.Embed(title="", description="", color=color)
        embed.set_author(name=actor_name, icon_url=actor.image_url)
        embed.set_thumbnail(url=actor.image_url)

        return embed

    def add_status_effect_to_embed(
        self, embed: discord.Embed, effect_data: EmbedDataCollection
    ) -> discord.Embed:
        for embed_data in effect_data.values():
            self.add_text_bar(embed, f"\n{embed_data.title}", embed_data.description)

    def get_status_effect_embed(
        self, actor: Actor, effect_data: EmbedDataCollection
    ) -> discord.Embed:
        actor_name = f"{actor.name}"

        color = self.SYSTEM_MESSAGE_COLOR
        if actor.is_enemy:
            color = discord.Color.red()

        embed = discord.Embed(title="", description="", color=color)
        embed.set_author(name=actor_name, icon_url=actor.image_url)
        embed.set_thumbnail(url=actor.image_url)

        for embed_data in effect_data.values():
            self.add_text_bar(embed, embed_data.title, embed_data.description)

        return embed

    def get_member_out_embed(
        self, actor: Actor, event_type: EncounterEventType, reason: str
    ) -> discord.Embed:
        actor_name = f"{actor.name}"

        content = f"{actor_name} left the encounter."
        if event_type == EncounterEventType.MEMBER_LEAVING:
            content += " They will be removed at the start of the next round."

        embed = discord.Embed(title="", description="", color=self.SYSTEM_MESSAGE_COLOR)
        embed.set_author(name=actor_name, icon_url=actor.image_url)
        self.add_text_bar(embed, "", content)

        if actor.image_url is not None:
            embed.set_thumbnail(url=actor.image_url)
        if reason is not None and len(reason) > 0:
            embed.add_field(name="Reason", value=reason)
        return embed

    def get_fight_disappear_embed(self, context: EncounterContext) -> discord.Embed:
        content = "This encounter timed out and is no longer available."

        embed = discord.Embed(title="", description="", color=self.SYSTEM_MESSAGE_COLOR)
        embed.set_author(
            name=self.bot.user.display_name, icon_url=self.bot.user.display_avatar.url
        )
        self.add_text_bar(embed, "", content)

        embed.set_thumbnail(url=context.opponent.image_url)
        return embed

    def add_spacer_to_embed(self, embed: discord.Embed) -> discord.Embed:
        embed.add_field(name="", value="")

    def add_turn_skip_to_embed(
        self, reason: str, actor: Actor, embed: discord.Embed
    ) -> discord.Embed:

        content = f"{actor.name}'s turn is skipped."
        self.add_text_bar(embed, "", content)
        if reason is not None and len(reason) > 0:
            embed.add_field(name="Reason", value=reason, inline=False)

    def get_turn_skip_embed(self, actor: Actor, reason: str) -> discord.Embed:
        actor_name = f"{actor.name}"

        content = f"{actor_name}'s turn is skipped."

        embed = discord.Embed(title="", description="", color=self.SYSTEM_MESSAGE_COLOR)
        embed.set_author(name=actor_name, icon_url=actor.image_url)
        self.add_text_bar(embed, "", content)

        if actor.image_url is not None:
            embed.set_thumbnail(url=actor.image_url)
        if reason is not None and len(reason) > 0:
            embed.add_field(name="Reason", value=reason, inline=False)
        return embed

    async def get_waiting_for_party_embed(self, party_size: int, opponent: Opponent):
        embed = discord.Embed(
            title="Waiting for players to arrive.", color=self.SYSTEM_MESSAGE_COLOR
        )

        message = f"Combat will initiate after {party_size} players join."
        self.add_text_bar(embed, "", message)

        embed.set_thumbnail(url=opponent.image_url)
        return embed

    async def get_initiation_embed(self, wait_time: float, opponent: Opponent):
        embed = discord.Embed(
            title="Get Ready to Fight!", color=self.SYSTEM_MESSAGE_COLOR
        )

        now = datetime.datetime.now().timestamp()
        timer = int(now + wait_time)

        message = f"Combat will start <t:{timer}:R>."
        embed.add_field(name=message, value="", inline=False)

        text = "Waiting for players to join."
        self.add_text_bar(embed, "", text)

        embed.set_thumbnail(url=opponent.image_url)
        return embed

    async def get_round_embed(self, context: EncounterContext, cont: bool = False):
        title = "New Round"
        if cont:
            title = "Round Continued.."
        embed = discord.Embed(title=title, color=self.SYSTEM_MESSAGE_COLOR)

        round_count = context.round_number
        self.add_text_bar(
            embed, "", f"Round {round_count}", Config.COMBAT_EMBED_MAX_WIDTH
        )

        initiative_list = context.initiative
        current_actor = context.current_actor
        initiative_display = ""

        for idx, actor in enumerate(initiative_list):
            if actor.is_out:
                continue
            number = idx + 1
            fraction = actor.current_hp / actor.max_hp
            if fraction == 1:
                percentage = f"{int( fraction * 100 )}"
            else:
                percentage = f"{( fraction * 100 ):.1f}"
            name = actor.name[:20]

            display_hp = f"{percentage}"
            display_hp_width = 7
            spacing = " " * max(0, (display_hp_width - len(display_hp) - 3))
            display_hp = f"{spacing}[{display_hp}%]"

            status_effects = ""
            if actor.defeated:
                status_effects = "💀"
            else:
                for effect in actor.status_effects:
                    if (
                        effect.status_effect.display_status
                        and effect.remaining_stacks > 0
                    ):
                        status_effects += (
                            f"{effect.status_effect.emoji}{effect.remaining_stacks}"
                        )

            if actor.id == current_actor.id:
                name = f">> {name} <<"

            width = Config.COMBAT_EMBED_MAX_WIDTH
            line = f"\n{number}. {display_hp} {name}"
            available = width - len(line) - 3

            if len(status_effects) <= 0:
                initiative_display += line
            elif len(status_effects) < available:
                line += f" {status_effects}"
                initiative_display += line
            else:
                initiative_display += f"{line}"
                spacing = " " * (len(f"\n{number}. {display_hp} "))
                initiative_display += f"\n   ╚ {status_effects}"

        initiative_display = f"```python\n{initiative_display}```"
        embed.add_field(name="Turn Order:", value=initiative_display, inline=False)

        embed.set_thumbnail(url=self.bot.user.display_avatar)
        return embed

    def get_notification_embed(
        self, title: str, message: str, actor: Actor = None
    ) -> discord.Embed:
        embed = discord.Embed(title=title, color=self.SYSTEM_MESSAGE_COLOR)
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

    def get_actor_join_request_embed(
        self,
        user: discord.Member,
        owner: discord.Member,
    ) -> discord.Embed:
        title = "A new player requests to join the battle!"
        message = f"{user.display_name} arrived! They need to be approved by the encounter owner {owner.display_name} to join the fight."
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

    async def get_gear_embed(
        self,
        gear: Gear,
        character: Character,
        show_data: bool = True,
        show_info: bool = False,
        equipped: bool = False,
        show_locked_state: bool = False,
        scrap_value: int = None,
        max_width: int = None,
        show_boundaries: bool = False,
    ) -> discord.Embed:
        enchantment_data = None
        if len(gear.enchantments) > 0:
            enchantment_data = []
            for enchantment in gear.enchantments:
                data = await self.enchantment_manager.get_gear_enchantment(
                    character, enchantment
                )
                enchantment_data.append(data)

        modifier_boundaries: dict[GearModifierType, tuple[float, float]] = None
        if show_boundaries:
            modifier_boundaries = {}
            for modifier_type, _ in gear.modifiers.items():
                if modifier_type == GearModifierType.CRANGLED:
                    continue
                modifier_boundaries[modifier_type] = (
                    await self.gear_manager.get_modifier_boundaries(
                        gear.base, gear.level, modifier_type
                    )
                )

        return gear.get_embed(
            show_data=show_data,
            show_info=show_info,
            equipped=equipped,
            show_locked_state=show_locked_state,
            scrap_value=scrap_value,
            max_width=max_width,
            enchantment_data=enchantment_data,
            modifier_boundaries=modifier_boundaries,
        )
