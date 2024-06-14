from combat.gear.gear import GearBase
from combat.gear.types import EquipmentSlot, GearBaseType, GearModifierType
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


class Empty(GearBase):

    def __init__(self):
        super().__init__(
            name="Empty",
            type=GearBaseType.EMPTY,
            description="This equipment slot is empty.",
            information="Defeat enemies to obtain items you can equip in this slot.",
            slot=EquipmentSlot.ACCESSORY,
            min_level=99,
            max_level=99,
            modifiers=[],
            skills=[],
            scaling=1,
        )


# default


class Default(GearBase):

    def __init__(
        self,
        name: str,
        type: GearBaseType,
        description: str,
        information: str,
        slot: EquipmentSlot,
        modifiers: list[GearModifierType] = None,
        skills: list[SkillType] = None,
        image_url: str = None,
    ):
        super().__init__(
            name=name,
            type=type,
            description=description,
            information=information,
            slot=slot,
            min_level=999,
            max_level=999,
            modifiers=modifiers,
            skills=skills,
            scaling=1,
            image_url=image_url,
        )


class DefaultPhys(Default):

    def __init__(self):
        super().__init__(
            name="Your Bare Fists",
            type=GearBaseType.DEFAULT_PHYS,
            description="No weapon? No problem! Just punch them in the face.",
            information="Default physical weapon. Cannot be scrapped.",
            slot=EquipmentSlot.WEAPON,
            modifiers=[
                GearModifierType.WEAPON_DAMAGE_MIN,
                GearModifierType.WEAPON_DAMAGE_MAX,
            ],
            skills=[SkillType.NORMAL_ATTACK, SkillType.HEAVY_ATTACK],
            image_url="https://i.imgur.com/QclR1yI.png",
        )


class DefaultMagical(Default):

    def __init__(self):
        super().__init__(
            name="Pure Imagination",
            type=GearBaseType.DEFAULT_MAGICAL,
            description="If you believe hard enough, you might just be able to cast something.",
            information="Default magical weapon. Cannot be scrapped.",
            slot=EquipmentSlot.WEAPON,
            modifiers=[
                GearModifierType.WEAPON_DAMAGE_MIN,
                GearModifierType.WEAPON_DAMAGE_MAX,
            ],
            skills=[SkillType.MAGIC_ATTACK],
            image_url="https://i.imgur.com/YDoeGbR.png",
        )


class DefaultHead(Default):

    def __init__(self):
        super().__init__(
            name="Bald",
            type=GearBaseType.DEFAULT_HEAD,
            description="You are bald.",
            information="Default headgear. Cannot be scrapped.",
            slot=EquipmentSlot.HEAD,
            modifiers=[GearModifierType.ARMOR],
            image_url="https://i.imgur.com/7Emekkj.png",
        )


class DefaultBody(Default):

    def __init__(self):
        super().__init__(
            name="Old Hoodle",
            type=GearBaseType.DEFAULT_BODY,
            description=(
                "You pulled this out of a random trash can. It makes you look "
                "homeless but at least it keeps you warm."
            ),
            information="Default body armor. Cannot be scrapped.",
            slot=EquipmentSlot.BODY,
            modifiers=[GearModifierType.ARMOR],
            image_url="https://i.imgur.com/hG2ADaB.png",
        )


class DefaultLegs(Default):

    def __init__(self):
        super().__init__(
            name="Yellow Undies",
            type=GearBaseType.DEFAULT_LEGS,
            description="They were white when you bought them.",
            information="Default leg armor. Cannot be scrapped.",
            slot=EquipmentSlot.LEGS,
            modifiers=[GearModifierType.ARMOR],
            image_url="https://i.imgur.com/SIEPjbA.png",
        )


# Tier 0


class Tier0(GearBase):

    def __init__(
        self,
        name: str,
        type: GearBaseType,
        description: str,
        information: str,
        slot: EquipmentSlot,
        modifiers: list[GearModifierType] = None,
        skills: list[SkillType] = None,
        image_url: str = None,
    ):
        super().__init__(
            name=name,
            type=type,
            description=description,
            information=information,
            slot=slot,
            min_level=1,
            max_level=4,
            modifiers=modifiers,
            skills=skills,
            scaling=1,
            image_url=image_url,
        )


class Stick_T0(Tier0):

    def __init__(self):
        super().__init__(
            name="Steady Stick",
            type=GearBaseType.STICK_T0,
            description="The ol' reliable. Your trusty stick would never let you down. Just give em a good whack and theyll surely shut up. ",
            information="Your basic starting weapon. Deals physical Damage.",
            slot=EquipmentSlot.WEAPON,
            modifiers=[
                GearModifierType.WEAPON_DAMAGE_MIN,
                GearModifierType.WEAPON_DAMAGE_MAX,
            ],
            skills=[SkillType.NORMAL_ATTACK, SkillType.HEAVY_ATTACK],
            image_url="https://i.imgur.com/25Lk0kb.png",
        )


class Wand_T0(Tier0):

    def __init__(self):
        super().__init__(
            name="Wonky Wand",
            type=GearBaseType.WAND_T0,
            description="Looks like someone tried to fix it with duct tape after breaking it. I hope it wont blow up.",
            information="Your basic starting weapon. Deals magical Damage.",
            slot=EquipmentSlot.WEAPON,
            modifiers=[
                GearModifierType.WEAPON_DAMAGE_MIN,
                GearModifierType.WEAPON_DAMAGE_MAX,
            ],
            skills=[SkillType.MAGIC_ATTACK],
            image_url="https://i.imgur.com/Y6em0vE.png",
        )


class HeadGear_T0(Tier0):

    def __init__(self):
        super().__init__(
            name="Cool Cap",
            type=GearBaseType.HEADGEAR_T0,
            description="A stylish hat that might not protect you from harm but looks hella wicked.",
            information="Tier 0 head piece.",
            slot=EquipmentSlot.HEAD,
            modifiers=[GearModifierType.ARMOR],
            image_url="https://i.imgur.com/a55rCkb.png",
        )


class BodyGear_T0(Tier0):

    def __init__(self):
        super().__init__(
            name="Sweet Shirt",
            type=GearBaseType.BODYGEAR_T0,
            description="A really stylish shirt that perfectly fits your body type. Sadly it doesnt do much against enemy attacks.",
            information="Tier 0 body piece.",
            slot=EquipmentSlot.BODY,
            modifiers=[GearModifierType.ARMOR],
            image_url="https://i.imgur.com/T5fxzq0.png",
        )


class LegGear_T0(Tier0):

    def __init__(self):
        super().__init__(
            name="Pretty Pants",
            type=GearBaseType.LEGGEAR_T0,
            description="Mom picked these for you, they are super comfy and make your butt look good.",
            information="Tier 0 leg piece.",
            slot=EquipmentSlot.LEGS,
            modifiers=[GearModifierType.ARMOR],
            image_url="https://i.imgur.com/AAH2XAr.png",
        )


class Necklace_T0(Tier0):

    def __init__(self):
        super().__init__(
            name="Nifty Necklace",
            type=GearBaseType.NECKLACE_T0,
            description="This necklace looks like it has seen a lot of use. With a bit of polish it might not look too shabby!",
            information="Tier 0 accessory",
            slot=EquipmentSlot.ACCESSORY,
            modifiers=[GearModifierType.DEXTERITY],
            image_url="https://i.imgur.com/BESjNWX.png",
        )


class Ring_T0(Tier0):

    def __init__(self):
        super().__init__(
            name="Rad Ring",
            type=GearBaseType.RING_T0,
            description="It' so freaking cute, you don't even care this was a kids toy extra from a cereal box.",
            information="Tier 0 accessory",
            slot=EquipmentSlot.ACCESSORY,
            modifiers=[GearModifierType.DEXTERITY],
            image_url="https://i.imgur.com/ukiMU3R.png",
        )


# Tier 1


class Tier1(GearBase):

    def __init__(
        self,
        name: str,
        type: GearBaseType,
        description: str,
        information: str,
        slot: EquipmentSlot,
        modifiers: list[GearModifierType] = None,
        skills: list[SkillType] = None,
        image_url: str = None,
    ):
        super().__init__(
            name=name,
            type=type,
            description=description,
            information=information,
            slot=slot,
            min_level=2,
            max_level=5,
            modifiers=modifiers,
            skills=skills,
            scaling=1.5,
            image_url=image_url,
        )


class Stick_T1(Tier1):

    def __init__(self):
        super().__init__(
            name="The Good Stick",
            type=GearBaseType.STICK_T1,
            description=(
                "You found a really nice and big stick to replace your steady stick with. "
                "Its bigger, looks more sword-like and made your brain go brr must pick up stick."
            ),
            information="Tier 1 physical weapon.",
            slot=EquipmentSlot.WEAPON,
            modifiers=[
                GearModifierType.WEAPON_DAMAGE_MIN,
                GearModifierType.WEAPON_DAMAGE_MAX,
            ],
            skills=[SkillType.MAGIC_ATTACK],
        )


class Wand_T1(Tier1):

    def __init__(self):
        super().__init__(
            name="Glowy Rock",
            type=GearBaseType.WAND_T1,
            description=(
                "You found a really pretty rock at the bed of a river, "
                "you don't know whether or not its actually meant for "
                "magic but you started using it as a catalyst for magic "
                "spells and it seems to be working better than your wonky wand."
            ),
            information="Tier 1 magical weapon.",
            slot=EquipmentSlot.WEAPON,
            modifiers=[
                GearModifierType.WEAPON_DAMAGE_MIN,
                GearModifierType.WEAPON_DAMAGE_MAX,
            ],
            skills=[SkillType.MAGIC_ATTACK],
        )


class HeadGear_T1(Tier1):

    def __init__(self):
        super().__init__(
            name="Coconut Shell",
            type=GearBaseType.HEADGEAR_T1,
            description=(
                "During your travels you found and started eating some coconuts, "
                "but after constantly struggling to break them open it finally "
                "clicked you could use one as a helmet. Lets hope you cleaned it out properly."
            ),
            information="Tier 1 head piece.",
            slot=EquipmentSlot.HEAD,
            modifiers=[GearModifierType.ARMOR],
        )


class BodyGear_T1(Tier1):

    def __init__(self):
        super().__init__(
            name="Thick Leather Jacket",
            type=GearBaseType.BODYGEAR_T1,
            description=(
                "You've always thought biker gangs were really cool and awesome "
                "so one birthday your mom surprised you with a really thick leather jacket. "
                "It's surprisingly effective as extra protection against attacks."
            ),
            information="Tier 1 body piece.",
            slot=EquipmentSlot.BODY,
            modifiers=[GearModifierType.ARMOR],
        )


class LegGear_T1(Tier1):

    def __init__(self):
        super().__init__(
            name="Stylish Jeans",
            type=GearBaseType.LEGGEAR_T1,
            description=(
                "You have a  REALLY sturdy pair of jeans that just seem impossible to "
                "break and give you some nice protection against in fights."
            ),
            information="Tier 1 leg piece.",
            slot=EquipmentSlot.BODY,
            modifiers=[GearModifierType.ARMOR],
        )


class Necklace_T1(Tier1):

    def __init__(self):
        super().__init__(
            name="Fancy Cross",
            type=GearBaseType.NECKLACE_T1,
            description=(
                "You don't know where its from or why it looks so fancy, "
                "but you found a cross that just looks super fancy and you "
                "keep it with you because it  just seems cool."
            ),
            information="Tier 1 accessory",
            slot=EquipmentSlot.ACCESSORY,
            modifiers=[GearModifierType.DEXTERITY],
        )


class Necklace_T1_2(Tier1):

    def __init__(self):
        super().__init__(
            name="Fake Diamond Ring",
            type=GearBaseType.NECKLACE_T1_2,
            description=(
                "You know its not a real diamond, but wearing something so stylish "
                "that looks like it should be extremely expensive just gives you "
                "a huge boost of confidence in combat."
            ),
            information="Tier 1 accessory",
            slot=EquipmentSlot.ACCESSORY,
            modifiers=[GearModifierType.DEXTERITY],
        )


# Tier 2


class Tier2(GearBase):

    def __init__(
        self,
        name: str,
        type: GearBaseType,
        description: str,
        information: str,
        slot: EquipmentSlot,
        modifiers: list[GearModifierType] = None,
        skills: list[SkillType] = None,
        image_url: str = None,
    ):
        super().__init__(
            name=name,
            type=type,
            description=description,
            information=information,
            slot=slot,
            min_level=3,
            max_level=6,
            modifiers=modifiers,
            skills=skills,
            scaling=2,
            image_url=image_url,
        )


class Stick_T2(Tier2):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.STICK_T2,
            description="",
            information="",
            slot=EquipmentSlot.WEAPON,
            modifiers=[
                GearModifierType.WEAPON_DAMAGE_MIN,
                GearModifierType.WEAPON_DAMAGE_MAX,
            ],
            skills=[SkillType.MAGIC_ATTACK],
        )


class Wand_T2(Tier2):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.WAND_T2,
            description="",
            information="",
            slot=EquipmentSlot.WEAPON,
            modifiers=[
                GearModifierType.WEAPON_DAMAGE_MIN,
                GearModifierType.WEAPON_DAMAGE_MAX,
            ],
            skills=[SkillType.MAGIC_ATTACK],
        )


class HeadGear_T2(Tier2):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.HEADGEAR_T2,
            description="",
            information="Tier 2 head piece.",
            slot=EquipmentSlot.HEAD,
            modifiers=[GearModifierType.ARMOR],
        )


class BodyGear_T2(Tier2):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.BODYGEAR_T2,
            description="",
            information="Tier 2 body piece.",
            slot=EquipmentSlot.BODY,
            modifiers=[GearModifierType.ARMOR],
        )


class LegGear_T2(Tier2):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.LEGGEAR_T2,
            description="",
            information="Tier 2 leg piece.",
            slot=EquipmentSlot.BODY,
            modifiers=[GearModifierType.ARMOR],
        )


class Necklace_T2(Tier2):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.NECKLACE_T2,
            description="",
            information="Tier 2 accessory",
            slot=EquipmentSlot.ACCESSORY,
            modifiers=[GearModifierType.DEXTERITY],
        )


# Tier 3


class Tier3(GearBase):

    def __init__(
        self,
        name: str,
        type: GearBaseType,
        description: str,
        information: str,
        slot: EquipmentSlot,
        modifiers: list[GearModifierType] = None,
        skills: list[SkillType] = None,
        image_url: str = None,
    ):
        super().__init__(
            name=name,
            type=type,
            description=description,
            information=information,
            slot=slot,
            min_level=4,
            max_level=10,
            modifiers=modifiers,
            skills=skills,
            scaling=2.5,
            image_url=image_url,
        )


class Stick_T3(Tier3):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.STICK_T3,
            description="",
            information="",
            slot=EquipmentSlot.WEAPON,
            modifiers=[
                GearModifierType.WEAPON_DAMAGE_MIN,
                GearModifierType.WEAPON_DAMAGE_MAX,
            ],
            skills=[SkillType.MAGIC_ATTACK],
        )


class Wand_T3(Tier3):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.WAND_T3,
            description="",
            information="",
            slot=EquipmentSlot.WEAPON,
            modifiers=[
                GearModifierType.WEAPON_DAMAGE_MIN,
                GearModifierType.WEAPON_DAMAGE_MAX,
            ],
            skills=[SkillType.MAGIC_ATTACK],
        )


class HeadGear_T3(Tier3):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.HEADGEAR_T3,
            description="",
            information="Tier 3 head piece.",
            slot=EquipmentSlot.HEAD,
            modifiers=[GearModifierType.ARMOR],
        )


class BodyGear_T3(Tier3):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.BODYGEAR_T3,
            description="",
            information="Tier 3 body piece.",
            slot=EquipmentSlot.BODY,
            modifiers=[GearModifierType.ARMOR],
        )


class LegGear_T3(Tier3):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.LEGGEAR_T3,
            description="",
            information="Tier 3 leg piece.",
            slot=EquipmentSlot.BODY,
            modifiers=[GearModifierType.ARMOR],
        )


class Necklace_T3(Tier3):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.NECKLACE_T3,
            description="",
            information="Tier 3 accessory",
            slot=EquipmentSlot.ACCESSORY,
            modifiers=[GearModifierType.DEXTERITY],
        )


# Tier 4


class Tier4(GearBase):

    def __init__(
        self,
        name: str,
        type: GearBaseType,
        description: str,
        information: str,
        slot: EquipmentSlot,
        modifiers: list[GearModifierType] = None,
        skills: list[SkillType] = None,
        image_url: str = None,
    ):
        super().__init__(
            name=name,
            type=type,
            description=description,
            information=information,
            slot=slot,
            min_level=6,
            max_level=12,
            modifiers=modifiers,
            skills=skills,
            scaling=3,
            image_url=image_url,
        )


class Stick_T4(Tier4):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.STICK_T4,
            description="",
            information="",
            slot=EquipmentSlot.WEAPON,
            modifiers=[
                GearModifierType.WEAPON_DAMAGE_MIN,
                GearModifierType.WEAPON_DAMAGE_MAX,
            ],
            skills=[SkillType.MAGIC_ATTACK],
        )


class Wand_T4(Tier4):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.WAND_T4,
            description="",
            information="",
            slot=EquipmentSlot.WEAPON,
            modifiers=[
                GearModifierType.WEAPON_DAMAGE_MIN,
                GearModifierType.WEAPON_DAMAGE_MAX,
            ],
            skills=[SkillType.MAGIC_ATTACK],
        )


class HeadGear_T4(Tier4):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.HEADGEAR_T4,
            description="",
            information="Tier 4 head piece.",
            slot=EquipmentSlot.HEAD,
            modifiers=[GearModifierType.ARMOR],
        )


class BodyGear_T4(Tier4):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.BODYGEAR_T4,
            description="",
            information="Tier 4 body piece.",
            slot=EquipmentSlot.BODY,
            modifiers=[GearModifierType.ARMOR],
        )


class LegGear_T4(Tier4):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.LEGGEAR_T4,
            description="",
            information="Tier 4 leg piece.",
            slot=EquipmentSlot.BODY,
            modifiers=[GearModifierType.ARMOR],
        )


class Necklace_T4(Tier4):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.NECKLACE_T4,
            description="",
            information="Tier 4 accessory",
            slot=EquipmentSlot.ACCESSORY,
            modifiers=[GearModifierType.DEXTERITY],
        )


# Tier 5


class Tier5(GearBase):

    def __init__(
        self,
        name: str,
        type: GearBaseType,
        description: str,
        information: str,
        slot: EquipmentSlot,
        modifiers: list[GearModifierType] = None,
        skills: list[SkillType] = None,
        image_url: str = None,
    ):
        super().__init__(
            name=name,
            type=type,
            description=description,
            information=information,
            slot=slot,
            min_level=8,
            max_level=12,
            modifiers=modifiers,
            skills=skills,
            scaling=3.5,
            image_url=image_url,
        )


class Stick_T5(Tier5):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.STICK_T5,
            description="",
            information="",
            slot=EquipmentSlot.WEAPON,
            modifiers=[
                GearModifierType.WEAPON_DAMAGE_MIN,
                GearModifierType.WEAPON_DAMAGE_MAX,
            ],
            skills=[SkillType.MAGIC_ATTACK],
        )


class Wand_T5(Tier5):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.WAND_T5,
            description="",
            information="",
            slot=EquipmentSlot.WEAPON,
            modifiers=[
                GearModifierType.WEAPON_DAMAGE_MIN,
                GearModifierType.WEAPON_DAMAGE_MAX,
            ],
            skills=[SkillType.MAGIC_ATTACK],
        )


class HeadGear_T5(Tier5):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.HEADGEAR_T5,
            description="",
            information="Tier 5 head piece.",
            slot=EquipmentSlot.HEAD,
            modifiers=[GearModifierType.ARMOR],
        )


class BodyGear_T5(Tier5):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.BODYGEAR_T5,
            description="",
            information="Tier 5 body piece.",
            slot=EquipmentSlot.BODY,
            modifiers=[GearModifierType.ARMOR],
        )


class LegGear_T5(Tier5):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.LEGGEAR_T5,
            description="",
            information="Tier 5 leg piece.",
            slot=EquipmentSlot.BODY,
            modifiers=[GearModifierType.ARMOR],
        )


class Necklace_T5(Tier5):

    def __init__(self):
        super().__init__(
            name="",
            type=GearBaseType.NECKLACE_T5,
            description="",
            information="Tier 5 accessory",
            slot=EquipmentSlot.ACCESSORY,
            modifiers=[GearModifierType.DEXTERITY],
        )
