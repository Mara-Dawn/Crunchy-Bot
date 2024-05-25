import discord


class EquipmentHeadEmbed(discord.Embed):

    def __init__(
        self,
        member: discord.Member,
        max_width: int = 44,
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
        max_width: int = 44,
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
        max_width: int = 44,
    ):
        description = "Here you can see your currently active skills."
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

    ITEMS_PER_PAGE = 7

    def __init__(
        self,
        member: discord.Member,
        max_width: int = 44,
    ):
        description = "Select the piece of gear you want to equip."
        if len(description) < max_width:
            spacing = max_width - len(description)
            description += " " * spacing

        description = f"```python\n{description}```"

        super().__init__(
            title="Gear Select",
            color=discord.Colour.purple(),
            description=description,
        )
        self.set_thumbnail(url=member.display_avatar.url)
