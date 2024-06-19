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
            base_value=1.5,
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
            base_value=3,
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
            base_value=0.3,
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
            image_url="https://i.imgur.com/JNNbXJa.png",
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


class MilkShot(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Milky Shower",
            skill_type=SkillType.MILK_SHOWER,
            description="Would fill your belly faster than Mentos x Coke. Don't munch on it",
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            cooldown=0,
            base_value=1,
            hits=1,
            aoe=True,
            droppable=False,
            image_url="https://i.imgur.com/60yGeAA.jpeg",
        )


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


class ToeStub(BaseSkill):

    def __init__(self):
        super().__init__(
            name="OUCH!",
            skill_type=SkillType.TOE_STUB,
            description="You stub your toe on one of its legs.",
            information="",
            skill_effect=SkillEffect.PHYSICAL_DAMAGE,
            cooldown=3,
            base_value=3,
            hits=1,
            aoe=True,
            droppable=False,
            image_url="https://i.imgur.com/MzFpvsV.png",
        )


class LookingGood(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Lookin' Good",
            skill_type=SkillType.LOOKING_GOOD,
            description="You angrily look at the table that just hurt you. Huh, it's a pretty nice table. Too bad it has to die.",
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            cooldown=0,
            base_value=0,
            hits=1,
            droppable=False,
            image_url="https://i.imgur.com/ryWhWTP.png",
        )


class AnkleAim(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Aim for the Ankle",
            skill_type=SkillType.ANKLE_AIM,
            description="It knows your weak point. Next time, bring walking boots.",
            information="",
            skill_effect=SkillEffect.PHYSICAL_DAMAGE,
            cooldown=0,
            base_value=1,
            hits=2,
            aoe=False,
            droppable=False,
            image_url="https://i.imgur.com/hPF4gsn.jpeg",
            author="Klee",
        )


class DownHill(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Run'em down the Hill",
            skill_type=SkillType.DOWN_HILL,
            description="You are lucky if you fall off half way.🌳👈🛒",
            information="",
            skill_effect=SkillEffect.PHYSICAL_DAMAGE,
            cooldown=2,
            base_value=10,
            hits=1,
            aoe=False,
            initial_cooldown=1,
            droppable=False,
            image_url="https://i.imgur.com/xN1gcXh.jpeg",
            author="Klee",
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


class Puke(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Puke",
            skill_type=SkillType.PUKE,
            description="You’re not sure if it’s actually puke. It’s very brown",
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            cooldown=0,
            base_value=2,
            hits=1,
            aoe=True,
            droppable=False,
            image_url="https://i.imgur.com/sj1I0Q1.jpeg",
            author="Klee",
        )


class TailWhip(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Tail Whip",
            skill_type=SkillType.TAIL_WHIP,
            description="But where is the tail? (You don’t want to know)",
            information="",
            skill_effect=SkillEffect.PHYSICAL_DAMAGE,
            cooldown=1,
            base_value=2,
            hits=2,
            droppable=False,
            image_url="https://i.imgur.com/nHvtBi3.jpeg",
            author="Klee",
        )


class Hold(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Shaking",
            skill_type=SkillType.HOLD,
            description="The mushroom is shaking and beaming with more intensity. It almost seems like he's swelling up.",
            information="",
            skill_effect=SkillEffect.PHYSICAL_DAMAGE,
            cooldown=0,
            base_value=0,
            hits=1,
            droppable=False,
            image_url="https://i.imgur.com/4S5sYFg.png",
            author="Lusa",
        )


class Burst(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Happy Time!",
            skill_type=SkillType.BURST,
            description="BOOM! The mushroom explodes in a huge burst of happiness and good feelings!",
            information="",
            skill_effect=SkillEffect.PHYSICAL_DAMAGE,
            cooldown=0,
            base_value=1,
            initial_cooldown=4,
            hits=1,
            aoe=True,
            droppable=False,
            image_url="https://i.imgur.com/dmlFE2t.png",
            author="Lusa",
        )


class Exercise(BaseSkill):

    def __init__(self):
        super().__init__(
            name="BRO-Workout!",
            skill_type=SkillType.EXERCISE,
            description="He loves you - lil damn cutie - he begins to show off his power. Nothing to worry about.",
            information="",
            skill_effect=SkillEffect.PHYSICAL_DAMAGE,
            cooldown=0,
            base_value=0,
            initial_cooldown=0,
            hits=1,
            aoe=False,
            droppable=False,
            image_url="https://i.imgur.com/0kg7AiZ.png",
            author="Franny",
        )


class BroArrows(BaseSkill):

    def __init__(self):
        super().__init__(
            name="BRO-Arrows!",
            skill_type=SkillType.BRO_ARROW,
            description="With Jupiter's arrow but poisoned by broccoli juice, BRO-Coli shows you the highest appreciation",
            information="",
            skill_effect=SkillEffect.PHYSICAL_DAMAGE,
            cooldown=2,
            base_value=1,
            initial_cooldown=1,
            hits=1,
            aoe=True,
            droppable=False,
            image_url="https://i.imgur.com/p3G9ZeB.png",
            author="Franny",
        )


class BroBiotics(BaseSkill):

    def __init__(self):
        super().__init__(
            name="BRO-Biotics!",
            skill_type=SkillType.BRO_FART,
            description="Oops, he must have forgotten to eat veggies and ate too much meat. Just needs some smol relaxation.",
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            cooldown=1,
            base_value=2,
            initial_cooldown=1,
            hits=1,
            aoe=True,
            droppable=False,
            image_url="https://i.imgur.com/yJr6wwC.png",
            author="Franny",
        )


class BroBlast(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Giga Broccoli Smell Attack",
            skill_type=SkillType.BRO_EXTRA_FART,
            description="You hate me? You love me? How about getting showered by my broccoli-smell fart.",
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            cooldown=3,
            base_value=6,
            initial_cooldown=5,
            hits=1,
            aoe=False,
            droppable=False,
            image_url="https://i.imgur.com/TIpBdai.png",
            author="Franny",
        )
