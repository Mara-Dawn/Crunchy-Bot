from combat.skills.types import DamageType, SkillType


class Skill:

    def __init__(
        self,
        name: str,
        type: SkillType,
        description: str,
        information: str,
        damage_type: DamageType,
        cooldown: int,
    ):
        self.name = name
        self.type = type
        self.description = description
        self.information = information
        self.damage_type = damage_type
        self.cooldown = cooldown
