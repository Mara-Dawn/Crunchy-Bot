import asyncio
import datetime
import random

import discord
from combat.actors import Actor, Opponent
from combat.encounter import EncounterContext, TurnData
from combat.enemies.types import EnemyType
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


class DaddyController(EnemyController):
    BOSS_LEVEL = {
        EnemyType.DADDY_P2: 3,
        # 6: None,
        # 9: None,
        # 12: None,
    }

    async def listen_for_event(self, event: BotEvent):
        pass

    def get_notification_embed(
        self, title: str, message: str, actor: Actor = None
    ) -> discord.Embed:
        embed = discord.Embed(title=title, color=discord.Colour.red())
        self.embed_manager.add_text_bar(embed, "", message, max_width=56)
        return embed

    async def send_story_box(
        self, title: str, message: str, thread: discord.Thread, wait: float = None
    ):
        embed = self.get_notification_embed(title, message)
        await thread.send("", embed=embed)
        if wait is None:
            wait = max(len(message) * 0.085, 4)
        await asyncio.sleep(wait)

    async def intro(self, encounter_id: int):
        encounter = await self.database.get_encounter_by_encounter_id(encounter_id)
        thread_id = await self.database.get_encounter_thread(encounter_id)
        thread = self.bot.get_channel(encounter.channel_id).get_thread(thread_id)

        title = "> ~* The Door *~"
        intro_message = "As you gather around the artifact, the lights in the room start to dim and a rather plain looking door appears in front of you."
        await self.send_story_box(title, intro_message, thread)

        title = ""
        intro_message = "You firmly grasp its handle and slowly start to push it open."
        await self.send_story_box(title, intro_message, thread)

        title = "> ~* A Sensual Experience *~"
        intro_message = (
            "The very first thing you notice is a heavy, musky air pouring out of the newly formed gap, enveloping you with "
            "a sensual and spicy aroma that reminds you of tobacco, leather and wood."
        )
        await self.send_story_box(title, intro_message, thread)

        title = ""
        intro_message = (
            "A warm feeling of safety and content overcomes you, "
            "but for some yet unknown reason you feel a growing weakness in your knees."
        )
        await self.send_story_box(title, intro_message, thread)

        title = "> ~* Anticipation *~"
        intro_message = "You manage to catch yourself.\nWith new resolve, you proceed to fully open the door infront of you."
        await self.send_story_box(title, intro_message, thread)

        title = ""
        intro_message = "And there he is."
        await self.send_story_box(title, intro_message, thread)

        title = ""
        intro_message = (
            "Looking right into your soul with his gentle, yet commanding eyes."
        )
        await self.send_story_box(title, intro_message, thread)

        title = ""
        intro_message = "He smirks."
        await self.send_story_box(title, intro_message, thread)

        title = "> ~* He Is Here *~"
        intro_message = "'Come closer darling, Daddy is waiting for you.'"
        await self.send_story_box(title, intro_message, thread)

    async def phase_change(self, context: EncounterContext):
        thread = context.thread

        title = "> ~* Conclusion *~"
        message = (
            "Beaten and Bruised by those, that should have submitted to him long ago, Daddy musters "
            "up the strength he has left and pushes you away from him."
        )
        await self.send_story_box(title, message, thread)

        title = ""
        message = "He tumbles a few steps back, first one, then another."
        await self.send_story_box(title, message, thread)

        title = ""
        message = "Completely out of breath, he crouches over."
        await self.send_story_box(title, message, thread)

        title = ""
        message = "His legs are shaking, any minute now he will collapse."
        await self.send_story_box(title, message, thread)

        title = ""
        message = "You take a step forward to deliver the final blow."
        await self.send_story_box(title, message, thread)

        title = "> ~* Conclusion? *~"
        message = "But wait!"
        await self.send_story_box(title, message, thread)

        title = ""
        message = "Your instincts stop you from moving any further."
        await self.send_story_box(title, message, thread)

        title = ""
        message = "Cold sweat starts running down your neck as you feel an overwhelming sense of dread creeping up your spine."
        await self.send_story_box(title, message, thread)

        title = "> ~* Renewed Vigor *~"
        message = "Wham! Within an instant, Daddy regains his composure and stomps on the ground demandingly."
        await self.send_story_box(title, message, thread)

        title = ""
        message = "His eyes pierce your soul, his gaze now full of excitement and determination."
        await self.send_story_box(title, message, thread)

        title = "> ~* Playtime Is Over *~"
        message = "He rips away his shirt, exposing his firm and chiseled upper body."
        await self.send_story_box(title, message, thread)

        title = ""
        message = "With a wild, hungry grin he readies himself for his next move."
        await self.send_story_box(title, message, thread)

        title = "> ~* Round Two *~"
        message = "'Looks like we have a little brat over here. I know just the right way to deal with pets that dont behave.'"
        await self.send_story_box(title, message, thread)

        title = ""
        message = "Its Daddys turn now."
        await self.send_story_box(title, message, thread)

    async def defeat(self, context: EncounterContext):
        thread = context.thread

        title = "> ~* Conclusion *~"
        message = "You hear an agonizing groan as Daddy drops down to his knees."
        await self.send_story_box(title, message, thread)

        title = ""
        message = (
            "He looks up at you one last time, a single tear rolling down his face."
        )
        await self.send_story_box(title, message, thread, wait=13)

        title = ""
        message = "'See you later, alligator.'"
        await self.send_story_box(title, message, thread)

    async def on_defeat(self, context: EncounterContext, opponent: Opponent):
        if opponent.enemy.type == EnemyType.DADDY_P2:
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
        else:
            await self.phase_change(context)
            encounter_event_type = EncounterEventType.ENEMY_PHASE_CHANGE

        event = EncounterEvent(
            datetime.datetime.now(),
            context.encounter.guild_id,
            context.encounter.id,
            opponent.id,
            encounter_event_type,
        )
        await self.controller.dispatch_event(event)

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
                embed_data = (
                    await self.status_effect_manager.handle_post_attack_status_effects(
                        context,
                        opponent,
                        target,
                        turn.skill,
                        damage_instance,
                    )
                )
                if embed_data is not None:
                    await self.context_loader.append_embeds_to_round(
                        context, opponent, embed_data
                    )

                for skill_status_effect in turn.skill.base_skill.status_effects:
                    application_value = None
                    match skill_status_effect.application:
                        case StatusEffectApplication.ATTACK_VALUE:
                            application_value = damage_instance.scaled_value
                        case StatusEffectApplication.DEFAULT:
                            pass

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
