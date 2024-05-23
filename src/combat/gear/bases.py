from combat.gear.gear import GearBase
from combat.gear.types import GearBaseType, GearModifierType, GearSlot
from combat.skills.types import SkillType

# Example
# class HeadGear_T0(GearBase):
#     def __init__(self):
#         super().__init__(
#             name="Cool Cap",
#             type=GearBaseType.WAND_T0,
#             description="A stylish hat that might not protect you from harm but looks hella wicked.",
#             information="Tier 0 head piece that can drop as a level 1 to 2 item.",
#             slot=GearSlot.HEAD,
#             min_level=1,
#             max_level=2,
#             skills=[],
#             modifiers=[GearModifierType.ARMOR],
#             scaling=1,
#             cost=0,
#             weight=None,
#             permanent=False,
#             secret=False,
#         )


# Base Items

# Tier 0


class Stick_T0(GearBase):

    def __init__(self):
        super().__init__(
            name="Steady Stick",
            type=GearBaseType.STICK_T0,
            description="The ol' reliable. Your trusty stick would never let you down. Just give em a good whack and theyll surely shut up. ",
            information="Your basic starting weapon. Deals physical Damage.",
            slot=GearSlot.WEAPON,
            min_level=1,
            max_level=3,
            modifiers=[
                GearModifierType.WEAPON_DAMAGE_MIN,
                GearModifierType.WEAPON_DAMAGE_MAX,
            ],
            skills=[SkillType.NORMAL_ATTACK, SkillType.HEAVY_ATTACK],
            scaling=1,
        )


class Wand_T0(GearBase):

    def __init__(self):
        super().__init__(
            name="Wonky Wand",
            type=GearBaseType.WAND_T0,
            description="Looks like someone tried to fix it with duct tape after breaking it. I hope it wont blow up.",
            information="Your basic starting weapon. Deals magical Damage.",
            slot=GearSlot.WEAPON,
            min_level=1,
            max_level=3,
            modifiers=[
                GearModifierType.WEAPON_DAMAGE_MIN,
                GearModifierType.WEAPON_DAMAGE_MAX,
            ],
            skills=[SkillType.MAGIC_ATTACK],
            scaling=1,
        )


class HeadGear_T0(GearBase):

    def __init__(self):
        super().__init__(
            name="Cool Cap",
            type=GearBaseType.HEADGEAR_T0,
            description="A stylish hat that might not protect you from harm but looks hella wicked.",
            information="Tier 0 head piece.",
            slot=GearSlot.HEAD,
            min_level=1,
            max_level=3,
            modifiers=[GearModifierType.ARMOR],
            scaling=1,
        )


class BodyGear_T0(GearBase):

    def __init__(self):
        super().__init__(
            name="Sweet Shirt",
            type=GearBaseType.BODYGEAR_T0,
            description="A really stylish shirt that perfectly fits your body type. Sadly it doesnt do much against enemy attacks.",
            information="Tier 0 body piece.",
            slot=GearSlot.BODY,
            min_level=1,
            max_level=3,
            modifiers=[GearModifierType.ARMOR],
            scaling=1,
        )


class LegGear_T0(GearBase):

    def __init__(self):
        super().__init__(
            name="Pretty Pants",
            type=GearBaseType.LEGGEAR_T0,
            description="Mom picked these for you, they are super comfy and make your butt look good.",
            information="Tier 0 leg piece.",
            slot=GearSlot.LEGS,
            min_level=1,
            max_level=3,
            modifiers=[GearModifierType.ARMOR],
            scaling=1,
        )


class Necklace_T0(GearBase):

    def __init__(self):
        super().__init__(
            name="Nifty Necklace",
            type=GearBaseType.NECKLACE_T0,
            description="This necklace looks like it has seen a lot of use. With a bit of polish it might not look too shabby!",
            information="Tier 0 accessory",
            slot=GearSlot.ACCESSORY,
            min_level=1,
            max_level=3,
            modifiers=[GearModifierType.DEXTERITY],
            scaling=1,
        )


# Tier 1


class Stick_T1(GearBase):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.STICK_T1,
            description="",
            information="",
            slot=GearSlot.WEAPON,
            min_level=2,
            max_level=5,
            modifiers=[
                GearModifierType.WEAPON_DAMAGE_MIN,
                GearModifierType.WEAPON_DAMAGE_MAX,
            ],
            skills=[SkillType.MAGIC_ATTACK],
            scaling=1.1,
        )


class Wand_T1(GearBase):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.WAND_T1,
            description="",
            information="",
            slot=GearSlot.WEAPON,
            min_level=2,
            max_level=5,
            modifiers=[
                GearModifierType.WEAPON_DAMAGE_MIN,
                GearModifierType.WEAPON_DAMAGE_MAX,
            ],
            skills=[SkillType.MAGIC_ATTACK],
            scaling=1,
        )


class HeadGear_T1(GearBase):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.HEADGEAR_T1,
            description="",
            information="Tier 1 head piece.",
            slot=GearSlot.HEAD,
            min_level=2,
            max_level=5,
            modifiers=[GearModifierType.ARMOR],
            scaling=1.1,
        )


class BodyGear_T1(GearBase):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.BODYGEAR_T1,
            description="",
            information="Tier 1 body piece.",
            slot=GearSlot.BODY,
            min_level=2,
            max_level=5,
            modifiers=[GearModifierType.ARMOR],
            scaling=1.1,
        )


class LegGear_T1(GearBase):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.LEGGEAR_T1,
            description="",
            information="Tier 1 leg piece.",
            slot=GearSlot.BODY,
            min_level=2,
            max_level=5,
            modifiers=[GearModifierType.ARMOR],
            scaling=1.1,
        )


class Necklace_T1(GearBase):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.NECKLACE_T1,
            description="",
            information="Tier 1 accessory",
            slot=GearSlot.ACCESSORY,
            min_level=2,
            max_level=5,
            modifiers=[GearModifierType.DEXTERITY],
            scaling=1.1,
        )


# Tier 2


class Stick_T2(GearBase):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.STICK_T2,
            description="",
            information="",
            slot=GearSlot.WEAPON,
            min_level=3,
            max_level=6,
            modifiers=[
                GearModifierType.WEAPON_DAMAGE_MIN,
                GearModifierType.WEAPON_DAMAGE_MAX,
            ],
            skills=[SkillType.MAGIC_ATTACK],
            scaling=1.2,
        )


class Wand_T2(GearBase):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.WAND_T2,
            description="",
            information="",
            slot=GearSlot.WEAPON,
            min_level=3,
            max_level=6,
            modifiers=[
                GearModifierType.WEAPON_DAMAGE_MIN,
                GearModifierType.WEAPON_DAMAGE_MAX,
            ],
            skills=[SkillType.MAGIC_ATTACK],
            scaling=1.2,
        )


class HeadGear_T2(GearBase):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.HEADGEAR_T2,
            description="",
            information="Tier 2 head piece.",
            slot=GearSlot.HEAD,
            min_level=3,
            max_level=6,
            modifiers=[GearModifierType.ARMOR],
            scaling=1.2,
        )


class BodyGear_T2(GearBase):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.BODYGEAR_T2,
            description="",
            information="Tier 2 body piece.",
            slot=GearSlot.BODY,
            min_level=3,
            max_level=6,
            modifiers=[GearModifierType.ARMOR],
            scaling=1.2,
        )


class LegGear_T2(GearBase):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.LEGGEAR_T2,
            description="",
            information="Tier 2 leg piece.",
            slot=GearSlot.BODY,
            min_level=3,
            max_level=6,
            modifiers=[GearModifierType.ARMOR],
            scaling=1.2,
        )


class Necklace_T2(GearBase):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.NECKLACE_T2,
            description="",
            information="Tier 2 accessory",
            slot=GearSlot.ACCESSORY,
            min_level=3,
            max_level=6,
            modifiers=[GearModifierType.DEXTERITY],
            scaling=1.2,
        )


# Tier 3


class Stick_T3(GearBase):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.STICK_T3,
            description="",
            information="",
            slot=GearSlot.WEAPON,
            min_level=5,
            max_level=8,
            modifiers=[
                GearModifierType.WEAPON_DAMAGE_MIN,
                GearModifierType.WEAPON_DAMAGE_MAX,
            ],
            skills=[SkillType.MAGIC_ATTACK],
            scaling=1.3,
        )


class Wand_T3(GearBase):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.WAND_T3,
            description="",
            information="",
            slot=GearSlot.WEAPON,
            min_level=5,
            max_level=8,
            modifiers=[
                GearModifierType.WEAPON_DAMAGE_MIN,
                GearModifierType.WEAPON_DAMAGE_MAX,
            ],
            skills=[SkillType.MAGIC_ATTACK],
            scaling=1.3,
        )


class HeadGear_T3(GearBase):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.HEADGEAR_T3,
            description="",
            information="Tier 3 head piece.",
            slot=GearSlot.HEAD,
            min_level=5,
            max_level=8,
            modifiers=[GearModifierType.ARMOR],
            scaling=1.3,
        )


class BodyGear_T3(GearBase):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.BODYGEAR_T3,
            description="",
            information="Tier 3 body piece.",
            slot=GearSlot.BODY,
            min_level=5,
            max_level=8,
            modifiers=[GearModifierType.ARMOR],
            scaling=1.3,
        )


class LegGear_T3(GearBase):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.LEGGEAR_T3,
            description="",
            information="Tier 3 leg piece.",
            slot=GearSlot.BODY,
            min_level=5,
            max_level=8,
            modifiers=[GearModifierType.ARMOR],
            scaling=1.3,
        )


class Necklace_T3(GearBase):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.NECKLACE_T3,
            description="",
            information="Tier 3 accessory",
            slot=GearSlot.ACCESSORY,
            min_level=5,
            max_level=8,
            modifiers=[GearModifierType.DEXTERITY],
            scaling=1.3,
        )


# Tier 4


class Stick_T4(GearBase):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.STICK_T4,
            description="",
            information="",
            slot=GearSlot.WEAPON,
            min_level=7,
            max_level=10,
            modifiers=[
                GearModifierType.WEAPON_DAMAGE_MIN,
                GearModifierType.WEAPON_DAMAGE_MAX,
            ],
            skills=[SkillType.MAGIC_ATTACK],
            scaling=1.4,
        )


class Wand_T4(GearBase):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.WAND_T4,
            description="",
            information="",
            slot=GearSlot.WEAPON,
            min_level=7,
            max_level=10,
            modifiers=[
                GearModifierType.WEAPON_DAMAGE_MIN,
                GearModifierType.WEAPON_DAMAGE_MAX,
            ],
            skills=[SkillType.MAGIC_ATTACK],
            scaling=1.4,
        )


class HeadGear_T4(GearBase):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.HEADGEAR_T4,
            description="",
            information="Tier 4 head piece.",
            slot=GearSlot.HEAD,
            min_level=7,
            max_level=10,
            modifiers=[GearModifierType.ARMOR],
            scaling=1.4,
        )


class BodyGear_T4(GearBase):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.BODYGEAR_T4,
            description="",
            information="Tier 4 body piece.",
            slot=GearSlot.BODY,
            min_level=7,
            max_level=10,
            modifiers=[GearModifierType.ARMOR],
            scaling=1.4,
        )


class LegGear_T4(GearBase):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.LEGGEAR_T4,
            description="",
            information="Tier 4 leg piece.",
            slot=GearSlot.BODY,
            min_level=7,
            max_level=10,
            modifiers=[GearModifierType.ARMOR],
            scaling=1.4,
        )


class Necklace_T4(GearBase):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.NECKLACE_T4,
            description="",
            information="Tier 4 accessory",
            slot=GearSlot.ACCESSORY,
            min_level=7,
            max_level=10,
            modifiers=[GearModifierType.DEXTERITY],
            scaling=1.4,
        )


# Tier 5


class Stick_T5(GearBase):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.STICK_T5,
            description="",
            information="",
            slot=GearSlot.WEAPON,
            min_level=9,
            max_level=12,
            modifiers=[
                GearModifierType.WEAPON_DAMAGE_MIN,
                GearModifierType.WEAPON_DAMAGE_MAX,
            ],
            skills=[SkillType.MAGIC_ATTACK],
            scaling=1.5,
        )


class Wand_T5(GearBase):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.WAND_T5,
            description="",
            information="",
            slot=GearSlot.WEAPON,
            min_level=9,
            max_level=12,
            modifiers=[
                GearModifierType.WEAPON_DAMAGE_MIN,
                GearModifierType.WEAPON_DAMAGE_MAX,
            ],
            skills=[SkillType.MAGIC_ATTACK],
            scaling=1.5,
        )


class HeadGear_T5(GearBase):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.HEADGEAR_T5,
            description="",
            information="Tier 5 head piece.",
            slot=GearSlot.HEAD,
            min_level=9,
            max_level=12,
            modifiers=[GearModifierType.ARMOR],
            scaling=1.5,
        )


class BodyGear_T5(GearBase):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.BODYGEAR_T5,
            description="",
            information="Tier 5 body piece.",
            slot=GearSlot.BODY,
            min_level=9,
            max_level=12,
            modifiers=[GearModifierType.ARMOR],
            scaling=1.5,
        )


class LegGear_T5(GearBase):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.LEGGEAR_T5,
            description="",
            information="Tier 5 leg piece.",
            slot=GearSlot.BODY,
            min_level=9,
            max_level=12,
            modifiers=[GearModifierType.ARMOR],
            scaling=1.5,
        )


class Necklace_T5(GearBase):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.NECKLACE_T5,
            description="",
            information="Tier 5 accessory",
            slot=GearSlot.ACCESSORY,
            min_level=9,
            max_level=12,
            modifiers=[GearModifierType.DEXTERITY],
            scaling=1.5,
        )
