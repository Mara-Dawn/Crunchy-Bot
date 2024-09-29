import random

import discord

from combat.gear.droppable import Droppable, DroppableBase
from combat.gear.types import Base, EquipmentSlot, Rarity
from combat.skills.status_effect import SkillStatusEffect, StatusEffectOutcome
from combat.skills.types import SkillEffect, SkillTarget, SkillType
from config import Config


class BaseSkill(DroppableBase):

    DEFAULT_IMAGE = {
        SkillEffect.PHYSICAL_DAMAGE: "https://i.imgur.com/FHvWc7b.png",
        SkillEffect.NEUTRAL_DAMAGE: "https://i.imgur.com/FHvWc7b.png",
        SkillEffect.MAGICAL_DAMAGE: "https://i.imgur.com/zr785IX.png",
        SkillEffect.HEALING: "https://i.imgur.com/AH7NRhc.png",
    }

    def __init__(
        self,
        name: str,
        skill_type: SkillType,
        description: str,
        information: str,
        skill_effect: SkillEffect,
        cooldown: int,
        base_value: float,
        initial_cooldown: int = None,
        min_level: int = 1,
        max_level: int = 99,
        droppable: bool = True,
        hits: int = 1,
        stacks: int = None,
        status_effects: list[SkillStatusEffect] = None,
        reset_after_encounter: bool = False,
        aoe: bool = False,
        weight: int = 100,
        image_url: str = None,
        default_target: SkillTarget = SkillTarget.OPPONENT,
        modifiable: bool = True,
        max_targets: int = None,
        no_scaling: bool = False,
        custom_crit: float = None,
        uniques: list[SkillType] = None,
        base_skill_type: SkillType = None,
        author: str = None,
        max_hits: int = None,
    ):
        super().__init__(
            name=name,
            base_type=Base.SKILL,
            slot=EquipmentSlot.SKILL,
            type=skill_type,
            min_level=min_level,
            max_level=max_level,
            weight=weight,
            droppable=droppable,
            uniques=uniques,
            author=author,
        )
        self.name = name
        self.skill_type = skill_type
        self.description = description
        self.information = information
        self.skill_effect = skill_effect
        self.cooldown = cooldown
        self.base_value = base_value
        self.initial_cooldown = initial_cooldown
        self.hits = hits
        self.stacks = stacks
        self.status_effects = status_effects
        self.reset_after_encounter = reset_after_encounter
        self.aoe = aoe
        self.modifiable = modifiable
        self.default_target = default_target
        self.image_url = image_url
        self.custom_crit = custom_crit
        self.max_targets = max_targets
        self.no_scaling = no_scaling
        self.max_hits = max_hits
        self.base_skill_type = base_skill_type

        if self.image_url is None:
            self.image_url = self.DEFAULT_IMAGE[self.skill_effect]

        if self.status_effects is None:
            self.status_effects = []

        if self.base_skill_type is None:
            self.base_skill_type = self.skill_type


class Skill(Droppable):

    EFFECT_LABEL_MAP = {
        SkillEffect.NEUTRAL_DAMAGE: "Damage",
        SkillEffect.PHYSICAL_DAMAGE: "Damage",
        SkillEffect.MAGICAL_DAMAGE: "Damage",
        SkillEffect.NOTHING: "",
        SkillEffect.BUFF: "Effect",
        SkillEffect.HEALING: "Healing",
    }

    RARITY_SORT_MAP = {
        Rarity.DEFAULT: 0,
        Rarity.COMMON: 1,
        Rarity.UNCOMMON: 2,
        Rarity.RARE: 3,
        Rarity.LEGENDARY: 4,
        Rarity.UNIQUE: 5,
    }

    EFFECT_SORT_MAP = {
        SkillEffect.PHYSICAL_DAMAGE: 0,
        SkillEffect.MAGICAL_DAMAGE: 1,
        SkillEffect.NEUTRAL_DAMAGE: 2,
        SkillEffect.STATUS_EFFECT_DAMAGE: 3,
        SkillEffect.HEALING: 4,
        SkillEffect.BUFF: 5,
        SkillEffect.NOTHING: 6,
    }

    RARITY_STACKS_SCALING = {
        Rarity.DEFAULT: 1,
        Rarity.COMMON: 1,
        Rarity.UNCOMMON: 1.2,
        Rarity.RARE: 1.5,
        Rarity.LEGENDARY: 2,
        Rarity.UNIQUE: 1,
    }

    RARITY_DAMAGE_SCALING = {
        Rarity.DEFAULT: 0,
        Rarity.COMMON: 0,
        Rarity.UNCOMMON: 0.1,
        Rarity.RARE: 0.2,
        Rarity.LEGENDARY: 0.3,
        Rarity.UNIQUE: 0,
    }

    def __init__(
        self,
        base_skill: BaseSkill,
        rarity: Rarity,
        level: int,
        locked: bool = False,
        id: int = None,
    ):
        if not SkillType.is_weapon_skill(base_skill.skill_type):
            base_skill.base_value = base_skill.base_value * (
                1 + (self.RARITY_DAMAGE_SCALING[rarity] / base_skill.hits)
            )
        if base_skill.stacks is not None:
            base_skill.stacks = int(
                base_skill.stacks * self.RARITY_STACKS_SCALING[rarity]
            )

        super().__init__(
            name=base_skill.name,
            base=base_skill,
            type=base_skill.skill_type,
            description=base_skill.description,
            information=base_skill.information,
            slot=EquipmentSlot.SKILL,
            level=level,
            rarity=rarity,
            base_value=base_skill.base_value,
            image_url=base_skill.image_url,
        )
        self.locked = locked
        self.base_skill = base_skill
        self.id = id

    def get_embed(
        self,
        show_data: bool = True,
        show_info: bool = False,
        equipped: bool = False,
        show_locked_state: bool = False,
        scrap_value: int = None,
        max_width: int = None,
    ) -> discord.Embed:
        if max_width is None:
            max_width = Config.COMBAT_EMBED_MAX_WIDTH
        # color = self.EFFECT_COLOR_MAP[self.base_skill.skill_effect]
        color = self.RARITY_COLOR_HEX_MAP[self.rarity]

        name = f"<- {self.name} ->"
        suffix = ""
        if equipped:
            color = discord.Color.purple()
            suffix += " [EQ]"
        elif self.locked and show_locked_state:
            suffix += " [🔒]"

        info_block = "```ansi\n"
        info_block += (
            f"{Droppable.RARITY_NAME_COLOR_MAP[self.rarity]}{name}[0m{suffix}"
        )

        slot = self.base.slot.value
        if SkillType.is_weapon_skill(self.base_skill.skill_type):
            slot = "Weapon Skill"

        spacing = " " * (max_width - len(name) - len(slot) - len(suffix) - 2)
        info_block += f"{spacing}[{slot}]"
        info_block += "```"

        description = f'"{self.description}"'

        if len(description) < max_width:
            description += " " + "\u00a0" * max_width

        prefixes = []
        suffixes = []

        if show_data:
            max_len_pre = 8
            max_len_suf = 9

            # Rarity
            name = "Rarity"
            spacing = " " * (max_len_suf - len(self.rarity.value))
            rarity_line = f"{name}: {self.rarity.value}{spacing}"
            rarity_line_colored = f"{name}: {Droppable.RARITY_COLOR_MAP[self.rarity]}{self.rarity.value}[0m{spacing}"
            suffixes.append((rarity_line_colored, len(rarity_line)))

            # Item Level
            # name = "Level"
            # spacing = " " * (max_len_suf - len(str(self.level)))
            # level_line = f"{name}: {self.level}{spacing}"
            # level_line_colored = f"{name}: [32m{self.level}[0m{spacing}"
            # suffixes.append((level_line_colored, len(level_line)))

            # Base Value
            if self.scaling > 0:
                name = "Power"
                suffix_sign = ""
                if self.base_skill.skill_effect == SkillEffect.BUFF:
                    suffix_sign = "%"
                spacing = " " * (max_len_pre - len(name))
                base_value_text = f"{spacing}{name}: {self.scaling:.1f}{suffix_sign}"
                base_value_text_colored = (
                    f"{spacing}{name}: [35m{self.scaling:.1f}{suffix_sign}[0m"
                )
                prefixes.append((base_value_text_colored, len(base_value_text)))

            # Hits
            if self.base_skill.hits > 1:
                name = "Hits"
                spacing = " " * (max_len_pre - len(name))
                type_text = f"{spacing}{name}: {self.base_skill.hits}"
                type_text_colored = f"{spacing}{name}: [35m{self.base_skill.hits}[0m"
                prefixes.append((type_text_colored, len(type_text)))

            # Type
            name = "Type"
            spacing = " " * (max_len_pre - len(name))
            type_text = f"{spacing}{name}: {self.base_skill.skill_effect.value}"
            type_text_colored = (
                f"{spacing}{name}: [35m{self.base_skill.skill_effect.value}[0m"
            )
            prefixes.append((type_text_colored, len(type_text)))

            # Cooldown
            if self.base_skill.cooldown > 0:
                name = "Cooldown"
                spacing = " " * (max_len_suf - len(f"{self.base_skill.cooldown} Turns"))
                cooldown_text = f"{name}: {self.base_skill.cooldown} Turns{spacing}"
                cooldown_text_colored = (
                    f"{name}: [35m{self.base_skill.cooldown}[0m Turns{spacing}"
                )
                suffixes.append((cooldown_text_colored, len(cooldown_text)))

            # Stacks
            max_stacks = self.base_skill.stacks
            if max_stacks is not None and max_stacks > 0:
                name = "Uses"
                spacing = " " * (max_len_pre - len(name))
                stacks_text = f"{spacing}{name}: {max_stacks} Turn(s)"
                stacks_text_colored = f"{spacing}{name}: [35m{max_stacks}[0m"

                if self.base_skill.reset_after_encounter:
                    append = " (per Combat)"
                else:
                    append = " (Total)"

                stacks_text += append
                stacks_text_colored += append

                prefixes.append((stacks_text_colored, len(stacks_text)))

            info_block += "```ansi\n"

            lines = max(len(prefixes), len(suffixes))

            for line in range(lines):
                prefix = ""
                suffix = ""
                len_prefix = 0
                len_suffix = 0
                if len(prefixes) > line:
                    len_prefix = prefixes[line][1]
                    prefix = prefixes[line][0]
                if len(suffixes) > line:
                    len_suffix = suffixes[line][1]
                    suffix = suffixes[line][0]

                spacing_width = max_width - len_prefix - len_suffix
                spacing = " " * spacing_width
                info_block += f"{prefix}{spacing}{suffix}\n"

            info_block += "```"

        info_block += f"```python\n{description}```"

        if scrap_value is not None:
            stock_label = "Stock: 1"
            scrap_label = f"Cost: ⚙️{scrap_value}"
            spacing_width = max_width - len(scrap_label) - len(stock_label)
            spacing = " " * spacing_width

            scrap_text = f"{stock_label}{spacing}{scrap_label}"
            info_block += f"```python\n{scrap_text}```"

        if show_info:
            info_block += f"```ansi\n[37m{self.information}```"

        embed = discord.Embed(title="", description=info_block, color=color)
        embed.set_thumbnail(url=self.base_skill.image_url)
        if self.base_skill.author is not None:
            embed.set_footer(text=f"by {self.base_skill.author}")
        return embed


class CharacterSkill:

    def __init__(
        self,
        skill: Skill,
        last_used: int,
        stacks_used: int,
        min_roll: int,
        max_roll: int,
        penalty: bool = False,
    ):
        self.skill = skill
        self.last_used = last_used
        self.stacks_used = stacks_used
        self.min_roll = min_roll
        self.max_roll = max_roll
        self.penalty = penalty

    def on_cooldown(self):
        if self.last_used is None or self.skill.base_skill.cooldown is None:
            return False
        return self.last_used < self.skill.base_skill.cooldown

    def stacks_left(self):
        if self.skill.base_skill.stacks is None or self.stacks_used is None:
            return None
        return self.skill.base_skill.stacks - self.stacks_used

    def get_embed(
        self,
        show_data: bool = True,
        show_full_data: bool = False,
        show_info: bool = False,
        equipped: bool = False,
        show_locked_state: bool = False,
        amount: int = None,
        max_width: int = None,
    ) -> discord.Embed:
        if max_width is None:
            max_width = Config.COMBAT_EMBED_MAX_WIDTH
        # color = self.skill.EFFECT_COLOR_MAP[self.skill.base_skill.skill_effect]
        color = self.skill.RARITY_COLOR_HEX_MAP[self.skill.rarity]

        if self.stacks_left() is not None and self.stacks_left() <= 0:
            color = discord.Color.dark_grey()

        suffix = ""
        if equipped:
            color = discord.Color.purple()
            suffix += " [EQ]"
        elif self.skill.locked and show_locked_state:
            suffix += " [🔒]"
        # name = f"<~ {self.skill.base_skill.name} ~>"
        name = f"<- {self.skill.base_skill.name} ->"

        info_block = "```ansi\n"
        info_block += (
            f"{Droppable.RARITY_NAME_COLOR_MAP[self.skill.rarity]}{name}[0m{suffix}"
        )

        slot = self.skill.base_skill.slot.value
        if SkillType.is_weapon_skill(self.skill.base_skill.skill_type):
            slot = "Weapon Skill"

        spacing = " " * (max_width - len(name) - len(slot) - len(suffix) - 2)
        info_block += f"{spacing}[{slot}]"
        info_block += "```"

        description = f'"{self.skill.base_skill.description}"'

        if len(description) < max_width:
            description += " " + "\u00a0" * max_width

        prefixes = []
        suffixes = []

        if show_data:
            max_len_pre = 8
            max_len_suf = 9

            if show_full_data:
                # Rarity
                name = "Rarity"
                spacing = " " * (max_len_suf - len(self.skill.rarity.value))
                rarity_line = f"{name}: {self.skill.rarity.value}{spacing}"
                rarity_line_colored = f"{name}: {Droppable.RARITY_COLOR_MAP[self.skill.rarity]}{self.skill.rarity.value}[0m{spacing}"
                suffixes.append((rarity_line_colored, len(rarity_line)))

                # Item Level
                # name = "Level"
                # spacing = " " * (max_len_suf - len(str(self.skill.level)))
                # level_line = f"{name}: {self.skill.level}{spacing}"
                # level_line_colored = f"{name}: [32m{self.skill.level}[0m{spacing}"
                # suffixes.append((level_line_colored, len(level_line)))

            # Damage
            caption = self.skill.EFFECT_LABEL_MAP[self.skill.base_skill.skill_effect]
            spacing = " " * (max_len_pre - len(caption))
            penalty = penalty_colored = ""
            if self.penalty:
                penalty = " [!]"
                penalty_colored = f"[30m{penalty}[0m "
            match self.skill.base_skill.skill_effect:
                case SkillEffect.BUFF:
                    damage_text = (
                        f"{spacing}{caption}: {self.skill.base_skill.base_value:.1f}%"
                    )
                    damage_text_colored = f"{spacing}{caption}: [35m{self.skill.base_skill.base_value:.1f}%[0m"
                case _:
                    damage_text = f"{spacing}{caption}: {self.min_roll} - {self.max_roll}{penalty}"
                    damage_text_colored = f"{spacing}{caption}: [35m{self.min_roll}[0m - [35m{self.max_roll}[0m{penalty_colored}"
            prefixes.append((damage_text_colored, len(damage_text)))

            # Hits
            if self.skill.base_skill.hits > 1:
                name = "Hits"
                spacing = " " * (max_len_pre - len(name))
                type_text = f"{spacing}{name}: {self.skill.base_skill.hits}"
                type_text_colored = (
                    f"{spacing}{name}: [35m{self.skill.base_skill.hits}[0m"
                )
                prefixes.append((type_text_colored, len(type_text)))

            # Type
            name = "Type"
            spacing = " " * (max_len_pre - len(name))
            type_text = f"{spacing}{name}: {self.skill.base_skill.skill_effect.value}"
            type_text_colored = (
                f"{spacing}{name}: [35m{self.skill.base_skill.skill_effect.value}[0m"
            )
            prefixes.append((type_text_colored, len(type_text)))

            # Cooldown
            if self.skill.base_skill.cooldown > 0:
                name = "Cooldown"
                spacing = " " * (
                    max_len_suf - len(f"{self.skill.base_skill.cooldown} Turns")
                )
                cooldown_text = (
                    f"{name}: {self.skill.base_skill.cooldown} Turns{spacing}"
                )
                cooldown_text_colored = (
                    f"{name}: [35m{self.skill.base_skill.cooldown}[0m Turns{spacing}"
                )
                suffixes.append((cooldown_text_colored, len(cooldown_text)))

            # Stacks
            max_stacks = self.skill.base_skill.stacks
            if max_stacks is not None and max_stacks > 0:
                name = "Uses"
                spacing = " " * (max_len_pre - len(name))

                stacks_text = f"{spacing}{name}: {self.stacks_left()}/{max_stacks}"
                stacks_text_colored = f"{spacing}{name}: [35m{self.stacks_left()}[0m/[35m{max_stacks}[0m"

                if self.skill.base_skill.reset_after_encounter:
                    append = " (per Combat)"
                else:
                    append = " (Total)"

                stacks_text += append
                stacks_text_colored += append

                prefixes.append((stacks_text_colored, len(stacks_text)))

            info_block += "```ansi\n"

            lines = max(len(prefixes), len(suffixes))

            for line in range(lines):
                prefix = ""
                suffix = ""
                len_prefix = 0
                len_suffix = 0
                if len(prefixes) > line:
                    len_prefix = prefixes[line][1]
                    prefix = prefixes[line][0]
                if len(suffixes) > line:
                    len_suffix = suffixes[line][1]
                    suffix = suffixes[line][0]

                spacing_width = max_width - len_prefix - len_suffix
                spacing = " " * spacing_width
                info_block += f"{prefix}{spacing}{suffix}\n"

            cooldown_info = ""
            if self.skill.base_skill.cooldown > 0 and self.on_cooldown():
                cooldown_remaining = self.skill.base_skill.cooldown - self.last_used
                cooldown_info = f"\navailable in [35m{cooldown_remaining}[0m turn(s)"

            info_block += f"{cooldown_info}```"

        if amount is not None and amount > 1:
            amount_text = f"amount: {amount}"
            spacing_width = max_width - max(11, len(amount_text))
            spacing = " " * spacing_width
            description += f"\n\n{spacing}{amount_text}"

        info_block += f"```python\n{description}```"

        if show_info:
            info_block += f"```ansi\n[37m{self.skill.base_skill.information}```"

        embed = discord.Embed(title="", description=info_block, color=color)
        embed.set_thumbnail(url=self.skill.base_skill.image_url)
        if show_full_data and self.skill.base_skill.author is not None:
            embed.set_footer(text=f"by {self.skill.base_skill.author}")
        return embed

    def add_to_embed(
        self,
        embed: discord.Embed,
        max_width: int = None,
        description_override: str = None,
    ) -> None:
        if max_width is None:
            max_width = Config.COMBAT_EMBED_MAX_WIDTH

        prefix = ""
        if self.skill.rarity.value != Rarity.DEFAULT and not SkillType.is_weapon_skill(
            self.skill.base_skill.base_skill_type
        ):
            prefix = f"*{self.skill.rarity.value}* "

        title = f"> {prefix}**{self.skill.name}** "
        description = f'"{self.skill.description}"'
        if description_override is not None:
            description = f'"{description_override}"'

        if len(description) < max_width:
            description += " " + "\u00a0" * max_width

        info_block = f"```python\n{description}```"

        embed.add_field(name=title, value=info_block, inline=False)


class SkillInstance:

    def __init__(
        self,
        weapon_roll: int,
        skill_base: float,
        modifier: float,
        critical_modifier: float,
        encounter_scaling: float,
        crit_chance: float,
        is_crit: bool | None = None,
    ):
        self.weapon_roll = weapon_roll
        self.skill_base = skill_base
        self.modifier = modifier
        self.critical_modifier = critical_modifier
        self.encounter_scaling = encounter_scaling
        self.critical_chance = crit_chance
        self.is_crit = is_crit

    @property
    def value(self):
        if self.is_crit is None:
            self.is_crit = random.random() < self.critical_chance

        value = self.weapon_roll * self.skill_base * self.modifier

        if self.is_crit:
            value *= self.critical_modifier

        return int(value)

    @property
    def raw_value(self):
        value = self.weapon_roll * self.skill_base * self.modifier
        return int(value)

    @property
    def scaled_value(self):
        if self.is_crit is None:
            self.is_crit = random.random() < self.critical_chance

        value = self.weapon_roll * self.skill_base * self.modifier

        if self.is_crit:
            value *= self.critical_modifier

        if value > 0:
            value = max(1, value * self.encounter_scaling)

        return int(value)

    def apply_effect_outcome(self, outcome: StatusEffectOutcome):
        if outcome.modifier is not None:
            self.modifier *= outcome.modifier
        if self.is_crit is None:
            if outcome.crit_chance is not None:
                self.critical_chance = outcome.crit_chance
            if outcome.crit_chance_modifier is not None:
                self.critical_chance *= outcome.crit_chance_modifier
