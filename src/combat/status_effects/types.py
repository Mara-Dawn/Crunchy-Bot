from enum import Enum


class StatusEffectType(str, Enum):
    BLEED = "Bleed"
    CLEANSE = "Cleanse"
    FULL_CLEANSE = "FullCleanse"
    STATUS_IMMUNE = "StatusImmune"
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
    CHUCKLE = "Chuckle"
    RAGE_QUIT = "RageQuit"
    HIGH = "High"
    POISON = "Poison"
    RANDOM = "Random"
    DEATH_PROTECTION = "DeathProtection"
    HEAL_OVER_TIME = "HealOverTime"
    FROST = "Frost"
    VULNERABLE = "Vulnerable"
    PHYS_VULN = "PhysVuln"
    MAGIC_VULN = "MagicVuln"

    PARTY_LEECH = "PartyLeech"

    FROGGED = "Frogged"
    STUN = "Stun"

    def is_cleansable(effect_type: "StatusEffectType"):
        return effect_type in [
            StatusEffectType.BLEED,
            StatusEffectType.POISON,
            StatusEffectType.BLIND,
        ]

    def is_negative(effect_type: "StatusEffectType"):
        return effect_type in [
            StatusEffectType.BLEED,
            StatusEffectType.BLIND,
            StatusEffectType.FLUSTERED,
            StatusEffectType.SIMP,
            StatusEffectType.FEAR,
            StatusEffectType.HIGH,
            StatusEffectType.POISON,
            StatusEffectType.FROST,
            StatusEffectType.VULNERABLE,
            StatusEffectType.MAGIC_VULN,
            StatusEffectType.PHYS_VULN,
            StatusEffectType.PARTY_LEECH,
            StatusEffectType.FROGGED,
            StatusEffectType.STUN,
        ]


class StatusEffectApplication(Enum):
    DEFAULT = 0
    ATTACK_VALUE = 1
    MANUAL_VALUE = 2
    RAW_ATTACK_VALUE = 3


class SkillStatusEffect:

    def __init__(
        self,
        status_effect_type: StatusEffectType,
        stacks: int,
        application: StatusEffectApplication = StatusEffectApplication.DEFAULT,
        application_value: float = None,
        application_chance: float = 1,
        self_target: bool = False,
    ):
        self.status_effect_type = status_effect_type
        self.stacks = stacks
        self.application = application
        self.application_value = application_value
        self.application_chance = application_chance
        self.self_target = self_target
