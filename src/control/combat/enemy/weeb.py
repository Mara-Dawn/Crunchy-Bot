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
            await self.discord.append_embed_to_round(context, embed)
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
        max_skill_targets: int | None = None,
    ):
        return await super().calculate_opponent_turn_data(
            context, skill, available_targets, hp_cache, 2
        )
