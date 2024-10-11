import asyncio
import datetime
import random
from abc import ABC, abstractmethod

import discord
from discord.ext import commands

from combat.actors import Actor, Opponent
from combat.effects.effect import EmbedDataCollection
from combat.encounter import EncounterContext, TurnDamageData, TurnData
from combat.enemies import *  # noqa: F403
from combat.skills.skill import Skill
from combat.skills.types import (
    SkillEffect,
    SkillTarget,
)
from combat.status_effects.types import StatusEffectApplication
from config import Config
from control.combat.combat_actor_manager import CombatActorManager
from control.combat.combat_embed_manager import CombatEmbedManager
from control.combat.combat_gear_manager import CombatGearManager
from control.combat.combat_skill_manager import CombatSkillManager
from control.combat.context_loader import ContextLoader
from control.combat.discord_manager import DiscordManager
from control.combat.effect_manager import CombatEffectManager
from control.combat.object_factory import ObjectFactory
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
        self.effect_manager: CombatEffectManager = self.controller.get_service(
            CombatEffectManager
        )
        self.context_loader: ContextLoader = self.controller.get_service(ContextLoader)
        self.factory: ObjectFactory = self.controller.get_service(ObjectFactory)
        self.discord: DiscordManager = self.controller.get_service(DiscordManager)
        self.log_name = "Enemy"

    async def listen_for_event(self, event: BotEvent):
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

            post_turn_embed_data = EmbedDataCollection()

            if turn.post_embed_data is not None:
                post_turn_embed_data.extend(turn.post_embed_data)

            for turn_damage_data in turn.damage_data:
                target = turn_damage_data.target
                damage_instance = turn_damage_data.instance

                total_damage = await self.actor_manager.get_skill_damage_after_defense(
                    target, turn.skill, damage_instance.scaled_value
                )
                outcome = await self.effect_manager.on_post_attack(
                    context,
                    opponent,
                    target,
                    turn.skill,
                    damage_instance,
                )
                if outcome.applied_effects is not None:
                    turn_damage_data.applied_status_effects.extend(
                        outcome.applied_effects
                    )

                if outcome.embed_data is not None:
                    post_turn_embed_data.extend(outcome.embed_data)

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
                        case StatusEffectApplication.RAW_ATTACK_VALUE:
                            application_value = (
                                await self.actor_manager.get_skill_damage_after_defense(
                                    target, turn.skill, damage_instance.raw_value
                                )
                            )

                    target = context.get_actor_by_id(target.id)

                    status_effect_target = target
                    if skill_status_effect.self_target:
                        status_effect_target = opponent

                    application_chance = skill_status_effect.application_chance
                    if damage_instance.is_crit:
                        application_chance = min(1, application_chance * 2)

                    if random.random() < application_chance:
                        outcome = await self.effect_manager.apply_status(
                            context,
                            opponent,
                            status_effect_target,
                            skill_status_effect.status_effect_type,
                            skill_status_effect.stacks,
                            application_value,
                        )

                        if outcome.embed_data is not None:
                            post_turn_embed_data.extend(outcome.embed_data)

                        if outcome.applied_effects is not None:
                            turn_damage_data.applied_status_effects.extend(
                                outcome.applied_effects
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

            context.current_turn_embed = self.embed_manager.get_turn_embed(opponent)
            await self.embed_manager.apply_attack_data_to_embed(
                context.current_turn_embed, turn
            )

            await self.discord.update_current_turn_embed_by_generator(
                context,
                self.embed_manager.get_actor_turn_embed_data(turn, context),
            )

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

            outcome = await self.effect_manager.on_post_skill(
                context,
                opponent,
                target,
                turn.skill,
            )
            if outcome.embed_data is not None:
                post_turn_embed_data.extend(outcome.embed_data)

            if post_turn_embed_data.length > 0:
                await asyncio.sleep(0.5)
                await self.discord.update_current_turn_embed(
                    context, post_turn_embed_data
                )

    async def calculate_aoe_skill(
        self,
        context: EncounterContext,
        skill: Skill,
        available_targets: list[Actor],
        hp_cache: dict[int, int],
    ) -> tuple[list[TurnDamageData], EmbedDataCollection]:
        skill_value_data = []
        post_embed_data = EmbedDataCollection()

        for target in available_targets:
            outcome = await self.effect_manager.on_attack(
                context, context.opponent, target, skill
            )
            if outcome.embed_data is not None:
                post_embed_data.extend(outcome.embed_data)

            instances = await self.skill_manager.get_skill_effect(
                context.opponent, skill, combatant_count=context.combat_scale
            )
            instance = instances[0]
            outcome.apply_to_instance(instance)

            current_hp = hp_cache.get(target.id, target.current_hp)

            if instance.value > 0:
                outcome = await self.effect_manager.on_damage_taken(
                    context,
                    target,
                    skill,
                )
                if outcome.embed_data is not None:
                    post_embed_data.extend(outcome.embed_data)
                    outcome.apply_to_instance(instance)

            total_damage = await self.actor_manager.get_skill_damage_after_defense(
                target, skill, instance.scaled_value
            )
            new_target_hp = min(max(0, current_hp - total_damage), target.max_hp)
            hp_cache[target.id] = new_target_hp

            damage_data = TurnDamageData(target, instance, new_target_hp)
            skill_value_data.append(damage_data)

        return skill_value_data, post_embed_data

    async def calculate_opponent_turn_data(
        self,
        context: EncounterContext,
        skill: Skill,
        available_targets: list[Actor],
        hp_cache: dict[int, int],
        max_skill_targets: int | None = None,
    ) -> TurnData:
        skill_value_data = []

        if skill.base_skill.default_target == SkillTarget.SELF:
            available_targets = [context.opponent]

        if skill.base_skill.aoe:
            skill_value_data, post_embed_data = await self.calculate_aoe_skill(
                context, skill, available_targets, hp_cache
            )
            return TurnData(
                actor=context.opponent,
                skill=skill,
                damage_data=skill_value_data,
                post_embed_data=post_embed_data,
            )

        damage_instances = await self.skill_manager.get_skill_effect(
            context.opponent, skill, combatant_count=context.combat_scale
        )
        post_embed_data = EmbedDataCollection()

        special_skill_modifier, description_override = (
            await self.skill_manager.get_special_skill_modifier(
                context,
                skill,
            )
        )

        skill_targets = []
        skill_target_ids = []

        for instance in damage_instances:
            if len(available_targets) <= 0:
                break

            if (
                skill.base_skill.max_targets is not None
                and len(skill_targets) >= skill.base_skill.max_targets
            ):
                target = random.choice(skill_targets)
            else:
                weights = []
                for actor in available_targets:
                    actor_weigt = 100
                    if actor in skill_targets:
                        actor_weigt = Config.ENEMY_RETARGET_WEIGHT
                    weights.append(actor_weigt)

                target = random.choices(available_targets, weights=weights)[0]

            skill_target_ids.append(target.id)
            if target not in skill_targets:
                skill_targets.append(target)

            current_hp = hp_cache.get(target.id, target.current_hp)

            outcome = await self.effect_manager.on_attack(
                context, context.opponent, target, skill
            )
            outcome.apply_to_instance(instance)
            if outcome.embed_data is not None:
                post_embed_data.extend(outcome.embed_data)

            if instance.value > 0:
                outcome = await self.effect_manager.on_damage_taken(
                    context,
                    target,
                    skill,
                )
                outcome.apply_to_instance(instance)
                if outcome.embed_data is not None:
                    post_embed_data.extend(outcome.embed_data)

            if special_skill_modifier != 1:
                instance.modifier *= special_skill_modifier

            total_damage = await self.actor_manager.get_skill_damage_after_defense(
                target, skill, instance.scaled_value
            )

            if skill.base_skill.skill_effect != SkillEffect.HEALING:
                total_damage *= -1

            new_target_hp = min(max(0, current_hp + total_damage), target.max_hp)

            damage_data = TurnDamageData(target, instance, new_target_hp)
            skill_value_data.append(damage_data)

            hp_cache[target.id] = new_target_hp
            available_targets = [
                actor
                for actor in available_targets
                if actor.id not in hp_cache
                or hp_cache[actor.id] > 0
                and (
                    max_skill_targets is None
                    or skill_target_ids.count(actor.id) < max_skill_targets
                )
            ]

        return TurnData(
            actor=context.opponent,
            skill=skill,
            damage_data=skill_value_data,
            post_embed_data=post_embed_data,
            description_override=description_override,
        )

    async def calculate_opponent_turn(
        self,
        context: EncounterContext,
    ) -> list[TurnData]:
        opponent = context.opponent

        available_skills = []

        sorted_skills = sorted(
            opponent.skills,
            key=lambda x: (
                x.base_skill.custom_value
                if x.base_skill.custom_value is not None
                else (
                    x.base_skill.base_value
                    if x.base_skill.skill_effect
                    not in [SkillEffect.HEALING, SkillEffect.BUFF]
                    else 100
                )
            ),
            reverse=True,
        )
        for skill in sorted_skills:
            skill_data = await self.skill_manager.get_skill_data(opponent, skill)
            if not skill_data.on_cooldown():
                available_skills.append(skill)

        skills_to_use = []

        for skill in available_skills:
            skills_to_use.append(skill)
            if len(skills_to_use) >= opponent.enemy.actions_per_turn:
                break

        available_targets = context.active_combatants

        hp_cache = {}
        turn_data = []
        for skill in skills_to_use:

            turn_data.append(
                await self.calculate_opponent_turn_data(
                    context, skill, available_targets, hp_cache
                )
            )
            available_targets = [
                actor
                for actor in available_targets
                if actor.id not in hp_cache or hp_cache[actor.id] > 0
            ]
            if len(available_targets) <= 0:
                break

        return turn_data
