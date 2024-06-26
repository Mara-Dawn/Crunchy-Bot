from datalayer.types import UserInteraction


class UserStats:

    def __init__(self):
        self.count_in = {}
        self.count_out = {}
        self.user_count_in = {}
        self.user_count_out = {}
        self.jail_total_duration = 0
        self.jail_count = 0
        self.timeout_total_duration = 0
        self.timeout_count = 0
        self.min_fart = 0
        self.max_fart = 0
        self.spam_score = 0
        self.total_added_to_others = 0
        self.total_added_to_self = 0
        self.total_reduced_from_others = 0
        self.total_reduced_from_self = 0

    def set_count_in(self, count_in: dict[UserInteraction, int]):
        self.count_in = count_in

    def set_count_out(self, count_out: dict[UserInteraction, int]):
        self.count_out = count_out

    def set_user_count_in(self, user_count_in: dict[str, int]):
        self.user_count_in = user_count_in

    def set_user_count_out(self, user_count_out: dict[str, int]):
        self.user_count_out = user_count_out

    def set_jail_total(self, duration: int):
        self.jail_total_duration = duration

    def set_jail_amount(self, amount: int):
        self.jail_count = amount

    def set_timeout_total(self, duration: int):
        self.timeout_total_duration = duration

    def set_timeout_amount(self, amount: int):
        self.timeout_count = amount

    def set_fart_stats(self, max_fart: int, min_fart: int):
        self.min_fart = min_fart
        self.max_fart = max_fart

    def set_spam_score(self, score: int):
        self.spam_score = score

    def set_total_added_others(self, total_added_to_others: int):
        self.total_added_to_others = total_added_to_others

    def set_total_reduced_from_others(self, total_reduced_from_others: int):
        self.total_reduced_from_others = total_reduced_from_others

    def set_total_added_self(self, total_added_to_self: int):
        self.total_added_to_self = total_added_to_self

    def set_total_reduced_from_self(self, total_reduced_from_self: int):
        self.total_reduced_from_self = total_reduced_from_self

    def get_slaps_recieved(self) -> int:
        return self.count_in[UserInteraction.SLAP]

    def get_slaps_given(self) -> int:
        return self.count_out[UserInteraction.SLAP]

    def get_pets_recieved(self) -> int:
        return self.count_in[UserInteraction.PET]

    def get_pets_given(self) -> int:
        return self.count_out[UserInteraction.PET]

    def get_farts_recieved(self) -> int:
        return self.count_in[UserInteraction.FART]

    def get_farts_given(self) -> int:
        return self.count_out[UserInteraction.FART]

    def __get_top(
        self, interaction_type: UserInteraction, amount: int, data: dict
    ) -> list[tuple]:
        if len(data) == 0:
            return {}

        lst = {k: v[interaction_type] for (k, v) in data.items()}
        lst_filtered = {}
        for k, v in lst.items():
            if v > 0:
                lst_filtered[k] = v
        lst_sorted = sorted(
            lst_filtered.items(), key=lambda item: item[1], reverse=True
        )
        if len(lst_sorted) == 1:
            return lst_sorted

        amount = min(amount, len(data))
        return lst_sorted[:amount]

    def get_top_slappers(self, amount: int) -> list[tuple]:
        return self.__get_top(UserInteraction.SLAP, amount, self.user_count_in)

    def get_top_petters(self, amount: int) -> list[tuple]:
        return self.__get_top(UserInteraction.PET, amount, self.user_count_in)

    def get_top_farters(self, amount: int) -> list[tuple]:
        return self.__get_top(UserInteraction.FART, amount, self.user_count_in)

    def get_top_slapperd(self, amount: int) -> list[tuple]:
        return self.__get_top(UserInteraction.SLAP, amount, self.user_count_out)

    def get_top_petterd(self, amount: int) -> list[tuple]:
        return self.__get_top(UserInteraction.PET, amount, self.user_count_out)

    def get_top_farterd(self, amount: int) -> list[tuple]:
        return self.__get_top(UserInteraction.FART, amount, self.user_count_out)

    def get_jail_count(self) -> int:
        return self.jail_count

    def get_jail_total(self) -> int:
        return self.jail_total_duration

    def get_timeout_count(self) -> int:
        return self.timeout_count

    def get_timeout_total(self) -> int:
        return self.timeout_total_duration

    def get_biggest_fart(self) -> int:
        return self.max_fart

    def get_smallest_fart(self) -> int:
        return self.min_fart

    def get_spam_score(self) -> int:
        return self.spam_score

    def get_total_added_to_others(self) -> int:
        return self.total_added_to_others

    def get_total_added_to_self(self) -> int:
        return self.total_added_to_self

    def get_total_reduced_from_others(self) -> int:
        return self.total_reduced_from_others

    def get_total_reduced_from_self(self) -> int:
        return self.total_reduced_from_self
