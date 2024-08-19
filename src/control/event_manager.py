import copy
import datetime
from typing import Any

from discord.ext import commands

from bot_util import BotUtil
from control.controller import Controller
from control.item_manager import ItemManager
from control.logger import BotLogger
from control.service import Service
from control.settings_manager import SettingsManager
from datalayer.database import Database
from datalayer.lootbox import LootBox
from datalayer.stats import UserStats
from datalayer.types import UserInteraction
from events.bat_event import BatEvent
from events.bot_event import BotEvent
from events.jail_event import JailEvent
from events.notification_event import NotificationEvent
from events.prediction_event import PredictionEvent
from events.types import (
    BeansEventType,
    EventType,
    JailEventType,
    PredictionEventType,
)
from items.types import ItemType
from view.types import RankingType


class EventManager(Service):

    def __init__(
        self,
        bot: commands.Bot,
        logger: BotLogger,
        database: Database,
        controller: Controller,
    ):
        super().__init__(bot, logger, database)
        self.controller = controller
        self.item_manager: ItemManager = self.controller.get_service(ItemManager)
        self.settings_manager: SettingsManager = self.controller.get_service(
            SettingsManager
        )
        self.log_name = "Events"

    async def listen_for_event(self, event: BotEvent):
        synchronized = False
        if event.synchronized:
            return

        match event.type:
            case EventType.JAIL:
                jail_event: JailEvent = event
                if jail_event.jail_event_type is JailEventType.RELEASE:
                    await self.database.log_jail_release(
                        jail_event.jail_id, int(jail_event.get_timestamp())
                    )
                    self.logger.log(
                        jail_event.guild_id,
                        f"Jail sentence `{jail_event.jail_id}` marked as released.",
                        self.log_name,
                    )
            case EventType.NOTIFICATION:
                notification_event: NotificationEvent = event
                message = notification_event.message
                if message is not None:
                    await self.mod_notification(notification_event.guild_id, message)
                return
            case EventType.PREDICTION:
                prediction_event: PredictionEvent = event
                notification = None
                match prediction_event.prediction_event_type:
                    case PredictionEventType.SUBMIT:
                        notification = f"<@{prediction_event.member_id}> has submitted a new potential Beans Prediction! Check it out with `/beans prediction_moderation`."
                    case PredictionEventType.DENY:
                        notification = f"<@{prediction_event.member_id}> has denied Beans Prediction nr. **{prediction_event.prediction_id}**."
                    case PredictionEventType.APPROVE:
                        notification = f"<@{prediction_event.member_id}> has approved Beans Prediction nr. **{prediction_event.prediction_id}**."
                    case PredictionEventType.LOCK:
                        notification = f"<@{prediction_event.member_id}> has locked Prediction nr. **{prediction_event.prediction_id}**."
                    case PredictionEventType.UNLOCK:
                        notification = f"<@{prediction_event.member_id}> has unlocked Prediction nr. **{prediction_event.prediction_id}**."
                    case PredictionEventType.EDIT:
                        notification = f"<@{prediction_event.member_id}> made changes to Beans Prediction nr. **{prediction_event.prediction_id}**."
                    case PredictionEventType.RESOLVE:
                        notification = f"<@{prediction_event.member_id}> initiated payout for Beans Prediction nr. **{prediction_event.prediction_id}**."
                    case PredictionEventType.REFUND:
                        notification = f"<@{prediction_event.member_id}> ended and refunded Beans Prediction nr. **{prediction_event.prediction_id}**."

                if notification is not None:
                    await self.mod_notification(prediction_event.guild_id, notification)
            case EventType.COMBAT:
                synchronized = True
            case EventType.ENCOUNTER:
                synchronized = True
            case EventType.STATUS_EFFECT:
                synchronized = True

        from_user = event.get_causing_user_id()
        args = event.get_type_specific_args()
        event_id = await self.database.log_event(event)
        self.__log_event(event, from_user, *args)

        if synchronized:
            sync_event = copy.deepcopy(event)
            sync_event.synchronized = True
            sync_event.id = event_id
            await self.controller.dispatch_event(sync_event)

    def __log_event(self, event: BotEvent, member_id: int, *args):
        event_type = event.type
        guild_id = event.guild_id
        parsed_args = []
        for arg in args:
            try:
                potential_user_id = int(arg)
            except (ValueError, TypeError):
                potential_user_id = None
            if potential_user_id is not None:
                name = BotUtil.get_name(self.bot, guild_id, potential_user_id, 30)
                if name is not None:
                    parsed_args.append(name)
                    continue
            parsed_args.append(arg)
        arguments = ", ".join([str(x) for x in parsed_args])
        self.logger.log(
            guild_id,
            f"{event_type.value} event was logged for {BotUtil.get_name(self.bot, guild_id, member_id, 30)}. Arguments: {arguments}",
            self.log_name,
        )

    async def mod_notification(self, guild_id: int, message: str):
        for channel_id in await self.settings_manager.get_mod_channels(guild_id):
            guild = self.bot.get_guild(guild_id)
            if guild is None:
                continue
            channel = guild.get_channel(channel_id)
            if channel is None:
                continue
            await channel.send(message)

    async def get_stunned_remaining(
        self, guild_id: int, user_id: int, base_duration: int
    ) -> int:
        last_bat_event: BatEvent = await self.database.get_last_bat_event_by_target(
            guild_id, user_id
        )

        if last_bat_event is None:
            return 0

        last_bat_time = last_bat_event.datetime
        last_bat_duration = last_bat_event.duration
        if last_bat_duration is None:
            last_bat_duration = base_duration

        diff = datetime.datetime.now() - last_bat_time
        if int(diff.total_seconds() / 60) <= last_bat_duration:
            release_timestamp = last_bat_time + datetime.timedelta(
                minutes=last_bat_duration
            )
            remainder = release_timestamp - datetime.datetime.now()
            return max(int(remainder.total_seconds()), 0)

        return 0

    async def has_jail_event_from_user(
        self, jail_id: int, guild_id: int, user_id: int, jail_event_type: JailEventType
    ) -> bool:
        events = await self.database.get_jail_events_by_user(guild_id, user_id)

        for event in events:
            if event.jail_id == jail_id and event.jail_event_type == jail_event_type:
                return True

        return False

    async def get_user_statistics(self, user_id: int) -> UserStats:
        events_out = await self.database.get_interaction_events_by_user(user_id)

        user_stats = UserStats()

        count_out = {
            UserInteraction.SLAP: 0,
            UserInteraction.PET: 0,
            UserInteraction.FART: 0,
        }
        user_count_out = {}

        for event in events_out:
            interaction_type = event.interaction_type

            if interaction_type not in count_out:
                continue

            count_out[interaction_type] += 1
            member_id = event.to_user_id
            if member_id not in user_count_out:
                user_count_out[member_id] = {
                    UserInteraction.SLAP: 0,
                    UserInteraction.PET: 0,
                    UserInteraction.FART: 0,
                }

            user_count_out[member_id][interaction_type] += 1

        user_stats.set_count_out(count_out)
        user_stats.set_user_count_out(user_count_out)

        events_in = await self.database.get_interaction_events_affecting_user(user_id)

        count_in = {
            UserInteraction.SLAP: 0,
            UserInteraction.PET: 0,
            UserInteraction.FART: 0,
        }
        user_count_in = {}

        for event in events_in:
            interaction_type = event.interaction_type

            count_in[interaction_type] += 1
            member_id = event.from_user_id
            if member_id not in user_count_in:
                user_count_in[member_id] = {
                    UserInteraction.SLAP: 0,
                    UserInteraction.PET: 0,
                    UserInteraction.FART: 0,
                }

            user_count_in[member_id][interaction_type] += 1

        user_stats.set_count_in(count_in)
        user_stats.set_user_count_in(user_count_in)

        jail_events = await self.database.get_jail_events_affecting_user(user_id)

        total_jail_duration = 0
        jail_stays = []
        total_added_to_self = 0
        total_reduced_from_self = 0

        for event in jail_events:
            duration = event.duration
            if event.jail_event_type in [
                JailEventType.FART,
                JailEventType.PET,
                JailEventType.SLAP,
            ]:
                if duration >= 0:
                    total_added_to_self += duration
                else:
                    total_reduced_from_self += duration

            total_jail_duration += duration
            jail_id = event.jail_id
            if jail_id not in jail_stays:
                jail_stays.append(jail_id)

        user_stats.set_jail_total(total_jail_duration)
        user_stats.set_jail_amount(len(jail_stays))

        jail_interaction_events = await self.database.get_jail_events_by_user(user_id)
        total_added_to_others = 0
        total_reduced_from_others = 0
        max_fart = None
        min_fart = None

        for event in jail_interaction_events:
            duration = event.duration
            if event.jail_event_type in [
                JailEventType.FART,
                JailEventType.PET,
                JailEventType.SLAP,
            ]:

                if duration >= 0:
                    total_added_to_others += duration
                else:
                    total_reduced_from_others += duration

            if event.jail_event_type == JailEventType.FART:
                if max_fart is None or min_fart is None:
                    max_fart = duration
                    min_fart = duration
                    continue

                max_fart = max(max_fart, duration)
                min_fart = min(min_fart, duration)

        user_stats.set_total_added_others(total_added_to_others)
        user_stats.set_total_added_self(total_added_to_self)
        user_stats.set_total_reduced_from_others(abs(total_reduced_from_others))
        user_stats.set_total_reduced_from_self(abs(total_reduced_from_self))
        user_stats.set_fart_stats(max_fart, min_fart)

        timeout_events = await self.database.get_timeout_events_by_user(user_id)

        total_timeout_duration = 0
        timeout_count = len(timeout_events)

        for event in timeout_events:
            total_timeout_duration += event.duration

        user_stats.set_timeout_total(total_timeout_duration)
        user_stats.set_timeout_amount(timeout_count)

        spam_events = await self.database.get_spam_events_by_user(user_id)
        spam_count = len(spam_events)
        user_stats.set_spam_score(spam_count)

        return user_stats

    async def __get_ranking_data_by_type(
        self,
        guild_id: int,
        outgoing: bool,
        interaction_type: UserInteraction,
        season: int,
    ) -> list[tuple[int, Any]]:
        guild_interaction_events = await self.database.get_guild_interaction_events(
            guild_id, interaction_type, season
        )
        parsing_list = {}

        for event in guild_interaction_events:
            user_id = event.to_user_id
            if outgoing:  # True = from, False = to
                user_id = event.from_user_id

            BotUtil.dict_append(parsing_list, user_id, 1)

        return sorted(parsing_list.items(), key=lambda item: item[1], reverse=True)

    async def get_user_rankings(
        self, guild_id: int, ranking_type: RankingType, season: int
    ) -> dict[str, Any]:
        parsing_list = {}
        ranking_data = []

        match ranking_type:
            case RankingType.SLAP:
                ranking_data = await self.__get_ranking_data_by_type(
                    guild_id,
                    outgoing=True,
                    interaction_type=UserInteraction.SLAP,
                    season=season,
                )
            case RankingType.PET:
                ranking_data = await self.__get_ranking_data_by_type(
                    guild_id,
                    outgoing=True,
                    interaction_type=UserInteraction.PET,
                    season=season,
                )
            case RankingType.FART:
                ranking_data = await self.__get_ranking_data_by_type(
                    guild_id,
                    outgoing=True,
                    interaction_type=UserInteraction.FART,
                    season=season,
                )
            case RankingType.SLAP_RECIEVED:
                ranking_data = await self.__get_ranking_data_by_type(
                    guild_id,
                    outgoing=False,
                    interaction_type=UserInteraction.SLAP,
                    season=season,
                )
            case RankingType.PET_RECIEVED:
                ranking_data = await self.__get_ranking_data_by_type(
                    guild_id,
                    outgoing=False,
                    interaction_type=UserInteraction.PET,
                    season=season,
                )
            case RankingType.FART_RECIEVED:
                ranking_data = await self.__get_ranking_data_by_type(
                    guild_id,
                    outgoing=False,
                    interaction_type=UserInteraction.FART,
                    season=season,
                )
            case RankingType.TIMEOUT_TOTAL:
                guild_timeout_events = await self.database.get_timeout_events_by_guild(
                    guild_id, season
                )
                for event in guild_timeout_events:
                    user_id = event.member_id
                    BotUtil.dict_append(parsing_list, user_id, event.duration)
                sorted_list = sorted(
                    parsing_list.items(), key=lambda item: item[1], reverse=True
                )
                converted = [
                    (k, BotUtil.strfdelta(v, inputtype="seconds"))
                    for (k, v) in sorted_list
                ]
                ranking_data = converted
            case RankingType.TIMEOUT_COUNT:
                guild_timeout_events = await self.database.get_timeout_events_by_guild(
                    guild_id, season
                )
                for event in guild_timeout_events:
                    user_id = event.member_id
                    BotUtil.dict_append(parsing_list, user_id, 1)
                ranking_data = sorted(
                    parsing_list.items(), key=lambda item: item[1], reverse=True
                )
            case RankingType.JAIL_TOTAL:
                jail_data = await self.database.get_jail_events_by_guild(
                    guild_id, season
                )
                for jail, events in jail_data.items():
                    for event in events:
                        user_id = jail.member_id
                        BotUtil.dict_append(parsing_list, user_id, event.duration)
                sorted_list = sorted(
                    parsing_list.items(), key=lambda item: item[1], reverse=True
                )
                converted = [
                    (k, BotUtil.strfdelta(v, inputtype="minutes"))
                    for (k, v) in sorted_list
                ]
                ranking_data = converted
            case RankingType.JAIL_COUNT:
                jail_data = await self.database.get_jail_events_by_guild(
                    guild_id, season
                )
                for jail, events in jail_data.items():
                    for event in events:
                        user_id = jail.member_id
                        if event.jail_event_type == JailEventType.JAIL:
                            BotUtil.dict_append(parsing_list, user_id, 1)
                ranking_data = sorted(
                    parsing_list.items(), key=lambda item: item[1], reverse=True
                )
            case RankingType.SPAM_SCORE:
                guild_spam_events = await self.database.get_spam_events_by_guild(
                    guild_id, season
                )
                for event in guild_spam_events:
                    user_id = event.member_id
                    BotUtil.dict_append(parsing_list, user_id, 1)
                ranking_data = sorted(
                    parsing_list.items(), key=lambda item: item[1], reverse=True
                )
            case RankingType.BEANS:
                parsing_list = await self.database.get_guild_beans_rankings(
                    guild_id, season
                )
                # only subtract lootboxes until patch where beans got removed.
                lootbox_purchases = await self.database.get_lootbox_purchases_by_guild(
                    guild_id,
                    datetime.datetime(year=2024, month=4, day=22, hour=14).timestamp(),
                    season,
                )
                loot_box_item = await self.item_manager.get_item(
                    guild_id, ItemType.LOOTBOX
                )
                for user_id, amount in lootbox_purchases.items():
                    if user_id in parsing_list:
                        parsing_list[user_id] -= amount * loot_box_item.cost
                sorted_list = sorted(
                    parsing_list.items(), key=lambda item: item[1], reverse=True
                )
                ranking_data = [(k, f"🅱️{v}") for (k, v) in sorted_list]
            case RankingType.BEANS_CURRENT:
                parsing_list = await self.database.get_guild_beans_rankings_current(
                    guild_id, season
                )
                # only subtract lootboxes until patch where beans got removed.
                lootbox_purchases = await self.database.get_lootbox_purchases_by_guild(
                    guild_id,
                    datetime.datetime(year=2024, month=4, day=22, hour=14).timestamp(),
                    season,
                )
                loot_box_item = await self.item_manager.get_item(
                    guild_id, ItemType.LOOTBOX
                )
                for user_id, amount in lootbox_purchases.items():
                    if user_id in parsing_list:
                        parsing_list[user_id] -= amount * loot_box_item.cost
                sorted_list = sorted(
                    parsing_list.items(), key=lambda item: item[1], reverse=True
                )
                ranking_data = [(k, f"🅱️{v}") for (k, v) in sorted_list]
            case RankingType.MIMICS:
                lootboxes = await self.database.get_lootboxes_by_guild(guild_id, season)
                total_dict = {}
                for user_id, lootbox in lootboxes:
                    if (
                        lootbox.beans < 0
                        or len(list(LootBox.MIMICS & lootbox.items.keys())) > 0
                    ):
                        BotUtil.dict_append(parsing_list, user_id, 1)
                    BotUtil.dict_append(total_dict, user_id, 1)
                mimic_data = sorted(
                    parsing_list.items(), key=lambda item: item[1], reverse=True
                )
                for user_id, mimic_count in mimic_data:
                    ranking_data.append(
                        (user_id, f"{mimic_count}/{total_dict[user_id]}")
                    )
            case RankingType.TOTAL_GAMBAD_SPENT:
                gamba_events = await self.database.get_guild_beans_events(
                    guild_id, [BeansEventType.GAMBA_COST], season
                )
                for event in gamba_events:
                    user_id = event.member_id
                    BotUtil.dict_append(parsing_list, user_id, abs(event.value))
                sorted_list = sorted(
                    parsing_list.items(), key=lambda item: item[1], reverse=True
                )
                ranking_data = [(k, f"🅱️{v}") for (k, v) in sorted_list]
            case RankingType.TOTAL_GAMBAD_WON:
                gamba_events = await self.database.get_guild_beans_events(
                    guild_id,
                    [BeansEventType.GAMBA_COST, BeansEventType.GAMBA_PAYOUT],
                    season,
                )
                for event in gamba_events:
                    user_id = event.member_id
                    BotUtil.dict_append(parsing_list, user_id, event.value)
                sorted_list = sorted(
                    parsing_list.items(), key=lambda item: item[1], reverse=True
                )
                ranking_data = [(k, f"🅱️{v}") for (k, v) in sorted_list]
            case RankingType.WIN_RATE:
                total_won: dict[int, int] = {}
                total_lost: dict[int, int] = {}
                user_list = set()
                gamba_events = await self.database.get_guild_beans_events(
                    guild_id, [BeansEventType.GAMBA_PAYOUT], season
                )
                for event in gamba_events:
                    user_id = event.member_id
                    if event.value > 0:
                        BotUtil.dict_append(total_won, user_id, 1)
                        user_list.add(user_id)
                    else:
                        BotUtil.dict_append(total_lost, user_id, 1)
                        user_list.add(user_id)

                for user_id in user_list:
                    win_amount = 0
                    cost_amount = 0
                    ratio = 0

                    if user_id in total_won:
                        win_amount = total_won[user_id]
                    else:
                        total_won[user_id] = 0
                    if user_id in total_lost:
                        cost_amount = total_lost[user_id]
                    else:
                        total_lost[user_id] = 0

                    total = win_amount + cost_amount
                    if total != 0:
                        ratio = round(win_amount / (total) * 100, 2)
                    parsing_list[user_id] = ratio

                sorted_list = sorted(
                    parsing_list.items(), key=lambda item: item[1], reverse=True
                )
                ranking_data = [
                    (k, f"{v}% ({total_won[k]}/{total_won[k] + total_lost[k]})")
                    for (k, v) in sorted_list
                ]
            case RankingType.AVG_GAMBA_GAIN:
                total_won: dict[int, int] = {}
                total_cost: dict[int, int] = {}
                user_list = set()
                gamba_events = await self.database.get_guild_beans_events(
                    guild_id,
                    [BeansEventType.GAMBA_COST, BeansEventType.GAMBA_PAYOUT],
                    season,
                )
                for event in gamba_events:
                    user_id = event.member_id
                    if event.value > 0:
                        BotUtil.dict_append(total_won, user_id, event.value)
                        user_list.add(user_id)
                    else:
                        BotUtil.dict_append(total_cost, user_id, abs(event.value))
                        user_list.add(user_id)

                for user_id in user_list:
                    win_amount = 0
                    cost_amount = 0
                    ratio = 0

                    if user_id in total_won:
                        win_amount = total_won[user_id]
                    else:
                        total_won[user_id] = 0
                    if user_id in total_cost:
                        cost_amount = total_cost[user_id]
                    else:
                        total_cost[user_id] = 0

                    if cost_amount != 0:
                        ratio = round(win_amount / cost_amount, 2)
                    parsing_list[user_id] = ratio

                sorted_list = sorted(
                    parsing_list.items(), key=lambda item: item[1], reverse=True
                )
                ranking_data = [
                    (k, f"{v} ({total_won[k]}/{total_cost[k]})")
                    for (k, v) in sorted_list
                ]
            case RankingType.WIN_STREAK:
                user_list: dict[int, int] = {}
                gamba_count: dict[int, int] = {}
                gamba_events = await self.database.get_guild_beans_events(
                    guild_id, [BeansEventType.GAMBA_PAYOUT], season
                )
                for event in gamba_events:
                    user_id = event.member_id
                    if event.value > 0:
                        BotUtil.dict_append(user_list, user_id, 1)
                    else:
                        user_list[user_id] = 0
                    BotUtil.dict_append(
                        parsing_list, user_id, user_list[user_id], mode="max"
                    )
                    BotUtil.dict_append(gamba_count, user_id, 1)

                sorted_list = sorted(
                    parsing_list.items(), key=lambda item: item[1], reverse=True
                )
                ranking_data = [
                    (k, f"{v} ({gamba_count[k]} total)") for (k, v) in sorted_list
                ]
            case RankingType.LOSS_STREAK:
                user_list: dict[int, int] = {}
                gamba_count: dict[int, int] = {}
                gamba_events = await self.database.get_guild_beans_events(
                    guild_id, [BeansEventType.GAMBA_PAYOUT], season
                )
                for event in gamba_events:
                    user_id = event.member_id
                    if event.value == 0:
                        BotUtil.dict_append(user_list, user_id, 1)
                    else:
                        user_list[user_id] = 0
                    BotUtil.dict_append(
                        parsing_list, user_id, user_list[user_id], mode="max"
                    )
                    BotUtil.dict_append(gamba_count, user_id, 1)

                sorted_list = sorted(
                    parsing_list.items(), key=lambda item: item[1], reverse=True
                )
                ranking_data = [
                    (k, f"{v} ({gamba_count[k]} total)") for (k, v) in sorted_list
                ]
            case RankingType.KARMA:
                guild_karma_events = await self.database.get_karma_events_by_guild(
                    guild_id, season
                )
                for event in guild_karma_events:
                    user_id = event.recipient_id
                    BotUtil.dict_append(parsing_list, user_id, event.amount)
                sorted_list = sorted(
                    parsing_list.items(), key=lambda item: item[1], reverse=True
                )
                ranking_data = [
                    (k, f"😇{v}") if v >= 0 else (k, f"😈{v}") for (k, v) in sorted_list
                ]
            case RankingType.GOLD_STARS:
                guild_positive_karma_events = (
                    await self.database.get_karma_events_by_guild(
                        guild_id, season, True
                    )
                )
                for event in guild_positive_karma_events:
                    user_id = event.recipient_id
                    BotUtil.dict_append(parsing_list, user_id, event.amount)
                sorted_list = sorted(
                    parsing_list.items(), key=lambda item: item[1], reverse=True
                )
                ranking_data = [(k, f"⭐{v}") for (k, v) in sorted_list]
            case RankingType.FUCK_YOUS:
                guild_negative_karma_events = (
                    await self.database.get_karma_events_by_guild(
                        guild_id, season, False
                    )
                )
                for event in guild_negative_karma_events:
                    user_id = event.recipient_id
                    BotUtil.dict_append(parsing_list, user_id, abs(event.amount))
                sorted_list = sorted(
                    parsing_list.items(), key=lambda item: item[1], reverse=True
                )
                ranking_data = [(k, f"🖕{v}") for (k, v) in sorted_list]
        return {
            BotUtil.get_name(self.bot, guild_id, user_id, 100): value
            for user_id, value in ranking_data
        }
