from combat.gear.gear import GearBase
from combat.gear.types import EquipmentSlot, GearBaseType, GearModifierType
from combat.skills.types import SkillType

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
        uniques: list[GearBaseType] = None,
        image_url: str = None,
    ):
        super().__init__(
            name=name,
            type=type,
            description=description,
            information=information,
            slot=slot,
            min_level=1,
            max_level=3,
            modifiers=modifiers,
            skills=skills,
            uniques=uniques,
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
            uniques=[GearBaseType.SHOOTER_WIG],
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
            uniques=[GearBaseType.HOT_PANTS],
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
            uniques=[GearBaseType.DEEZ_NUTS],
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
        uniques: list[GearBaseType] = None,
        image_url: str = None,
    ):
        super().__init__(
            name=name,
            type=type,
            description=description,
            information=information,
            slot=slot,
            min_level=2,
            max_level=4,
            modifiers=modifiers,
            skills=skills,
            uniques=uniques,
            scaling=1.1,
            image_url=image_url,
            author="Mia",
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
            skills=[SkillType.NORMAL_ATTACK, SkillType.HEAVY_ATTACK],
            image_url="https://i.imgur.com/nUnH9G0.png",
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
            image_url="https://i.imgur.com/rAGti7v.png",
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
            uniques=[GearBaseType.SHOOTER_WIG],
            modifiers=[GearModifierType.ARMOR],
            image_url="https://i.imgur.com/LGEy5Km.png",
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
            uniques=[GearBaseType.FAST_FOOD_CAP],
            modifiers=[GearModifierType.ARMOR],
            image_url="https://i.imgur.com/oAWzovW.png",
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
            slot=EquipmentSlot.LEGS,
            modifiers=[GearModifierType.ARMOR],
            uniques=[GearBaseType.HOT_PANTS],
            image_url="https://i.imgur.com/F10kbxJ.png",
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
            uniques=[GearBaseType.DEEZ_NUTS],
            image_url="https://i.imgur.com/XyoEXnO.png",
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
            uniques=[GearBaseType.RABBIT_FOOT],
            slot=EquipmentSlot.ACCESSORY,
            modifiers=[GearModifierType.DEXTERITY],
            image_url="https://i.imgur.com/HfhMNNW.png",
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
        uniques: list[GearBaseType] = None,
        image_url: str = None,
        author=None,
    ):
        if author is None:
            author = "Klee"
        super().__init__(
            name=name,
            type=type,
            description=description,
            information=information,
            slot=slot,
            min_level=3,
            max_level=5,
            modifiers=modifiers,
            skills=skills,
            uniques=uniques,
            scaling=1.2,
            image_url=image_url,
            author=author,
        )


class Stick_T2(Tier2):

    def __init__(self):
        super().__init__(
            name="Trusty Old Pipe",
            type=GearBaseType.STICK_T2,
            description="By the looks of it, it was straight before it got used.",
            information="",
            slot=EquipmentSlot.WEAPON,
            modifiers=[
                GearModifierType.WEAPON_DAMAGE_MIN,
                GearModifierType.WEAPON_DAMAGE_MAX,
            ],
            skills=[SkillType.NORMAL_ATTACK, SkillType.HEAVY_ATTACK],
            uniques=[GearBaseType.TAPE_MEASURE],
            image_url="https://i.imgur.com/2YUEVzU.jpg",
        )


class Wand_T2(Tier2):

    def __init__(self):
        super().__init__(
            name="Sharp af Chacram",
            type=GearBaseType.WAND_T2,
            description="It seems to resonate with you. Cuts what ever you wanna cut on its own.",
            information="",
            slot=EquipmentSlot.WEAPON,
            modifiers=[
                GearModifierType.WEAPON_DAMAGE_MIN,
                GearModifierType.WEAPON_DAMAGE_MAX,
            ],
            uniques=[GearBaseType.FROZEN_WAND],
            skills=[SkillType.MAGIC_ATTACK],
            image_url="https://i.imgur.com/skJlaSy.jpg",
        )


class HeadGear_T2(Tier2):

    def __init__(self):
        super().__init__(
            name="Evolution of the Fedora.",
            type=GearBaseType.HEADGEAR_T2,
            description="Not sure if Nice Guy would approve.",
            information="Tier 2 head piece.",
            slot=EquipmentSlot.HEAD,
            modifiers=[GearModifierType.ARMOR],
            image_url="https://i.imgur.com/AjKaSDI.jpg",
        )


class HeadGear_T2_2(Tier2):

    def __init__(self):
        super().__init__(
            name="President Dump",
            type=GearBaseType.HEADGEAR_T2_2,
            description="Does a 'Sssshhlorp' sound when putting it on.",
            information="Tier 2 head piece.",
            slot=EquipmentSlot.HEAD,
            modifiers=[GearModifierType.ARMOR],
            image_url="https://i.imgur.com/7pCIdFM.png",
            author="Lusa",
        )


class BodyGear_T2(Tier2):

    def __init__(self):
        super().__init__(
            name="Chonky Tux",
            type=GearBaseType.BODYGEAR_T2,
            description="Probably worn by Eli",
            information="Tier 2 body piece.",
            slot=EquipmentSlot.BODY,
            modifiers=[GearModifierType.ARMOR],
            image_url="https://i.imgur.com/Gz4EdMg.jpg",
        )


class LegGear_T2(Tier2):

    def __init__(self):
        super().__init__(
            name="Small Pants",
            type=GearBaseType.LEGGEAR_T2,
            description="Probably won't even match the tuxedo, but the stripes make the pants go faster",
            information="Tier 2 leg piece.",
            slot=EquipmentSlot.LEGS,
            modifiers=[GearModifierType.ARMOR],
            image_url="https://i.imgur.com/DHTmPOz.jpg",
        )


class Necklace_T2_1(Tier2):

    def __init__(self):
        super().__init__(
            name="Best Gear Ring",
            type=GearBaseType.NECKLACE_T2_1,
            description="The gear looks glued onto it",
            information="Tier 2 accessory",
            slot=EquipmentSlot.ACCESSORY,
            modifiers=[GearModifierType.DEXTERITY],
            image_url="https://i.imgur.com/f6vB7tO.jpg",
        )


class Necklace_T2_2(Tier2):

    def __init__(self):
        super().__init__(
            name="Broken Pocket watch",
            type=GearBaseType.NECKLACE_T2_2,
            description="Doesn't work anymore, but the gril is cute",
            information="Tier 2 accessory",
            slot=EquipmentSlot.ACCESSORY,
            modifiers=[GearModifierType.DEXTERITY],
            image_url="https://i.imgur.com/wRUMfXz.jpg",
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
        uniques: list[GearBaseType] = None,
        image_url: str = None,
    ):
        super().__init__(
            name=name,
            type=type,
            description=description,
            information=information,
            slot=slot,
            min_level=4,
            max_level=6,
            modifiers=modifiers,
            uniques=uniques,
            skills=skills,
            scaling=1.3,
            image_url=image_url,
            author="Franny",
        )


class Stick_T3(Tier3):

    def __init__(self):
        super().__init__(
            name="Water Bucket",
            type=GearBaseType.STICK_T3,
            description="is that a horn or teeth? is that blood or tomato sauce? we dont know, but surely this is a legendary stick dealing massive physical damage.",
            information="Tier 3 physical weapon.",
            slot=EquipmentSlot.WEAPON,
            modifiers=[
                GearModifierType.WEAPON_DAMAGE_MIN,
                GearModifierType.WEAPON_DAMAGE_MAX,
            ],
            skills=[SkillType.NORMAL_ATTACK, SkillType.HEAVY_ATTACK],
            image_url="https://i.imgur.com/IQnu2I6.png",
        )


class Icicle(Tier3):

    def __init__(self):
        super().__init__(
            name="Icicle",
            type=GearBaseType.ICICLE,
            description=(
                "It might look like a shiny blue carrot, but this icicle is "
                "so much more than a nutritious treat (please don't eat it, "
                "it is not nutricious at all). Don't forget to wear gloves when "
                "handling this deadly, ice cold shiv!"
            ),
            information="",
            slot=EquipmentSlot.WEAPON,
            modifiers=[
                GearModifierType.WEAPON_DAMAGE_MIN,
                GearModifierType.WEAPON_DAMAGE_MAX,
            ],
            skills=[SkillType.ICY_TOUCH, SkillType.GO_FOR_THE_EYES],
            uniques=[GearBaseType.KATANA],
            image_url="https://i.imgur.com/LovPOVj.png",
        )
        self.scaling = 1.4
        self.weight = 60
        self.author = "Kiwi"


class Wand_T3(Tier3):

    def __init__(self):
        super().__init__(
            name="WHM SHB relic v2",
            type=GearBaseType.WAND_T3,
            description="It was once said, the best wand is the wand that can never hold the crytal. Yes it is by pure magic that the crystal stays on this branch.",
            information="Tier 3 magical weapon.",
            slot=EquipmentSlot.WEAPON,
            modifiers=[
                GearModifierType.WEAPON_DAMAGE_MIN,
                GearModifierType.WEAPON_DAMAGE_MAX,
            ],
            skills=[SkillType.MAGIC_ATTACK],
            image_url="https://i.imgur.com/CEjleY7.png",
        )


class HeadGear_T3_1(Tier3):

    def __init__(self):
        super().__init__(
            name="Headband of Peace and Love",
            type=GearBaseType.HEADGEAR_T3_1,
            description="Collection of all rewards striped around your baldy shiny head: the teeth of goblins and even your own rotten teeth coreved in blood or tomato sauce, none knows.",
            information="Tier 3 head piece.",
            slot=EquipmentSlot.HEAD,
            uniques=[GearBaseType.CAT_HEAD],
            modifiers=[GearModifierType.ARMOR],
            image_url="https://i.imgur.com/IVcrasV.png",
        )


class HeadGear_T3_2(Tier3):

    def __init__(self):
        super().__init__(
            name="A Memory of Childhood",
            type=GearBaseType.HEADGEAR_T3_2,
            description="Collection of all rewards striped around your baldy shiny head - the BALLS that we all played with when we were small.",
            information="Tier 3 head piece.",
            slot=EquipmentSlot.HEAD,
            modifiers=[GearModifierType.ARMOR],
            image_url="https://i.imgur.com/YRRjh6k.png",
        )


class BodyGear_T3_1(Tier3):

    def __init__(self):
        super().__init__(
            name="Leather Jacket",
            type=GearBaseType.BODYGEAR_T3_1,
            description="See these bling bling dindonk dindonks? It is the source of all of my POWER!",
            information="Tier 3 body piece.",
            slot=EquipmentSlot.BODY,
            modifiers=[GearModifierType.ARMOR],
            image_url="https://i.imgur.com/DIosQoG.png",
        )


class BodyGear_T3_2(Tier3):

    def __init__(self):
        super().__init__(
            name="Leather Jacket",
            type=GearBaseType.BODYGEAR_T3_2,
            description="See these bling bling dindonk dindonks? It is the source of all of my POWER!",
            information="Tier 3 body piece.",
            slot=EquipmentSlot.BODY,
            modifiers=[GearModifierType.ARMOR],
            image_url="https://i.imgur.com/rvjshYX.png",
        )


class LegGear_T3(Tier3):

    def __init__(self):
        super().__init__(
            name="Giga Sandals",
            type=GearBaseType.LEGGEAR_T3,
            description="The true hero must have travelled a lot. These THICC sandals are the best choice to make you feel comfortable wherever the battle takes place.",
            information="Tier 3 leg piece. (Comment from Franny: have to add a slip for consensus and actually i have no idea how such sandale works since i dont wear them lol)",
            slot=EquipmentSlot.LEGS,
            uniques=[GearBaseType.CAT_LEGS],
            modifiers=[GearModifierType.ARMOR],
            image_url="https://i.imgur.com/zezOsp4.png",
        )


class Necklace_T3_1(Tier3):

    def __init__(self):
        super().__init__(
            name="ASMR of Johnny Walker",
            type=GearBaseType.NECKLACE_T3_1,
            description="Found in a chest far away in the desert of the CRUNCHY kingdom, maybe it belongs to a dog?",
            information="Tier 3 accessory",
            slot=EquipmentSlot.ACCESSORY,
            modifiers=[GearModifierType.DEXTERITY],
            uniques=[
                GearBaseType.CAT_TAIL,
                GearBaseType.CAT_HANDS,
            ],
            image_url="https://i.imgur.com/fkzteQU.png",
        )


class Necklace_T3_2(Tier3):

    def __init__(self):
        super().__init__(
            name="ASMR of Johnny Walker",
            type=GearBaseType.NECKLACE_T3_2,
            description="Found in a chest far away in the desert of the CRUNCHY kingdom, you are not sure if it is a crystal or just plastic.",
            information="Tier 3 accessory",
            slot=EquipmentSlot.ACCESSORY,
            modifiers=[GearModifierType.DEXTERITY],
            uniques=[
                GearBaseType.CAT_TAIL,
                GearBaseType.CAT_HANDS,
            ],
            image_url="https://i.imgur.com/9ceo3Yj.png",
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
        uniques: list[GearBaseType] = None,
        image_url: str = None,
    ):
        super().__init__(
            name=name,
            type=type,
            description=description,
            information=information,
            slot=slot,
            min_level=5,
            max_level=7,
            modifiers=modifiers,
            skills=skills,
            uniques=uniques,
            scaling=1.4,
            image_url=image_url,
            author="Lusa",
        )


class Stick_T4(Tier4):

    def __init__(self):
        super().__init__(
            name="Eepy Pillow",
            type=GearBaseType.STICK_T4,
            description=(
                "Your favourite pillow. You've been using it since you were small and it "
                "has gotten crusty and stiff over time. Perfect for pillow fights and killing monsters."
            ),
            information="",
            slot=EquipmentSlot.WEAPON,
            modifiers=[
                GearModifierType.WEAPON_DAMAGE_MIN,
                GearModifierType.WEAPON_DAMAGE_MAX,
            ],
            uniques=[
                GearBaseType.KEBAB_SKEWER,
            ],
            skills=[SkillType.NORMAL_ATTACK, SkillType.HEAVY_ATTACK],
            image_url="https://i.imgur.com/quQ83yx.png",
        )


class Dagger(Tier4):

    def __init__(self):
        super().__init__(
            name="Dagger",
            type=GearBaseType.DAGGER,
            description="It's a dagger. It does daggery things.",
            information="",
            slot=EquipmentSlot.WEAPON,
            modifiers=[
                GearModifierType.WEAPON_DAMAGE_MIN,
                GearModifierType.WEAPON_DAMAGE_MAX,
            ],
            uniques=[GearBaseType.KATANA],
            skills=[SkillType.DAGGER_STAB, SkillType.DAGGER_BACKSTAB],
            image_url="https://i.imgur.com/fQdjeVe.png",
        )
        self.scaling = 1.5
        self.weight = 60
        self.author = "Kiwi"


class Blahaj(Tier4):

    def __init__(self):
        super().__init__(
            name="Blåhaj",
            type=GearBaseType.BLAHAJ,
            description=(
                "Your mom bought it as an emotional support plush. "
                "Her words were 'It will protect you from bullies', and you took that literally."
            ),
            information="",
            slot=EquipmentSlot.WEAPON,
            modifiers=[
                GearModifierType.WEAPON_DAMAGE_MIN,
                GearModifierType.WEAPON_DAMAGE_MAX,
            ],
            skills=[SkillType.SHARK_CHOMP, SkillType.SHARK_BEAM],
            image_url="https://i.imgur.com/wnZmZbB.jpeg",
        )
        self.scaling = 1.55
        self.weight = 60
        self.author = "Shen"


class Wand_T4(Tier4):

    def __init__(self):
        super().__init__(
            name="Eepy Glowy Pillow",
            type=GearBaseType.WAND_T4,
            description=(
                "You love this cuddly pillow so much that it started to "
                "absorb your feelings for it, granting it magical powers."
            ),
            information="",
            slot=EquipmentSlot.WEAPON,
            modifiers=[
                GearModifierType.WEAPON_DAMAGE_MIN,
                GearModifierType.WEAPON_DAMAGE_MAX,
            ],
            skills=[SkillType.MAGIC_ATTACK],
            image_url="https://i.imgur.com/n9qrOAv.png",
        )


class HeadGear_T4(Tier4):

    def __init__(self):
        super().__init__(
            name="Eepy Pillow Helmet",
            type=GearBaseType.HEADGEAR_T4,
            description="With the power of duct tape and your grandmas old pillows you managed to tape together the worlds most comfy headgear.",
            information="Tier 4 head piece.",
            slot=EquipmentSlot.HEAD,
            modifiers=[GearModifierType.ARMOR],
            uniques=[
                GearBaseType.KEBAB_HAT,
            ],
            image_url="https://i.imgur.com/WUSr2XH.png",
        )


class BodyGear_T4(Tier4):

    def __init__(self):
        super().__init__(
            name="Eepy Pillow Armor",
            type=GearBaseType.BODYGEAR_T4,
            description=(
                "Someones very concerned mother once crafted this suit out of worry "
                "for her child when it wanted to play with its friends. "
                "Now you use it to defend against monsters."
            ),
            information="Tier 4 body piece.",
            slot=EquipmentSlot.BODY,
            modifiers=[GearModifierType.ARMOR],
            uniques=[
                GearBaseType.FEMALE_ARMOR,
                GearBaseType.KEBAB_APRON,
            ],
            image_url="https://i.imgur.com/6qSt8Zg.png",
        )


class LegGear_T4(Tier4):

    def __init__(self):
        super().__init__(
            name="Eepy Pillow Pants",
            type=GearBaseType.LEGGEAR_T4,
            description=(
                "You swear that you hurt your shins on that stupid drawer for the last time! "
                "As a protective countermeasure you wrap your entire lower body in pillows, "
                "earning you weird looks from your friends."
            ),
            information="Tier 4 leg piece.",
            slot=EquipmentSlot.LEGS,
            uniques=[
                GearBaseType.KEBAB_PANTS,
            ],
            modifiers=[GearModifierType.ARMOR],
            image_url="https://i.imgur.com/43nxRE5.png",
        )


class Necklace_T4(Tier4):

    def __init__(self):
        super().__init__(
            name="Eepy Sleepy Moon",
            type=GearBaseType.NECKLACE_T4,
            description=(
                "A faint, gentle melody plays when closer inspecting this little trinket. "
                "Dont listen for too long or you might doze off."
            ),
            information="Tier 4 accessory",
            slot=EquipmentSlot.ACCESSORY,
            modifiers=[GearModifierType.DEXTERITY],
            image_url="https://i.imgur.com/hr5PCRd.png",
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
        uniques: list[GearBaseType] = None,
        image_url: str = None,
    ):
        super().__init__(
            name=name,
            type=type,
            description=description,
            information=information,
            slot=slot,
            min_level=7,
            max_level=8,
            modifiers=modifiers,
            skills=skills,
            uniques=uniques,
            scaling=1.5,
            image_url=image_url,
            author="Lusa",
        )


class Stick_T5(Tier5):

    def __init__(self):
        super().__init__(
            name="Happy Painter Pallette and Brush",
            type=GearBaseType.STICK_T5,
            description="A palette of warm colors. Perfect to draw pictures beautiful landscapes and dreamy places.",
            information="",
            slot=EquipmentSlot.WEAPON,
            modifiers=[
                GearModifierType.WEAPON_DAMAGE_MIN,
                GearModifierType.WEAPON_DAMAGE_MAX,
            ],
            skills=[SkillType.NORMAL_ATTACK, SkillType.HEAVY_ATTACK],
            image_url="https://i.imgur.com/OTtSPXQ.png",
        )


class Wand_T5(Tier5):

    def __init__(self):
        super().__init__(
            name="Spicy Painter Pallette and Brush",
            type=GearBaseType.WAND_T5,
            description="These colors give the artist a little bit of that extra kick. They will really spice up your paintings. Or your enemies eyes.",
            information="",
            slot=EquipmentSlot.WEAPON,
            modifiers=[
                GearModifierType.WEAPON_DAMAGE_MIN,
                GearModifierType.WEAPON_DAMAGE_MAX,
            ],
            skills=[SkillType.MAGIC_ATTACK],
            image_url="https://i.imgur.com/nMptWYj.png",
        )


class HeadGear_T5(Tier5):

    def __init__(self):
        super().__init__(
            name="Happy Painter Wig",
            type=GearBaseType.HEADGEAR_T5,
            description="Floofy, puffy and soft. It smells a bit like old people but you immediately feel safe and calm when putting it on.",
            information="Tier 5 head piece.",
            slot=EquipmentSlot.HEAD,
            modifiers=[GearModifierType.ARMOR],
            image_url="https://i.imgur.com/gQuNCvP.png",
            uniques=[
                GearBaseType.PROFESSIONAL_DISGUISE,
            ],
        )


class BodyGear_T5(Tier5):

    def __init__(self):
        super().__init__(
            name="Happy Painter Shirt",
            type=GearBaseType.BODYGEAR_T5,
            description=(
                "An artist doesn't require much when it comes to wearing a shirt. "
                "Especially a talented one like you. I am talking about slaying monsters of course."
            ),
            information="Tier 5 body piece.",
            slot=EquipmentSlot.BODY,
            modifiers=[GearModifierType.ARMOR],
            image_url="https://i.imgur.com/3JhjIwz.png",
        )


class LegGear_T5(Tier5):

    def __init__(self):
        super().__init__(
            name="Happy Painter Jeans",
            type=GearBaseType.LEGGEAR_T5,
            description=(
                "With these stylish pants you really show everyone how much you loved the 70s. "
                "That, and the smell of weed they keep emanating."
            ),
            information="Tier 5 leg piece.",
            slot=EquipmentSlot.LEGS,
            modifiers=[GearModifierType.ARMOR],
            image_url="https://i.imgur.com/qoqWNh8.png",
        )


class Necklace_T5(Tier5):

    def __init__(self):
        super().__init__(
            name="Happy Little Trees",
            type=GearBaseType.NECKLACE_T5,
            description=(
                "This painting just brightens up your day every time you look at it. "
                "It reminds you to keep on going after all those happy little accidents."
            ),
            information="Tier 5 accessory",
            slot=EquipmentSlot.ACCESSORY,
            modifiers=[GearModifierType.DEXTERITY],
            image_url="https://i.imgur.com/Ik9GuY1.png",
        )


class Necklace_T5_2(Tier5):

    def __init__(self):
        super().__init__(
            name="Happy Beard",
            type=GearBaseType.NECKLACE_T5_2,
            description="The beard gives your face a friendly vibe and makes you much more likeable.",
            information="Tier 5 accessory",
            slot=EquipmentSlot.ACCESSORY,
            modifiers=[GearModifierType.DEXTERITY],
            image_url="https://i.imgur.com/tuREpEs.png",
        )
