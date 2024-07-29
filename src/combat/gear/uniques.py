from combat.gear.bases import (
    BodyGear_T3_1,
    HeadGear_T2,
    LegGear_T0,
    LegGear_T2,
    Necklace_T0,
    Necklace_T2_1,
    Necklace_T2_2,
    Stick_T2,
)
from combat.gear.types import GearBaseType, GearModifierType
from combat.skills.skills import BloodRage, FineAss, SecondWind
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
                GearModifierType.MAGIC: 4,
                GearModifierType.ATTACK: 4,
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
                GearModifierType.MAGIC: 2,
                GearModifierType.ATTACK: 2,
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
                GearModifierType.MAGIC: 2,
                GearModifierType.ATTACK: 2,
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
                GearModifierType.MAGIC: 2,
                GearModifierType.ATTACK: 2,
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
                GearModifierType.MAGIC: 2,
                GearModifierType.ATTACK: 2,
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


# Skills


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
