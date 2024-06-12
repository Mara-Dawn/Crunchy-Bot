from combat.skills.skill import BaseSkill
from combat.skills.types import SkillEffect, SkillTarget, SkillType

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
            base_value=1,
            hits=1,
            stacks=None,
            reset_after_encounter=False,
            droppable=False,
            image_url="https://i.imgur.com/B6TuHg3.png",
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
            base_value=1,
            hits=1,
            stacks=None,
            reset_after_encounter=False,
            droppable=False,
            image_url="https://i.imgur.com/najJyC1.png",
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
            base_value=4,
            droppable=False,
            image_url="https://i.imgur.com/1Cf7nVB.png",
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
            base_value=2,
            droppable=False,
            image_url="https://i.imgur.com/RnbJR20.png",
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
            base_value=3,
            stacks=1,
            reset_after_encounter=True,
            default_target=SkillTarget.SELF,
            image_url="https://i.imgur.com/AH7NRhc.png",
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
            base_value=6,
            stacks=3,
            reset_after_encounter=False,
            image_url="https://i.imgur.com/pq1aJsn.png",
        )


class FireBall(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Fire Ball",
            skill_type=SkillType.FIRE_BALL,
            description="A true classic. Extremely powerful and highly effective.",
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            cooldown=10,
            base_value=10,
            stacks=1,
            reset_after_encounter=False,
            image_url="https://i.imgur.com/tzbLY8h.png",
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
            base_value=2,
            hits=1,
            droppable=False,
            image_url="https://i.imgur.com/nfF8ROY.png",
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
            base_value=1,
            hits=2,
            droppable=False,
            image_url="https://i.imgur.com/svYQ8jJ.png",
        )


class MLady(BaseSkill):

    def __init__(self):
        super().__init__(
            name="M'Lady",
            skill_type=SkillType.M_LADY,
            description="He hits you with a lethal dose of cringe",
            information="",
            skill_effect=SkillEffect.PHYSICAL_DAMAGE,
            cooldown=2,
            base_value=4,
            hits=1,
            droppable=False,
            image_url="https://i.imgur.com/JQYWUuW.png",
        )


class FedoraTip(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Tips Fedora",
            skill_type=SkillType.FEDORA_TIP,
            description="He tips his hat with a smoothness only possible with hundrets of hours of practice.",
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            cooldown=0,
            base_value=1,
            hits=1,
            aoe=True,
            droppable=False,
            image_url="https://i.imgur.com/NaRYfaS.png",
        )
