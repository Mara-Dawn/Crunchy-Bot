import discord


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
        description = "Manage your gear here. Equip pieces, lock them to keep them safe or scrap anything you don't need."
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
        description += "Once you equip a skill it will be removed from your inventory. Equipping a new skill [31mwill override the old one[0m."
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
        description += "Once you equip a skill it will be removed from your inventory. Equipping a new skill [31mwill override the old one[0m."
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
