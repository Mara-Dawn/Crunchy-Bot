import discord

from combat.effects.effect import Effect
from combat.effects.types import EffectTrigger
from combat.enchantments.types import EnchantmentEffect, EnchantmentType
from combat.gear.droppable import Droppable, DroppableBase
from combat.gear.types import Base, EquipmentSlot, Rarity
from combat.skills.types import SkillEffect
from config import Config
from control.types import FieldData


class BaseEnchantment(DroppableBase):

    DEFAULT_IMAGE = {
        EnchantmentEffect.EFFECT: "https://i.imgur.com/FHvWc7b.png",
        EnchantmentEffect.CRAFTING: "https://i.imgur.com/FHvWc7b.png",
    }

    def __init__(
        self,
        name: str,
        enchantment_type: EnchantmentType,
        description: str,
        information: str,
        enchantment_effect: EnchantmentEffect,
        value: float = 0,
        slot: EquipmentSlot = EquipmentSlot.ANY,
        min_level: int = 1,
        max_level: int = 99,
        droppable: bool = True,
        weight: int = 100,
        fixed_rarity: Rarity = None,
        image_url: str = None,
        uniques: list[EnchantmentType] = None,
        base_enchantment_type: EnchantmentType = None,
        author: str = None,
    ):
        super().__init__(
            name=name,
            base_type=Base.ENCHANTMENT,
            slot=slot,
            type=enchantment_type,
            min_level=min_level,
            max_level=max_level,
            weight=weight,
            droppable=droppable,
            uniques=uniques,
            author=author,
        )
        self.name = name
        self.value = value
        self.enchantment_type = enchantment_type
        self.description = description
        self.information = information
        self.enchantment_effect = enchantment_effect
        self.image_url = image_url
        self.base_enchantment_type = base_enchantment_type
        self.fixed_rarity = fixed_rarity

        if self.image_url is None:
            self.image_url = self.DEFAULT_IMAGE[self.enchantment_effect]

        if self.base_enchantment_type is None:
            self.base_enchantment_type = self.enchantment_type


class BaseCraftingEnchantment(BaseEnchantment):

    def __init__(
        self,
        name: str,
        enchantment_type: EnchantmentType,
        description: str,
        information: str,
        value: float = 0,
        slot: EquipmentSlot = EquipmentSlot.ANY,
        min_level: int = 1,
        max_level: int = 99,
        droppable: bool = True,
        weight: int = 100,
        fixed_rarity: Rarity = None,
        image_url: str = None,
        uniques: list[EnchantmentType] = None,
        base_enchantment_type: EnchantmentType = None,
        author: str = None,
    ):
        super().__init__(
            name=name,
            enchantment_type=enchantment_type,
            description=description,
            information=information,
            enchantment_effect=EnchantmentEffect.CRAFTING,
            value=value,
            slot=slot,
            min_level=min_level,
            max_level=max_level,
            droppable=droppable,
            weight=weight,
            fixed_rarity=fixed_rarity,
            image_url=image_url,
            uniques=uniques,
            base_enchantment_type=base_enchantment_type,
            author=author,
        )


class BaseEffectEnchantment(BaseEnchantment, Effect):

    def __init__(
        self,
        name: str,
        enchantment_type: EnchantmentType,
        description: str,
        information: str,
        value: float = 0,
        slot: EquipmentSlot = EquipmentSlot.ANY,
        min_level: int = 1,
        max_level: int = 99,
        droppable: bool = True,
        stacks: int = None,
        hits: int = 1,
        cooldown: int = 0,
        initial_cooldown: int = None,
        reset_after_encounter: bool = False,
        weight: int = 100,
        fixed_rarity: Rarity = None,
        image_url: str = None,
        uniques: list[EnchantmentType] = None,
        base_enchantment_type: EnchantmentType = None,
        author: str = None,
        trigger: list[EffectTrigger] = None,
        consumed: list[EffectTrigger] = None,
        skill_effect: SkillEffect = None,
        emoji: str = None,
        delay_trigger: bool = False,
        delay_consume: bool = False,
        delay_for_source_only: bool = False,
        single_description: bool = False,
    ):
        BaseEnchantment.__init__(
            self,
            name=name,
            enchantment_type=enchantment_type,
            description=description,
            information=information,
            enchantment_effect=EnchantmentEffect.EFFECT,
            value=value,
            slot=slot,
            min_level=min_level,
            max_level=max_level,
            droppable=droppable,
            weight=weight,
            fixed_rarity=fixed_rarity,
            image_url=image_url,
            uniques=uniques,
            base_enchantment_type=base_enchantment_type,
            author=author,
        )
        Effect.__init__(
            self,
            effect_type=enchantment_type,
            name=name,
            description=description,
            trigger=trigger,
            consumed=consumed,
            skill_effect=skill_effect,
            emoji=emoji,
            delay_trigger=delay_trigger,
            delay_consume=delay_consume,
            delay_for_source_only=delay_for_source_only,
            single_description=single_description,
        )
        self.stacks = stacks
        self.cooldown = cooldown
        self.initial_cooldown = initial_cooldown
        self.reset_after_encounter = reset_after_encounter
        self.hits = hits


class Enchantment(Droppable):

    TYPE_LABEL_MAP = {
        EnchantmentEffect.CRAFTING: "Crafting",
        EnchantmentEffect.EFFECT: "Gear Effect",
    }

    EFFECT_LABEL_MAP = {
        SkillEffect.NEUTRAL_DAMAGE: "Damage",
        SkillEffect.PHYSICAL_DAMAGE: "Damage",
        SkillEffect.MAGICAL_DAMAGE: "Damage",
        SkillEffect.EFFECT_DAMAGE: "Damage",
        SkillEffect.NOTHING: "",
        SkillEffect.BUFF: "Effect",
        SkillEffect.HEALING: "Healing",
    }

    EFFECT_TYPE_LABEL_MAP = {
        SkillEffect.NEUTRAL_DAMAGE: "Neutral Dmg.",
        SkillEffect.PHYSICAL_DAMAGE: "Phys. Dmg.",
        SkillEffect.MAGICAL_DAMAGE: "Mag. Dmg.",
        SkillEffect.EFFECT_DAMAGE: "Neutral Dmg.",
        SkillEffect.NOTHING: "Special",
        SkillEffect.BUFF: "Buff",
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
        EnchantmentEffect.CRAFTING: 0,
        EnchantmentEffect.EFFECT: 1,
    }

    RARITY_STACKS_SCALING = {
        Rarity.DEFAULT: 1,
        Rarity.COMMON: 1,
        Rarity.UNCOMMON: 1.2,
        Rarity.RARE: 1.5,
        Rarity.LEGENDARY: 2,
        Rarity.UNIQUE: 1,
    }

    RARITY_VALUE_SCALING = {
        Rarity.DEFAULT: 1,
        Rarity.COMMON: 1,
        Rarity.UNCOMMON: 1.1,
        Rarity.RARE: 1.2,
        Rarity.LEGENDARY: 1.3,
        Rarity.UNIQUE: 1,
    }

    def __init__(
        self,
        base_enchantment: BaseEnchantment,
        rarity: Rarity,
        level: int,
        locked: bool = False,
        id: int = None,
    ):
        base_enchantment.value *= self.RARITY_VALUE_SCALING[rarity]

        super().__init__(
            name=base_enchantment.name,
            base=base_enchantment,
            type=base_enchantment.enchantment_type,
            description=base_enchantment.description,
            information=base_enchantment.information,
            slot=base_enchantment.slot,
            level=level,
            rarity=rarity,
            base_value=base_enchantment.value,
            image_url=base_enchantment.image_url,
        )
        self.locked = locked
        self.base_enchantment = base_enchantment
        self.id = id

    def get_embed(
        self,
        show_data: bool = True,
        show_info: bool = False,
        show_locked_state: bool = False,
        scrap_value: int = None,
        amount: int = None,
        max_width: int = None,
    ) -> discord.Embed:
        if max_width is None:
            max_width = Config.COMBAT_EMBED_MAX_WIDTH

        color = self.RARITY_COLOR_HEX_MAP[self.rarity]

        name = f"<~ {self.name} ~>"
        suffix = ""

        if self.locked and show_locked_state:
            suffix += " [🔒]"

        info_block = "```ansi\n"
        info_block += (
            f"{Droppable.RARITY_NAME_COLOR_MAP[self.rarity]}{name}[0m{suffix}"
        )

        effect = "Enchantment"

        spacing = " " * (max_width - len(name) - len(effect) - len(suffix) - 2)
        info_block += f"{spacing}[{effect}]"
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

            # Type
            name = "Type"
            type_value = self.TYPE_LABEL_MAP[
                self.base_enchantment.enchantment_effect.value
            ]
            spacing = " " * (max_len_pre - len(name))
            type_text = f"{spacing}{name}: {type_value}"
            type_text_colored = f"{spacing}{name}: [35m{type_value}[0m"
            prefixes.append((type_text_colored, len(type_text)))

            # Base Value
            value = self.base_enchantment.value
            if value > 0:
                name = "Value"
                suffix_sign = ""
                spacing = " " * (max_len_pre - len(name))
                base_value_text = f"{spacing}{name}: {value:.1f}{suffix_sign}"
                base_value_text_colored = (
                    f"{spacing}{name}: [35m{value:.1f}{suffix_sign}[0m"
                )
                prefixes.append((base_value_text_colored, len(base_value_text)))

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

        if amount is not None and amount > 1:
            amount_text = f"amount: {amount}"
            spacing_width = max_width - max(11, len(amount_text))
            spacing = " " * spacing_width
            description += f"\n{spacing}{amount_text}"

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
        embed.set_thumbnail(url=self.base_enchantment.image_url)
        if self.base_enchantment.author is not None:
            embed.set_footer(text=f"by {self.base_enchantment.author}")
        return embed


class EffectEnchantment(Enchantment):

    def __init__(
        self,
        base_enchantment: BaseEffectEnchantment,
        rarity: Rarity,
        level: int,
        locked: bool = False,
        priority: int = 100,
        id: int = None,
    ):
        super().__init__(
            base_enchantment=base_enchantment,
            rarity=rarity,
            level=level,
            locked=locked,
            id=id,
        )
        if base_enchantment.stacks is not None:
            base_enchantment.stacks = int(
                base_enchantment.stacks * self.RARITY_STACKS_SCALING[rarity]
            )
        self.base_enchantment: BaseEffectEnchantment = base_enchantment
        self.priority = priority

    def get_embed(
        self,
        show_data: bool = True,
        show_info: bool = False,
        show_locked_state: bool = False,
        scrap_value: int = None,
        amount: int = None,
        max_width: int = None,
    ) -> discord.Embed:
        if max_width is None:
            max_width = Config.COMBAT_EMBED_MAX_WIDTH

        color = self.RARITY_COLOR_HEX_MAP[self.rarity]

        name = f"<~ {self.name} ~>"
        suffix = ""

        if self.locked and show_locked_state:
            suffix += " [🔒]"

        info_block = "```ansi\n"
        info_block += (
            f"{Droppable.RARITY_NAME_COLOR_MAP[self.rarity]}{name}[0m{suffix}"
        )

        effect = "Enchantment"

        spacing = " " * (max_width - len(name) - len(effect) - len(suffix) - 2)
        info_block += f"{spacing}[{effect}]"
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

            # Base Value
            if self.scaling > 0:
                name = "Power"
                suffix_sign = ""
                if (
                    self.base_enchantment.skill_effect is not None
                    and self.base_enchantment.skill_effect == SkillEffect.BUFF
                ):
                    suffix_sign = "%"
                spacing = " " * (max_len_pre - len(name))
                base_value_text = f"{spacing}{name}: {self.scaling:.1f}{suffix_sign}"
                base_value_text_colored = (
                    f"{spacing}{name}: [35m{self.scaling:.1f}{suffix_sign}[0m"
                )
                prefixes.append((base_value_text_colored, len(base_value_text)))

            # Hits
            if self.base_enchantment.hits > 1:
                name = "Hits"
                spacing = " " * (max_len_pre - len(name))
                type_text = f"{spacing}{name}: {self.base_enchantment.hits}"
                type_text_colored = (
                    f"{spacing}{name}: [35m{self.base_enchantment.hits}[0m"
                )
                prefixes.append((type_text_colored, len(type_text)))

            # Type
            name = "Type"
            type_value = self.TYPE_LABEL_MAP[
                self.base_enchantment.enchantment_effect.value
            ]
            spacing = " " * (max_len_pre - len(name))
            type_text = f"{spacing}{name}: {type_value}"
            type_text_colored = f"{spacing}{name}: [35m{type_value}[0m"
            prefixes.append((type_text_colored, len(type_text)))

            if self.base_enchantment.skill_effect is not None:
                # Type
                name = "Effect"
                effect_value = self.EFFECT_TYPE_LABEL_MAP[
                    self.base_enchantment.skill_effect.value
                ]
                spacing = " " * (max_len_pre - len(name))
                type_text = f"{spacing}{name}: {effect_value}"
                type_text_colored = f"{spacing}{name}: [35m{effect_value}[0m"
                prefixes.append((type_text_colored, len(type_text)))

            # Slot
            name = "Slot"
            spacing = " " * (max_len_suf - len(self.base_enchantment.slot.value))
            type_text = f"{name}: {self.base_enchantment.slot.value}{spacing}"
            type_text_colored = (
                f"{name}: [35m{self.base_enchantment.slot.value}[0m{spacing}"
            )
            suffixes.append((type_text_colored, len(type_text)))

            # Cooldown
            if self.base_enchantment.cooldown > 0:
                name = "Cooldown"
                spacing = " " * (
                    max_len_suf - len(f"{self.base_enchantment.cooldown} Turns")
                )
                cooldown_text = (
                    f"{name}: {self.base_enchantment.cooldown} Turns{spacing}"
                )
                cooldown_text_colored = (
                    f"{name}: [35m{self.base_enchantment.cooldown}[0m Turns{spacing}"
                )
                suffixes.append((cooldown_text_colored, len(cooldown_text)))

            # Stacks
            max_stacks = self.base_enchantment.stacks
            if max_stacks is not None and max_stacks > 0:
                name = "Uses"
                spacing = " " * (max_len_pre - len(name))
                stacks_text = f"{spacing}{name}: {max_stacks}"
                stacks_text_colored = f"{spacing}{name}: [35m{max_stacks}[0m"

                if self.base_enchantment.reset_after_encounter:
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

        if amount is not None and amount > 1:
            amount_text = f"amount: {amount}"
            spacing_width = max_width - max(11, len(amount_text))
            spacing = " " * spacing_width
            description += f"\n{spacing}{amount_text}"

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
        embed.set_thumbnail(url=self.base_enchantment.image_url)
        if self.base_enchantment.author is not None:
            embed.set_footer(text=f"by {self.base_enchantment.author}")
        return embed

    def add_to_embed(
        self,
        embed: discord.Embed,
        max_width: int = None,
        description_override: str = None,
    ) -> None:
        data = self.get_embed_field(max_width, description_override)
        embed.add_field(name=data.name, value=data.value, inline=data.inline)

    def get_embed_field(
        self,
        max_width: int = None,
        description_override: str = None,
    ):
        if max_width is None:
            max_width = Config.COMBAT_EMBED_MAX_WIDTH

        name = f"<~ {self.name} ~>"
        suffix = ""

        info_block = "```ansi\n"
        info_block += (
            f"{Droppable.RARITY_NAME_COLOR_MAP[self.rarity]}{name}[0m{suffix}"
        )

        effect = "Enchantment"

        spacing = " " * (max_width - len(name) - len(effect) - len(suffix) - 2)
        info_block += f"{spacing}[{effect}]"
        info_block += "```"

        description = f'"{self.description}"'

        if len(description) < max_width:
            description += " " + "\u00a0" * max_width

        prefixes = []
        suffixes = []

        max_len_pre = 8
        max_len_suf = 9

        info_block += "```ansi\n"

        # Rarity
        name = "Rarity"
        spacing = " " * (max_len_suf - len(self.rarity.value))
        rarity_line = f"{name}: {self.rarity.value}{spacing}"
        rarity_line_colored = f"{name}: {Droppable.RARITY_COLOR_MAP[self.rarity]}{self.rarity.value}[0m{spacing}"
        suffixes.append((rarity_line_colored, len(rarity_line)))

        # Base Value
        if self.scaling > 0:
            name = "Power"
            suffix_sign = ""
            if (
                self.base_enchantment.skill_effect is not None
                and self.base_enchantment.skill_effect == SkillEffect.BUFF
            ):
                suffix_sign = "%"
            spacing = " " * (max_len_pre - len(name))
            base_value_text = f"{spacing}{name}: {self.scaling:.1f}{suffix_sign}"
            base_value_text_colored = (
                f"{spacing}{name}: [35m{self.scaling:.1f}{suffix_sign}[0m"
            )
            prefixes.append((base_value_text_colored, len(base_value_text)))

        # Hits
        if self.base_enchantment.hits > 1:
            name = "Hits"
            spacing = " " * (max_len_pre - len(name))
            type_text = f"{spacing}{name}: {self.base_enchantment.hits}"
            type_text_colored = (
                f"{spacing}{name}: [35m{self.base_enchantment.hits}[0m"
            )
            prefixes.append((type_text_colored, len(type_text)))

        if self.base_enchantment.skill_effect is not None:
            # Type
            name = "Effect"
            effect_value = self.EFFECT_TYPE_LABEL_MAP[
                self.base_enchantment.skill_effect.value
            ]
            spacing = " " * (max_len_pre - len(name))
            type_text = f"{spacing}{name}: {effect_value}"
            type_text_colored = f"{spacing}{name}: [35m{effect_value}[0m"
            prefixes.append((type_text_colored, len(type_text)))

        # Cooldown
        if self.base_enchantment.cooldown > 0:
            name = "Cooldown"
            spacing = " " * (
                max_len_suf - len(f"{self.base_enchantment.cooldown} Turns")
            )
            cooldown_text = f"{name}: {self.base_enchantment.cooldown} Turns{spacing}"
            cooldown_text_colored = (
                f"{name}: [35m{self.base_enchantment.cooldown}[0m Turns{spacing}"
            )
            suffixes.append((cooldown_text_colored, len(cooldown_text)))

        # Stacks
        max_stacks = self.base_enchantment.stacks
        if max_stacks is not None and max_stacks > 0:
            name = "Uses"
            spacing = " " * (max_len_pre - len(name))
            stacks_text = f"{spacing}{name}: {max_stacks}"
            stacks_text_colored = f"{spacing}{name}: [35m{max_stacks}[0m"

            if self.base_enchantment.reset_after_encounter:
                append = " (per Combat)"
            else:
                append = " (Total)"

            stacks_text += append
            stacks_text_colored += append

            prefixes.append((stacks_text_colored, len(stacks_text)))

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

        return FieldData("", info_block, False)


class GearEnchantment:

    def __init__(
        self,
        enchantment: EffectEnchantment,
        last_used: int,
        stacks_used: int,
        min_roll: int,
        max_roll: int,
        penalty: bool = False,
    ):
        self.enchantment = enchantment
        self.last_used = last_used
        self.stacks_used = stacks_used
        self.min_roll = min_roll
        self.max_roll = max_roll
        self.penalty = penalty

    def on_cooldown(self):
        if self.last_used is None or self.enchantment.base_enchantment.cooldown is None:
            return False
        return self.last_used < self.enchantment.base_enchantment.cooldown

    def stacks_left(self):
        if self.enchantment.base_enchantment.stacks is None or self.stacks_used is None:
            return None
        return self.enchantment.base_enchantment.stacks - self.stacks_used

    def get_embed(
        self,
        show_data: bool = True,
        show_full_data: bool = False,
        show_info: bool = False,
        show_locked_state: bool = False,
        amount: int = None,
        max_width: int = None,
    ) -> discord.Embed:
        if max_width is None:
            max_width = Config.COMBAT_EMBED_MAX_WIDTH
        color = self.enchantment.RARITY_COLOR_HEX_MAP[self.enchantment.rarity]

        if self.stacks_left() is not None and self.stacks_left() <= 0:
            color = discord.Color.dark_grey()

        suffix = ""
        if self.enchantment.locked and show_locked_state:
            suffix += " [🔒]"

        name = f"<~ {self.enchantment.base_enchantment.name} ~>"

        info_block = "```ansi\n"
        info_block += f"{Droppable.RARITY_NAME_COLOR_MAP[self.enchantment.rarity]}{name}[0m{suffix}"

        effect = "Enchantment"
        spacing = " " * (max_width - len(name) - len(effect) - len(suffix) - 2)
        info_block += f"{spacing}[{effect}]"
        info_block += "```"

        description = f'"{self.enchantment.base_enchantment.description}"'

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
                spacing = " " * (max_len_suf - len(self.enchantment.rarity.value))
                rarity_line = f"{name}: {self.enchantment.rarity.value}{spacing}"
                rarity_line_colored = f"{name}: {Droppable.RARITY_COLOR_MAP[self.enchantment.rarity]}{self.enchantment.rarity.value}[0m{spacing}"
                suffixes.append((rarity_line_colored, len(rarity_line)))

            # Damage

            if self.enchantment.base_enchantment.value > 0:
                caption = self.enchantment.EFFECT_LABEL_MAP[
                    self.enchantment.base_enchantment.skill_effect
                ]
                spacing = " " * (max_len_pre - len(caption))
                penalty = penalty_colored = ""
                if self.penalty:
                    penalty = " [!]"
                    penalty_colored = f"[30m{penalty}[0m "
                match self.enchantment.base_enchantment.skill_effect:
                    case SkillEffect.BUFF:
                        damage_text = f"{spacing}{caption}: {self.enchantment.base_enchantment.base_value:.1f}%"
                        damage_text_colored = f"{spacing}{caption}: [35m{self.enchantment.base_enchantment.base_value:.1f}%[0m"
                    case _:
                        damage_text = f"{spacing}{caption}: {self.min_roll} - {self.max_roll}{penalty}"
                        damage_text_colored = f"{spacing}{caption}: [35m{self.min_roll}[0m - [35m{self.max_roll}[0m{penalty_colored}"
                prefixes.append((damage_text_colored, len(damage_text)))

            # Hits
            if self.enchantment.base_enchantment.hits > 1:
                name = "Hits"
                spacing = " " * (max_len_pre - len(name))
                type_text = f"{spacing}{name}: {self.enchantment.base_enchantment.hits}"
                type_text_colored = f"{spacing}{name}: [35m{self.enchantment.base_enchantment.hits}[0m"
                prefixes.append((type_text_colored, len(type_text)))

            # Type
            name = "Type"
            type_value = Enchantment.TYPE_LABEL_MAP[
                self.enchantment.base_enchantment.enchantment_effect.value
            ]
            spacing = " " * (max_len_pre - len(name))
            type_text = f"{spacing}{name}: {type_value}"
            type_text_colored = f"{spacing}{name}: [35m{type_value}[0m"
            prefixes.append((type_text_colored, len(type_text)))

            # Effect
            if self.enchantment.base_enchantment.skill_effect is not None:
                # Type
                name = "Effect"
                effect_value = Enchantment.EFFECT_TYPE_LABEL_MAP[
                    self.enchantment.base_enchantment.skill_effect.value
                ]
                spacing = " " * (max_len_pre - len(name))
                type_text = f"{spacing}{name}: {effect_value}"
                type_text_colored = f"{spacing}{name}: [35m{effect_value}[0m"
                prefixes.append((type_text_colored, len(type_text)))

            # Slot
            name = "Slot"
            spacing = " " * (
                max_len_suf - len(self.enchantment.base_enchantment.slot.value)
            )
            type_text = (
                f"{name}: {self.enchantment.base_enchantment.slot.value}{spacing}"
            )
            type_text_colored = f"{name}: [35m{self.enchantment.base_enchantment.slot.value}[0m{spacing}"
            suffixes.append((type_text_colored, len(type_text)))

            # Cooldown
            if self.enchantment.base_enchantment.cooldown > 0:
                name = "Cooldown"
                spacing = " " * (
                    max_len_suf
                    - len(f"{self.enchantment.base_enchantment.cooldown} Turns")
                )
                cooldown_text = f"{name}: {self.enchantment.base_enchantment.cooldown} Turns{spacing}"
                cooldown_text_colored = f"{name}: [35m{self.enchantment.base_enchantment.cooldown}[0m Turns{spacing}"
                suffixes.append((cooldown_text_colored, len(cooldown_text)))

            # Stacks
            max_stacks = self.enchantment.base_enchantment.stacks
            if max_stacks is not None and max_stacks > 0:
                name = "Uses"
                spacing = " " * (max_len_pre - len(name))

                stacks_text = f"{spacing}{name}: {self.stacks_left()}/{max_stacks}"
                stacks_text_colored = f"{spacing}{name}: [35m{self.stacks_left()}[0m/[35m{max_stacks}[0m"

                if self.enchantment.base_enchantment.reset_after_encounter:
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
            if self.enchantment.base_enchantment.cooldown > 0 and self.on_cooldown():
                cooldown_remaining = (
                    self.enchantment.base_enchantment.cooldown - self.last_used
                )
                cooldown_info = f"\navailable in [35m{cooldown_remaining}[0m turn(s)"

            info_block += f"{cooldown_info}```"

        if amount is not None and amount > 1:
            amount_text = f"amount: {amount}"
            spacing_width = max_width - max(11, len(amount_text))
            spacing = " " * spacing_width
            description += f"\n{spacing}{amount_text}"

        info_block += f"```python\n{description}```"

        if show_info:
            info_block += (
                f"```ansi\n[37m{self.enchantment.base_enchantment.information}```"
            )

        embed = discord.Embed(title="", description=info_block, color=color)
        embed.set_thumbnail(url=self.enchantment.base_enchantment.image_url)
        if show_full_data and self.enchantment.base_enchantment.author is not None:
            embed.set_footer(text=f"by {self.enchantment.base_enchantment.author}")
        return embed

    def add_to_embed(
        self,
        embed: discord.Embed,
        max_width: int = None,
        description_override: str = None,
    ) -> None:
        data = self.get_embed_field(max_width, description_override)
        embed.add_field(name=data.name, value=data.value, inline=data.inline)

    def get_embed_field(
        self,
        max_width: int = None,
        description_override: str = None,
    ):
        if max_width is None:
            max_width = Config.COMBAT_EMBED_MAX_WIDTH

        name = f"<~ {self.enchantment.base_enchantment.name} ~>"

        info_block = "```ansi\n"
        info_block += (
            f"{Droppable.RARITY_NAME_COLOR_MAP[self.enchantment.rarity]}{name}[0m"
        )

        effect = "Enchantment"
        spacing = " " * (max_width - len(name) - len(effect) - 2)
        info_block += f"{spacing}[{effect}]"
        info_block += "```"

        description = f'"{self.enchantment.base_enchantment.description}"'

        if len(description) < max_width:
            description += " " + "\u00a0" * max_width

        prefixes = []
        suffixes = []

        max_len_pre = 8
        max_len_suf = 9

        info_block += "```ansi\n"

        # Damage
        if self.enchantment.base_enchantment.value > 0:
            caption = self.enchantment.EFFECT_LABEL_MAP[
                self.enchantment.base_enchantment.skill_effect
            ]
            spacing = " " * (max_len_pre - len(caption))
            penalty = penalty_colored = ""
            if self.penalty:
                penalty = " [!]"
                penalty_colored = f"[30m{penalty}[0m "
            match self.enchantment.base_enchantment.skill_effect:
                case SkillEffect.BUFF:
                    damage_text = f"{spacing}{caption}: {self.enchantment.base_enchantment.value:.1f}%"
                    damage_text_colored = f"{spacing}{caption}: [35m{self.enchantment.base_enchantment.value:.1f}%[0m"
                case _:
                    damage_text = f"{spacing}{caption}: {self.min_roll} - {self.max_roll}{penalty}"
                    damage_text_colored = f"{spacing}{caption}: [35m{self.min_roll}[0m - [35m{self.max_roll}[0m{penalty_colored}"
            prefixes.append((damage_text_colored, len(damage_text)))

        # Hits
        if self.enchantment.base_enchantment.hits > 1:
            name = "Hits"
            spacing = " " * (max_len_pre - len(name))
            type_text = f"{spacing}{name}: {self.enchantment.base_enchantment.hits}"
            type_text_colored = (
                f"{spacing}{name}: [35m{self.enchantment.base_enchantment.hits}[0m"
            )
            prefixes.append((type_text_colored, len(type_text)))

        # Effect
        if self.enchantment.base_enchantment.skill_effect is not None:
            # Type
            name = "Effect"
            effect_value = Enchantment.EFFECT_TYPE_LABEL_MAP[
                self.enchantment.base_enchantment.skill_effect.value
            ]
            spacing = " " * (max_len_pre - len(name))
            type_text = f"{spacing}{name}: {effect_value}"
            type_text_colored = f"{spacing}{name}: [35m{effect_value}[0m"
            prefixes.append((type_text_colored, len(type_text)))

        # Cooldown
        if self.enchantment.base_enchantment.cooldown > 0:
            name = "Cooldown"
            spacing = " " * (
                max_len_suf - len(f"{self.enchantment.base_enchantment.cooldown} Turns")
            )
            cooldown_text = (
                f"{name}: {self.enchantment.base_enchantment.cooldown} Turns{spacing}"
            )
            cooldown_text_colored = f"{name}: [35m{self.enchantment.base_enchantment.cooldown}[0m Turns{spacing}"
            suffixes.append((cooldown_text_colored, len(cooldown_text)))

        # Stacks
        max_stacks = self.enchantment.base_enchantment.stacks
        if max_stacks is not None and max_stacks > 0:
            name = "Uses"
            spacing = " " * (max_len_pre - len(name))

            stacks_text = f"{spacing}{name}: {self.stacks_left()}/{max_stacks}"
            stacks_text_colored = (
                f"{spacing}{name}: [35m{self.stacks_left()}[0m/[35m{max_stacks}[0m"
            )

            if self.enchantment.base_enchantment.reset_after_encounter:
                append = " (per Combat)"
            else:
                append = " (Total)"

            stacks_text += append
            stacks_text_colored += append

            prefixes.append((stacks_text_colored, len(stacks_text)))

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
        if self.enchantment.base_enchantment.cooldown > 0 and self.on_cooldown():
            cooldown_remaining = (
                self.enchantment.base_enchantment.cooldown - self.last_used
            )
            cooldown_info = f"\navailable in [35m{cooldown_remaining}[0m turn(s)"

            info_block += f"{cooldown_info}"

        if description_override is not None:
            description = f'"{description_override}"'

        info_block += "```"
        info_block += f"```python\n{description}```"

        return FieldData("", info_block, False)


class CraftDisplayWrapper(GearEnchantment):

    def __init__(
        self,
        enchantment: Enchantment,
    ):
        super().__init__(
            enchantment=enchantment,
            last_used=0,
            stacks_used=0,
            min_roll=0,
            max_roll=0,
            penalty=False,
        )

    def get_embed(
        self,
        show_data: bool = True,
        show_full_data: bool = False,
        show_info: bool = False,
        show_locked_state: bool = False,
        amount: int = None,
        max_width: int = None,
    ) -> discord.Embed:
        return self.enchantment.get_embed(
            show_data=show_data,
            show_info=show_info,
            show_locked_state=show_locked_state,
            amount=amount,
            max_width=max_width,
        )
