from combat.skills.skill import BaseSkill
from combat.skills.types import SkillEffect, SkillType

# Base skills


class EmptySkill(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Empty",
            skill_type=SkillType.EMPTY,
            description="This skill slot is currently empty.",
            information="",
            skill_effect=SkillEffect.PHYSICAL_DAMAGE,
            cooldown=0,
            scaling=1,
            hits=1,
            stacks=None,
            reset_after_encounter=False,
            droppable=False,
            image="empty.png",
        )


class NormalAttack(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Normal Attack",
            skill_type=SkillType.NORMAL_ATTACK,
            description="You perform a swing with your weapon.",
            information="This is the most basic attack you can use. Comes with physical weapons.",
            skill_effect=SkillEffect.PHYSICAL_DAMAGE,
            cooldown=0,
            scaling=1,
            hits=1,
            stacks=None,
            reset_after_encounter=False,
            droppable=False,
        )


class HeavyAttack(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Heavy Attack",
            skill_type=SkillType.HEAVY_ATTACK,
            description="You perform a forceful strike with your weapon.",
            information="Your other basic weapon skill that comes with physical weapons.",
            skill_effect=SkillEffect.PHYSICAL_DAMAGE,
            cooldown=2,
            scaling=4,
            droppable=False,
        )


class MagicAttack(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Magic Attack",
            skill_type=SkillType.MAGIC_ATTACK,
            description="You perform a basic magical blast with your weapon.",
            information="Your basic magical attack skill. Comes with magical weapons.",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            cooldown=0,
            scaling=2,
            droppable=False,
        )


# Special Skills


class SecondWind(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Second Wind",
            skill_type=SkillType.SECOND_WIND,
            description="Heal yourself for a small amount.",
            information="",
            skill_effect=SkillEffect.HEALING,
            cooldown=0,
            scaling=1,
            stacks=1,
            reset_after_encounter=True,
        )


class GigaBonk(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Giga Bonk",
            skill_type=SkillType.GIGA_BONK,
            description="A MASSIVE swing with your weapon!",
            information="",
            skill_effect=SkillEffect.PHYSICAL_DAMAGE,
            cooldown=5,
            scaling=6,
            stacks=3,
            reset_after_encounter=False,
        )


class FireBall(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Fire Ball",
            skill_type=SkillType.FIRE_BALL,
            description="A true classic. Extremely powerful and highly effective.",
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            cooldown=0,
            scaling=10,
            stacks=1,
            reset_after_encounter=False,
        )


# Enemy Skills


class DeezNuts(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Deez Nuts",
            skill_type=SkillType.DEEZ_NUTS,
            description="He forces his nuts into your mouth.",
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            cooldown=1,
            scaling=2,
            hits=1,
            droppable=False,
        )


class Bonk(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Bonk",
            skill_type=SkillType.BONK,
            description="He Slaps you multiple times with his mighty stick.",
            information="",
            skill_effect=SkillEffect.PHYSICAL_DAMAGE,
            cooldown=0,
            scaling=1,
            hits=2,
            droppable=False,
        )