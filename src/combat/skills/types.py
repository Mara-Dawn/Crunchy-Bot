from enum import Enum


class SkillType(str, Enum):
    EMPTY = "EmptySkill"
    NORMAL_ATTACK = "NormalAttack"
    HEAVY_ATTACK = "HeavyAttack"
    MAGIC_ATTACK = "MagicAttack"

    SECOND_WIND = "SecondWind"
    GIGA_BONK = "GigaBonk"

    DEEZ_NUTS = "DeezNuts"
    BONK = "Bonk"


class SkillEffect(str, Enum):
    PHYSICAL_DAMAGE = "Physical"
    MAGICAL_DAMAGE = "Magical"
    HEALING = "Healing"


class DamageInstance:

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
