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
            author="Klee",
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


class FrostAttack(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Beans Frost Attack",
            skill_type=SkillType.FROST_ATTACK,
            description="The frozen bean manifest a small frozen orb and shoot it to the enemy.",
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            cooldown=0,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.FROST,
                    1,
                )
            ],
            base_value=1.5,
            droppable=False,
            image_url="https://i.imgur.com/QRs4GXX.png",
            author="Waldheld",
        )


class FrozenDrops(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Beans Frozen Drops",
            skill_type=SkillType.FROZEN_DROPS,
            description="The bean concentrate to manifest multiple frozen drops to let them fall on the enemy.",
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            cooldown=2,
            base_value=1,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.FROST,
                    1,
                )
            ],
            hits=3,
            droppable=False,
            image_url="https://i.imgur.com/r0ZqBon.png",
            author="Waldheld",
        )


class DonerKebab(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Döner Kebab",
            skill_type=SkillType.DONER_KEBAB,
            description=(
                "With great speed you skillfuilly assemble a beatiful doner "
                "kebab and toss it at your foe. Has a small chance to blind and poison your target."
            ),
            information="",
            skill_effect=SkillEffect.PHYSICAL_DAMAGE,
            cooldown=0,
            base_value=1,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.POISON,
                    1,
                    application_chance=0.2,
                ),
                SkillStatusEffect(
                    StatusEffectType.BLIND,
                    1,
                    application_chance=0.2,
                ),
            ],
            droppable=False,
            image_url="https://i.imgur.com/mFR1cN5.png",
            author="Lusa",
        )


class KebabSmile(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Kebab Man Smile",
            skill_type=SkillType.KEBAB_SMILE,
            description=(
                "You embody the friendly kebab man and embolden your party with phrases such as "
                "'Yes chef!', 'With or without onion?' and 'Ahh why not spicy?'. Everyone feels "
                " happy and heals for a small amount."
            ),
            information="",
            skill_effect=SkillEffect.HEALING,
            cooldown=3,
            base_value=0.1,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.CLEANSE,
                    1,
                ),
            ],
            aoe=True,
            droppable=False,
            image_url="https://i.imgur.com/TD9P3CR.png",
            author="Lusa",
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
            author="Lusa",
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
            min_level=4,
            base_value=0.17,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.HEAL_OVER_TIME,
                    5,
                    StatusEffectApplication.RAW_ATTACK_VALUE,
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
            base_value=0.10,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.HEAL_OVER_TIME,
                    5,
                    StatusEffectApplication.RAW_ATTACK_VALUE,
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


class Foresight(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Creepy Glass Ball",
            skill_type=SkillType.FORESIGHT,
            description=(
                "The magic orb of space and time grants you a small glimpse of the future. "
                "Most of the time it just shows you embarassing memories from your childhood though. "
                "Your party will take reduced damage in the next two turns. "
            ),
            information="",
            skill_effect=SkillEffect.BUFF,
            cooldown=6,
            min_level=5,
            base_value=45,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.PROTECTION,
                    2,
                    StatusEffectApplication.ATTACK_VALUE,
                ),
            ],
            stacks=3,
            aoe=True,
            weight=30,
            reset_after_encounter=False,
            default_target=SkillTarget.SELF,
            image_url="https://i.imgur.com/lgBwv4v.png",
            author="Lusa",
        )


class ColorfulVase(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Colorful Vase",
            skill_type=SkillType.COLORFUL_VASE,
            description=(
                "A beautiful vase in vibrant colors, it will definitely brighten "
                "up your room (or even your mind). Heals you and guarantees a critical "
                "hit on your next two turns. However, you are also blinded."
            ),
            information="",
            skill_effect=SkillEffect.HEALING,
            cooldown=5,
            min_level=2,
            base_value=0.4,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.CLEANSE,
                    1,
                ),
                SkillStatusEffect(
                    StatusEffectType.ZONED_IN,
                    2,
                ),
                SkillStatusEffect(
                    StatusEffectType.BLIND,
                    2,
                ),
            ],
            stacks=3,
            aoe=False,
            reset_after_encounter=False,
            uniques=[],
            default_target=SkillTarget.SELF,
            image_url="https://i.imgur.com/BWMS7qy.png",
            author="Kiwi",
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


class NeuronActivation(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Neuron Activation",
            skill_type=SkillType.NEURON_ACTIVATION,
            description=(
                "A spark lights up in the vast and dark space inside your head. It slowly rises upwards and shines bright and strong. "
                "A neuron fired off a signal! This historical event will dramatically increase the effect of your next skill."
            ),
            information="",
            skill_effect=SkillEffect.BUFF,
            cooldown=8,
            min_level=4,
            base_value=85,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.NEURON_ACTIVE,
                    1,
                    StatusEffectApplication.ATTACK_VALUE,
                )
            ],
            stacks=2,
            aoe=False,
            weight=25,
            reset_after_encounter=False,
            uniques=[],
            default_target=SkillTarget.SELF,
            image_url="https://i.imgur.com/gVVnWTi.png",
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
            uniques=[SkillType.GENERATIONAL_SLIPPER],
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


class CoolCucumber(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Suspicious Cucumber",
            skill_type=SkillType.COOL_CUCUMBER,
            description=(
                "A cucumber with a slight glazing of something along one of its ends. "
                "It finds and inserts itself into the orifice of whatever it is aimed at with surprising ease. "
                "It will implant a seed, that will siphon health from the enemy to all party members for a few turns."
            ),
            information="",
            skill_effect=SkillEffect.PHYSICAL_DAMAGE,
            cooldown=5,
            base_value=3,
            min_level=4,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.PARTY_LEECH,
                    3,
                    StatusEffectApplication.ATTACK_VALUE,
                )
            ],
            stacks=4,
            reset_after_encounter=False,
            image_url="https://i.imgur.com/eHO6xNE.jpeg",
            author="Solris",
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
            cooldown=8,
            base_value=7.5,
            stacks=2,
            weight=50,
            reset_after_encounter=False,
            image_url="https://i.imgur.com/tzbLY8h.png",
        )


class IceBall(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Ice Ball",
            skill_type=SkillType.ICE_BALL,
            description="Everyone can shoot fire balls, this ice ball should do the same but colder.",
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            cooldown=5,
            min_level=2,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.FROST,
                    1,
                )
            ],
            base_value=5.5,
            stacks=3,
            weight=70,
            reset_after_encounter=False,
            image_url="https://i.imgur.com/mFbbWVm.png",
            author="Waldheld",
        )


class PartyDrugs(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Party Drugs",
            skill_type=SkillType.PARTY_DRUGS,
            description=(
                "This stuff will make you taste colours and see things you cant even imagine when sober! "
                "You take a pill and immediately fire a purple-green beam of magical vomit at your enemy. "
                "You are high for the next 3 turns, ramdomly modifying your attacks."
            ),
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            cooldown=6,
            status_effects=[
                SkillStatusEffect(StatusEffectType.HIGH, 3, self_target=True)
            ],
            min_level=4,
            base_value=6,
            stacks=3,
            reset_after_encounter=False,
            image_url="https://i.imgur.com/M4P2k4J.png",
            author="Lusa",
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
            initial_cooldown=0,
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
            initial_cooldown=0,
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
            initial_cooldown=1,
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
                "forces you down to the floor. For 3 turns your attacks have a 30% "
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
                    1,
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
            max_hits=3,
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
                    application_chance=0.7,
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


class ChefsKnife(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Chef's Knife",
            skill_type=SkillType.CHEFS_KNIFE,
            description=(
                "The Bonterry stabs you with its knife. "
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
            custom_value=99,
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


class Erase(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Erase",
            skill_type=SkillType.ERASE,
            description=(
                "The Scribbler takes out his oversized pen and uses the eraser end to erase you."
            ),
            information="",
            skill_effect=SkillEffect.PHYSICAL_DAMAGE,
            initial_cooldown=1,
            cooldown=2,
            base_value=4,
            hits=1,
            aoe=False,
            droppable=False,
            image_url="https://i.imgur.com/Zgf5YHf.png",
            author="Lusa",
        )


class EyePoke(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Eye Poke",
            skill_type=SkillType.EYE_POKE,
            description=(
                "The Scribbler takes a few quick stabs at your eyes. Watch out!"
            ),
            information="",
            skill_effect=SkillEffect.PHYSICAL_DAMAGE,
            initial_cooldown=0,
            cooldown=3,
            base_value=1,
            hits=2,
            aoe=False,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.BLIND,
                    1,
                ),
            ],
            droppable=False,
            image_url="https://i.imgur.com/aJnhIlV.png",
            author="Lusa",
        )


class PaperCuts(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Paper Cuts",
            skill_type=SkillType.PAPER_CUTS,
            description=(
                "Light as a feather the Scribbler swooshes around, cutting everyone with its razor sharp paper edges."
            ),
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            initial_cooldown=0,
            cooldown=0,
            base_value=2,
            hits=1,
            aoe=True,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.BLEED,
                    1,
                    StatusEffectApplication.ATTACK_VALUE,
                ),
            ],
            droppable=False,
            image_url="https://i.imgur.com/YjWVjfA.png",
            author="Lusa",
        )


class OmaeWa(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Omae wa mou shindeiru",
            skill_type=SkillType.OMAE_WA,
            description=(
                "He teleports behind you and slowly unsheathes his katana. "
                "The moonlight is glistening and reflecting on his glasses. "
                "A faint smirk forms on his face. Then, THUNDER CRACKS! With a swift strike, he slices his opponent!"
            ),
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            initial_cooldown=0,
            cooldown=3,
            base_value=3.5,
            custom_crit=1,
            hits=1,
            max_targets=1,
            aoe=False,
            droppable=False,
            image_url="https://i.imgur.com/ZF21vKW.png",
            author="Lusa",
        )


class PotatoChip(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Potato Chip",
            skill_type=SkillType.POTATO_CHIP,
            description=(
                "He is calculating a million possibilities and figuring out the best way to defeat you. "
                "He smiles, because he knows that you, yes you, are doomed! His attacks will hit a lot harder next turn."
            ),
            information="",
            skill_effect=SkillEffect.BUFF,
            initial_cooldown=3,
            cooldown=3,
            base_value=30,
            aoe=False,
            default_target=SkillTarget.SELF,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.INSPIRED,
                    1,
                    StatusEffectApplication.ATTACK_VALUE,
                )
            ],
            droppable=False,
            image_url="https://i.imgur.com/ICdd9V7.png",
            author="Lusa",
        )


class Dakimakura(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Dakimakura",
            skill_type=SkillType.DAKIMAKURA,
            description=(
                "He throws his dakimakura at you! What is that awful smell? And why is it sticky??? "
                "You are so disgusted that you can't do anything on your next turn."
            ),
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            initial_cooldown=0,
            cooldown=1,
            base_value=1,
            aoe=False,
            hits=1,
            max_targets=2,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.STUN,
                    1,
                )
            ],
            droppable=False,
            image_url="https://i.imgur.com/wbMjzR0.png",
            author="Lusa",
        )


class WeebKawaii(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Kawaii Desu Neeee ~",
            skill_type=SkillType.WEEB_KAWAII,
            description=(
                "He uses his anime eyes to be extra cute just for you. "
                "You cannot resist the power of his UwU and you feel your will to fight him fade. "
                "You will deal halved damage on your next two turns."
            ),
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            initial_cooldown=0,
            cooldown=3,
            base_value=1,
            aoe=False,
            hits=2,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.SIMP,
                    2,
                )
            ],
            droppable=False,
            image_url="https://i.imgur.com/laNHppG.png",
            author="Lusa",
        )


class WeebSplaining(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Weeb-Splaining",
            skill_type=SkillType.WEEB_SPLAINING,
            description=(
                "He keeps on talking about his favourite anime and what a bitch the main character is for "
                "not going for the romantic route he wished for. He was obviously meant to be together "
                "with his male childhood friend! This keeps on going for so long that your ears start bleeding."
            ),
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            initial_cooldown=1,
            cooldown=1,
            base_value=3,
            aoe=True,
            hits=1,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.BLEED,
                    2,
                    StatusEffectApplication.ATTACK_VALUE,
                )
            ],
            droppable=False,
            image_url="https://i.imgur.com/ZSxtSfL.png",
            author="Lusa",
        )


class Alchemy(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Full Metal Alchemy",
            skill_type=SkillType.ALCHEMY,
            description=(
                "Through the law of equivalent exchange he "
                "transmutes his bottled up emotions and the dark terrors of his past into a pure, malicious "
                "energy affecting all of you. You get afflicted with random status effects."
            ),
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            initial_cooldown=2,
            cooldown=3,
            base_value=2.5,
            aoe=True,
            hits=1,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.RANDOM,
                    1,
                    StatusEffectApplication.ATTACK_VALUE,
                ),
                SkillStatusEffect(
                    StatusEffectType.FLUSTERED,
                    1,
                    application_chance=0.05,
                ),
                SkillStatusEffect(
                    StatusEffectType.STUN,
                    1,
                    application_chance=0.05,
                ),
                SkillStatusEffect(
                    StatusEffectType.BLEED,
                    10,
                    StatusEffectApplication.ATTACK_VALUE,
                    application_chance=0.05,
                ),
                SkillStatusEffect(
                    StatusEffectType.FROGGED,
                    2,
                    application_chance=0.05,
                ),
                SkillStatusEffect(
                    StatusEffectType.SIMP,
                    1,
                    application_chance=0.1,
                ),
            ],
            droppable=False,
            image_url="https://i.imgur.com/0t9hkLd.png",
            author="Lusa",
        )


class WeebiHameHa(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Weebi Hame Ha!",
            skill_type=SkillType.WEEBI_HAME_HA,
            description=(
                "A concentrated beam of pure anime power, filled with the love for his waifu, explodes from his palms "
                "and all over your face and body."
            ),
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            initial_cooldown=0,
            cooldown=10,
            base_value=1,
            aoe=True,
            custom_crit=1,
            hits=1,
            modifiable=False,
            droppable=False,
            image_url="https://i.imgur.com/B1Ig4Nj.png",
            author="Lusa",
        )


class WeebiDamaCharge1(BaseSkill):

    def __init__(self):
        super().__init__(
            name="HAAAAAAAAAA!!!",
            skill_type=SkillType.WEEBI_DAMA_CHARGE_1,
            description=(
                "He rises up into the air and with both arms held up high, he charges a massive ball of energy above his head. "
                "While doing so he does not stop screaming his lungs out. Maybe it increases his focus, who knows. "
                "It keeps getting bigger though, so you better do something fast!"
            ),
            information="",
            skill_effect=SkillEffect.BUFF,
            initial_cooldown=1,
            default_target=SkillTarget.SELF,
            cooldown=10,
            base_value=10000,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.INSPIRED,
                    1337,
                    StatusEffectApplication.ATTACK_VALUE,
                ),
            ],
            aoe=False,
            hits=1,
            modifiable=False,
            droppable=False,
            image_url="https://i.imgur.com/GfELHio.png",
            author="Lusa",
        )


class WeebiDamaCharge2(BaseSkill):

    def __init__(self):
        super().__init__(
            name="HAAAAAAAAAAaaaaAAAAAAAAAA!!!",
            skill_type=SkillType.WEEBI_DAMA_CHARGE_2,
            description=(
                "He keeps on screaming, its getting even more violent! "
                "Bolts of lightning start to zap around on the surface of the ever growing energy ball."
            ),
            information="",
            skill_effect=SkillEffect.BUFF,
            initial_cooldown=2,
            default_target=SkillTarget.SELF,
            cooldown=10,
            base_value=10000,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.INSPIRED,
                    6969,
                    StatusEffectApplication.ATTACK_VALUE,
                ),
            ],
            aoe=False,
            hits=1,
            modifiable=False,
            droppable=False,
            image_url="https://i.imgur.com/GfELHio.png",
            author="Lusa",
        )


class WeebiDamaCharge3(BaseSkill):

    def __init__(self):
        super().__init__(
            name="HAAAAAAAAAA- *Cough* -AAAAaAAaAeeaaAaaee!!!",
            skill_type=SkillType.WEEBI_DAMA_CHARGE_3,
            description=(
                "His screams start to become more of a screech as he pulls out the last of his energy reserves. "
                "The orb now blocks out most of the sky and starts to vibrate. Its gonna blow soon!"
            ),
            information="",
            skill_effect=SkillEffect.BUFF,
            initial_cooldown=3,
            default_target=SkillTarget.SELF,
            cooldown=10,
            base_value=10000,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.INSPIRED,
                    9001,
                    StatusEffectApplication.ATTACK_VALUE,
                ),
            ],
            aoe=False,
            hits=1,
            modifiable=False,
            droppable=False,
            image_url="https://i.imgur.com/GfELHio.png",
            author="Lusa",
        )


class WeebiDama(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Weebi-Dama",
            skill_type=SkillType.WEEBI_DAMA,
            description=(
                "With one final outcry he lowers his arms, dropping the immense mass down on you. Its Joever, you had a good run. "
                "Your bodies disintergrate instantly and nothing is left behind."
            ),
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            initial_cooldown=4,
            cooldown=0,
            base_value=2,
            aoe=True,
            hits=1,
            modifiable=False,
            droppable=False,
            image_url="https://i.imgur.com/GfELHio.png",
            author="Lusa",
        )


class MeowTiara(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Meow Tiara :3",
            skill_type=SkillType.MEOW_TIARA,
            description=(
                "She winks at you playfully and pulls out a cat eared tiara. With a cute twirl she skillfully "
                "tosses it towards you and it perfectly lands on your head. Wow! Suddenly you feel a spine shattering shock "
                "exploding inside your head, jolting through your entire body. You realize, that she is your queen and you love her forever. "
                "Your nose is bleeding and you cannot hurt her on your next turn."
            ),
            information="",
            skill_effect=SkillEffect.PHYSICAL_DAMAGE,
            initial_cooldown=0,
            cooldown=0,
            base_value=3,
            aoe=False,
            hits=1,
            max_targets=1,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.FLUSTERED,
                    1,
                ),
                SkillStatusEffect(
                    StatusEffectType.BLEED,
                    3,
                    StatusEffectApplication.ATTACK_VALUE,
                ),
            ],
            droppable=False,
            image_url="https://i.imgur.com/dXzQSrC.png",
            author="Lusa",
        )


class MeowSpiral(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Meow Spiral Heart Attack :3",
            skill_type=SkillType.MEOW_SPIRAL,
            description=(
                "She performs a twirly dance, waving her scepter in big, wavy spirals as sparkles form and slowly glitter around her. "
                "As she strikes a final pose, she raises it up high in the air and summons a large whirling spiral of funny shaped "
                "hearts that quickly grows and envelops you all. You realize that those 'hearts' actually hurt quite a lot "
                "when they smack you in the face!"
            ),
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            initial_cooldown=0,
            cooldown=1,
            base_value=1,
            aoe=False,
            hits=6,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.SIMP,
                    1,
                ),
                SkillStatusEffect(
                    StatusEffectType.BLEED,
                    3,
                    StatusEffectApplication.ATTACK_VALUE,
                ),
            ],
            droppable=False,
            image_url="https://i.imgur.com/x5t2E6h.png",
            author="Lusa",
        )


class MeowKiss(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Starlight Honeymeow Therapy Kiss :3",
            skill_type=SkillType.MEOW_KISS,
            description=(
                "Darkness beyond twilight, crimson beyond blood that flows, "
                "Buried in the stream of time is where your power grows. \n\n"
                "I pledge myself to conquer all the foes who stand "
                "Before the mighty gift bestowed in my unworthy hand. \n\n"
                "Let the fools who stand before me be destroyed by the power you and I possess! "
            ),
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            initial_cooldown=1,
            cooldown=2,
            base_value=3,
            aoe=True,
            hits=1,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.BLEED,
                    3,
                    StatusEffectApplication.ATTACK_VALUE,
                ),
                SkillStatusEffect(
                    StatusEffectType.STUN,
                    1,
                    application_chance=0.3,
                ),
                SkillStatusEffect(
                    StatusEffectType.RANDOM,
                    1,
                    StatusEffectApplication.ATTACK_VALUE,
                ),
            ],
            droppable=False,
            image_url="https://i.imgur.com/yG15RnX.png",
            author="Lusa",
        )


class BackInMyDays(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Back In My Days",
            skill_type=SkillType.BACK_IN_MY_DAYS,
            description=(
                "He keeps talking and talking about the good old times and "
                "literally makes your ears bleed. Literally!!"
            ),
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            initial_cooldown=1,
            cooldown=0,
            base_value=4,
            aoe=True,
            hits=1,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.BLEED,
                    2,
                    StatusEffectApplication.ATTACK_VALUE,
                ),
            ],
            droppable=False,
            image_url="https://i.imgur.com/B11mxMc.png",
            author="Kiwi",
        )


class OutdatedAdvice(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Outdated Advice",
            skill_type=SkillType.OUTDATED_ADVICE,
            description=(
                "The Boomer gives you unsolicited and completely irrelevant advice "
                "and makes you question your own judgement. "
            ),
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            initial_cooldown=0,
            cooldown=1,
            base_value=1,
            aoe=False,
            hits=1,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.BLIND,
                    2,
                ),
            ],
            droppable=False,
            image_url="https://i.imgur.com/Af2MfSG.png",
            author="Kiwi",
        )


class NostalgiaBomb(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Nostalgia Bomb",
            skill_type=SkillType.NOSTALGIA_BOMB,
            description=(
                "The Boomer reminisces about his 'glory days' with such intensity, "
                "that it creates a wave of nostalgia. You get lost in your own "
                "memories and suddenly vividly remember all the times you embarrassed yourself."
            ),
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            initial_cooldown=1,
            cooldown=2,
            base_value=5,
            aoe=True,
            hits=1,
            status_effects=[],
            droppable=False,
            image_url="https://i.imgur.com/Rno01UO.png",
            author="Kiwi",
        )


class BigSalami(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Big Ass Salami",
            skill_type=SkillType.BIG_SALAMI,
            description=(
                "He takes out a big ass salami and slaps you in the face with it. Twice."
            ),
            information="",
            skill_effect=SkillEffect.PHYSICAL_DAMAGE,
            initial_cooldown=0,
            cooldown=0,
            base_value=1,
            aoe=False,
            hits=2,
            custom_crit=0,
            max_targets=1,
            no_scaling=True,
            status_effects=[],
            droppable=False,
            image_url="https://i.imgur.com/m1uToVo.png",
            author="Waldheld",
        )


class WienerBomb(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Wiener Bomb",
            skill_type=SkillType.WIENER_BOMB,
            description=(
                "Is this a delicious bbq you're smelling? NO! It's a bomb! "
                "A bomb filled with wieners!! It explodes and shoots flaming hot wieners everywhere!"
            ),
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            initial_cooldown=1,
            cooldown=1,
            base_value=4,
            aoe=True,
            hits=1,
            status_effects=[],
            droppable=False,
            image_url="https://i.imgur.com/qKaiEUL.png",
            author="Waldheld",
        )


class BratwurstBreak(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Delicious Bratwurst Break",
            skill_type=SkillType.BRATWURST_BREAK,
            description=(
                "The Sausage Butcher munches on his own supply! He eats a bratwurst and heals himself."
            ),
            information="",
            skill_effect=SkillEffect.HEALING,
            default_target=SkillTarget.SELF,
            initial_cooldown=2,
            cooldown=2,
            base_value=0.25,
            aoe=False,
            hits=1,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.CLEANSE,
                    1,
                ),
            ],
            droppable=False,
            image_url="https://i.imgur.com/r9JxieA.png",
            author="Waldheld",
        )


class FurryHug(BaseSkill):

    def __init__(self):
        super().__init__(
            name="The Furry Hug",
            skill_type=SkillType.FURRY_HUG,
            description=(
                "You feel your throat swelling up. The amount of fur that appeared "
                "almost chokes you. Also your eyes start to tear. You can’t see shit anymore."
            ),
            information="",
            skill_effect=SkillEffect.PHYSICAL_DAMAGE,
            cooldown=0,
            base_value=1,
            aoe=True,
            hits=1,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.BLIND,
                    1,
                ),
            ],
            droppable=False,
            image_url="https://i.imgur.com/9mhfVc1.jpeg",
            author="Feye",
        )


class RoughLove(BaseSkill):

    def __init__(self):
        super().__init__(
            name="Rough Love",
            skill_type=SkillType.ROUGH_LOVE,
            description=(
                "Mango starts to shower you with her affection. "
                "She starts to groom you and you can feel how your skin rips apart. "
            ),
            information="",
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            cooldown=1,
            base_value=3,
            aoe=False,
            hits=1,
            status_effects=[
                SkillStatusEffect(
                    StatusEffectType.BLEED,
                    3,
                    StatusEffectApplication.ATTACK_VALUE,
                ),
            ],
            droppable=False,
            image_url="https://i.imgur.com/DIXSht4.jpeg",
            author="Feye",
        )


class NoThankYou(BaseSkill):

    def __init__(self):
        super().__init__(
            name="No Thank You",
            skill_type=SkillType.NO_THANK_YOU,
            description=(
                "You notice Mango rubbing around your legs when she suddenly stops. "
                "She has had enough. The next thing you see is a polished claw aiming for your face."
            ),
            information="",
            skill_effect=SkillEffect.PHYSICAL_DAMAGE,
            initial_cooldown=2,
            cooldown=2,
            base_value=4,
            aoe=False,
            hits=1,
            droppable=False,
            image_url="https://i.imgur.com/yhiC1w8.jpeg",
            author="Feye",
        )
