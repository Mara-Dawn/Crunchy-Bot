from dataclasses import dataclass

import discord
from discord.ext import commands

from combat.encounter import EncounterContext
from combat.skills.types import SkillEffect, SkillType
from combat.status_effects.types import StatusEffectType
from control.combat.object_factory import ObjectFactory
from control.controller import Controller
from control.logger import BotLogger
from control.service import Service
from datalayer.database import Database
from events.bot_event import BotEvent
from events.combat_event import CombatEvent
from events.types import CombatEventType


@dataclass
class EncounterStatistic:
    label: str
    member_id: int
    info: str
    value: str

    def add_to_embed(self, embed: discord.Embed):
        content = f"<@{self.member_id}>: "
        content += f"**{self.value}**"
        if self.info is not None:
            content += f" *[{self.info}]*"
        embed.add_field(
            name=self.label,
            value=content,
            inline=False,
        )
        return embed


class EncounterStatistics(Service):

    def __init__(
        self,
        bot: commands.Bot,
        logger: BotLogger,
        database: Database,
        controller: Controller,
    ):
        super().__init__(bot, logger, database)
        self.controller = controller
        self.factory: ObjectFactory = self.controller.get_service(ObjectFactory)
        self.log_name = "EncounterStatistics"

    async def listen_for_event(self, event: BotEvent):
        pass

    async def add_to_embed(self, context: EncounterContext, embed: discord.Embed):
        stat = await self.get_highest_hit(context)
        if stat is not None:
            stat.add_to_embed(embed)

        stat = await self.get_highest_total_damage(context)
        if stat is not None:
            stat.add_to_embed(embed)

        stat = await self.get_highest_total_damage_taken(context)
        if stat is not None:
            stat.add_to_embed(embed)

        stat = await self.get_highest_total_healed(context)
        if stat is not None:
            stat.add_to_embed(embed)

    async def get_highest_hit(self, context: EncounterContext):
        max_hit: CombatEvent | None = None

        for event in context.combat_events:
            if event.combat_event_type == CombatEventType.MEMBER_TURN_STEP:
                if event.skill_value is None or event.skill_value <= 0:
                    continue
                skill = await self.factory.get_base_skill(event.skill_type)

                if skill.skill_effect not in [
                    SkillEffect.MAGICAL_DAMAGE,
                    SkillEffect.PHYSICAL_DAMAGE,
                    SkillEffect.NEUTRAL_DAMAGE,
                    SkillEffect.EFFECT_DAMAGE,
                ]:
                    continue

                if max_hit is None:
                    max_hit = event
                if event.display_value > max_hit.display_value:
                    max_hit = event

        if max_hit is None:
            return None

        skill = await self.factory.get_base_skill(max_hit.skill_type)
        return EncounterStatistic(
            "Highest Hit", max_hit.member_id, skill.name, max_hit.display_value
        )

    async def get_highest_total_damage(self, context: EncounterContext):
        damage_sum = {}

        for event in context.combat_events:
            if event.combat_event_type in [
                CombatEventType.MEMBER_TURN_STEP,
                CombatEventType.STATUS_EFFECT_OUTCOME,
                CombatEventType.ENCHANTMENT_EFFECT_OUTCOME,
            ]:
                if event.skill_value is None or event.skill_value <= 0:
                    continue

                if event.skill_type in SkillType:
                    skill = await self.factory.get_base_skill(event.skill_type)

                    if skill.skill_effect not in [
                        SkillEffect.MAGICAL_DAMAGE,
                        SkillEffect.PHYSICAL_DAMAGE,
                        SkillEffect.NEUTRAL_DAMAGE,
                        SkillEffect.EFFECT_DAMAGE,
                    ]:
                        continue
                if event.skill_type in StatusEffectType:
                    status_effect = await self.factory.get_status_effect(
                        event.skill_type
                    )

                    if status_effect.skill_effect not in [
                        SkillEffect.MAGICAL_DAMAGE,
                        SkillEffect.PHYSICAL_DAMAGE,
                        SkillEffect.NEUTRAL_DAMAGE,
                        SkillEffect.EFFECT_DAMAGE,
                    ]:
                        continue

                if event.member_id not in damage_sum:
                    damage_sum[event.member_id] = event.display_value
                    continue

                damage_sum[event.member_id] += event.display_value

        if len(damage_sum) == 0:
            return None

        highest_dmg_member_id = max(damage_sum, key=damage_sum.get)

        dmg_total = sum(damage_sum.values())
        percentage = damage_sum[highest_dmg_member_id] / dmg_total

        return EncounterStatistic(
            "Highest Total Damage",
            highest_dmg_member_id,
            f"{int(percentage*100)}%",
            damage_sum[highest_dmg_member_id],
        )

    async def get_highest_total_damage_taken(self, context: EncounterContext):
        damage_sum = {}

        for event in context.combat_events:
            if event.combat_event_type in [
                CombatEventType.ENEMY_TURN_STEP,
                CombatEventType.STATUS_EFFECT_OUTCOME,
                CombatEventType.ENCHANTMENT_EFFECT_OUTCOME,
            ]:
                if event.skill_value is None or event.skill_value <= 0:
                    continue
                if event.target_id < 0:
                    # exclude enemies
                    continue

                if event.skill_type in SkillType:
                    skill = await self.factory.get_base_skill(event.skill_type)

                    if skill.skill_effect not in [
                        SkillEffect.MAGICAL_DAMAGE,
                        SkillEffect.PHYSICAL_DAMAGE,
                        SkillEffect.NEUTRAL_DAMAGE,
                        SkillEffect.EFFECT_DAMAGE,
                    ]:
                        continue
                if event.skill_type in StatusEffectType:
                    status_effect = await self.factory.get_status_effect(
                        event.skill_type
                    )

                    if status_effect.skill_effect not in [
                        SkillEffect.MAGICAL_DAMAGE,
                        SkillEffect.PHYSICAL_DAMAGE,
                        SkillEffect.NEUTRAL_DAMAGE,
                        SkillEffect.EFFECT_DAMAGE,
                    ]:
                        continue

                if event.target_id not in damage_sum:
                    damage_sum[event.target_id] = event.display_value
                    continue

                damage_sum[event.target_id] += event.display_value

        if len(damage_sum) == 0:
            return None

        highest_dmg_member_id = max(damage_sum, key=damage_sum.get)

        dmg_total = sum(damage_sum.values())
        percentage = damage_sum[highest_dmg_member_id] / dmg_total

        return EncounterStatistic(
            "Highest Total Damage Taken",
            highest_dmg_member_id,
            f"{int(percentage*100)}%",
            damage_sum[highest_dmg_member_id],
        )

    async def get_highest_total_healed(self, context: EncounterContext):
        healing_sum = {}

        for event in context.combat_events:
            if event.combat_event_type in [
                CombatEventType.MEMBER_TURN_STEP,
                CombatEventType.STATUS_EFFECT_OUTCOME,
                CombatEventType.ENCHANTMENT_EFFECT_OUTCOME,
            ]:
                if event.skill_value is None or event.skill_value <= 0:
                    continue

                if event.skill_type in SkillType:
                    skill = await self.factory.get_base_skill(event.skill_type)

                    if skill.skill_effect not in [
                        SkillEffect.HEALING,
                    ]:
                        continue
                if event.skill_type in StatusEffectType:
                    status_effect = await self.factory.get_status_effect(
                        event.skill_type
                    )

                    if status_effect.skill_effect not in [
                        SkillEffect.HEALING,
                    ]:
                        continue

                if event.member_id not in healing_sum:
                    healing_sum[event.member_id] = event.display_value
                    continue

                healing_sum[event.member_id] += event.display_value

        if len(healing_sum) == 0:
            return None

        highest_healing_member_id = max(healing_sum, key=healing_sum.get)

        healing_total = sum(healing_sum.values())
        percentage = healing_sum[highest_healing_member_id] / healing_total

        return EncounterStatistic(
            "Highest Total Healing",
            highest_healing_member_id,
            f"{int(percentage*100)}%",
            healing_sum[highest_healing_member_id],
        )
