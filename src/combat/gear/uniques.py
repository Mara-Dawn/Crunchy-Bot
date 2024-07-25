from combat.gear.bases import LegGear_T0, Necklace_T0
from combat.gear.types import GearBaseType, GearModifierType


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
                GearModifierType.ARMOR: 1,
                GearModifierType.CONSTITUTION: -1.5,
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
                GearModifierType.ARMOR: 5,
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
