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
        hits: int = 1,
    ):
        self.name = name
        self.type = type
        self.description = description
        self.information = information
        self.skill_effect = skill_effect
        self.cooldown = cooldown
        self.base_value = base_value
        self.hits = hits


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
        max_width: int = 44,
    ) -> None:
        title = f"> {self.skill.name} "
        description = f'"{self.skill.description}"'

        cooldown_info = ""
        if self.skill.cooldown > 0 and self.on_cooldown():
            cooldown_remaining = self.skill.cooldown - self.last_used
            cooldown_info = f"\navailable in [35m{cooldown_remaining}[0m turn(s)"

        if len(description) < max_width:
            spacing = max_width - len(description)
            description += " " * spacing

        prefixes = []
        suffixes = []

        info_block = f"```python\n{description}```"

        if show_data:
            # Type
            type_text = f"    Type: {self.skill.skill_effect.value}"
            type_text_colored = f"    Type: [35m{self.skill.skill_effect.value}[0m"
            prefixes.append((type_text_colored, len(type_text)))

            # Cooldoqwn
            cooldown_text = f"Cooldown: {self.skill.cooldown} Turn(s)"
            cooldown_text_colored = f"Cooldown: [35m{self.skill.cooldown} Turn(s)[0m"
            prefixes.append((cooldown_text_colored, len(cooldown_text)))

            # Type
            damage_text = f"Damage: {self.min_roll} - {self.max_roll}"
            damage_text_colored = (
                f"Damage: [35m{self.min_roll}[0m - [35m{self.max_roll}[0m"
            )
            suffixes.append((damage_text_colored, len(damage_text)))

            info_block += "```ansi\n"

            lines = max(len(prefixes), len(suffixes))

            for line in range(lines):
                prefix = ""
                suffix = ""
                if len(prefixes) > line:
                    len_prefix = prefixes[line][1]
                    prefix = prefixes[line][0]
                if len(suffixes) > line:
                    len_suffix = suffixes[line][1]
                    suffix = suffixes[line][0]

                spacing_width = max_width - len_prefix - len_suffix
                spacing = " " * spacing_width
                info_block += f"{prefix}{spacing}{suffix}\n"

            info_block += cooldown_info
            info_block += "```\n\n"

        if show_info:
            info_block += f"```ansi\n[37m{self.skill.information}```"

        embed.add_field(name=title, value=info_block, inline=False)
