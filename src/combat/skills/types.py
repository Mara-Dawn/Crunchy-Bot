from enum import Enum


class StatusEffectType(str, Enum):
    BLEED = "Bleed"
    CLEANSE = "Cleanse"
    BLIND = "Blind"
    FLUSTERED = "Flustered"
    INSPIRED = "Inspired"
    RAGE = "Rage"
    FEAR = "Fear"
    RAGE_QUIT = "RageQuit"
    HIGH = "High"
    POISON = "Poison"
    RANDOM = "Random"
    DEATH_PROTECTION = "DeathProtection"
    HEAL_OVER_TIME = "HealOverTime"


class SkillType(str, Enum):
    EMPTY = "EmptySkill"

    # Player Skills
    # Physical
    NORMAL_ATTACK = "NormalAttack"
    HEAVY_ATTACK = "HeavyAttack"

    TAPE_ATTACK = "TapeAttack"

    SECOND_WIND = "SecondWind"
    SECOND_HEART = "SecondHeart"
    SMELLING_SALT = "SmellingSalt"
    FAMILY_PIZZA = "FamilyPizza"
    HOLY_GANG_SIGNS = "HolyGangSigns"
    LOOKSMAXXING = "LooksMaxxing"
    GIGA_BONK = "GigaBonk"
    SLICE_N_DICE = "SliceAndDice"

    # Neutral
    POCKET_SAND = "PocketSand"
    BLOOD_RAGE = "BloodRage"
    WAR_RAGE = "WarGodRage"
    PHYSICAL_MISSILE = "PhysicalMissile"
    FINE_ASS = "FineAss"
    NOT_SO_FINE_ASS = "NotSoFineAss"

    # Magical
    MAGIC_ATTACK = "MagicAttack"
    FIRE_BALL = "FireBall"
    MAGIC_MISSILE = "MagicMissile"
    PARTY_DRUGS = "PartyDrugs"
    SPECTRAL_HAND = "SpectralHand"

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

    # Mimic
    DEVOUR = "Devour"
    LOOT_SPIT = "LootSpit"

    # School Bully
    WEDGIE = "Wedgie"
    KNEE_KICK = "KneeKick"
    HA_HA = "HaHa"

    # Daddy
    HAIR_PULL = "HairPull"
    BELT = "Belt"
    TIE_YOU_UP = "TieYouUp"
    BUTT_SLAP = "ButtSlap"
    WHIP = "Whip"
    ON_YOUR_KNEES = "OnYourKnees"

    @staticmethod
    def is_weapon_skill(skill_type: "SkillType"):
        return skill_type in [
            SkillType.NORMAL_ATTACK,
            SkillType.HEAVY_ATTACK,
            SkillType.TAPE_ATTACK,
            SkillType.MAGIC_ATTACK,
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


class StatusEffectApplication(Enum):
    DEFAULT = 0
    ATTACK_VALUE = 1


class SkillInstance:

    def __init__(
        self,
        weapon_roll: int,
        skill_base: float,
        modifier: float,
        critical_modifier: float,
        encounter_scaling: float,
        is_crit: bool,
    ):
        self.weapon_roll = weapon_roll
        self.skill_base = skill_base
        self.modifier = modifier
        self.critical_modifier = critical_modifier
        self.encounter_scaling = encounter_scaling
        self.is_crit = is_crit

        self.value = self.weapon_roll * self.skill_base * self.modifier
        self.raw_value = int(self.value)
        if self.is_crit:
            self.value *= self.critical_modifier

        self.scaled_value = 0
        if self.value > 0:
            self.scaled_value = max(1, int(self.value * self.encounter_scaling))
        self.value: int = int(self.value)

    def apply_effect_modifier(self, modifier: float):
        self.value *= modifier
        self.raw_value = int(self.value)
        self.scaled_value = 0
        if self.value > 0:
            self.scaled_value = max(1, int(self.value * self.encounter_scaling))
        self.value: int = int(self.value)
