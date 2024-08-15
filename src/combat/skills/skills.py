from combat.skills.skill import BaseSkill
from combat.skills.status_effect import SkillStatusEffect
from combat.skills.types import (
    SkillEffect,
    SkillTarget,
    SkillType,
    StatusEffectApplication,
    StatusEffectType,
)

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


class TapeAttack(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Tape Attack",
            skill_type=SkillType.TAPE_ATTACK,
            description="You throw out your tape and quickly retract it, inflicting deep, bleeding wounds on your enemies.",
            information="Weapon skill unique to the Tape Measure item. Causes 4 stacks of bleeding with each hit.",
            skill_effect=SkillEffect.PHYSICAL_DAMAGE,
            cooldown=0,
            base_value=1.5,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.BLEED,
                    2,
                    StatusEffectApplication.ATTACK_VALUE,
                )
            ],
            droppable=False,
            image_url="https://i.imgur.com/cw1aPuB.jpeg",
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
            description="Heal yourself for a small amount. Also cleanses bleeding and poison.",
            information="",
            skill_effect=SkillEffect.HEALING,
            cooldown=0,
            base_value=0.3,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.CLEANSE,
                    1,
                )
            ],
            stacks=1,
            uniques=[SkillType.SMELLING_SALT],
            reset_after_encounter=True,
            default_target=SkillTarget.SELF,
            image_url="https://i.imgur.com/AH7NRhc.png",
        )


class SecondHeart(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Second Heart",
            skill_type=SkillType.SECOND_HEART,
            description=(
                "You gain a second heart, healing yourself for a moderate amount at the same time. "
                "The second heart will protect you from the next killing blow, leaving you at 1 hp instead."
            ),
            information="",
            skill_effect=SkillEffect.HEALING,
            cooldown=5,
            min_level=4,
            base_value=0.5,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.DEATH_PROTECTION,
                    1,
                ),
                SkillStatusEffect(
                    StatusEffectType.CLEANSE,
                    1,
                ),
            ],
            stacks=2,
            default_target=SkillTarget.SELF,
            image_url="https://i.imgur.com/LQvjQbL.png",
        )


class FamilyPizza(BaseSkill):

    def __init__(self):
        super().__init__(
            name="The Last Family Pizza",
            skill_type=SkillType.FAMILY_PIZZA,
            description="Share this blessed meal with your entire party, restoring a moderate amount of health for everyone.",
            information="",
            skill_effect=SkillEffect.HEALING,
            cooldown=5,
            min_level=3,
            base_value=0.35,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.CLEANSE,
                    1,
                )
            ],
            stacks=2,
            aoe=True,
            reset_after_encounter=False,
            default_target=SkillTarget.SELF,
            image_url="https://i.imgur.com/2QbwSA4.png",
            author="Lusa",
        )


class LooksMaxxing(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Looksmaxxing",
            skill_type=SkillType.LOOKSMAXXING,
            description=(
                "Shh, can't talk. Im mewing. "
                "Your efforts grant you 5 turns of moderate health gain over time."
            ),
            information="",
            skill_effect=SkillEffect.HEALING,
            cooldown=5,
            # min_level=4,
            min_level=5,
            base_value=0.15,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.HEAL_OVER_TIME,
                    5,
                    StatusEffectApplication.ATTACK_VALUE,
                ),
                SkillStatusEffect(
                    StatusEffectType.CLEANSE,
                    1,
                ),
            ],
            stacks=5,
            aoe=False,
            reset_after_encounter=False,
            default_target=SkillTarget.SELF,
            image_url="https://i.imgur.com/kyYqGkl.png",
            author="Lusa",
        )


class HolyGangSigns(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Holy Gang Signs",
            skill_type=SkillType.HOLY_GANG_SIGNS,
            description=(
                "You show off the dope new gang signs you learned at church school. "
                "Your buddies are not impressed, but at least you lighten the mood. Everyone gains a minor "
                "heal over time effect for 5 rounds."
            ),
            information="",
            skill_effect=SkillEffect.HEALING,
            cooldown=5,
            min_level=5,
            base_value=0.08,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.HEAL_OVER_TIME,
                    5,
                    StatusEffectApplication.ATTACK_VALUE,
                ),
                SkillStatusEffect(
                    StatusEffectType.CLEANSE,
                    1,
                ),
            ],
            stacks=2,
            aoe=True,
            weight=40,
            reset_after_encounter=False,
            default_target=SkillTarget.SELF,
            image_url="https://i.imgur.com/KoclK4q.png",
            author="Lusa",
        )


class FineAss(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Fine Ass",
            skill_type=SkillType.FINE_ASS,
            description=(
                "You worked hard for that fine piece of meat and you're not afraid to show it! "
                "As you draw blank you bless your group with increased damage on the next two turns."
            ),
            information="Idk stuns your opponent or something, i just wanted to draw ass - Lusa",
            skill_effect=SkillEffect.BUFF,
            cooldown=5,
            min_level=3,
            base_value=15,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.INSPIRED,
                    2,
                    StatusEffectApplication.ATTACK_VALUE,
                )
            ],
            stacks=2,
            aoe=True,
            reset_after_encounter=False,
            uniques=[SkillType.NOT_SO_FINE_ASS],
            default_target=SkillTarget.SELF,
            image_url="https://i.imgur.com/wWYtgye.png",
            author="Lusa",
        )


class SliceAndDice(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Slice and Dice",
            skill_type=SkillType.SLICE_N_DICE,
            description="You inflict deep cuts that make the enemy bleed for 3 rounds.",
            information="",
            skill_effect=SkillEffect.PHYSICAL_DAMAGE,
            cooldown=3,
            min_level=2,
            base_value=2.5,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.BLEED,
                    3,
                    StatusEffectApplication.ATTACK_VALUE,
                )
            ],
            stacks=5,
            reset_after_encounter=False,
            image_url="https://i.imgur.com/58ldGRq.png",
            author="Lusa",
        )


class BloodRage(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Karen Rage",
            skill_type=SkillType.BLOOD_RAGE,
            description="Your coupons expired last month and your opponent has the audacity to follow policy laws! UNACCEPTABLE!! Your next 4 attacks cause bleeding.",
            information="",
            skill_effect=SkillEffect.NEUTRAL_DAMAGE,
            cooldown=6,
            base_value=1,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.RAGE,
                    4,
                    self_target=True,
                )
            ],
            stacks=3,
            min_level=3,
            weight=50,
            reset_after_encounter=False,
            uniques=[SkillType.WAR_RAGE],
            image_url="https://i.imgur.com/gQeNSR7.png",
            author="Lusa",
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
            base_value=5,
            stacks=3,
            reset_after_encounter=False,
            image_url="https://i.imgur.com/JNNbXJa.png",
        )


class PhysicalMissile(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Physical Missile",
            skill_type=SkillType.PHYSICAL_MISSILE,
            description="Shoots three physical projectiles at the enemy.",
            information="",
            skill_effect=SkillEffect.PHYSICAL_DAMAGE,
            cooldown=4,
            base_value=1.5,
            stacks=5,
            hits=3,
            min_level=2,
            reset_after_encounter=False,
            image_url="https://i.imgur.com/RLl8thA.png",
            author="Lusa",
        )


class PocketSand(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Pocket Sand",
            skill_type=SkillType.POCKET_SAND,
            description="Blinds opponent for two rounds, making them likely to miss their attack.",
            information="Some attacks are unaffected.",
            skill_effect=SkillEffect.NEUTRAL_DAMAGE,
            cooldown=4,
            base_value=1,
            min_level=2,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.BLIND,
                    2,
                )
            ],
            stacks=2,
            reset_after_encounter=False,
            image_url="https://i.imgur.com/JNvyMTt.png",
            author="Lusa",
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
            base_value=7.5,
            stacks=2,
            weight=50,
            reset_after_encounter=False,
            image_url="https://i.imgur.com/tzbLY8h.png",
        )


class PartyDrugs(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Party Drugs",
            skill_type=SkillType.PARTY_DRUGS,
            description=(
                "This stuff will make you taste colours and see things you cant even imagine when sober! "
                "You take a hit and immediately fire a purple-green beam of magical vomit at your enemy. "
                "You are high for the next 3 turns."
            ),
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            cooldown=6,
            status_effects=[
                SkillStatusEffect(StatusEffectType.HIGH, 3, self_target=True)
            ],
            # min_level=4,
            min_level=5,
            base_value=6,
            stacks=3,
            reset_after_encounter=False,
            image_url="https://i.imgur.com/M4P2k4J.png",
        )


class MagicMissile(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Magic Missile",
            skill_type=SkillType.MAGIC_MISSILE,
            description="Shoots three magical projectiles at the enemy.",
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            cooldown=4,
            base_value=1.5,
            stacks=5,
            min_level=2,
            hits=3,
            reset_after_encounter=False,
            image_url="https://i.imgur.com/NnNfa5U.png",
            author="Lusa",
        )


class SpectralHand(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Spectral Claw",
            skill_type=SkillType.SPECTRAL_HAND,
            description=(
                "You summon a spectral claw that mimics your own movements, allowing you "
                "to strike multiple times in quick succession. The magic is a bit unstable and "
                "will inflict random status effects on the enemy."
            ),
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            cooldown=5,
            base_value=1,
            hits=5,
            stacks=5,
            min_level=5,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.RANDOM,
                    1,
                    StatusEffectApplication.ATTACK_VALUE,
                )
            ],
            image_url="https://i.imgur.com/s1tXlJB.png",
            author="Lusa",
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


class GarlicBreath(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Garlic Breath",
            skill_type=SkillType.GARLIC_BREATH,
            description="His breath smells so bad that your eye sight becomes blurry.",
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            cooldown=0,
            base_value=1,
            hits=1,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.BLIND,
                    1,
                )
            ],
            aoe=True,
            droppable=False,
            image_url="https://i.imgur.com/41JkjRY.png",
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
            skill_effect=SkillEffect.NOTHING,
            cooldown=0,
            base_value=0,
            hits=1,
            droppable=False,
            image_url="https://i.imgur.com/ryWhWTP.png",
        )


class BigHonk(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Big Honk",
            skill_type=SkillType.BIG_HONK,
            description="Its glass shattering screeches destroy your eardrums. making you bleed for two turns",
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            cooldown=0,
            base_value=1,
            hits=1,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.BLEED,
                    2,
                    StatusEffectApplication.ATTACK_VALUE,
                )
            ],
            aoe=True,
            droppable=False,
            image_url="https://i.imgur.com/xUdZUmt.png",
        )


class AssBite(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Ass Bite",
            skill_type=SkillType.ASS_BITE,
            description="The furious beast buries its beak into your butt cheek.",
            information="",
            skill_effect=SkillEffect.PHYSICAL_DAMAGE,
            cooldown=2,
            base_value=3,
            hits=1,
            aoe=False,
            droppable=False,
            image_url="https://i.imgur.com/AyJniv9.png",
        )


class AroundTheWorld(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Yo Mama Joke",
            skill_type=SkillType.AROUND_THE_WORLD,
            description="",
            information="",
            skill_effect=SkillEffect.PHYSICAL_DAMAGE,
            cooldown=0,
            base_value=2,
            hits=1,
            aoe=True,
            droppable=False,
            image_url="https://i.imgur.com/RmeyRjX.png",
        )


class Sit(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Crashing Down",
            skill_type=SkillType.SIT,
            description="Your mom is exhausted from all the jokes and needs to sit down. On you.",
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            cooldown=2,
            initial_cooldown=2,
            base_value=5,
            hits=1,
            aoe=True,
            droppable=False,
            image_url="https://i.imgur.com/4d9ac5X.png",
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
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.BLEED,
                    2,
                    StatusEffectApplication.ATTACK_VALUE,
                )
            ],
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
            base_value=7,
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
            description="He tips his hat with a smoothness only possible with hundreds of hours of practice.",
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


class ItHurts(BaseSkill):

    def __init__(self):
        super().__init__(
            name="It Hurts!",
            skill_type=SkillType.IT_HURTS,
            description="You feel it festering and convulsing, almost as if it had a mind of its own.",
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            cooldown=0,
            base_value=2,
            hits=2,
            droppable=False,
            image_url="https://i.imgur.com/7zlTlbv.png",
            author="Lusa",
        )


class Pop(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Pop!",
            skill_type=SkillType.POP,
            description="The pressure suddenly releases, exploding into a huge mess of boiling puss.",
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            cooldown=2,
            initial_cooldown=2,
            base_value=7,
            hits=1,
            aoe=True,
            droppable=False,
            image_url="https://i.imgur.com/4z9Wo4G.png",
            author="Lusa",
        )


class Hold(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Shaking",
            skill_type=SkillType.HOLD,
            description="The mushroom is shaking and beaming with more intensity. It almost seems like he's swelling up.",
            information="",
            skill_effect=SkillEffect.NOTHING,
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
            modifiable=False,
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
            skill_effect=SkillEffect.NOTHING,
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
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.BLEED,
                    2,
                    StatusEffectApplication.ATTACK_VALUE,
                )
            ],
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


class StanceOff(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Stance Off",
            skill_type=SkillType.STANCE_OFF,
            description="With this one simple trick he can wipe the entire party!",
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            cooldown=2,
            base_value=3,
            hits=1,
            status_effects=[
                SkillStatusEffect(StatusEffectType.RAGE_QUIT, 1, self_target=True)
            ],
            aoe=True,
            droppable=False,
            image_url="https://i.imgur.com/iQgErzQ.png",
            author="Lusa",
        )


class YPYT(BaseSkill):

    def __init__(self):
        super().__init__(
            name="YPYT",
            skill_type=SkillType.YPYT,
            description="The audacity! Did you really think you could run ahead and pull on your own?",
            information="",
            skill_effect=SkillEffect.PHYSICAL_DAMAGE,
            cooldown=0,
            base_value=2,
            initial_cooldown=1,
            hits=2,
            aoe=False,
            droppable=False,
            image_url="https://i.imgur.com/or3sdhr.png",
            author="Lusa",
        )


class DeadTank(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Asmon Swap",
            skill_type=SkillType.DEAD_TANK,
            description="Oops teehee, looks like someone forgot to mitigate. (Or didnt know what that means in the first place)",
            information="",
            skill_effect=SkillEffect.PHYSICAL_DAMAGE,
            cooldown=3,
            base_value=8,
            initial_cooldown=1,
            hits=1,
            aoe=False,
            droppable=False,
            image_url="https://i.imgur.com/m5Hm98i.png",
            author="Lusa",
        )


class HairPull(BaseSkill):

    def __init__(self):
        super().__init__(
            name="I'm in Charge.",
            skill_type=SkillType.HAIR_PULL,
            description=(
                "He grabs your hair and pulls you closer. 'Do not resist. I will reward you.'"
                " you hear him say in his deep, masculine voice. You are too flustered"
                " to do anything that would harm him on your next turn."
            ),
            information="",
            skill_effect=SkillEffect.NEUTRAL_DAMAGE,
            cooldown=1,
            base_value=1,
            initial_cooldown=1,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.FLUSTERED,
                    1,
                )
            ],
            hits=1,
            max_targets=1,
            aoe=False,
            droppable=False,
            image_url="https://i.imgur.com/UyVqfip.png",
            author="Lusa",
        )


class Whip(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Stay in line.",
            skill_type=SkillType.WHIP,
            description=(
                "He deems you in need of punishment and lashes out with his big, long whip."
            ),
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            cooldown=0,
            base_value=0.5,
            hits=1,
            aoe=True,
            droppable=False,
            image_url="https://i.imgur.com/tYCz3eB.png",
            author="Lusa",
        )


class Belt(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Now you've done it.",
            skill_type=SkillType.BELT,
            description=(
                "Daddy had enough of you. With a single smooth movement he removes his belt, "
                "leaving his crotch dangerously exposed. Then he starts swinging."
            ),
            information="",
            skill_effect=SkillEffect.PHYSICAL_DAMAGE,
            initial_cooldown=3,
            cooldown=3,
            base_value=1.5,
            hits=5,
            aoe=False,
            droppable=False,
            image_url="https://i.imgur.com/jDVxvn7.png",
            author="Lusa",
        )


class TieYouUp(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Know your place.",
            skill_type=SkillType.TIE_YOU_UP,
            description=(
                "Oh no, Daddy caught you! He ties up your hands and "
                "forces you down to the floor. For 3 turns your attacks have a 50% "
                "chance to miss."
            ),
            information="",
            skill_effect=SkillEffect.NEUTRAL_DAMAGE,
            cooldown=2,
            initial_cooldown=1,
            base_value=1,
            hits=1,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.BLIND,
                    3,
                )
            ],
            max_targets=1,
            aoe=False,
            droppable=False,
            image_url="https://i.imgur.com/pOkokRc.png",
            author="Lusa",
        )


class ButtSlap(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Behave.",
            skill_type=SkillType.BUTT_SLAP,
            description=(
                "Daddys hand slams into your butt cheek with the force of a wild bear, leaving "
                "a surprisingly detailed red imprint behind.\nThe sound of the impact can be heard from "
                "miles away, followed by noises you didnt even know you were capable of."
            ),
            information="",
            skill_effect=SkillEffect.PHYSICAL_DAMAGE,
            cooldown=2,
            base_value=2,
            hits=1,
            aoe=False,
            droppable=False,
            image_url="https://i.imgur.com/RUiAaQ8.png",
            author="Lusa",
        )


class OnYourKnees(BaseSkill):

    def __init__(self):
        super().__init__(
            name="On your knees.",
            skill_type=SkillType.ON_YOUR_KNEES,
            description=(
                "You are unable to resist Daddys command. As you look up to his face, "
                "he continues: 'Close your eyes and open wide.' \n"
                "You are not quite sure what happened next, but you feel like you could use "
                "a shower after he finished."
            ),
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            cooldown=4,
            base_value=2,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.BLEED,
                    3,
                    StatusEffectApplication.ATTACK_VALUE,
                )
            ],
            hits=1,
            max_targets=1,
            aoe=False,
            droppable=False,
            image_url="https://i.imgur.com/7NIpn6i.png",
            author="Lusa",
        )


class FearSkill(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Fear",
            skill_type=SkillType.FEAR,
            description="Your despair increases as you look at it.",
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            cooldown=0,
            base_value=1,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.FEAR,
                    1,
                )
            ],
            hits=1,
            aoe=True,
            droppable=False,
            image_url="https://i.imgur.com/73CgqTW.png",
            author="Lusa",
        )


class Feasting(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Feasting",
            skill_type=SkillType.FEASTING,
            description="It opens its jaws and consumes your fear.",
            information="",
            skill_effect=SkillEffect.PHYSICAL_DAMAGE,
            cooldown=2,
            initial_cooldown=2,
            base_value=3,
            hits=1,
            aoe=False,
            droppable=False,
            image_url="https://i.imgur.com/oikAU23.png",
            author="Lusa",
        )


class FatAss(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Fat Ass",
            skill_type=SkillType.FAT_ASS,
            description="Eli doesn't care. He got a big dumpy and uses it to crush you. Oh and youre blind.",
            information="",
            skill_effect=SkillEffect.PHYSICAL_DAMAGE,
            cooldown=3,
            initial_cooldown=1,
            base_value=7,
            hits=1,
            aoe=False,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.BLIND,
                    3,
                )
            ],
            droppable=False,
            image_url="https://i.imgur.com/XJZAq46.png",
            author="Lusa",
        )


class CatScreech(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Screech",
            skill_type=SkillType.CAT_SCREECH,
            description="Eli lets you know he is not satisfied. He never is.",
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            cooldown=2,
            base_value=2,
            hits=1,
            aoe=True,
            droppable=False,
            image_url="https://i.imgur.com/z3A1C59.png",
            author="Lusa",
        )


class OhLawdHeComin(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Oh Lawd He Comin",
            skill_type=SkillType.OH_LAWD_HE_COMIN,
            description="You feel the earth shake as Eli starts to set his immense mass in motion.",
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            cooldown=0,
            base_value=1,
            hits=1,
            aoe=True,
            droppable=False,
            image_url="https://i.imgur.com/AHKl27r.png",
            author="Lusa",
        )


class HomelessPleading(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Pleading",
            skill_type=SkillType.HOMELESS_PLEADING,
            description="She looks at you with her deeply sad eyes filled with pain and suffering.",
            information="",
            skill_effect=SkillEffect.NOTHING,
            cooldown=0,
            base_value=0,
            hits=1,
            aoe=False,
            droppable=False,
            image_url="https://i.imgur.com/n9opGtQ.png",
            author="Lusa",
        )


class HomelessBegging(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Begging",
            skill_type=SkillType.HOMELESS_BEGGING,
            description="She opens her hands towards you and asks for a couple of beans.",
            information="",
            skill_effect=SkillEffect.NOTHING,
            cooldown=1,
            base_value=1,
            hits=1,
            aoe=False,
            droppable=False,
            image_url="https://i.imgur.com/u6tWk2c.png",
            author="Lusa",
        )


class ThunderCrack(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Thunder Crack",
            skill_type=SkillType.THUNDER_CRACK,
            description="Bolts of lightning hit you like a truck. Or like a nice bong rip. You are unsure.",
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            cooldown=0,
            base_value=1,
            hits=1,
            aoe=True,
            droppable=False,
            image_url="https://i.imgur.com/VjfI6u2.png",
            author="Lusa",
        )


class UsedNeedles(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Used Needles",
            skill_type=SkillType.USED_NEEDLES,
            description="You scared it and it throws a bunch of used needles at your face. You start feeling a bit dizzy as they hit you.",
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            cooldown=1,
            base_value=1,
            hits=4,
            aoe=False,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.HIGH,
                    1,
                )
            ],
            droppable=False,
            image_url="https://i.imgur.com/MMdiHRv.png",
            author="Lusa",
        )


class TimeToSlice(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Time to Slice",
            skill_type=SkillType.TIME_TO_SLICE,
            description="Playtime is over, honey. Time to die.",
            information="",
            skill_effect=SkillEffect.PHYSICAL_DAMAGE,
            cooldown=1,
            initial_cooldown=2,
            base_value=2,
            hits=3,
            aoe=False,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.BLEED,
                    1,
                    StatusEffectApplication.ATTACK_VALUE,
                )
            ],
            droppable=False,
            image_url="https://i.imgur.com/1sw80nK.png",
            author="Lusa",
        )


class StepOnYou(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Steps on You",
            skill_type=SkillType.STEP_ON_YOU,
            description=(
                "She commands you to lay down infront of her and you oblige, unable to resist. "
                "Then she raises her heel and stomps down on your head. You are under Mommy's spell and "
                "unable to hurt her on your next turn."
            ),
            information="",
            skill_effect=SkillEffect.PHYSICAL_DAMAGE,
            cooldown=2,
            initial_cooldown=0,
            base_value=5,
            hits=1,
            aoe=False,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.FLUSTERED,
                    1,
                )
            ],
            droppable=False,
            image_url="https://i.imgur.com/NkkAnTD.png",
            author="Lusa",
        )


class Choke(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Nightmare Chokehold",
            skill_type=SkillType.CHOKE,
            description=(
                "She grabs your throat and chokes you until you almost pass out. "
                "You hear a crazy giggle as she watches you struggle for air. "
                "Your mind will be foggy for one turn, randomly modifying your next action."
            ),
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            cooldown=0,
            initial_cooldown=1,
            base_value=1,
            hits=1,
            aoe=False,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.HIGH,
                    1,
                )
            ],
            droppable=False,
            image_url="https://i.imgur.com/XJhXZ7N.png",
            author="Lusa",
        )


class HoeKnees(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Hoe-Knees",
            skill_type=SkillType.HOE_KNEES,
            description=("These knees are surprisingly pointy."),
            information="",
            skill_effect=SkillEffect.PHYSICAL_DAMAGE,
            cooldown=0,
            base_value=3,
            hits=1,
            aoe=False,
            droppable=False,
            image_url="https://i.imgur.com/rUjLLHK.png",
            author="Lusa",
        )


class HoeShank(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Hoe-Shank",
            skill_type=SkillType.HOE_SHANK,
            description=(
                "The hoe pulls out a scary looking hunting knive and goes to town on your guts."
            ),
            information="",
            skill_effect=SkillEffect.PHYSICAL_DAMAGE,
            cooldown=1,
            base_value=2,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.BLEED,
                    3,
                    StatusEffectApplication.ATTACK_VALUE,
                )
            ],
            hits=2,
            aoe=False,
            droppable=False,
            image_url="https://i.imgur.com/Mb4fIEV.png",
            author="Lusa",
        )


class HoeSpread(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Hoe-Spread",
            skill_type=SkillType.HOE_SPREAD,
            description=(
                "Her ultimate move, she spreads her legs and releases the stench of decades of "
                "abuse and neglect on you. You are poisoned for two turns, inflicting a portion of your dealt "
                "damage back on yourself."
            ),
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            cooldown=2,
            base_value=1,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.POISON,
                    2,
                )
            ],
            hits=1,
            aoe=True,
            droppable=False,
            image_url="https://i.imgur.com/JLv30Mg.png",
            author="Lusa",
        )


class Devour(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Devour",
            skill_type=SkillType.DEVOUR,
            description=("The mimic opens its jaws and chomps down on you."),
            information="",
            skill_effect=SkillEffect.PHYSICAL_DAMAGE,
            cooldown=0,
            base_value=5,
            hits=1,
            aoe=False,
            droppable=False,
            image_url="https://i.imgur.com/ZCaSqPK.png",
            author="Lusa",
        )


class LootSpit(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Loot Spit",
            skill_type=SkillType.LOOT_SPIT,
            description=(
                "It belches out a load of random items and weapons from its belly which are now heading your way. "
                "Some of them might inflict random status effects."
            ),
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            cooldown=1,
            base_value=2,
            hits=4,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.RANDOM,
                    1,
                    StatusEffectApplication.ATTACK_VALUE,
                )
            ],
            aoe=False,
            droppable=False,
            image_url="https://i.imgur.com/azlOtJ1.png",
            author="Lusa",
        )


class Wedgie(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Wedgie",
            skill_type=SkillType.WEDGIE,
            description=(
                "He sneaks up on you, grabs you by the underwear and pulls as hard as he can! "
                "You feel your crotch getting warm and wet. Did you pee your pants? Oh nevermind, its just blood."
            ),
            information="",
            skill_effect=SkillEffect.PHYSICAL_DAMAGE,
            cooldown=2,
            initial_cooldown=0,
            base_value=7,
            hits=1,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.BLEED,
                    6,
                    StatusEffectApplication.ATTACK_VALUE,
                )
            ],
            aoe=False,
            droppable=False,
            image_url="https://i.imgur.com/DjSROSI.png",
            author="Lusa",
        )


class KneeKick(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Knee Kick",
            skill_type=SkillType.KNEE_KICK,
            description=(
                "OW! Your kneecaps! This is gonna hurt for a while. You start to cry."
            ),
            information="",
            skill_effect=SkillEffect.PHYSICAL_DAMAGE,
            cooldown=0,
            initial_cooldown=1,
            base_value=3,
            hits=1,
            aoe=False,
            droppable=False,
            image_url="https://i.imgur.com/TMVdgZt.png",
            author="Lusa",
        )


class HaHa(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Ha Ha!",
            skill_type=SkillType.HA_HA,
            description=(
                "He points at you and laughs. Look at how pathetic you are. What a looser!"
            ),
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            cooldown=0,
            base_value=2,
            hits=1,
            aoe=True,
            droppable=False,
            image_url="https://i.imgur.com/nQFkAQn.png",
            author="Lusa",
        )


class ChefsKnive(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Chef's Knive",
            skill_type=SkillType.CHEFS_KNIVE,
            description=(
                "The Bonterry stabs you with its knive. "
                "Its what it does best and it hurts a lot."
            ),
            information="",
            skill_effect=SkillEffect.PHYSICAL_DAMAGE,
            cooldown=0,
            base_value=1.5,
            hits=1,
            aoe=False,
            droppable=False,
            image_url="https://i.imgur.com/9VoHmE5.png",
            author="Lusa",
        )


class Karma(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Karma",
            skill_type=SkillType.KARMA,
            description=(
                "the souls of @ fallen bonterries drives bonterry kings grudge. "
                "He stabs you with no remorse."
            ),
            information="",
            skill_effect=SkillEffect.PHYSICAL_DAMAGE,
            cooldown=3,
            initial_cooldown=1,
            base_value=1,
            hits=1,
            aoe=False,
            droppable=False,
            image_url="https://i.imgur.com/kNETgLS.png",
            author="Lusa",
        )


class Gloom(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Gloom",
            skill_type=SkillType.GLOOM,
            description=(
                "Bonterry king wants you to suffer and despair, just like his friends did."
            ),
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            cooldown=2,
            base_value=3,
            hits=1,
            aoe=True,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.BLEED,
                    3,
                    StatusEffectApplication.ATTACK_VALUE,
                ),
                SkillStatusEffect(
                    StatusEffectType.BLIND,
                    1,
                ),
            ],
            droppable=False,
            image_url="https://i.imgur.com/g2azYst.png",
            author="Lusa",
        )


class Sparkles(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Sparkles",
            skill_type=SkillType.SPARKLES,
            description=(
                "The fairy swooshes around your heads and fills the air with bright sparkes. "
                "The brightness hurts your eyes!"
            ),
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            cooldown=20,
            base_value=1,
            hits=1,
            aoe=True,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.EVASIVE,
                    1,
                    StatusEffectApplication.MANUAL_VALUE,
                    application_value=25,
                    self_target=True,
                ),
                SkillStatusEffect(
                    StatusEffectType.BLIND,
                    1,
                ),
            ],
            droppable=False,
            image_url="https://i.imgur.com/OVhMx6V.png",
            author="Lusa",
        )


class GetFrogged(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Get Frogged",
            skill_type=SkillType.GET_FROGGED,
            description=(
                "The fairy turns you into a frog as she giggles quietly and bounces around in the air. "
                "Your actions have a 50% chance to fail for the next two turns."
            ),
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            cooldown=2,
            initial_cooldown=1,
            base_value=3,
            hits=1,
            aoe=False,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.FROGGED,
                    2,
                ),
            ],
            droppable=False,
            image_url="https://i.imgur.com/OaGk8cF.png",
            author="Lusa",
        )


class Whispering(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Whispering",
            skill_type=SkillType.WHISPERING,
            description=(
                "With a soft giggle, the fairy whispers something incredibly cringe into your ear. "
                "It is bad enough to stun you for two turns."
            ),
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            cooldown=3,
            initial_cooldown=2,
            base_value=3,
            hits=1,
            aoe=False,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.STUN,
                    2,
                ),
            ],
            droppable=False,
            image_url="https://i.imgur.com/Ji8Ww7d.png",
            author="Lusa",
        )


class FollowMe(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Follow Me!",
            skill_type=SkillType.FOLLOW_ME,
            description=(
                "The Fairies magical voice is leading you deeper and deeper into the woods. "
                "Unable to resist, you walk into a monster nest."
            ),
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            initial_cooldown=1,
            cooldown=0,
            base_value=2,
            hits=1,
            aoe=True,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.BLEED,
                    3,
                    StatusEffectApplication.ATTACK_VALUE,
                ),
            ],
            droppable=False,
            image_url="https://i.imgur.com/odiIUnp.png",
            author="Lusa",
        )
