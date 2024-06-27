from enum import Enum


class StatusEffectType(str, Enum):
    BLEED = "Bleed"
    CLEANSE = "Cleanse"
    BLIND = "Blind"


class SkillType(str, Enum):
    EMPTY = "EmptySkill"

    # Player Skills
    # Physical
    NORMAL_ATTACK = "NormalAttack"
    HEAVY_ATTACK = "HeavyAttack"

    SECOND_WIND = "SecondWind"
    GIGA_BONK = "GigaBonk"
    SLICE_N_DICE = "SliceAndDice"

    # Neutral
    POCKET_SAND = "PocketSand"

    # Magical
    MAGIC_ATTACK = "MagicAttack"
    FIRE_BALL = "FireBall"

    # Enemy Skills
    # Mind Goblin
    DEEZ_NUTS = "DeezNuts"
    BONK = "Bonk"

    # Mind Goblin
    MILK_SHOWER = "MilkShot"

    # Table
    TOE_STUB = "ToeStub"
    LOOKING_GOOD = "LookingGood"

    # Table
    ANKLE_AIM = "AnkleAim"
    DOWN_HILL = "DownHill"

    # Nice Guy
    M_LADY = "MLady"
    FEDORA_TIP = "FedoraTip"

    # Nice Guy
    PUKE = "Puke"
    TAIL_WHIP = "TailWhip"

    # Happy Mushroom
    HOLD = "Hold"
    BURST = "Burst"

    # BRO-Coli
    EXERCISE = "Exercise"
    BRO_ARROW = "BroArrows"
    BRO_FART = "BroBiotics"
    BRO_EXTRA_FART = "BroBlast"

    @staticmethod
    def is_weapon_skill(skill_type: "SkillType"):
        return skill_type in [
            SkillType.NORMAL_ATTACK,
            SkillType.HEAVY_ATTACK,
            SkillType.MAGIC_ATTACK,
        ]


class SkillEffect(str, Enum):
    PHYSICAL_DAMAGE = "Physical"
    MAGICAL_DAMAGE = "Magical"
    STATUS_EFFECT_DAMAGE = "Status"
    NEUTRAL_DAMAGE = "Neutral"
    HEALING = "Healing"


class SkillTarget(Enum):
    OPPONENT = 0
    SELF = 1


class StatusEffectTrigger(Enum):
    START_OF_TURN = 0
    END_OF_TURN = 1
    START_OF_ROUND = 2
    END_OF_ROUND = 3
    ON_DAMAGE_TAKEN = 4
    ON_HEALTH_GAINED = 5
    ON_HP_CHANGE = 6
    ON_ATTACK = 7


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

        self.scaled_value = max(1, int(self.value * self.encounter_scaling))
        self.value: int = int(self.value)
