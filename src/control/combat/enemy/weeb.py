import datetime
import random

from combat.actors import Actor, Opponent
from combat.encounter import EncounterContext, TurnData
from combat.enemies.types import EnemyType
from combat.skills.skill import Skill
from combat.skills.types import SkillEffect, SkillTarget
from control.combat.enemy.enemy_controller import EnemyController
from events.bot_event import BotEvent
from events.encounter_event import EncounterEvent
from events.types import (
    EncounterEventType,
)


class WeebController(EnemyController):
    BOSS_LEVEL = {
        EnemyType.WEEB_P2: 6,
        EnemyType.WEEB_P3: 6,
    }

    async def listen_for_event(self, event: BotEvent):
        pass

    async def intro(self, encounter_id: int):
        encounter = await self.database.get_encounter_by_encounter_id(encounter_id)
        thread_id = await self.database.get_encounter_thread(encounter_id)
        thread = self.bot.get_channel(encounter.channel_id).get_thread(thread_id)

        title = "> ~* The Door *~"
        intro_message = "As you gather around the artifact, the lights in the room start to dim and a rather plain looking door appears in front of you."
        await self.send_story_box(title, intro_message, thread)

    async def phase_change_one(self, context: EncounterContext):
        thread = context.thread

        title = "> ~* Conclusion *~"
        message = (
            "Beaten and Bruised by those, that should have submitted to him long ago, Daddy musters "
            "up the strength he has left and pushes you away from him."
        )
        await self.send_story_box(title, message, thread)

    async def phase_change_two(self, context: EncounterContext):
        thread = context.thread

        title = "> ~* Conclusion *~"
        message = (
            "Beaten and Bruised by those, that should have submitted to him long ago, Daddy musters "
            "up the strength he has left and pushes you away from him."
        )
        await self.send_story_box(title, message, thread)

    async def defeat(self, context: EncounterContext):
        thread = context.thread

        title = "> ~* Conclusion *~"
        message = "You hear an agonizing groan as Daddy drops down to his knees."
        await self.send_story_box(title, message, thread)

    async def on_defeat(self, context: EncounterContext, opponent: Opponent):
        if opponent.enemy.type == EnemyType.WEEB_P1:
            await self.phase_change_one(context)
            encounter_event_type = EncounterEventType.ENEMY_PHASE_CHANGE
        elif opponent.enemy.type == EnemyType.WEEB_P2:
            await self.phase_change_two(context)
            encounter_event_type = EncounterEventType.ENEMY_PHASE_CHANGE
        else:
            await self.defeat(context)
            encounter_event_type = EncounterEventType.ENEMY_DEFEAT
            embed = self.embed_manager.get_actor_defeated_embed(opponent)
            await context.thread.send("", embed=embed)
            guild_level = await self.database.get_guild_level(context.thread.guild.id)
            if guild_level == self.BOSS_LEVEL[opponent.enemy.type]:
                guild_level += 1
                await self.database.set_guild_level(
                    context.thread.guild.id, guild_level
                )

        event = EncounterEvent(
            datetime.datetime.now(),
            context.encounter.guild_id,
            context.encounter.id,
            opponent.id,
            encounter_event_type,
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

        targets = []

        for instance in damage_instances:
            if len(available_targets) <= 0:
                break

            target = random.choice(available_targets)
            targets.append(target.id)

            if target.id not in hp_cache:
                current_hp = await self.actor_manager.get_actor_current_hp(
                    target, context.combat_events
                )
            else:
                current_hp = hp_cache[target.id]

            effect_modifier, instance_post_embed_data = (
                await self.status_effect_manager.handle_attack_status_effects(
                    context, context.opponent, skill
                )
            )
            instance.apply_effect_modifier(effect_modifier)
            if instance_post_embed_data is not None:
                post_embed_data = post_embed_data | instance_post_embed_data

            on_damage_effect_modifier, dmg_taken_embed_data = (
                await self.status_effect_manager.handle_on_damage_taken_status_effects(
                    context,
                    target,
                    skill,
                )
            )
            if dmg_taken_embed_data is not None:
                post_embed_data = post_embed_data | dmg_taken_embed_data

            instance.apply_effect_modifier(on_damage_effect_modifier)

            total_damage = await self.actor_manager.get_skill_damage_after_defense(
                target, skill, instance.scaled_value
            )

            new_target_hp = min(max(0, current_hp - total_damage), target.max_hp)

            damage_data.append((target, instance, new_target_hp))

            hp_cache[target.id] = new_target_hp
            available_targets = [
                actor
                for actor in available_targets
                if (actor.id not in hp_cache or hp_cache[actor.id] > 0)
                and targets.count(actor.id) < 2
            ]

        return TurnData(
            actor=context.opponent,
            skill=skill,
            damage_data=damage_data,
            post_embed_data=post_embed_data,
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
                if x.base_skill.skill_effect != SkillEffect.BUFF
                else 0
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
