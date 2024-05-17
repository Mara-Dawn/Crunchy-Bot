from combat.skills.skill import Skill
from combat.skills.types import DamageType, SkillType

# class Example(Skill):

#     def __init__(self):
#         super().__init__(
#             name="Example Skill",
#             type=SkillType.EXAMPLE,
#             description="Example description",
#             information="Example information",
#             damage_type=DamageType.PHYSICAL,
#             cooldown=60,
#         )


class NormalAttack(Skill):

    def __init__(self):
        super().__init__(
            name="Normal Attack",
            type=SkillType.NORMAL_ATTACK,
            description="Attack the enemy with your weapon.",
            information="This is the most basic attack you can use. Comes with physical weapons.",
            damage_type=DamageType.PHYSICAL,
            cooldown=15,
        )


class HeavyAttack(Skill):

    def __init__(self):
        super().__init__(
            name="Heavy Attack",
            type=SkillType.HEAVY_ATTACK,
            description="You perform a strong swing with your weapon.",
            information="Your other basic weapon skill that comes with physical weapons.",
            damage_type=DamageType.PHYSICAL,
            cooldown=60 * 5,
        )


class MagicAttack(Skill):

    def __init__(self):
        super().__init__(
            name="Magic Attack",
            type=SkillType.HEAVY_ATTACK,
            description="You perform a basic magical blast with your weapon.",
            information="Your basic magical attack skill. Comes with magical weapons.",
            damage_type=DamageType.MAGIC,
            cooldown=30,
        )
