import discord

from combat.gear.gear import Gear
from combat.gear.types import Rarity
from combat.types import UnlockableFeature
from config import Config


class EquipmentHeadEmbed(discord.Embed):

    def __init__(
        self,
        member: discord.Member,
        is_owner: bool = True,
        max_width: int = 45,
    ):
        description = "Here you can see the gear you are currently wearing."
        if not is_owner:
            description = (
                f"Here you can see the gear {member.display_name} is currently wearing."
            )
        if len(description) < max_width:
            spacing = max_width - len(description)
            description += " " * spacing

        description = f"```\n{description}```"

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
        is_owner: bool = True,
        max_width: int = 45,
    ):
        description = "Here you can see how your gear affects you in combat."
        if not is_owner:
            description = f"Here you can see {member.display_name}'s attributes."
        if len(description) < max_width:
            spacing = max_width - len(description)
            description += " " * spacing

        description = f"```\n{description}```"

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
        is_owner: bool = True,
        max_width: int = 45,
    ):
        description = "Here you can see your currently equipped skills.\n"
        if not is_owner:
            description = f"Here you can see the skills {member.display_name} is currently using.\n"
        if len(description) < max_width:
            spacing = max_width - len(description)
            description += " " * spacing

        description = f"```\n{description}```"

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
            "[EQ] - Item is currently equipped.\n\n"
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
        description += "[EQ] - Item is currently equipped.\n\n"
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
            "[EQ] - Item is currently equipped.\n\n"
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


class EnchantmentHeadEmbed(discord.Embed):

    ITEMS_PER_PAGE = 4

    def __init__(
        self,
        member: discord.Member,
        max_width: int = 45,
    ):
        description = "Manage your enchantments and apply them to your gear pieces.\n\n"
        description += "Once you apply an enchantment it will be removed from your inventory. Applying a new enchantment [31mwill override the old one[0m.\n\n"
        description += "[30m[!][0m - Damage penalty for using the wrong weapon type."

        if len(description) < max_width:
            spacing = max_width - len(description)
            description += " " * spacing

        description = f"```ansi\n{description}```"

        super().__init__(
            title="Enchantment Table",
            color=discord.Colour.purple(),
            description=description,
        )
        self.set_thumbnail(url=member.display_avatar.url)


class EnchantmentSpacerEmbed(discord.Embed):

    ITEMS_PER_PAGE = 4

    def __init__(
        self,
        member: discord.Member,
        gear: Gear | None,
        max_width: int = 45,
    ):
        if gear is None:
            description = (
                "No gear has been selected. "
                "Select a piece of equipment to apply Enchantments to it."
            )
            title = "Empty"
        else:
            description = (
                "Select one of the following enchantments to apply to "
                "your selected piece of equipment."
            )
            title = f"Crafting with {gear.rarity.value} {gear.name}"

        if len(description) < max_width:
            spacing = max_width - len(description)
            description += " " * spacing

        description = f"```ansi\n{description}```"

        super().__init__(
            title=title,
            color=discord.Colour.purple(),
            description=description,
        )
        self.set_thumbnail(url=member.display_avatar.url)


class ForgeEmbed(discord.Embed):

    def __init__(
        self,
        member: discord.Member,
        forge_level: int,
        max_rarity: Rarity,
        max_width: int = 45,
    ):
        description = (
            "Toss your scrap into this gaping hole and it will spit out random items for you.\n\n"
            "Alternatively you can combine any three items in here to forge them into a new one. "
            "Try to find all the possible combinations!\n\n"
            f"Max item level: [35m{forge_level}[0m\n"
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
        requirement: int,
        progress: int,
        fresh_prog: bool,
        additional_info: str = None,
        max_width: int = 45,
    ):
        progress = min(progress, requirement)
        description = (
            "Random encounters will spawn here, group up and strategize together to overcome them.\n"
            "As you defeat more enemies, your level will rise and unlock more powerful foes with even better rewards.\n\n"
            f"Current Server Level: [35m{guild_level}[0m\n"
        )

        if (
            fresh_prog
            and progress < Config.FORGE_UNLOCK_REQUIREMENT
            and guild_level >= Config.UNLOCK_LEVELS[UnlockableFeature.FORGE_SCRAP]
        ):
            description += f"Progress to next forge level: [35m{progress}[0m/[35m{Config.FORGE_UNLOCK_REQUIREMENT}[0m\n"

        if guild_level < Config.MAX_LVL:
            description += f"Progress to next guild level: [35m{progress}[0m/[35m{requirement}[0m"

            if guild_level in Config.BOSS_LEVELS and progress >= requirement:
                description += "\n[31mDefeat The Boss To Progress.[0m"
        else:
            description += "You reached this seasons maximum level. Congratulations!"

        if len(description) < max_width:
            spacing = max_width - len(description)
            description += " " * spacing

        description = f"```ansi\n{description}```"

        if additional_info is not None:
            description += additional_info

        super().__init__(
            title="Combat Zone",
            color=discord.Colour.purple(),
            description=description,
        )
        self.set_thumbnail(url=member.display_avatar.url)
