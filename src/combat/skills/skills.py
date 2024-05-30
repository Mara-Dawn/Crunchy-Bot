from combat.gear.types import Rarity
from combat.skills.skill import BaseSkill, Skill
from combat.skills.types import SkillEffect, SkillType

# Base skills


class NormalAttackBase(BaseSkill):

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
        )


class NormalAttack(Skill):
    def __init__(self):
        super().__init__(
            base_skill=NormalAttackBase(),
            rarity=Rarity.NORMAL,
            level=1,
        )


class HeavyAttackBase(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Heavy Attack",
            skill_type=SkillType.HEAVY_ATTACK,
            description="You perform a forceful strike with your weapon.",
            information="Your other basic weapon skill that comes with physical weapons.",
            skill_effect=SkillEffect.PHYSICAL_DAMAGE,
            cooldown=2,
            scaling=4,
        )


class HeavyAttack(Skill):
    def __init__(self):
        super().__init__(
            base_skill=HeavyAttackBase(),
            rarity=Rarity.NORMAL,
            level=1,
        )


class MagicAttackBase(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Magic Attack",
            skill_type=SkillType.MAGIC_ATTACK,
            description="You perform a basic magical blast with your weapon.",
            information="Your basic magical attack skill. Comes with magical weapons.",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            cooldown=0,
            scaling=2,
        )


class MagicAttack(Skill):
    def __init__(self):
        super().__init__(
            base_skill=MagicAttackBase(),
            rarity=Rarity.NORMAL,
            level=1,
        )


# Special Skills


class SecondWind(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Second Wind",
            skill_type=SkillType.SECOND_WIND,
            description="",
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
            description="",
            information="",
            skill_effect=SkillEffect.PHYSICAL_DAMAGE,
            cooldown=5,
            scaling=10,
            stacks=3,
            reset_after_encounter=False,
        )


# Enemy Skills


class EnemySkill(Skill):
    def __init__(self, base_skill: BaseSkill):
        super().__init__(
            base_skill=base_skill,
            rarity=Rarity.NORMAL,
            level=1,
        )


class DeezNuts(EnemySkill):

    def __init__(self):
        base_skill = BaseSkill(
            name="Deez Nuts",
            skill_type=SkillType.DEEZ_NUTS,
            description="He forces his nuts into your mouth.",
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            cooldown=1,
            scaling=2,
            hits=1,
        )
        super().__init__(base_skill)


class Bonk(EnemySkill):

    def __init__(self):
        base_skill = BaseSkill(
            name="Bonk",
            skill_type=SkillType.BONK,
            description="He Slaps you multiple times with his mighty stick.",
            information="",
            skill_effect=SkillEffect.PHYSICAL_DAMAGE,
            cooldown=0,
            scaling=1,
            hits=2,
        )
        super().__init__(base_skill)
