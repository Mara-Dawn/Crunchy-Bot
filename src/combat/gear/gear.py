import discord

from combat.enchantments.enchantment import (
    EffectEnchantment,
    GearEnchantment,
)
from combat.gear.droppable import Droppable, DroppableBase
from combat.gear.types import (
    Base,
    EquipmentSlot,
    GearBaseType,
    GearModifierType,
    Rarity,
)
from combat.skills.types import SkillEffect, SkillType
from forge.forgable import Forgeable
from view.object.embed import (
    AffixBlock,
    DisplayBlock,
    MultiPrefix,
    ObjectDisplay,
    ObjectParameters,
    Prefix,
    Suffix,
)
from view.object.types import ObjectType, ValueColor, ValueType


class GearBase(DroppableBase):

    DEFAULT_IMAGES = {
        EquipmentSlot.WEAPON: "https://i.imgur.com/AJoTZdu.png",
        EquipmentSlot.HEAD: "https://i.imgur.com/AJoTZdu.png",
        EquipmentSlot.BODY: "https://i.imgur.com/AJoTZdu.png",
        EquipmentSlot.LEGS: "https://i.imgur.com/AJoTZdu.png",
        EquipmentSlot.ACCESSORY: "https://i.imgur.com/AJoTZdu.png",
    }

    def __init__(
        self,
        name: str,
        type: GearBaseType,
        description: str,
        information: str,
        slot: EquipmentSlot,
        min_level: int,
        max_level: int,
        modifiers: list[GearModifierType],
        skills: list[SkillType] = None,
        scaling: int = 1,
        weight: int = None,
        droppable: bool = True,
        permanent: bool = False,
        secret: bool = False,
        image_url: str = None,
        uniques: list[GearBaseType] = None,
        author: str = None,
    ):
        super().__init__(
            name=name,
            base_type=Base.GEAR,
            type=type,
            slot=slot,
            min_level=min_level,
            max_level=max_level,
            weight=weight,
            droppable=droppable,
            uniques=uniques,
            author=author,
        )
        self.name = name
        self.type = type
        self.description = description
        self.information = information
        self.modifiers = modifiers
        self.image_url = image_url

        self.skills = skills
        if self.skills is None:
            self.skills = []

        self.scaling = scaling
        self.permanent = permanent
        self.secret = secret

        if self.image_url is None:
            self.image_url = self.DEFAULT_IMAGES[self.slot]

    def get_allowed_modifiers(self):
        match self.slot:
            case EquipmentSlot.HEAD:
                return [
                    GearModifierType.DEFENSE,
                    GearModifierType.CONSTITUTION,
                    GearModifierType.HEALING,
                    GearModifierType.ATTACK,
                    GearModifierType.MAGIC,
                ]
            case EquipmentSlot.BODY:
                return [
                    GearModifierType.DEFENSE,
                    GearModifierType.CONSTITUTION,
                    GearModifierType.HEALING,
                    GearModifierType.CRIT_DAMAGE,
                    GearModifierType.CRIT_RATE,
                    GearModifierType.ATTACK,
                    GearModifierType.MAGIC,
                ]
            case EquipmentSlot.LEGS:
                return [
                    GearModifierType.DEFENSE,
                    GearModifierType.CONSTITUTION,
                    GearModifierType.HEALING,
                    GearModifierType.DEXTERITY,
                    GearModifierType.ATTACK,
                    GearModifierType.MAGIC,
                ]
            case EquipmentSlot.WEAPON:
                return [
                    GearModifierType.HEALING,
                    GearModifierType.CRIT_DAMAGE,
                    GearModifierType.CRIT_RATE,
                    GearModifierType.DEXTERITY,
                    GearModifierType.ATTACK,
                    GearModifierType.MAGIC,
                ]
            case EquipmentSlot.ACCESSORY:
                return [
                    GearModifierType.CONSTITUTION,
                    GearModifierType.HEALING,
                    GearModifierType.CRIT_DAMAGE,
                    GearModifierType.CRIT_RATE,
                    GearModifierType.ATTACK,
                    GearModifierType.MAGIC,
                ]


class Gear(Droppable, Forgeable):

    def __init__(
        self,
        name: str,
        base: GearBase,
        rarity: Rarity,
        level: int,
        modifiers: dict[GearModifierType, float],
        skills: list[SkillType],
        enchantments: list[EffectEnchantment],
        locked: bool = False,
        id: int = None,
    ):
        if name == "" or name is None:
            name = base.name
        self.name = name
        Droppable.__init__(
            self,
            name=name,
            base=base,
            type=base.type,
            description=base.description,
            information=base.information,
            slot=base.slot,
            rarity=rarity,
            level=level,
            base_value=base.scaling,
            image_url=base.image_url,
        )
        self.base = base
        self.rarity = rarity
        self.level = level
        self.modifiers = modifiers

        index_map = {v: i for i, v in enumerate(GearModifierType.prio())}
        self.modifiers = dict(
            sorted(self.modifiers.items(), key=lambda pair: index_map[pair[0]])
        )

        self.skills = skills
        self.enchantments = enchantments
        self.locked = locked
        self.id = id

        Forgeable.__init__(
            self,
            name=self.name,
            id=id,
            object_type=ObjectType.GEAR,
            forge_type=base.type,
            value=base.scaling,
            level=level,
            rarity=rarity,
            image_url=base.image_url,
        )

    def display(
        self,
        equipped: bool = False,
        show_locked_state: bool = False,
        scrap_value: int = None,
        enchantment_data: list[GearEnchantment] = None,
        modifier_boundaries: dict[GearModifierType, tuple[float, float]] = None,
    ) -> ObjectDisplay:
        parameters = ObjectParameters(
            object_type=ObjectType.GEAR,
            name=self.name,
            group=self.base.slot.value,
            description=self.description,
            rarity=self.rarity,
            equipped=equipped,
            locked=(self.locked and show_locked_state),
            information=self.information,
        )

        prefixes: list[Prefix] = []
        suffixes: list[Suffix] = []

        suffixes.append(Suffix("Rarity", self.rarity.value, ValueType.STRING))
        suffixes.append(Suffix("Level", self.level, ValueType.INT))

        if self.base.slot == EquipmentSlot.WEAPON and len(self.base.skills) > 0:

            damage_types = []
            for skill_type in self.base.skills:
                if SkillType.is_magical_weapon_skill(skill_type):
                    effect = SkillEffect.MAGICAL_DAMAGE
                if SkillType.is_physical_weapon_skill(skill_type):
                    effect = SkillEffect.PHYSICAL_DAMAGE
                if effect not in damage_types:
                    damage_types.append(effect)

            name = "Damage Type"
            if len(damage_types) > 1:
                name += "s"

            for idx, damage_type in enumerate(damage_types):
                if idx == 0:
                    prefixes.append(Prefix(name, damage_type.value, ValueType.STRING))
                else:
                    prefixes.append(Prefix(None, damage_type.value, ValueType.STRING))

        flat_damage_modifiers = {}

        for modifier_type, value in self.modifiers.items():
            if modifier_type in [
                GearModifierType.WEAPON_DAMAGE_MIN,
                GearModifierType.WEAPON_DAMAGE_MAX,
            ]:
                flat_damage_modifiers[modifier_type] = value
                continue

            name = modifier_type.value

            if GearModifierType.no_value(modifier_type):
                prefixes.append(Prefix(name, None, ValueType.NONE))
            else:
                display_value = GearModifierType.display_value(modifier_type, value)
                prefixes.append(Prefix(name, display_value, ValueType.STRING))

            if modifier_boundaries is not None and not GearModifierType.no_value(
                modifier_type
            ):
                min_value, max_value = modifier_boundaries[modifier_type]
                min_value = GearModifierType.display_value(modifier_type, min_value)
                max_value = GearModifierType.display_value(modifier_type, max_value)

                prefixes.append(
                    Prefix(
                        None,
                        f"[{min_value}-{max_value}]",
                        ValueType.STRING,
                        value_color=ValueColor.GREY,
                    )
                )

        if len(flat_damage_modifiers) == 2:
            name = "Hit Damage"
            display_value_min = GearModifierType.display_value(
                GearModifierType.WEAPON_DAMAGE_MIN,
                flat_damage_modifiers[GearModifierType.WEAPON_DAMAGE_MIN],
            )
            display_value_max = GearModifierType.display_value(
                GearModifierType.WEAPON_DAMAGE_MAX,
                flat_damage_modifiers[GearModifierType.WEAPON_DAMAGE_MAX],
            )
            prefixes.insert(
                0,
                MultiPrefix(
                    name,
                    values=[display_value_min, display_value_max],
                    value_separator=" - ",
                    value_type=ValueType.INT,
                ),
            )

            if modifier_boundaries is not None:
                min_value_min, max_value_min = modifier_boundaries[
                    GearModifierType.WEAPON_DAMAGE_MIN
                ]
                min_value_min = GearModifierType.display_value(
                    GearModifierType.WEAPON_DAMAGE_MIN, min_value_min
                )
                max_value_min = GearModifierType.display_value(
                    GearModifierType.WEAPON_DAMAGE_MIN, max_value_min
                )

                min_value_max, max_value_max = modifier_boundaries[
                    GearModifierType.WEAPON_DAMAGE_MAX
                ]
                min_value_max = GearModifierType.display_value(
                    GearModifierType.WEAPON_DAMAGE_MAX, min_value_max
                )
                max_value_max = GearModifierType.display_value(
                    GearModifierType.WEAPON_DAMAGE_MAX, max_value_max
                )

                line = f"[{min_value_min}-{max_value_min}] - [{min_value_max}-{max_value_max}]"
                prefixes.insert(
                    1,
                    Prefix(
                        None,
                        line,
                        ValueType.STRING,
                        value_color=ValueColor.GREY,
                    ),
                )
                suffixes.insert(1, Suffix.EMPTY())

        extra_displays: list[ObjectDisplay] = []

        if enchantment_data is None and len(self.enchantments) > 0:
            for enchantment in self.enchantments:
                extra_displays.append(enchantment.display())
        elif enchantment_data is not None:
            for gear_enchantment in enchantment_data:
                extra_displays.append(gear_enchantment.display())

        extra_blocks: list[DisplayBlock] = []

        if scrap_value is not None:
            prefix = Prefix("Stock", 1, ValueType.INT)
            suffix = Suffix("Cost", f"⚙️{scrap_value}", ValueType.STRING)
            extra_blocks.append(AffixBlock([prefix], [suffix], parameters.max_width))

        return ObjectDisplay(
            parameters=parameters,
            prefixes=prefixes,
            suffixes=suffixes,
            extra_displays=extra_displays,
            extra_blocks=extra_blocks,
            thumbnail_url=self.image_url,
            author=self.base.author,
        )

    def get_embed(
        self,
        show_data: bool = True,
        show_info: bool = False,
        equipped: bool = False,
        show_locked_state: bool = False,
        scrap_value: int = None,
        max_width: int = None,
        enchantment_data: list[GearEnchantment] = None,
        modifier_boundaries: dict[GearModifierType, tuple[float, float]] = None,
    ) -> discord.Embed:
        display = self.display(
            equipped=equipped,
            show_locked_state=show_locked_state,
            scrap_value=scrap_value,
            enchantment_data=enchantment_data,
            modifier_boundaries=modifier_boundaries,
        )
        return display.get_embed(show_info)
