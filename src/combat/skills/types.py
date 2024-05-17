from enum import Enum


class SkillType(str, Enum):
    NORMAL_ATTACK = "NormalAttack"
    HEAVY_ATTACK = "HeavyAttack"
    MAGIC_ATTACK = "MagicAttack"


class DamageType(Enum):
    PHYSICAL = 0
    MAGIC = 1
