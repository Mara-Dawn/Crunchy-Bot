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
        EnemyType.WEEB_P1: 6,
        EnemyType.WEEB_P2: 6,
        EnemyType.WEEB_P3: 6,
    }

    async def listen_for_event(self, event: BotEvent):
        pass

    async def intro(self, encounter_id: int):
        encounter = await self.database.get_encounter_by_encounter_id(encounter_id)
        thread_id = await self.database.get_encounter_thread(encounter_id)
        thread = self.bot.get_channel(encounter.channel_id).get_thread(thread_id)

        title = ""
        intro_message = "Ooo ho ho, what is this? A great and terrible object, from a time long past..."
        await self.send_story_box(
            title, intro_message, thread, img_url="https://i.imgur.com/VAtRjZK.png"
        )

        intro_message = "During the Dark Times, a great foe, a man made a demon! Ravaged these lands for a century. "
        await self.send_story_box(title, intro_message, thread)

        intro_message = (
            "It was said no mortal could kill the creature, but before our kingdom could be cast "
            "into fiery damnation, a great hero, sealed the beast away in this very object."
        )
        await self.send_story_box(title, intro_message, thread)

        intro_message = (
            "The seal has since weakened and is now about to fail! Will you, great warriors, fell the devil within "
            "that is ready to be unleashed? "
        )
        await self.send_story_box(title, intro_message, thread)

        intro_message = "Ready yourselves champions, steel your courage, and send this foul creature back into the dark abyss."
        await self.send_story_box(title, intro_message, thread)

        intro_message = "The object begins to rumble and falls from your hand."
        await self.send_story_box(title, intro_message, thread)

        intro_message = (
            "A shockwave sends you flying backwards as a CRACK bellows from the object."
        )
        await self.send_story_box(title, intro_message, thread)

        intro_message = "The seal flips open, a blinding light bursts forth! "
        await self.send_story_box(
            title, intro_message, thread, img_url="https://i.imgur.com/KOUFuax.png"
        )

        intro_message = (
            "The cute cat ears, that slightly attractive femboy demeanour, confused sexual "
            "feelings twist inside you, this isn't some regular hell spawn.. "
        )
        await self.send_story_box(title, intro_message, thread)

        intro_message = "This is the pinnacle of depravity"
        await self.send_story_box(title, intro_message, thread)

        intro_message = "Virginity ascended"
        await self.send_story_box(title, intro_message, thread)

        intro_message = "A Weeb!"
        await self.send_story_box(
            title, intro_message, thread, img_url="https://i.imgur.com/kauVRZ7.png"
        )

        intro_message = (
            "'Sugoi!', the great demon squeals, hugging its body pillow and blushing."
        )
        await self.send_story_box(title, intro_message, thread)

        intro_message = (
            "'Yamete kudasai, my precious kawaii Nami belongs to me', it tugs at the pillow harder and pouts, "
            "'you can't have her baka!'."
        )
        await self.send_story_box(title, intro_message, thread)

        intro_message = "The demon screams, 'TATAKAI!!!'"
        await self.send_story_box(title, intro_message, thread)

        context = await self.context_loader.load_encounter_context(encounter_id)
        event = EncounterEvent(
            datetime.datetime.now(),
            context.encounter.guild_id,
            context.encounter.id,
            context.opponent.id,
            EncounterEventType.ENEMY_PHASE_CHANGE,
        )
        await self.controller.dispatch_event(event)

    async def phase_change_one(self, context: EncounterContext):
        thread = context.thread

        title = "> ~* Conclusion *~"
        message = "SIgh"
        await self.send_story_box(
            title, message, thread, img_url="https://i.imgur.com/IjTRslE.png"
        )

        title = "> ~* Conclusion *~"
        message = "EyeGlow"
        await self.send_story_box(
            title, message, thread, img_url="https://i.imgur.com/AXwZnLk.png"
        )

        title = "> ~* Conclusion *~"
        message = "Electro"
        await self.send_story_box(
            title, message, thread, img_url="https://i.imgur.com/TgaCkkd.png"
        )

        title = "> ~* Conclusion *~"
        message = "Sayan"
        await self.send_story_box(
            title, message, thread, img_url="https://i.imgur.com/NqBCRA1.png"
        )

    async def phase_change_two(self, context: EncounterContext):
        thread = context.thread

        title = "> ~* Conclusion *~"
        message = "Feet Transform"
        await self.send_story_box(
            title, message, thread, img_url="https://i.imgur.com/yKOyQqr.png"
        )

        title = "> ~* Conclusion *~"
        message = "Feet Transform"
        await self.send_story_box(
            title, message, thread, img_url="https://i.imgur.com/FFCi2bh.png"
        )

        title = "> ~* Conclusion *~"
        message = "Cat Tiara appears"
        await self.send_story_box(
            title, message, thread, img_url="https://i.imgur.com/YAiviPk.png"
        )

        title = "> ~* Conclusion *~"
        message = "Wand"
        await self.send_story_box(
            title, message, thread, img_url="https://i.imgur.com/nQsHtje.png"
        )

        title = "> ~* Conclusion *~"
        message = "girl"
        await self.send_story_box(
            title, message, thread, img_url="https://i.imgur.com/cm6h34f.png"
        )

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
            if outcome.embed_data is not None:
                post_embed_data = post_embed_data | outcome.embed_data

            instance.apply_effect_outcome(outcome)

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
