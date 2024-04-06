import datetime
from typing import Any, List, Tuple
from discord.ext import commands
from bot_util import BotUtil
from control.controller import Controller
from control.service import Service
from control.logger import BotLogger
from datalayer.jail import UserJail
from datalayer.database import Database
from datalayer.types import UserInteraction
from datalayer.stats import UserStats
from events.bot_event import BotEvent
from events.jail_event import JailEvent
from events.types import JailEventType, EventType
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
        self.settings_manager = None
        self.log_name = "Events"

    async def listen_for_event(self, event: BotEvent):
        match event.get_type():
            case EventType.JAIL:
                jail_event: JailEvent = event
                if jail_event.get_jail_event_type() is JailEventType.RELEASE:
                    self.database.log_jail_release(
                        jail_event.get_jail_id(), int(jail_event.get_timestamp())
                    )
                    self.logger.log(
                        jail_event.get_guild_id(),
                        f"Jail sentence `{jail_event.get_jail_id()}` marked as released.",
                        self.log_name,
                    )

        from_user = event.get_causing_user_id()
        args = event.get_type_specific_args()
        self.database.log_event(event)
        self.__log_event(event, from_user, *args)

    def __log_event(self, event: BotEvent, member_id: int, *args):
        event_type = event.get_type()
        guild_id = event.get_guild_id()
        parsed_args = []
        for arg in args:
            try:
                potential_user_id = int(arg)
            except ValueError:
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

    def get_stunned_remaining(
        self, guild_id: int, user_id: int, base_duration: int
    ) -> int:
        last_bat_event = self.database.get_last_bat_event_by_target(guild_id, user_id)

        if last_bat_event is None:
            return 0

        last_bat_time = last_bat_event.get_datetime()

        diff = datetime.datetime.now() - last_bat_time
        if int(diff.total_seconds() / 60) <= base_duration:
            release_timestamp = last_bat_time + datetime.timedelta(
                minutes=base_duration
            )
            remainder = release_timestamp - datetime.datetime.now()
            return max(int(remainder.total_seconds()), 0)

        return 0

    def get_jail_duration(self, jail: UserJail) -> int:
        events = self.database.get_jail_events_by_jail(jail.get_id())
        total_duration = 0
        for event in events:
            total_duration += event.get_duration()

        return total_duration

    def get_jail_remaining(self, jail: UserJail) -> float:
        duration = self.get_jail_duration(jail)
        release_timestamp = jail.get_jailed_on() + datetime.timedelta(minutes=duration)
        remainder = release_timestamp - datetime.datetime.now()
        return max(remainder.total_seconds() / 60, 0)

    def has_jail_event_from_user(
        self, jail_id: int, user_id: int, jail_event_type: JailEventType
    ) -> bool:
        events = self.database.get_jail_events_by_user(user_id)

        for event in events:
            if (
                event.get_jail_id() == jail_id
                and event.get_jail_event_type() == jail_event_type
            ):
                return True

        return False

    def get_user_statistics(self, user_id: int) -> UserStats:
        events_out = self.database.get_interaction_events_by_user(user_id)

        user_stats = UserStats()

        count_out = {
            UserInteraction.SLAP: 0,
            UserInteraction.PET: 0,
            UserInteraction.FART: 0,
        }
        user_count_out = {}

        for event in events_out:
            interaction_type = event.get_interaction_type()

            if interaction_type not in count_out:
                continue

            count_out[interaction_type] += 1
            member_id = event.get_to_user()
            if member_id not in user_count_out:
                user_count_out[member_id] = {
                    UserInteraction.SLAP: 0,
                    UserInteraction.PET: 0,
                    UserInteraction.FART: 0,
                }

            user_count_out[member_id][interaction_type] += 1

        user_stats.set_count_out(count_out)
        user_stats.set_user_count_out(user_count_out)

        events_in = self.database.get_interaction_events_affecting_user(user_id)

        count_in = {
            UserInteraction.SLAP: 0,
            UserInteraction.PET: 0,
            UserInteraction.FART: 0,
        }
        user_count_in = {}

        for event in events_in:
            interaction_type = event.get_interaction_type()

            count_in[interaction_type] += 1
            member_id = event.get_from_user()
            if member_id not in user_count_in:
                user_count_in[member_id] = {
                    UserInteraction.SLAP: 0,
                    UserInteraction.PET: 0,
                    UserInteraction.FART: 0,
                }

            user_count_in[member_id][interaction_type] += 1

        user_stats.set_count_in(count_in)
        user_stats.set_user_count_in(user_count_in)

        jail_events = self.database.get_jail_events_affecting_user(user_id)

        total_jail_duration = 0
        jail_stays = []
        total_added_to_self = 0
        total_reduced_from_self = 0

        for event in jail_events:
            duration = event.get_duration()
            if event.get_jail_event_type() in [
                JailEventType.FART,
                JailEventType.PET,
                JailEventType.SLAP,
            ]:
                if duration >= 0:
                    total_added_to_self += duration
                else:
                    total_reduced_from_self += duration

            total_jail_duration += duration
            jail_id = event.get_jail_id()
            if jail_id not in jail_stays:
                jail_stays.append(jail_id)

        user_stats.set_jail_total(total_jail_duration)
        user_stats.set_jail_amount(len(jail_stays))

        jail_interaction_events = self.database.get_jail_events_by_user(user_id)
        total_added_to_others = 0
        total_reduced_from_others = 0
        max_fart = None
        min_fart = None

        for event in jail_interaction_events:
            duration = event.get_duration()
            if event.get_jail_event_type() in [
                JailEventType.FART,
                JailEventType.PET,
                JailEventType.SLAP,
            ]:

                if duration >= 0:
                    total_added_to_others += duration
                else:
                    total_reduced_from_others += duration

            if event.get_jail_event_type() == JailEventType.FART:
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

        timeout_events = self.database.get_timeout_events_by_user(user_id)

        total_timeout_duration = 0
        timeout_count = len(timeout_events)

        for event in timeout_events:
            total_timeout_duration += event.get_duration()

        user_stats.set_timeout_total(total_timeout_duration)
        user_stats.set_timeout_amount(timeout_count)

        spam_events = self.database.get_spam_events_by_user(user_id)
        spam_count = len(spam_events)
        user_stats.set_spam_score(spam_count)

        return user_stats

    def __get_ranking_data_by_type(
        self, guild_id: int, outgoing: bool, interaction_type: UserInteraction
    ) -> List[Tuple[int, Any]]:
        guild_interaction_events = self.database.get_guild_interaction_events(
            guild_id, interaction_type
        )
        parsing_list = {}

        for event in guild_interaction_events:
            user_id = event.get_to_user()
            if outgoing:  # True = from, False = to
                user_id = event.get_from_user()

            BotUtil.dict_append(parsing_list, user_id, 1)

        return sorted(parsing_list.items(), key=lambda item: item[1], reverse=True)

    def get_user_rankings(
        self, guild_id: int, ranking_type: RankingType
    ) -> List[Tuple[int, Any]]:
        parsing_list = {}
        match ranking_type:
            case RankingType.SLAP:
                return self.__get_ranking_data_by_type(
                    guild_id, outgoing=True, interaction_type=UserInteraction.SLAP
                )
            case RankingType.PET:
                return self.__get_ranking_data_by_type(
                    guild_id, outgoing=True, interaction_type=UserInteraction.PET
                )
            case RankingType.FART:
                return self.__get_ranking_data_by_type(
                    guild_id, outgoing=True, interaction_type=UserInteraction.FART
                )
            case RankingType.SLAP_RECIEVED:
                return self.__get_ranking_data_by_type(
                    guild_id, outgoing=False, interaction_type=UserInteraction.SLAP
                )
            case RankingType.PET_RECIEVED:
                return self.__get_ranking_data_by_type(
                    guild_id, outgoing=False, interaction_type=UserInteraction.PET
                )
            case RankingType.FART_RECIEVED:
                return self.__get_ranking_data_by_type(
                    guild_id, outgoing=False, interaction_type=UserInteraction.FART
                )
            case RankingType.TIMEOUT_TOTAL:
                guild_timeout_events = self.database.get_timeout_events_by_guild(
                    guild_id
                )
                for event in guild_timeout_events:
                    user_id = event.get_member()
                    BotUtil.dict_append(parsing_list, user_id, event.get_duration())
                sorted_list = sorted(
                    parsing_list.items(), key=lambda item: item[1], reverse=True
                )
                converted = [
                    (k, BotUtil.strfdelta(v, inputtype="seconds"))
                    for (k, v) in sorted_list
                ]
                return converted
            case RankingType.TIMEOUT_COUNT:
                guild_timeout_events = self.database.get_timeout_events_by_guild(
                    guild_id
                )
                for event in guild_timeout_events:
                    user_id = event.get_member()
                    BotUtil.dict_append(parsing_list, user_id, 1)
                return sorted(
                    parsing_list.items(), key=lambda item: item[1], reverse=True
                )
            case RankingType.JAIL_TOTAL:
                jail_data = self.database.get_jail_events_by_guild(guild_id)
                for jail, events in jail_data.items():
                    for event in events:
                        user_id = jail.get_member_id()
                        BotUtil.dict_append(parsing_list, user_id, event.get_duration())
                sorted_list = sorted(
                    parsing_list.items(), key=lambda item: item[1], reverse=True
                )
                converted = [
                    (k, BotUtil.strfdelta(v, inputtype="minutes"))
                    for (k, v) in sorted_list
                ]
                return converted
            case RankingType.JAIL_COUNT:
                jail_data = self.database.get_jail_events_by_guild(guild_id)
                for jail, events in jail_data.items():
                    for event in events:
                        user_id = jail.get_member_id()
                        if event.get_jail_event_type() == JailEventType.JAIL:
                            BotUtil.dict_append(parsing_list, user_id, 1)
                return sorted(
                    parsing_list.items(), key=lambda item: item[1], reverse=True
                )
            case RankingType.SPAM_SCORE:
                guild_spam_events = self.database.get_spam_events_by_guild(guild_id)
                for event in guild_spam_events:
                    user_id = event.get_member()
                    BotUtil.dict_append(parsing_list, user_id, 1)
                return sorted(
                    parsing_list.items(), key=lambda item: item[1], reverse=True
                )
            case RankingType.BEANS:
                parsing_list = self.database.get_guild_beans_rankings(guild_id)
                lootbox_purchases = self.database.get_lootbox_purchases_by_guild(
                    guild_id
                )
                loot_box_item = self.bot.item_manager.get_item(
                    guild_id, ItemType.LOOTBOX
                )
                for user_id, amount in lootbox_purchases.items():
                    if user_id in parsing_list.keys():
                        parsing_list[user_id] -= amount * loot_box_item.get_cost()
                sorted_list = sorted(
                    parsing_list.items(), key=lambda item: item[1], reverse=True
                )
                converted = [(k, f"🅱️{v}") for (k, v) in sorted_list]
                return converted
            case RankingType.MIMICS:
                parsing_list = self.database.get_lootbox_mimics(guild_id)
                return sorted(
                    parsing_list.items(), key=lambda item: item[1], reverse=True
                )
            # case RankingType.TOTAL_GAMBAD_SPENT:
            #     gamba_events = self.database.get_guild_beans_events(guild_id, [BeansEventType.GAMBA_COST])
            #     for event in gamba_events:
            #         user_id = event.get_member()
            #         BotUtil.dict_append(parsing_list, user_id, abs(event.get_value()))
            #     return sorted(parsing_list.items(), key=lambda item: item[1], reverse=True)
            # case RankingType.TOTAL_GAMBAD_WON:
            #     pass
