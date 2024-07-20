import datetime
import random

from combat.actors import Actor, Opponent
from combat.encounter import EncounterContext, TurnData
from combat.skills.skill import Skill
from combat.skills.types import (
    StatusEffectApplication,
)
from control.combat.enemy.enemy_controller import EnemyController
from events.bot_event import BotEvent
from events.combat_event import CombatEvent
from events.encounter_event import EncounterEvent
from events.types import (
    CombatEventType,
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

    async def handle_turn(self, context: EncounterContext):
        turn_data = await self.calculate_opponent_turn(context)
        opponent = context.opponent

        for turn in turn_data:
            await self.context_loader.append_embed_generator_to_round(
                context, self.embed_manager.handle_actor_turn_embed(turn, context)
            )

            if turn.post_embed is not None:
                await self.context_loader.append_embed_to_round(
                    context, turn.post_embed
                )

            for target, damage_instance, _ in turn.damage_data:
                total_damage = await self.actor_manager.get_skill_damage_after_defense(
                    target, turn.skill, damage_instance.scaled_value
                )
                await self.status_effect_manager.handle_post_attack_status_effects(
                    context,
                    opponent,
                    target,
                    turn.skill,
                    damage_instance,
                )

                for skill_status_effect in turn.skill.base_skill.status_effects:
                    application_value = None
                    match skill_status_effect.application:
                        case StatusEffectApplication.ATTACK_VALUE:
                            application_value = damage_instance.scaled_value
                        case StatusEffectApplication.DEFAULT:
                            pass

                    context = await self.context_loader.load_encounter_context(
                        context.encounter.id
                    )
                    target = context.get_actor(target.id)

                    status_effect_target = target
                    if skill_status_effect.self_target:
                        status_effect_target = opponent

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
                    None,
                    CombatEventType.ENEMY_TURN,
                )
                await self.controller.dispatch_event(event)

    async def calculate_opponent_turn_data(
        self,
        context: EncounterContext,
        skill: Skill,
        available_targets: list[Actor],
        hp_cache: dict[int, int],
    ):
        damage_data = []

        if skill.base_skill.aoe:
            damage_data, post_embed = await self.calculate_aoe_skill(
                context, skill, available_targets, hp_cache
            )
            return TurnData(
                actor=context.opponent,
                skill=skill,
                damage_data=damage_data,
                post_embed=post_embed,
            )

        damage_instances = await self.skill_manager.get_skill_effect(
            context.opponent, skill, combatant_count=context.get_combat_scale()
        )
        post_embed = None

        for instance in damage_instances:
            if len(available_targets) <= 0:
                break

            target = random.choice(available_targets)

            if target.id not in hp_cache:
                current_hp = await self.actor_manager.get_actor_current_hp(
                    target, context.combat_events
                )
            else:
                current_hp = hp_cache[target.id]

            effect_modifier, instance_post_embed = (
                await self.status_effect_manager.handle_attack_status_effects(
                    context, context.opponent, skill
                )
            )
            instance.apply_effect_modifier(effect_modifier)
            if instance_post_embed is not None:
                post_embed = instance_post_embed

            total_damage = await self.actor_manager.get_skill_damage_after_defense(
                target, skill, instance.scaled_value
            )

            new_target_hp = min(max(0, current_hp - total_damage), target.max_hp)

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
            post_embed=post_embed,
        )

    async def calculate_opponent_turn(
        self,
        context: EncounterContext,
    ) -> list[TurnData]:
        opponent = context.opponent

        available_skills = []

        sorted_skills = sorted(
            opponent.skills, key=lambda x: x.base_skill.base_value, reverse=True
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
