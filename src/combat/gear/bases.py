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
#             base_skills=[],
#             base_modifiers=[GearModifierType.ARMOR],
#             cost=0,
#             weight=None,
#             permanent=False,
#             secret=False,
#         )


# Base Items


## Weapon Bases


class Stick_T0(GearBase):

    def __init__(self):
        super().__init__(
            name="Steady Stick",
            type=GearBaseType.STICK_T0,
            description="The ol' reliable. Your trusty stick would never let you down. Just give em a good whack and theyll surely shut up. ",
            information="Your basic starting weapon. Deals physical Damage.",
            slot=GearSlot.HEAD,
            min_level=1,
            max_level=2,
            base_modifiers=[
                GearModifierType.WEAPON_DAMAGE_MIN,
                GearModifierType.WEAPON_DAMAGE_MAX,
            ],
            base_skills=[SkillType.NORMAL_ATTACK, SkillType.HEAVY_ATTACK],
        )


class Wand_T0(GearBase):

    def __init__(self):
        super().__init__(
            name="Wonky Wand",
            type=GearBaseType.WAND_T0,
            description="Looks like someone tried to fix it with duct tape after breaking it. I hope it wont blow up.",
            information="Your basic starting weapon. Deals magical Damage.",
            slot=GearSlot.HEAD,
            min_level=1,
            max_level=2,
            base_modifiers=[
                GearModifierType.WEAPON_DAMAGE_MIN,
                GearModifierType.WEAPON_DAMAGE_MAX,
            ],
            base_skills=[SkillType.MAGIC_ATTACK],
        )


## Headgear Bases


class HeadGear_T0(GearBase):

    def __init__(self):
        super().__init__(
            name="Cool Cap",
            type=GearBaseType.HEADGEAR_T0,
            description="A stylish hat that might not protect you from harm but looks hella wicked.",
            information="Tier 0 head piece.",
            slot=GearSlot.HEAD,
            min_level=1,
            max_level=2,
            base_modifiers=[GearModifierType.ARMOR],
        )


## Body Bases


class BodyGear_T0(GearBase):

    def __init__(self):
        super().__init__(
            name="Sweet Shirt",
            type=GearBaseType.BODYGEAR_T0,
            description="A really stylish shirt that perfectly fits your body type. Sadly it doesnt do much against enemy attacks.",
            information="Tier 0 body piece.",
            slot=GearSlot.BODY,
            min_level=1,
            max_level=2,
            base_modifiers=[GearModifierType.ARMOR],
        )


## Leg Bases


class LegGear_T0(GearBase):

    def __init__(self):
        super().__init__(
            name="Pretty Pants",
            type=GearBaseType.LEGGEAR_T0,
            description="Mom picked these for you, they are super comfy and make your butt look good.",
            information="Tier 0 leg piece.",
            slot=GearSlot.LEGS,
            min_level=1,
            max_level=2,
            base_modifiers=[GearModifierType.ARMOR],
        )
