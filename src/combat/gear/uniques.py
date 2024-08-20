from combat.gear.bases import (
    BodyGear_T3_1,
    BodyGear_T4,
    HeadGear_T0,
    HeadGear_T1,
    HeadGear_T2,
    HeadGear_T4,
    HeadGear_T5,
    LegGear_T0,
    LegGear_T2,
    LegGear_T4,
    Necklace_T0,
    Necklace_T1_2,
    Necklace_T2_1,
    Necklace_T2_2,
    Stick_T2,
    Stick_T4,
)
from combat.gear.types import GearBaseType, GearModifierType
from combat.skills.skills import BloodRage, FineAss, GigaBonk, SecondWind
from combat.skills.status_effect import SkillStatusEffect
from combat.skills.types import (
    SkillEffect,
    SkillTarget,
    SkillType,
    StatusEffectApplication,
    StatusEffectType,
)


class Unique:

    def __init__(
        self,
        unique_modifiers: dict[GearModifierType, float],
    ):
        self.unique_modifiers = unique_modifiers
        self.uniques = [self.type]


class HotPants(LegGear_T0, Unique):

    def __init__(self):
        LegGear_T0.__init__(self)
        self.name = "Jorts"
        self.type = GearBaseType.HOT_PANTS
        self.description = "Your dad wore these before he 'lost' them in the woods."
        self.image_url = "https://i.imgur.com/ghnKDaz.png"
        self.author = "Lusa"
        Unique.__init__(
            self,
            unique_modifiers={
                GearModifierType.CONSTITUTION: -2,
                GearModifierType.MAGIC: 3,
                GearModifierType.ATTACK: 3,
            },
        )


class DeezNutsAccessory(Necklace_T0, Unique):

    def __init__(self):
        Necklace_T0.__init__(self)
        self.name = "Deez Nuts"
        self.type = GearBaseType.DEEZ_NUTS
        self.description = "Stainless steel orbs enveloped in textured leather. They protect the wearer from ligma and other sugondese afflictions."
        self.image_url = "https://i.imgur.com/cLlYtkF.png"
        self.author = "Lusa"
        Unique.__init__(
            self,
            unique_modifiers={
                GearModifierType.ARMOR: 3,
                GearModifierType.DEFENSE: 6,
                GearModifierType.HEALING: 4,
            },
        )


class UselessAmulet(Necklace_T0, Unique):

    def __init__(self):
        Necklace_T0.__init__(self)
        self.name = "Rusty Amulet"
        self.type = GearBaseType.USELESS_AMULET
        self.description = "This amulet was once someones priced possession but now it collects dust in your backpack."
        self.image_url = "https://i.imgur.com/ddpZGON.png"
        self.author = "Lusa"
        Unique.__init__(
            self,
            unique_modifiers={
                GearModifierType.DEXTERITY: 0,
            },
        )


class TapeMeasure(Stick_T2, Unique):

    def __init__(self):
        Stick_T2.__init__(self)
        self.name = "Tape Measure"
        self.type = GearBaseType.TAPE_MEASURE
        self.description = (
            "By throwing and pulling back this increidibly sharp measuring tape, "
            "you can hurt your opponents and make them bleed! Just be careful to not "
            "cut yourself."
        )
        self.image_url = "https://i.imgur.com/cw1aPuB.jpeg"
        self.author = "Klee"
        self.skills = [SkillType.TAPE_ATTACK]
        Unique.__init__(
            self,
            unique_modifiers={
                GearModifierType.WEAPON_DAMAGE_MIN: 1,
                GearModifierType.WEAPON_DAMAGE_MAX: 1,
                GearModifierType.ATTACK: 1,
                GearModifierType.CRIT_RATE: 0.5,
                GearModifierType.CRIT_DAMAGE: 1,
            },
        )


class CatHead(HeadGear_T2, Unique):

    def __init__(self):
        HeadGear_T2.__init__(self)
        self.name = "Cat Ears & Nose"
        self.type = GearBaseType.CAT_HEAD
        self.description = (
            "Embrace your feline nature with these cute cat accessories. "
            "Don't worry about how they stay attached, you'll figure it out."
        )
        self.image_url = "https://i.imgur.com/DSEAUoX.png"
        self.author = "Lusa"
        Unique.__init__(
            self,
            unique_modifiers={
                GearModifierType.ARMOR: 0.5,
                GearModifierType.EVASION: 1,
                GearModifierType.MAGIC: 1.5,
                GearModifierType.ATTACK: 1.5,
                GearModifierType.CRIT_RATE: 0.5,
                GearModifierType.CRIT_DAMAGE: 1,
            },
        )


class CatLegs(LegGear_T2, Unique):

    def __init__(self):
        LegGear_T2.__init__(self)
        self.name = "Cat Stockings"
        self.type = GearBaseType.CAT_LEGS
        self.description = "Throw off your enemies by leaving little cute cat footprints behind. They'll never find you!"
        self.image_url = "https://i.imgur.com/1KNBMTf.png"
        self.author = "Lusa"
        Unique.__init__(
            self,
            unique_modifiers={
                GearModifierType.ARMOR: 0.5,
                GearModifierType.EVASION: 1,
                GearModifierType.MAGIC: 1.5,
                GearModifierType.ATTACK: 1.5,
                GearModifierType.CRIT_RATE: 0.5,
                GearModifierType.CRIT_DAMAGE: 1,
            },
        )


class CatTail(Necklace_T2_1, Unique):

    def __init__(self):
        Necklace_T2_1.__init__(self)
        self.name = "Cat Tail"
        self.type = GearBaseType.CAT_TAIL
        self.description = "Improve your balance with this useful tail accessory."
        self.image_url = "https://i.imgur.com/DhhRDT2.png"
        self.author = "Lusa"
        Unique.__init__(
            self,
            unique_modifiers={
                GearModifierType.DEXTERITY: 3,
                GearModifierType.EVASION: 1,
                GearModifierType.MAGIC: 1.5,
                GearModifierType.ATTACK: 1.5,
                GearModifierType.CRIT_RATE: 0.5,
                GearModifierType.CRIT_DAMAGE: 1,
            },
        )


class CatHands(Necklace_T2_2, Unique):

    def __init__(self):
        Necklace_T2_2.__init__(self)
        self.name = "Cat Gloves"
        self.type = GearBaseType.CAT_HANDS
        self.description = "These gloves will keep you warm while still letting you scratch your nails against the couch cushions."
        self.image_url = "https://i.imgur.com/LIkiSeW.png"
        self.author = "Lusa"
        Unique.__init__(
            self,
            unique_modifiers={
                GearModifierType.DEXTERITY: 3,
                GearModifierType.EVASION: 1,
                GearModifierType.MAGIC: 1.5,
                GearModifierType.ATTACK: 1.5,
                GearModifierType.CRIT_RATE: 0.5,
                GearModifierType.CRIT_DAMAGE: 1,
            },
        )


class FemaleArmor(BodyGear_T3_1, Unique):

    def __init__(self):
        BodyGear_T3_1.__init__(self)
        self.name = "Female Armor"
        self.type = GearBaseType.FEMALE_ARMOR
        self.description = (
            "This intricate design promises the best possible protection from enemy attacks. "
            "Extremely fashionable and highly sought after."
        )
        self.image_url = "https://i.imgur.com/OtTlqk5.png"
        self.author = "Lusa"
        Unique.__init__(
            self,
            unique_modifiers={
                GearModifierType.ARMOR: 2,
                GearModifierType.EVASION: 2,
                GearModifierType.DEFENSE: 6,
            },
        )


class KebabHat(HeadGear_T4, Unique):

    def __init__(self):
        HeadGear_T4.__init__(self)
        self.name = "Kebab Hat & Beard"
        self.type = GearBaseType.KEBAB_HAT
        self.description = "Only a true kebab chef wears such a majestic mustache."
        self.image_url = "https://i.imgur.com/QToRVBg.png"
        self.author = "Lusa"
        Unique.__init__(
            self,
            unique_modifiers={
                GearModifierType.ARMOR: 1,
                GearModifierType.EVASION: 0.5,
                GearModifierType.ATTACK: 0.5,
                GearModifierType.HEALING: 2.5,
                GearModifierType.CRIT_RATE: 0.5,
            },
        )


class KebabApron(BodyGear_T4, Unique):

    def __init__(self):
        BodyGear_T4.__init__(self)
        self.name = "Kebab Apron"
        self.type = GearBaseType.KEBAB_APRON
        self.description = (
            "Your grandpa used this apron back when he opened the Kebab shop. "
            "The decades of grease and sweat give it a very distinguished aroma."
        )
        self.image_url = "https://i.imgur.com/3xInorn.png"
        self.author = "Lusa"
        Unique.__init__(
            self,
            unique_modifiers={
                GearModifierType.ARMOR: 1,
                GearModifierType.EVASION: 0.5,
                GearModifierType.ATTACK: 0.5,
                GearModifierType.HEALING: 2,
                GearModifierType.CRIT_RATE: 0.5,
                GearModifierType.CRIT_DAMAGE: 0.5,
            },
        )


class KebabPants(LegGear_T4, Unique):

    def __init__(self):
        LegGear_T4.__init__(self)
        self.name = "Kebab Pants"
        self.type = GearBaseType.KEBAB_PANTS
        self.description = (
            "The kebab man is always well dressed under his apron. "
            "With these stylish pants and some classic slippers you are well equipped to handle a skewer."
        )
        self.image_url = "https://i.imgur.com/mmbiA2S.png"
        self.author = "Lusa"
        Unique.__init__(
            self,
            unique_modifiers={
                GearModifierType.ARMOR: 1,
                GearModifierType.EVASION: 0.5,
                GearModifierType.ATTACK: 0.5,
                GearModifierType.HEALING: 2.5,
                GearModifierType.CRIT_DAMAGE: 0.5,
            },
        )


class KebabSkewer(Stick_T4, Unique):

    def __init__(self):
        Stick_T4.__init__(self)
        self.name = "Kebab Skewer"
        self.type = GearBaseType.KEBAB_SKEWER
        self.description = (
            "A fresh, beatiful kebab skewer. It is greasy, heavy and smells delicious."
        )
        self.image_url = "https://i.imgur.com/yarx7l2.png"
        self.author = "Lusa"
        self.skills = [SkillType.DONER_KEBAB, SkillType.KEBAB_SMILE]
        Unique.__init__(
            self,
            unique_modifiers={
                GearModifierType.WEAPON_DAMAGE_MIN: 1,
                GearModifierType.WEAPON_DAMAGE_MAX: 1,
                GearModifierType.ATTACK: 1,
                GearModifierType.HEALING: 2.5,
            },
        )


class RabbitFoot(Necklace_T1_2, Unique):

    def __init__(self):
        Necklace_T1_2.__init__(self)
        self.name = "Rabbit Foot"
        self.type = GearBaseType.RABBIT_FOOT
        self.description = "Oh wow, lucky! Someone dropped their rabbit foot. Surely it will bring you more luck that it did for its previous owner. It does look a little weird though, how curious..."
        self.image_url = "https://i.imgur.com/aLUBL2Y.png"
        self.author = "Lusa"
        Unique.__init__(
            self,
            unique_modifiers={
                GearModifierType.DEXTERITY: 4,
                GearModifierType.CRIT_RATE: 4,
            },
        )


class FastFoodCap(HeadGear_T1, Unique):

    def __init__(self):
        HeadGear_T1.__init__(self)
        self.name = "Fast Food Cap"
        self.type = GearBaseType.FAST_FOOD_CAP
        self.description = "Nothing can phase you, you have seen it all."
        self.image_url = "https://i.imgur.com/iXoO6xH.png"
        self.author = "Lusa"
        Unique.__init__(
            self,
            unique_modifiers={
                GearModifierType.ARMOR: 3,
                GearModifierType.EVASION: 2,
                GearModifierType.DEFENSE: 5,
                GearModifierType.HEALING: 2.5,
                GearModifierType.DEXTERITY: 2,
            },
        )


class ShooterWig(HeadGear_T0, Unique):

    def __init__(self):
        HeadGear_T0.__init__(self)
        self.name = "Shooter Wig"
        self.type = GearBaseType.SHOOTER_WIG
        self.description = "Give off cool dad vibes wile shooting your gun with this high quality shooting wig."
        self.image_url = "https://i.imgur.com/V8z1W9s.png"
        self.author = "Lusa"
        Unique.__init__(
            self,
            unique_modifiers={
                GearModifierType.ARMOR: 1,
                GearModifierType.DEXTERITY: 2,
                GearModifierType.CRIT_RATE: 2,
                GearModifierType.CRIT_DAMAGE: 6,
            },
        )


class ProfessionalDisguise(HeadGear_T5, Unique):

    def __init__(self):
        HeadGear_T5.__init__(self)
        self.name = "Professional Disguise"
        self.type = GearBaseType.PROFESSIONAL_DISGUISE
        self.description = (
            "When equipping this highly advanced masking device, you greatly increase "
            "the chance of enemies mistaking you for a harmless bystander."
        )
        self.image_url = "https://i.imgur.com/8pUj385.png"
        self.author = "Lusa"
        Unique.__init__(
            self,
            unique_modifiers={
                GearModifierType.ARMOR: 1,
                GearModifierType.EVASION: 3,
            },
        )


# Skills


class GenerationalSlipper(GigaBonk, Unique):

    def __init__(self):
        GigaBonk.__init__(self)
        self.name = "Generational Slipper"
        self.skill_type = SkillType.GENERATIONAL_SLIPPER
        self.description = (
            "This is a slipper that has been in your family for generations. "
            "Your mom threw it to you with high precision, but not at you (This time). "
            "Now your turn has come."
        )
        self.image_url = "https://i.imgur.com/X0n7DRG.png"
        self.cooldown = 3
        self.base_value = 6
        self.stacks = 2
        self.author = "Lusa"
        Unique.__init__(
            self,
            unique_modifiers={},
        )


class WarGodRage(BloodRage, Unique):

    def __init__(self):
        BloodRage.__init__(self)
        self.name = "Warrior Rage"
        self.skill_type = SkillType.WAR_RAGE
        self.description = (
            "You are absolutely infuriated. Completely flabbergasted by the sheer AUDACITY! "
            "Who do they think they are!? Your anger transforms you from a mere Karen into an "
            "ancient and fearsome god of war. Causes bleeding and blindness on hit. Your next 6 attacks cause bleeding. "
        )
        self.image_url = "https://i.imgur.com/LcHx044.png"
        self.cooldown = 6
        self.base_value = 3
        self.skill_effect = SkillEffect.PHYSICAL_DAMAGE
        self.status_effects = [
            SkillStatusEffect(
                StatusEffectType.RAGE,
                6,
                self_target=True,
            ),
            SkillStatusEffect(
                StatusEffectType.BLEED,
                6,
                StatusEffectApplication.ATTACK_VALUE,
            ),
            SkillStatusEffect(
                StatusEffectType.BLIND,
                1,
            ),
        ]
        self.stacks = 6
        self.author = "Lusa"
        Unique.__init__(
            self,
            unique_modifiers={},
        )


class SmellingSalt(SecondWind, Unique):

    def __init__(self):
        SecondWind.__init__(self)
        self.name = "Smelling Salt"
        self.skill_type = SkillType.SMELLING_SALT
        self.description = (
            "This stuff is crazy, it smells so incredibly disgusting that it would even "
            "bring back your grandmas grandma from the grave. Using it revives a random defeated party member."
        )
        self.image_url = "https://i.imgur.com/nER6d1X.png"
        self.skill_effect = SkillEffect.HEALING
        self.stacks = 1
        self.default_target = SkillTarget.RANDOM_DEFEATED_PARTY_MEMBER
        self.reset_after_encounter = False
        self.author = "Lusa"
        Unique.__init__(
            self,
            unique_modifiers={},
        )


class NotSoFineAss(FineAss, Unique):

    def __init__(self):
        FineAss.__init__(self)
        self.name = "Not So Fine Ass"
        self.skill_type = SkillType.NOT_SO_FINE_ASS
        self.description = (
            "You try to inspire your party with your mighty fine booty, but what is this? You accidentally "
            "let out a massive fart instead. "
            "How embarassing! Luckily people are laughing about it, boosting everyones damage for 4 turns."
        )
        self.image_url = "https://i.imgur.com/K2pTHqP.png"
        self.base_value = 20
        self.status_effects = [
            SkillStatusEffect(
                StatusEffectType.INSPIRED,
                4,
                StatusEffectApplication.ATTACK_VALUE,
            )
        ]
        Unique.__init__(
            self,
            unique_modifiers={},
        )
