import datetime
import random

from combat.actors import Actor, Opponent
from combat.encounter import EncounterContext, TurnData
from combat.skills.skill import Skill
from combat.skills.types import SkillEffect, SkillTarget
from control.combat.enemy.enemy_controller import EnemyController
from events.bot_event import BotEvent
from events.encounter_event import EncounterEvent
from events.types import (
    EncounterEventType,
)


class BasicEnemyController(EnemyController):

    async def listen_for_event(self, event: BotEvent):
        pass

    async def on_defeat(self, context: EncounterContext, opponent: Opponent):
        encounter_event_type = EncounterEventType.ENEMY_DEFEAT
        embed = self.embed_manager.get_actor_defeated_embed(opponent)
        await context.thread.send("", embed=embed)

        event = EncounterEvent(
            datetime.datetime.now(),
            context.encounter.guild_id,
            context.encounter.id,
            opponent.id,
            encounter_event_type,
        )
        await self.controller.dispatch_event(event)

    async def intro(self, encounter_id: int):
        pass

    async def calculate_opponent_turn_data(
        self,
        context: EncounterContext,
        skill: Skill,
        available_targets: list[Actor],
        hp_cache: dict[int, int],
    ):
        damage_data = []

        if skill.base_skill.default_target == SkillTarget.SELF:
            available_targets = [context.opponent]

        if skill.base_skill.aoe:
            damage_data, post_embed_data = await self.calculate_aoe_skill(
                context, skill, available_targets, hp_cache
            )
            return TurnData(
                actor=context.opponent,
                skill=skill,
                damage_data=damage_data,
                post_embed_data=post_embed_data,
            )

        damage_instances = await self.skill_manager.get_skill_effect(
            context.opponent, skill, combatant_count=context.get_combat_scale()
        )
        post_embed_data = {}

        special_skill_modifier, description_override = (
            await self.skill_manager.get_special_skill_modifier(
                context,
                skill,
            )
        )

        skill_targets = []

        for instance in damage_instances:
            if len(available_targets) <= 0:
                break

            if (
                skill.base_skill.max_targets is not None
                and len(skill_targets) >= skill.base_skill.max_targets
            ):
                target = random.choice(skill_targets)
            else:
                target = random.choice(available_targets)

            if target not in skill_targets:
                skill_targets.append(target)

            if target.id not in hp_cache:
                current_hp = await self.actor_manager.get_actor_current_hp(
                    target, context.combat_events
                )
            else:
                current_hp = hp_cache[target.id]

            context = await self.context_loader.load_encounter_context(
                context.encounter.id
            )
            outcome = await self.status_effect_manager.handle_attack_status_effects(
                context, context.opponent, skill
            )
            instance.apply_effect_outcome(outcome)
            if outcome.embed_data is not None:
                post_embed_data = post_embed_data | outcome.embed_data

            context = await self.context_loader.load_encounter_context(
                context.encounter.id
            )
            outcome = (
                await self.status_effect_manager.handle_on_damage_taken_status_effects(
                    context,
                    target,
                    skill,
                )
            )
            instance.apply_effect_outcome(outcome)
            if outcome.embed_data is not None:
                post_embed_data = post_embed_data | outcome.embed_data

            if special_skill_modifier != 1:
                instance.modifier *= special_skill_modifier

            total_damage = await self.actor_manager.get_skill_damage_after_defense(
                target, skill, instance.scaled_value
            )

            if skill.base_skill.skill_effect != SkillEffect.HEALING:
                total_damage *= -1

            new_target_hp = min(max(0, current_hp + total_damage), target.max_hp)

            damage_data.append((target, instance, new_target_hp))

            hp_cache[target.id] = new_target_hp
            available_targets = [
                actor
                for actor in available_targets
                if actor.id not in hp_cache or hp_cache[actor.id] > 0
            ]

        return TurnData(
            actor=context.opponent,
            skill=skill,
            damage_data=damage_data,
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
                x.base_skill.base_value
                if x.base_skill.skill_effect != SkillEffect.HEALING
                else 100
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

        available_targets = context.get_active_combatants()

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
