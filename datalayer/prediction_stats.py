import discord

from datalayer.prediction import Prediction


class PredictionStats:

    def __init__(
        self,
        prediction: Prediction,
        bets: dict[int, int],
        author_name: str,
        moderator_name: str = None,
    ):
        self.prediction = prediction
        self.bets = bets
        self.author_name = author_name
        self.moderator_name = moderator_name

        if bets is None:
            self.bets = {}

        for id in prediction.outcomes:
            if id not in self.bets:
                self.bets[id] = 0

    def __get_content(
        self,
        max_width: int,
        moderator: bool = False,
        user_bet: tuple[int, int] = None,
    ):
        total = sum(self.bets.values())
        description = ""
        outcome_nr = 0
        outcome_prefixes = ["a)", "b)", "c)", "d)"]
        for outcome_id, outcome in self.prediction.outcomes.items():
            bets = self.bets[outcome_id]

            if bets is None:
                bets = 0

            description += f"```python\n{outcome_prefixes[outcome_nr]} {outcome}"
            outcome_nr += 1  # noqa: SIM113

            prefix = ""
            suffix = f"total bets: 🅱️{bets}"

            if bets > 0:
                odds = round(1 / (bets / total), 2)
                if int(odds) == odds:
                    odds = int(odds)
                prefix += f"odds: 1:{odds}"

            spacing = max_width - len(prefix) - len(suffix)
            description += f"\n\n{prefix}{' '*spacing}{suffix}"

            if user_bet is not None and user_bet[0] == outcome_id:
                suffix = f"your bet: 🅱️{user_bet[1]}"
                spacing = max_width - len(suffix)
                description += f"\n{' '*spacing}{suffix}"

            description += "```"

        if moderator:

            prefix = f"\nStatus: '{self.prediction.state}'"

            suffix = f" id: {self.prediction.id}"

            spacing = max(0, max_width - len(prefix) - len(suffix))
            description += f"```python\n{prefix}{' '*spacing}{suffix}"

            if self.moderator_name is not None:
                description += f"\n(by {self.moderator_name})"

            description += "```"

        description += f"by {self.author_name}"

        return f"\n{description}"

    def get_odds(self, outcome_id: int):
        bets = self.bets[outcome_id]
        if bets is None:
            return 0

        total = sum(self.bets.values())
        return 1 / (bets / total)

    def get_embed(self, moderator: bool = False) -> discord.Embed:
        color = discord.Colour.purple()
        title = f"> > {self.prediction.content} "

        info_block = self.__get_content(53, moderator)

        embed = discord.Embed(title=title, description=info_block, color=color)

        return embed

    def add_to_embed(
        self,
        embed: discord.Embed,
        max_width: int,
        user_bet: tuple[int, int] = None,
        moderator: bool = False,
    ) -> None:
        title = f"> > {self.prediction.content}"

        info_block = self.__get_content(max_width, moderator, user_bet)

        embed.add_field(name=title, value=info_block, inline=False)
