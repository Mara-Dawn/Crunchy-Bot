import random
from dataclasses import dataclass
from enum import Enum


class StatusEffectType(str, Enum):
    BLEED = "Bleed"
    CLEANSE = "Cleanse"
    PROTECTION = "Protection"
    BLIND = "Blind"
    EVASIVE = "Evasive"
    FLUSTERED = "Flustered"
    SIMP = "Simp"
    INSPIRED = "Inspired"
    NEURON_ACTIVE = "NeuronActive"
    ZONED_IN = "ZonedIn"
    RAGE = "Rage"
    FEAR = "Fear"
    RAGE_QUIT = "RageQuit"
    HIGH = "High"
    POISON = "Poison"
    RANDOM = "Random"
    DEATH_PROTECTION = "DeathProtection"
    HEAL_OVER_TIME = "HealOverTime"
    FROST = "Frost"

    PARTY_LEECH = "PartyLeech"

    FROGGED = "Frogged"
    STUN = "Stun"


class SkillType(str, Enum):
    EMPTY = "EmptySkill"

    # Player Skills
    # Physical
    NORMAL_ATTACK = "NormalAttack"
    HEAVY_ATTACK = "HeavyAttack"

    TAPE_ATTACK = "TapeAttack"
    DONER_KEBAB = "DonerKebab"
    KEBAB_SMILE = "KebabSmile"

    SECOND_WIND = "SecondWind"
    SECOND_HEART = "SecondHeart"
    SMELLING_SALT = "SmellingSalt"
    FAMILY_PIZZA = "FamilyPizza"
    HOLY_GANG_SIGNS = "HolyGangSigns"
    FORESIGHT = "Foresight"
    LOOKSMAXXING = "LooksMaxxing"
    GIGA_BONK = "GigaBonk"
    GENERATIONAL_SLIPPER = "GenerationalSlipper"
    SLICE_N_DICE = "SliceAndDice"
    COOL_CUCUMBER = "CoolCucumber"

    # Neutral
    POCKET_SAND = "PocketSand"
    BLOOD_RAGE = "BloodRage"
    WAR_RAGE = "WarGodRage"
    PHYSICAL_MISSILE = "PhysicalMissile"
    FINE_ASS = "FineAss"
    COLORFUL_VASE = "ColorfulVase"
    NOT_SO_FINE_ASS = "NotSoFineAss"
    NEURON_ACTIVATION = "NeuronActivation"

    # Magical
    MAGIC_ATTACK = "MagicAttack"
    FIRE_BALL = "FireBall"
    MAGIC_MISSILE = "MagicMissile"
    PARTY_DRUGS = "PartyDrugs"
    SPECTRAL_HAND = "SpectralHand"

    FROST_ATTACK = "FrostAttack"
    FROZEN_DROPS = "FrozenDrops"
    ICE_BALL = "IceBall"

    # Enemy Skills
    # Mind Goblin
    DEEZ_NUTS = "DeezNuts"
    BONK = "Bonk"

    # Garlic Dog
    GARLIC_BREATH = "GarlicBreath"

    # Mind Goblin
    MILK_SHOWER = "MilkShot"

    # Table
    TOE_STUB = "ToeStub"
    LOOKING_GOOD = "LookingGood"

    # Goose
    BIG_HONK = "BigHonk"
    ASS_BITE = "AssBite"

    # Table
    ANKLE_AIM = "AnkleAim"
    DOWN_HILL = "DownHill"

    # Nice Guy
    M_LADY = "MLady"
    FEDORA_TIP = "FedoraTip"

    # Your Mom
    AROUND_THE_WORLD = "AroundTheWorld"
    SIT = "Sit"

    # Nice Guy
    PUKE = "Puke"
    TAIL_WHIP = "TailWhip"

    # Pimple
    IT_HURTS = "ItHurts"
    POP = "Pop"

    # Happy Mushroom
    HOLD = "Hold"
    BURST = "Burst"

    # BRO-Coli
    EXERCISE = "Exercise"
    BRO_ARROW = "BroArrows"
    BRO_FART = "BroBiotics"
    BRO_EXTRA_FART = "BroBlast"

    # DF Tank
    STANCE_OFF = "StanceOff"
    DEAD_TANK = "DeadTank"
    YPYT = "YPYT"

    # Cuddles
    FEAR = "FearSkill"
    FEASTING = "Feasting"

    # Eli
    FAT_ASS = "FatAss"
    OH_LAWD_HE_COMIN = "OhLawdHeComin"
    CAT_SCREECH = "CatScreech"

    # Homeless Woman
    HOMELESS_PLEADING = "HomelessPleading"
    HOMELESS_BEGGING = "HomelessBegging"

    # Crackachu
    THUNDER_CRACK = "ThunderCrack"
    USED_NEEDLES = "UsedNeedles"

    # Mommy
    TIME_TO_SLICE = "TimeToSlice"
    STEP_ON_YOU = "StepOnYou"
    CHOKE = "Choke"

    # Hoe
    HOE_KNEES = "HoeKnees"
    HOE_SHANK = "HoeShank"
    HOE_SPREAD = "HoeSpread"

    # Scribbler
    ERASE = "Erase"
    EYE_POKE = "EyePoke"
    PAPER_CUTS = "PaperCuts"

    # Mimic
    DEVOUR = "Devour"
    LOOT_SPIT = "LootSpit"

    # School Bully
    WEDGIE = "Wedgie"
    KNEE_KICK = "KneeKick"
    HA_HA = "HaHa"

    # Bonterry
    CHEFS_KNIVE = "ChefsKnive"

    # Bonterry King
    KARMA = "Karma"
    GLOOM = "Gloom"

    # Fairy
    SPARKLES = "Sparkles"
    GET_FROGGED = "GetFrogged"
    WHISPERING = "Whispering"
    FOLLOW_ME = "FollowMe"

    # Boomer
    BACK_IN_MY_DAYS = "BackInMyDays"
    OUTDATED_ADVICE = "OutdatedAdvice"
    NOSTALGIA_BOMB = "NostalgiaBomb"

    # Sausage Butcher
    BIG_SALAMI = "BigSalami"
    WIENER_BOMB = "WienerBomb"
    BRATWURST_BREAK = "BratwurstBreak"

    # Mango the Cat
    FURRY_HUG = "FurryHug"
    ROUGH_LOVE = "RoughLove"
    NO_THANK_YOU = "NoThankYou"

    # Daddy
    HAIR_PULL = "HairPull"
    BELT = "Belt"
    TIE_YOU_UP = "TieYouUp"
    BUTT_SLAP = "ButtSlap"
    WHIP = "Whip"
    ON_YOUR_KNEES = "OnYourKnees"

    # Weeb
    OMAE_WA = "OmaeWa"
    POTATO_CHIP = "PotatoChip"
    DAKIMAKURA = "Dakimakura"
    WEEB_KAWAII = "WeebKawaii"
    WEEB_SPLAINING = "WeebSplaining"
    ALCHEMY = "Alchemy"

    WEEBI_HAME_HA = "WeebiHameHa"
    WEEBI_DAMA_CHARGE_1 = "WeebiDamaCharge1"
    WEEBI_DAMA_CHARGE_2 = "WeebiDamaCharge2"
    WEEBI_DAMA_CHARGE_3 = "WeebiDamaCharge3"
    WEEBI_DAMA = "WeebiDama"

    MEOW_TIARA = "MeowTiara"
    MEOW_SPIRAL = "MeowSpiral"
    MEOW_KISS = "MeowKiss"

    @staticmethod
    def is_weapon_skill(skill_type: "SkillType"):
        return skill_type in [
            SkillType.NORMAL_ATTACK,
            SkillType.HEAVY_ATTACK,
            SkillType.MAGIC_ATTACK,
            SkillType.FROST_ATTACK,
            SkillType.FROZEN_DROPS,
            SkillType.TAPE_ATTACK,
            SkillType.DONER_KEBAB,
            SkillType.KEBAB_SMILE,
        ]


class SkillEffect(str, Enum):
    PHYSICAL_DAMAGE = "Physical"
    MAGICAL_DAMAGE = "Magical"
    STATUS_EFFECT_DAMAGE = "Status"
    NEUTRAL_DAMAGE = "Neutral"
    NOTHING = "Nothing"
    BUFF = "Buff"
    HEALING = "Healing"


class SkillTarget(Enum):
    OPPONENT = 0
    SELF = 1
    PARTY = 2
    RANDOM_PARTY_MEMBER = 3
    RANDOM_DEFEATED_PARTY_MEMBER = 4


class StatusEffectTrigger(Enum):
    START_OF_TURN = 0
    END_OF_TURN = 1
    START_OF_ROUND = 2
    END_OF_ROUND = 3
    ON_DAMAGE_TAKEN = 4
    ON_DEATH = 5
    ON_ATTACK = 7
    POST_ATTACK = 8
    ATTRIBUTE = 9


class StatusEffectApplication(Enum):
    DEFAULT = 0
    ATTACK_VALUE = 1
    MANUAL_VALUE = 2


@dataclass
class StatusEffectOutcome:
    value: int | None = None
    modifier: float | None = None
    crit_chance: float | None = None
    crit_chance_modifier: float | None = None
    initiative: int | None = None
    info: str | None = None
    embed_data: dict[str, str] | None = None

    @staticmethod
    def EMPTY():
        return StatusEffectOutcome()


class SkillInstance:

    def __init__(
        self,
        weapon_roll: int,
        skill_base: float,
        modifier: float,
        critical_modifier: float,
        encounter_scaling: float,
        crit_chance: float,
        is_crit: bool | None = None,
    ):
        self.weapon_roll = weapon_roll
        self.skill_base = skill_base
        self.modifier = modifier
        self.critical_modifier = critical_modifier
        self.encounter_scaling = encounter_scaling
        self.critical_chance = crit_chance
        self.is_crit = is_crit

    @property
    def value(self):
        if self.is_crit is None:
            self.is_crit = random.random() < self.critical_chance

        value = self.weapon_roll * self.skill_base * self.modifier

        if self.is_crit:
            value *= self.critical_modifier

        return int(value)

    @property
    def raw_value(self):
        value = self.weapon_roll * self.skill_base * self.modifier
        return int(value)

    @property
    def scaled_value(self):
        if self.is_crit is None:
            self.is_crit = random.random() < self.critical_chance

        value = self.weapon_roll * self.skill_base * self.modifier

        if self.is_crit:
            value *= self.critical_modifier

        if value > 0:
            value = max(1, value * self.encounter_scaling)

        return int(value)

    def apply_effect_outcome(self, outcome: StatusEffectOutcome):
        if outcome.modifier is not None:
            self.modifier *= outcome.modifier
        if self.is_crit is None:
            if outcome.crit_chance is not None:
                self.critical_chance = outcome.crit_chance
            if outcome.crit_chance_modifier is not None:
                self.critical_chance *= outcome.crit_chance_modifier
