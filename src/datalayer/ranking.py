from view.types import RankingType


class RankingDefinition:

    def __init__(
        self,
        type: RankingType,
        title: int,
        description: int,
        emoji: str,
    ):
        self.type = type
        self.title = title
        self.description = description
        self.emoji = emoji


class Ranking:
    DEFINITIONS = {
        RankingType.BEANS: RankingDefinition(
            type=RankingType.BEANS,
            title="Beans Ranking Highscores (excl. Shop/Transfers)",
            description="Beans Ranking Highscores",
            emoji="🅱️",
        ),
        RankingType.BEANS_CURRENT: RankingDefinition(
            type=RankingType.BEANS_CURRENT,
            title="Beans Rankings Current",
            description="Beans Rankings Current (Might be lower than high score)",
            emoji="🅱️",
        ),
        RankingType.TOTAL_GAMBAD_SPENT: RankingDefinition(
            type=RankingType.TOTAL_GAMBAD_SPENT,
            title="Beans spent on Gamba Rankings",
            description="Who has the biggest gamba addiction? (Beans spent on Gamba)",
            emoji="🅱️",
        ),
        RankingType.TOTAL_GAMBAD_WON: RankingDefinition(
            type=RankingType.TOTAL_GAMBAD_WON,
            title="Beans won from Gamba Rankings",
            description="Who won the most from their gamba addiciton?",
            emoji="🅱️",
        ),
        RankingType.MIMICS: RankingDefinition(
            type=RankingType.MIMICS,
            title="Mimic Count Rankings",
            description="Who gets vored the most? (Mimics/Total)",
            emoji="🧰",
        ),
        RankingType.SLAP: RankingDefinition(
            type=RankingType.SLAP,
            title="Slap Rankings",
            description="Who slapped the most users?",
            emoji="✋",
        ),
        RankingType.PET: RankingDefinition(
            type=RankingType.PET,
            title="Pet Rankings",
            description="Who petted the most users?",
            emoji="🥰",
        ),
        RankingType.FART: RankingDefinition(
            type=RankingType.FART,
            title="Fart Rankings",
            description="Who farted on the most users?",
            emoji="💩",
        ),
        RankingType.SLAP_RECIEVED: RankingDefinition(
            type=RankingType.SLAP_RECIEVED,
            title="Slaps Recieved Rankings",
            description="Who was slapped the most?",
            emoji="💢",
        ),
        RankingType.PET_RECIEVED: RankingDefinition(
            type=RankingType.PET_RECIEVED,
            title="Pets Recieved Rankings",
            description="Who was petted the most?",
            emoji="💜",
        ),
        RankingType.FART_RECIEVED: RankingDefinition(
            type=RankingType.FART_RECIEVED,
            title="Farts Recieved Rankings",
            description="Who was farted on the most?",
            emoji="💀",
        ),
        RankingType.TIMEOUT_TOTAL: RankingDefinition(
            type=RankingType.TIMEOUT_TOTAL,
            title="Total Timeout Duration Rankings",
            description="Who spent the most time in timeout?",
            emoji="⏰",
        ),
        RankingType.TIMEOUT_COUNT: RankingDefinition(
            type=RankingType.TIMEOUT_COUNT,
            title="Timeout Count Rankings",
            description="Who has the most timeouts?",
            emoji="🔁",
        ),
        RankingType.JAIL_TOTAL: RankingDefinition(
            type=RankingType.JAIL_TOTAL,
            title="Total Jail Duration Rankings",
            description="Who spent the most time in jail?",
            emoji="⏲",
        ),
        RankingType.JAIL_COUNT: RankingDefinition(
            type=RankingType.JAIL_COUNT,
            title="Jail Count Rankings",
            description="Who has the most jail sentences?",
            emoji="🏛",
        ),
        RankingType.SPAM_SCORE: RankingDefinition(
            type=RankingType.SPAM_SCORE,
            title="Spam Score Rankings",
            description="Who is the biggest spammer?",
            emoji="📢",
        ),
    }
