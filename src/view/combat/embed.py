import discord
from combat.gear.types import Rarity
from config import Config


class EquipmentHeadEmbed(discord.Embed):

    def __init__(
        self,
        member: discord.Member,
        max_width: int = 45,
    ):
        description = "Here you can see the gear you are currently wearing."
        if len(description) < max_width:
            spacing = max_width - len(description)
            description += " " * spacing

        description = f"```python\n{description}```"

        super().__init__(
            title="Equipped Gear",
            color=discord.Colour.purple(),
            description=description,
        )
        self.set_thumbnail(url=member.display_avatar.url)


class AttributesHeadEmbed(discord.Embed):

    def __init__(
        self,
        member: discord.Member,
        max_width: int = 45,
    ):
        description = "Here you can see how your gear affects you in combat."
        if len(description) < max_width:
            spacing = max_width - len(description)
            description += " " * spacing

        description = f"```python\n{description}```"

        super().__init__(
            title="Character Attributes",
            color=discord.Colour.purple(),
            description=description,
        )
        self.set_thumbnail(url=member.display_avatar.url)


class SkillsHeadEmbed(discord.Embed):

    def __init__(
        self,
        member: discord.Member,
        max_width: int = 45,
    ):
        description = "Here you can see your currently equipped skills.\n"
        if len(description) < max_width:
            spacing = max_width - len(description)
            description += " " * spacing

        description = f"```python\n{description}```"

        super().__init__(
            title="Equipped Skills",
            color=discord.Colour.purple(),
            description=description,
        )
        self.set_thumbnail(url=member.display_avatar.url)


class SelectGearHeadEmbed(discord.Embed):

    ITEMS_PER_PAGE = 4

    def __init__(
        self,
        member: discord.Member,
        max_width: int = 45,
    ):
        description = "Manage your gear here. Equip pieces, lock them to keep them safe or scrap anything you don't need.\n\n"
        description += (
            "[🔒] - Item is locked and wont get scrapped by any scrap buttons."
        )
        if len(description) < max_width:
            spacing = max_width - len(description)
            description += " " * spacing

        description = f"```ansi\n{description}```"

        super().__init__(
            title="Gear Select",
            color=discord.Colour.purple(),
            description=description,
        )
        self.set_thumbnail(url=member.display_avatar.url)


class ManageSkillHeadEmbed(discord.Embed):

    ITEMS_PER_PAGE = 4

    def __init__(
        self,
        member: discord.Member,
        max_width: int = 45,
    ):
        description = "Manage your skills here. Equip new ones, lock the ones you want to keep safe and scrap the ones you don't need.\n\n"
        description += "Once you equip a skill it will be removed from your inventory. Equipping a new skill [31mwill override the old one[0m.\n\n"
        description += (
            "[🔒] - Item is locked and wont get scrapped by any scrap buttons.\n\n"
        )
        description += "[30m[!][0m - Damage penalty for using the wrong weapon type."
        if len(description) < max_width:
            spacing = max_width - len(description)
            description += " " * spacing

        description = f"```ansi\n{description}```"

        super().__init__(
            title="Manage Skills",
            color=discord.Colour.purple(),
            description=description,
        )
        self.set_thumbnail(url=member.display_avatar.url)


class SelectSkillHeadEmbed(discord.Embed):

    ITEMS_PER_PAGE = 4

    def __init__(
        self,
        member: discord.Member,
        max_width: int = 45,
    ):
        description = "Select the skills you want to equip.\n\n"
        description += "Once you equip a skill it will be removed from your inventory. Equipping a new skill [31mwill override the old one[0m.\n\n"
        description += (
            "[🔒] - Item is locked and wont get scrapped by any scrap buttons.\n\n"
        )
        description += "[30m[!][0m - Damage penalty for using the wrong weapon type."

        if len(description) < max_width:
            spacing = max_width - len(description)
            description += " " * spacing

        description = f"```ansi\n{description}```"

        super().__init__(
            title="Skill Select",
            color=discord.Colour.purple(),
            description=description,
        )
        self.set_thumbnail(url=member.display_avatar.url)


class ForgeEmbed(discord.Embed):

    def __init__(
        self,
        member: discord.Member,
        guild_level: int,
        max_rarity: Rarity,
        max_width: int = 45,
    ):
        description = (
            "Toss your scrap into this gaping hole and it will spit out random items for you.\n\n"
            f"Max item level: [35m{guild_level}[0m\n"
            f"Max item rarity: [35m{max_rarity.value}[0m"
        )

        if len(description) < max_width:
            spacing = max_width - len(description)
            description += " " * spacing

        description = f"```ansi\n{description}```"

        super().__init__(
            title="The Mighty Forge",
            color=discord.Colour.purple(),
            description=description,
        )
        # self.set_thumbnail(url=member.display_avatar.url)
        self.set_image(url="https://i.imgur.com/Up107tP.png")


class EnemyOverviewEmbed(discord.Embed):

    def __init__(
        self,
        member: discord.Member,
        guild_level: int,
        progress: int,
        max_width: int = 45,
    ):
        description = (
            "Random encounters will spawn here, group up and strategize together to overcome them.\n"
            "As you defeat more enemies, your level will rise and unlock more powerful foes with even better rewards.\n\n"
            f"Current Server Level: [35m{guild_level}[0m\n"
            f"Progress to next level: [35m{progress}[0m/[35m{Config.LEVEL_REQUIREMENTS[guild_level]}[0m"
            # f" lvl.[35m{guild_level}[0m Enemies\n"
        )

        progress = min(progress, Config.LEVEL_REQUIREMENTS[guild_level])

        if (
            guild_level
        ) in Config.BOSS_LEVELS and progress == Config.LEVEL_REQUIREMENTS[guild_level]:
            description += "\n[31mA POWERFUL FOE IS APPROACHING[0m"

        if len(description) < max_width:
            spacing = max_width - len(description)
            description += " " * spacing

        description = f"```ansi\n{description}```"

        super().__init__(
            title="Combat Zone",
            color=discord.Colour.purple(),
            description=description,
        )
        self.set_thumbnail(url=member.display_avatar.url)
