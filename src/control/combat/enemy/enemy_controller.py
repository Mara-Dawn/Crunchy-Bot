from abc import ABC, abstractmethod

import discord
from combat.actors import Actor
from combat.encounter import EncounterContext
from combat.enemies import *  # noqa: F403
from combat.skills.skill import Skill
from combat.skills.types import SkillInstance
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
from discord.ext import commands
from events.bot_event import BotEvent


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
    async def handle_turn(self, context: EncounterContext):
        pass

    async def calculate_aoe_skill(
        self,
        context: EncounterContext,
        skill: Skill,
        available_targets: list[Actor],
        hp_cache: dict[int, int],
    ) -> tuple[list[tuple[Actor, SkillInstance, float], discord.Embed]]:
        damage_data = []

        effect_modifier, post_embed = (
            await self.status_effect_manager.handle_attack_status_effects(
                context, context.opponent, skill
            )
        )
        for target in available_targets:
            instances = await self.skill_manager.get_skill_effect(
                context.opponent, skill, combatant_count=context.get_combat_scale()
            )
            instance = instances[0]
            instance.apply_effect_modifier(effect_modifier)

            if target.id not in hp_cache:
                current_hp = await self.actor_manager.get_actor_current_hp(
                    target, context.combat_events
                )
            else:
                current_hp = hp_cache[target.id]

            total_damage = await self.actor_manager.get_skill_damage_after_defense(
                target, skill, instance.scaled_value
            )
            new_target_hp = min(max(0, current_hp - total_damage), target.max_hp)
            hp_cache[target.id] = new_target_hp

            damage_data.append((target, instance, new_target_hp))
        return damage_data, post_embed
