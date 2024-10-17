import asyncio
import datetime

from combat.encounter import EncounterContext
from combat.engine.states.state import State
from combat.engine.types import StateType
from combat.gear.types import Base, Rarity
from config import Config
from control.controller import Controller
from control.types import UserSettingType
from events.beans_event import BeansEvent
from events.bot_event import BotEvent
from events.types import BeansEventType
from items.types import ItemType
from view.combat.special_drop import SpecialDropView


class LootPayoutState(State):
    BOSS_KEY = {
        3: ItemType.DADDY_KEY,
        6: ItemType.WEEB_KEY,
        9: None,
        12: None,
    }

    def __init__(self, controller: Controller, context: EncounterContext):
        super().__init__(controller, context)
        self.state_type: StateType = StateType.LOOT_PAYOUT
        self.next_state: StateType = None

    async def startup(self):
        context = self.context
        loot = await self.gear_manager.roll_enemy_loot(context)

        now = datetime.datetime.now()

        for member, member_loot in loot.items():

            await asyncio.sleep(1)
            beans = member_loot[0]
            embeds = []
            loot_head_embed = await self.embed_manager.get_loot_embed(member, beans)
            embeds.append(loot_head_embed)

            message = await self.discord.send_message(
                context.thread, content=f"<@{member.id}>", embeds=embeds
            )

            event = BeansEvent(
                now,
                member.guild.id,
                BeansEventType.COMBAT_LOOT,
                member.id,
                beans,
            )
            await self.controller.dispatch_event(event)

            auto_scrap = await self.user_settings_manager.get(
                member.id, context.encounter.guild_id, UserSettingType.AUTO_SCRAP
            )
            if auto_scrap is None:
                auto_scrap = 0
            auto_scrap = int(auto_scrap)

            gear_to_scrap = []
            for drop in member_loot[1]:
                if (
                    drop.level <= auto_scrap
                    and drop.base.base_type != Base.SKILL
                    and drop.base.base_type != Base.ENCHANTMENT
                    and drop.rarity != Rarity.UNIQUE
                ):
                    gear_to_scrap.append(drop)
                    continue
                embeds.append(drop.get_embed())
                await asyncio.sleep(1)
                await self.discord.edit_message(message, embeds=embeds)

            if len(gear_to_scrap) > 0:
                total_scrap = await self.gear_manager.scrap_gear(
                    member, context.encounter.guild_id, gear_to_scrap
                )
                scrap_embed = await self.embed_manager.get_loot_scrap_embed(
                    member, total_scrap, auto_scrap
                )
                embeds.append(scrap_embed)
                await asyncio.sleep(1)
                await self.discord.edit_message(message, embeds=embeds)

            item = member_loot[2]

            if item is not None:
                item = await self.item_manager.give_item(
                    member.guild.id, member.id, item
                )
                embeds.append(
                    item.get_embed(self.bot, show_title=True, show_price=False)
                )
                await asyncio.sleep(1)

                await self.discord.edit_message(message, embeds=embeds)

        if await self.drop_boss_key_check(context):
            item_type = self.BOSS_KEY[context.encounter.enemy_level]
            if item_type is None:
                return
            item = await self.item_manager.get_item(context.thread.guild.id, item_type)
            view = SpecialDropView(
                self.controller,
                context.encounter.id,
                item,
                delay=Config.BOSS_KEY_CLAIM_DELAY,
            )
            embed = self.embed_manager.get_special_item_embed(
                item, delay_claim=Config.BOSS_KEY_CLAIM_DELAY
            )
            message = await self.discord.send_message(
                context.thread, embed=embed, view=view
            )
            view.set_message(message)

        self.done = True
        self.quit = True

    async def handle(self, event: BotEvent) -> bool:
        return False

    async def update(self):
        pass

    async def drop_boss_key_check(self, context: EncounterContext) -> bool:
        guild = context.thread.guild
        guild_level = await self.database.get_guild_level(guild.id)

        if context.encounter.enemy_level != guild_level:
            return False
        if context.encounter.enemy_level == Config.MAX_LVL:
            return False
        if guild_level not in Config.BOSS_LEVELS:
            return False

        progress, requirement = await self.database.get_guild_level_progress(
            guild.id, guild_level
        )

        return progress == requirement
