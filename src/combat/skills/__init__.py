from combat.skills.skill import Skill
from combat.skills.types import SkillEffect, SkillType

# class Example(Skill):

#     def __init__(self):
#         super().__init__(
#             name="Example Skill",
#             type=SkillType.EXAMPLE,
#             description="Example description",
#             information="Example information",
#             damage_type=DamageType.PHYSICAL,
#             cooldown=60,
#             base_value=1,
#             hits=1,
#         )

# Base skills


class NormalAttack(Skill):

    def __init__(self):
        super().__init__(
            name="Normal Attack",
            type=SkillType.NORMAL_ATTACK,
            description="You perform a swing with your weapon.",
            information="This is the most basic attack you can use. Comes with physical weapons.",
            skill_effect=SkillEffect.PHYSICAL_DAMAGE,
            cooldown=0,
            base_value=1,
        )


class HeavyAttack(Skill):

    def __init__(self):
        super().__init__(
            name="Heavy Attack",
            type=SkillType.HEAVY_ATTACK,
            description="You perform a forceful strike with your weapon.",
            information="Your other basic weapon skill that comes with physical weapons.",
            skill_effect=SkillEffect.PHYSICAL_DAMAGE,
            cooldown=2,
            base_value=4,
        )


class MagicAttack(Skill):

    def __init__(self):
        super().__init__(
            name="Magic Attack",
            type=SkillType.MAGIC_ATTACK,
            description="You perform a basic magical blast with your weapon.",
            information="Your basic magical attack skill. Comes with magical weapons.",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            cooldown=0,
            base_value=2,
        )


# Special Skills


# Enemy Skills


class DeezNuts(Skill):

    def __init__(self):
        super().__init__(
            name="Deez Nuts",
            type=SkillType.DEEZ_NUTS,
            description="He Slaps you with his mighty stick and forces his nuts into your mouth.",
            information="",
            skill_effect=SkillEffect.PHYSICAL_DAMAGE,
            cooldown=0,
            base_value=2,
            hits=1,
        )
