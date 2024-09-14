import asyncio
import datetime
import random
from abc import ABC, abstractmethod

import discord
from discord.ext import commands

from combat.actors import Actor, Opponent
from combat.encounter import EncounterContext
from combat.enemies import *  # noqa: F403
from combat.skills.skill import Skill
from combat.skills.types import (
    SkillEffect,
    SkillInstance,
    StatusEffectApplication,
)
from control.combat.combat_actor_manager import CombatActorManager
from control.combat.combat_embed_manager import CombatEmbedManager
from control.combat.combat_gear_manager import CombatGearManager
from control.combat.combat_skill_manager import CombatSkillManager
from control.combat.context_loader import ContextLoader
from control.combat.object_factory import ObjectFactory
from control.combat.status_effect_manager import CombatStatusEffectManager
from control.controller import Controller
from control.item_manager import ItemManager
from control.logger import BotLogger
from control.service import Service
from control.settings_manager import SettingsManager
from datalayer.database import Database
from events.bot_event import BotEvent
from events.combat_event import CombatEvent
from events.types import CombatEventType


class EnemyController(Service, ABC):

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
        self.skill_manager: CombatSkillManager = self.controller.get_service(
            CombatSkillManager
        )
        self.actor_manager: CombatActorManager = self.controller.get_service(
            CombatActorManager
        )
        self.embed_manager: CombatEmbedManager = self.controller.get_service(
            CombatEmbedManager
        )
        self.gear_manager: CombatGearManager = self.controller.get_service(
            CombatGearManager
        )
        self.status_effect_manager: CombatStatusEffectManager = (
            self.controller.get_service(CombatStatusEffectManager)
        )
        self.context_loader: ContextLoader = self.controller.get_service(ContextLoader)
        self.factory: ObjectFactory = self.controller.get_service(ObjectFactory)
        self.log_name = "Enemy"

    async def listen_for_event(self, event: BotEvent):
        pass

    @abstractmethod
    async def calculate_opponent_turn(self, context: EncounterContext):
        pass

    @abstractmethod
    async def intro(self, encounter_id: int):
        pass

    @abstractmethod
    async def on_defeat(self, context: EncounterContext, opponent: Opponent):
        pass

    def get_notification_embed(
        self, title: str, message: str, img_url: str = None
    ) -> discord.Embed:
        embed = discord.Embed(title=title, color=discord.Colour.red())
        self.embed_manager.add_text_bar(embed, "", message, max_width=56)
        if img_url is not None:
            embed.set_image(url=img_url)
        return embed

    async def send_story_box(
        self,
        title: str,
        message: str,
        thread: discord.Thread,
        img_url: str = None,
        wait: float = None,
    ):
        if img_url is not None:
            embed = discord.Embed(color=discord.Colour.red())
            embed.set_image(url=img_url)
            await thread.send("", embed=embed)
            await asyncio.sleep(1)

        embed = self.get_notification_embed(title, message)
        await thread.send("", embed=embed)

        if wait is None:
            wait = max(len(message) * 0.085, 4)

        if img_url is not None:
            wait += 1
        await asyncio.sleep(wait)

    async def handle_turn(self, context: EncounterContext):
        turn_data = await self.calculate_opponent_turn(context)
        opponent = context.opponent

        for turn in turn_data:
            await self.context_loader.append_embed_generator_to_round(
                context, self.embed_manager.handle_actor_turn_embed(turn, context)
            )

            if turn.post_embed_data is not None:
                await self.context_loader.append_embeds_to_round(
                    context, opponent, turn.post_embed_data
                )

            for target, damage_instance, _ in turn.damage_data:
                total_damage = await self.actor_manager.get_skill_damage_after_defense(
                    target, turn.skill, damage_instance.scaled_value
                )
                outcome = (
                    await self.status_effect_manager.handle_post_attack_status_effects(
                        context,
                        opponent,
                        target,
                        turn.skill,
                        damage_instance,
                    )
                )
                if outcome.embed_data is not None:
                    await self.context_loader.append_embeds_to_round(
                        context, opponent, outcome.embed_data
                    )

                for skill_status_effect in turn.skill.base_skill.status_effects:
                    application_value = None
                    match skill_status_effect.application:
                        case StatusEffectApplication.ATTACK_VALUE:
                            if turn.skill.base_skill.skill_effect == SkillEffect.BUFF:
                                application_value = turn.skill.base_skill.base_value
                            else:
                                application_value = total_damage
                        case StatusEffectApplication.MANUAL_VALUE:
                            application_value = skill_status_effect.application_value
                        case StatusEffectApplication.DEFAULT:
                            if total_damage <= 0:
                                application_value = total_damage

                    target = context.get_actor_by_id(target.id)

                    status_effect_target = target
                    if skill_status_effect.self_target:
                        status_effect_target = opponent

                    application_chance = skill_status_effect.application_chance
                    if damage_instance.is_crit:
                        application_chance = min(1, application_chance * 2)

                    if random.random() < application_chance:
                        await self.status_effect_manager.apply_status(
                            context,
                            opponent,
                            status_effect_target,
                            skill_status_effect.status_effect_type,
                            skill_status_effect.stacks,
                            application_value,
                        )

                event = CombatEvent(
                    datetime.datetime.now(),
                    context.encounter.guild_id,
                    context.encounter.id,
                    opponent.id,
                    target.id,
                    turn.skill.base_skill.skill_type,
                    total_damage,
                    total_damage,
                    None,
                    CombatEventType.ENEMY_TURN_STEP,
                )
                await self.controller.dispatch_event(event)
            event = CombatEvent(
                datetime.datetime.now(),
                context.encounter.guild_id,
                context.encounter.id,
                opponent.id,
                None,
                turn.skill.base_skill.skill_type,
                None,
                None,
                None,
                CombatEventType.ENEMY_TURN,
            )
            await self.controller.dispatch_event(event)

    async def calculate_aoe_skill(
        self,
        context: EncounterContext,
        skill: Skill,
        available_targets: list[Actor],
        hp_cache: dict[int, int],
    ) -> tuple[list[tuple[Actor, SkillInstance, float], dict[str, str]]]:
        damage_data = []
        post_embed_data = {}

        for target in available_targets:
            outcome = await self.status_effect_manager.handle_attack_status_effects(
                context, context.opponent, skill
            )
            if outcome.embed_data is not None:
                post_embed_data = post_embed_data | outcome.embed_data

            instances = await self.skill_manager.get_skill_effect(
                context.opponent, skill, combatant_count=context.combat_scale
            )
            instance = instances[0]
            instance.apply_effect_outcome(outcome)

            current_hp = hp_cache.get(target.id, target.current_hp)

            outcome = (
                await self.status_effect_manager.handle_on_damage_taken_status_effects(
                    context,
                    target,
                    skill,
                )
            )
            if outcome.embed_data is not None:
                post_embed_data = post_embed_data | outcome.embed_data

            instance.apply_effect_outcome(outcome)

            total_damage = await self.actor_manager.get_skill_damage_after_defense(
                target, skill, instance.scaled_value
            )
            new_target_hp = min(max(0, current_hp - total_damage), target.max_hp)
            hp_cache[target.id] = new_target_hp

            damage_data.append((target, instance, new_target_hp))
        return damage_data, post_embed_data
