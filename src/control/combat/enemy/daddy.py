import datetime

from combat.actors import Actor, Opponent
from combat.encounter import EncounterContext
from combat.enemies.types import EnemyType
from combat.skills.skill import Skill
from control.combat.enemy.enemy_controller import EnemyController
from events.bot_event import BotEvent
from events.encounter_event import EncounterEvent
from events.types import (
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
        message = "It's Daddys turn now."
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
            await self.discord.append_embed_to_round(context, embed)
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

    async def calculate_opponent_turn_data(
        self,
        context: EncounterContext,
        skill: Skill,
        available_targets: list[Actor],
        hp_cache: dict[int, int],
        max_skill_targets: int | None = None,
    ):
        return await super().calculate_opponent_turn_data(
            context, skill, available_targets, hp_cache, 2
        )
