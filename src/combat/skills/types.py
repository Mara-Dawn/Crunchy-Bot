from enum import Enum


class SkillType(str, Enum):
    NORMAL_ATTACK = "NormalAttack"
    HEAVY_ATTACK = "HeavyAttack"
    MAGIC_ATTACK = "MagicAttack"


class SkillEffect(Enum):
    PHYSICAL_DAMAGE = 0
    MAGICAL_DAMAGE = 1
    HEALING = 2
