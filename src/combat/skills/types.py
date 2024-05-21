from enum import Enum


class SkillType(str, Enum):
    NORMAL_ATTACK = "NormalAttack"
    HEAVY_ATTACK = "HeavyAttack"
    MAGIC_ATTACK = "MagicAttack"

    DEEZ_NUTS = "DeezNuts"


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
        is_crit: bool,
    ):
        self.weapon_roll = weapon_roll
        self.skill_base = skill_base
        self.modifier = modifier
        self.critical_modifier = critical_modifier
        self.is_crit = is_crit

        self.value = self.weapon_roll * self.skill_base * self.modifier
        if self.is_crit:
            self.value *= self.critical_modifier

        self.value: int = int(self.value)
