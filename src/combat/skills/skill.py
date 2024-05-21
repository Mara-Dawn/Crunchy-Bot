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


class SkillData:

    def __init__(self, skill: Skill, last_used: int, min_roll: int, max_roll: int):
        self.skill = skill
        self.last_used = last_used
        self.min_roll = min_roll
        self.max_roll = max_roll

    def on_cooldown(self):
        if self.last_used is None:
            return False
        return self.last_used < self.skill.cooldown

    def add_to_embed(
        self,
        embed: discord.Embed,
        show_info: bool = False,
        show_data: bool = False,
        max_width: int = 42,
    ) -> None:
        title = f"> ~* {self.skill.name} *~"
        description = f'"{self.skill.description}"'
        cooldown_info = ""
        if self.skill.cooldown > 0 and self.on_cooldown():
            cooldown_remaining = self.skill.cooldown - self.last_used
            cooldown_info = f"\n*available in {cooldown_remaining}* turns."

        if len(description) < max_width:
            spacing = max_width - len(description)
            description += " " * spacing

        prefixes = []
        suffixes = []

        if show_data:
            prefixes.append(f"Cooldown: {self.skill.cooldown}")
            prefixes.append(f'Effect: "{self.skill.skill_effect.value}"')
            suffixes.append(f"Damage: {self.min_roll} - {self.max_roll}")

        info_block = f"{cooldown_info}```python\n{description}\n\n"

        lines = max(len(prefixes), len(suffixes))

        for line in range(lines):
            len_prefix = 0
            len_suffix = 0
            prefix = ""
            suffix = ""
            if len(prefixes) > line:
                len_prefix = len(prefixes[line])
                prefix = prefixes[line]
            if len(suffixes) > line:
                len_suffix = len(suffixes[line])
                suffix = suffixes[line]

            spacing_width = max_width - len_prefix - len_suffix
            spacing = " " * spacing_width
            info_block += f"{prefix}{spacing}{suffix}\n"

        info_block += "```"

        if show_info:
            info_block += f"```ansi\n[37m{self.skill.information}```"

        embed.add_field(name=title, value=info_block, inline=False)
