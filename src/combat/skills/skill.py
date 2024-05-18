import discord
from combat.skills.types import SkillEffect, SkillType


class Skill:

    def __init__(
        self,
        name: str,
        type: SkillType,
        description: str,
        information: str,
        skill_effect: SkillEffect,
        cooldown: int,
        base_value: int,
    ):
        self.name = name
        self.type = type
        self.description = description
        self.information = information
        self.skill_effect = skill_effect
        self.cooldown = cooldown
        self.base_value = base_value

    def add_to_embed(self, embed: discord.Embed, show_info: bool = False) -> None:
        title = f"> ~* {self.name} *~"
        description = self.description
        info_block = f'```python\n"{description}"```'
        if show_info:
            info_block += f"```ansi\n[37m{self.information}```"
        embed.add_field(name=title, value=info_block, inline=False)
