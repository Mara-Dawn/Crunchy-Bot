from combat.gear.bases import LegGear_T0, Necklace_T0
from combat.gear.types import GearBaseType, GearModifierType
from combat.skills.skills import BloodRage, SecondWind
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
