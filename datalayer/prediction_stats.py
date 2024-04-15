import discord

from datalayer.prediction import Prediction
from datalayer.types import PredictionState


class PredictionStats:

    def __init__(
        self,
        prediction: Prediction,
        bets: dict[int, int],
        author_name: str,
        moderator_name: str = None,
        winning_outcome_id: int = None,
    ):
        self.prediction = prediction
        self.bets = bets
        self.author_name = author_name
        self.moderator_name = moderator_name
        self.winning_outcome_id = winning_outcome_id

        if bets is None:
            self.bets = {}

        for id in prediction.outcomes:
            if id not in self.bets:
                self.bets[id] = 0

    def get_odds(self, outcome_id: int):
        bets = self.bets[outcome_id]
        if bets is None or bets == 0:
            return 0

        total = sum(self.bets.values())
        if total == 0:
            return 0
        return 1 / (bets / total)

    def get_embed(
        self, user_bet: tuple[int, int] = None, moderator: bool = False
    ) -> discord.Embed:
        color = discord.Colour.purple()

        locked = ""
        embed_description = ""

        if self.prediction.comment is not None:
            embed_description += f"\n{self.prediction.comment}"

        if self.prediction.state == PredictionState.LOCKED:
            locked = " 🔒 "
            embed_description = "This prediction has been locked in."

        if (
            self.prediction.lock_datetime is not None
            and self.prediction.state != PredictionState.LOCKED
        ):
            embed_description += f"\nThis prediction will be locked <t:{self.prediction.get_timestamp()}:R>"

        title = f"> {locked}{self.prediction.content}{locked}"
        embed = discord.Embed(title=title, description=embed_description, color=color)

        max_width = 56
        description = ""
        total = sum(self.bets.values())
        outcome_nr = 0
        outcome_prefixes = ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]

        for outcome_id, outcome in self.prediction.outcomes.items():

            bets = self.bets[outcome_id]

            if bets is None:
                bets = 0
            winner = ""
            if outcome_id == self.winning_outcome_id:
                winner = "[WINNER] "

            name = f"᲼᲼\n{outcome_prefixes[outcome_nr]} ) {winner}{outcome}"
            outcome_nr += 1  # noqa: SIM113
            description = ""  # f"> **{outcome}**\n"

            prefix = ""
            suffix = f"total bets: 🅱️{bets}"

            if bets > 0:
                odds = round(1 / (bets / total), 2)
                if int(odds) == odds:
                    odds = int(odds)
                prefix += f"odds: 1:{odds}"

            spacing = max_width - len(prefix) - len(suffix)
            description += f"```python\n{prefix}{' '*spacing}{suffix}"

            if user_bet is not None and user_bet[0] == outcome_id:
                suffix = f"your bet: 🅱️{user_bet[1]}"
                spacing = max_width - len(suffix)
                description += f"\n{' '*spacing}{suffix}"

            description += "```"

            embed.add_field(name=name, value=description, inline=False)

        if moderator:

            prefix = f"\nStatus: '{self.prediction.state.value}'"

            suffix = f" id: {self.prediction.id}"

            spacing = max(0, max_width - len(prefix) - len(suffix))
            description = f"```python\n{prefix}{' '*spacing}{suffix}"

            if self.moderator_name is not None:
                description += f"\n(by {self.moderator_name})"

            description += "```"

            embed.add_field(name="", value=description, inline=False)

        embed.add_field(name="", value=f"by {self.author_name}", inline=False)

        return embed
