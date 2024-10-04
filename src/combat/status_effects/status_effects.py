from combat.skills.types import SkillEffect
from combat.status_effects.status_effect import (
    StatusEffect,
)
from combat.status_effects.types import (
    StatusEffectTrigger,
    StatusEffectType,
)


class Bleed(StatusEffect):

    def __init__(self):
        super().__init__(
            effect_type=StatusEffectType.BLEED,
            name="Bleed",
            description="You slowly bleed out.",
            trigger=[StatusEffectTrigger.END_OF_TURN],
            consumed=[StatusEffectTrigger.END_OF_TURN],
            emoji="🩸",
            display_status=True,
        )


class Cleanse(StatusEffect):

    def __init__(self):
        super().__init__(
            effect_type=StatusEffectType.CLEANSE,
            name="Cleanse",
            description="Cleanses Bleeding.",
            trigger=[StatusEffectTrigger.ON_SELF_APPLICATION],
            consumed=[StatusEffectTrigger.ON_SELF_APPLICATION],
            priority=1,
            max_stacks=1,
            emoji="🩹",
            apply_on_miss=True,
            override=True,
        )


class FullCleanse(StatusEffect):

    def __init__(self):
        super().__init__(
            effect_type=StatusEffectType.FULL_CLEANSE,
            name="Full Cleanse",
            description="Cleanses all ailments.",
            trigger=[StatusEffectTrigger.ON_SELF_APPLICATION],
            consumed=[StatusEffectTrigger.ON_SELF_APPLICATION],
            priority=1,
            max_stacks=1,
            emoji="🩹",
            apply_on_miss=True,
            override=True,
        )


class StatusImmune(StatusEffect):

    def __init__(self):
        super().__init__(
            effect_type=StatusEffectType.STATUS_IMMUNE,
            name="Status Immunity",
            description="Unaffected by harmful ailments.",
            trigger=[StatusEffectTrigger.ON_STATUS_APPLICATION],
            consumed=[StatusEffectTrigger.END_OF_APPLICANT_TURN],
            priority=1,
            emoji="🕶️",
            apply_on_miss=True,
            override=True,
            display_status=True,
            delay_consume=True,
            delay_for_source_only=True,
        )


class Flustered(StatusEffect):

    def __init__(self):
        super().__init__(
            effect_type=StatusEffectType.FLUSTERED,
            name="Flustered",
            description="You cannot harm your opponent.",
            trigger=[StatusEffectTrigger.ON_ATTACK],
            consumed=[StatusEffectTrigger.END_OF_TURN],
            emoji="😳",
            display_status=True,
            override=True,
            single_description=True,
            delay_consume=True,
            delay_for_source_only=True,
        )


class Simp(StatusEffect):

    def __init__(self):
        super().__init__(
            effect_type=StatusEffectType.SIMP,
            name="SO CUTE OMG",
            description="Your attacks are half as effective.",
            trigger=[StatusEffectTrigger.ON_ATTACK],
            consumed=[StatusEffectTrigger.END_OF_TURN],
            emoji="😍",
            display_status=True,
            stack=True,
            single_description=True,
            delay_consume=True,
            delay_for_source_only=True,
        )


class Blind(StatusEffect):

    def __init__(self):
        super().__init__(
            effect_type=StatusEffectType.BLIND,
            name="Blind",
            description="You have a chance to miss your attack.",
            trigger=[StatusEffectTrigger.ON_ATTACK],
            consumed=[StatusEffectTrigger.END_OF_TURN],
            emoji="👁️",
            display_status=True,
            override=True,
            single_description=True,
            delay_consume=True,
            delay_for_source_only=True,
        )


class Frost(StatusEffect):

    def __init__(self):
        super().__init__(
            effect_type=StatusEffectType.FROST,
            name="Frost",
            description="You are slowed.",
            trigger=[StatusEffectTrigger.ATTRIBUTE, StatusEffectTrigger.ON_ATTACK],
            consumed=[StatusEffectTrigger.END_OF_ROUND],
            emoji="🥶",
            display_status=True,
            delay_consume=True,
            single_description=True,
        )


class Evasive(StatusEffect):

    def __init__(self):
        super().__init__(
            effect_type=StatusEffectType.EVASIVE,
            name="Evasive",
            description="You have a chance to evade attacks.",
            trigger=[StatusEffectTrigger.ON_DAMAGE_TAKEN],
            consumed=[],
            emoji="➰",
            display_status=False,
            override=True,
            apply_on_miss=True,
        )


class RageQuit(StatusEffect):

    def __init__(self):
        super().__init__(
            effect_type=StatusEffectType.RAGE_QUIT,
            name="Rage Quit",
            description="'Ive had enough! You guys suck!' he proclaims and promptly leaves the instance.",
            trigger=[StatusEffectTrigger.START_OF_TURN],
            consumed=[],
            emoji="😡",
            display_status=False,
            override=True,
            apply_on_miss=True,
        )


class Rage(StatusEffect):

    def __init__(self):
        super().__init__(
            effect_type=StatusEffectType.RAGE,
            name="Rage",
            description="Your attacks cause bleeding",
            trigger=[StatusEffectTrigger.POST_ATTACK],
            consumed=[StatusEffectTrigger.POST_ATTACK],
            emoji="😡",
            display_status=True,
            stack=True,
            apply_on_miss=True,
        )


class Fear(StatusEffect):

    def __init__(self):
        super().__init__(
            effect_type=StatusEffectType.FEAR,
            name="Fear",
            description="You are scared.",
            trigger=[StatusEffectTrigger.ON_DAMAGE_TAKEN],
            consumed=[],
            emoji="😨",
            display_status=True,
            single_description=True,
            stack=True,
        )


class Chuckle(StatusEffect):

    def __init__(self):
        super().__init__(
            effect_type=StatusEffectType.CHUCKLE,
            name="Chuckle",
            description="You can barely contain your laughter.",
            trigger=[StatusEffectTrigger.ON_DAMAGE_TAKEN],
            consumed=[],
            emoji="🤡",
            display_status=True,
            single_description=True,
            stack=True,
        )


class Protection(StatusEffect):

    def __init__(self):
        super().__init__(
            effect_type=StatusEffectType.PROTECTION,
            name="Protection",
            description="Damage Reduction",
            trigger=[StatusEffectTrigger.ON_DAMAGE_TAKEN],
            consumed=[StatusEffectTrigger.END_OF_APPLICANT_TURN],
            emoji="🛡️",
            display_status=True,
            override=True,
            apply_on_miss=True,
            single_description=True,
            delay_consume=True,
        )


class Inspired(StatusEffect):

    def __init__(self):
        super().__init__(
            effect_type=StatusEffectType.INSPIRED,
            name="Inspired",
            description="Increased Damage",
            trigger=[StatusEffectTrigger.ON_ATTACK],
            consumed=[StatusEffectTrigger.END_OF_TURN],
            emoji="🍑",
            max_stacks=99999,
            display_status=True,
            override=True,
            apply_on_miss=True,
            delay_consume=True,
            delay_trigger=True,
            delay_for_source_only=True,
        )


class NeuronActive(StatusEffect):

    def __init__(self):
        super().__init__(
            effect_type=StatusEffectType.NEURON_ACTIVE,
            name="Neuron Active",
            description="Increased Damage",
            trigger=[StatusEffectTrigger.ON_ATTACK],
            consumed=[StatusEffectTrigger.END_OF_TURN],
            emoji="🧠",
            display_status=True,
            override=True,
            apply_on_miss=True,
            delay_consume=True,
            delay_trigger=True,
            delay_for_source_only=True,
        )


class ZonedIn(StatusEffect):

    def __init__(self):
        super().__init__(
            effect_type=StatusEffectType.ZONED_IN,
            name="Zoned In",
            description="Guaranteed Crit",
            trigger=[StatusEffectTrigger.ON_ATTACK],
            consumed=[StatusEffectTrigger.END_OF_TURN],
            emoji="🫨",
            display_status=True,
            override=True,
            apply_on_miss=True,
            delay_consume=True,
            delay_trigger=True,
            delay_for_source_only=True,
        )


class High(StatusEffect):

    def __init__(self):
        super().__init__(
            effect_type=StatusEffectType.HIGH,
            name="High",
            description="Your attacks randomly deal more or less damage.",
            trigger=[StatusEffectTrigger.ON_ATTACK],
            consumed=[StatusEffectTrigger.END_OF_TURN],
            emoji="🤯",
            display_status=True,
            stack=True,
            single_description=True,
            delay_consume=True,
            delay_trigger=True,
            delay_for_source_only=True,
        )


class Vulnerable(StatusEffect):

    def __init__(self):
        super().__init__(
            effect_type=StatusEffectType.VULNERABLE,
            name="Vulnerable",
            description="Damage is increased.",
            trigger=[StatusEffectTrigger.ON_DAMAGE_TAKEN],
            consumed=[StatusEffectTrigger.END_OF_APPLICANT_TURN],
            emoji="💥",
            display_status=True,
            single_description=True,
            delay_consume=True,
            override=True,
        )


class PhysVuln(StatusEffect):

    def __init__(self):
        super().__init__(
            effect_type=StatusEffectType.PHYS_VULN,
            name="Armor Crushed",
            description="Physical damage is increased.",
            trigger=[StatusEffectTrigger.ON_DAMAGE_TAKEN],
            consumed=[StatusEffectTrigger.END_OF_APPLICANT_TURN],
            emoji="🎇",
            display_status=True,
            single_description=True,
            delay_consume=True,
            override=True,
        )


class MagicVuln(StatusEffect):

    def __init__(self):
        super().__init__(
            effect_type=StatusEffectType.MAGIC_VULN,
            name="Mind Break",
            description="Magical damage is increased.",
            trigger=[StatusEffectTrigger.ON_DAMAGE_TAKEN],
            consumed=[StatusEffectTrigger.END_OF_APPLICANT_TURN],
            emoji="🎆",
            display_status=True,
            single_description=True,
            delay_consume=True,
            override=True,
        )


class Poison(StatusEffect):

    def __init__(self):
        super().__init__(
            effect_type=StatusEffectType.POISON,
            name="Poisoned",
            description="You inflict some of your outgoing damage back on yourself.",
            trigger=[StatusEffectTrigger.POST_ATTACK],
            consumed=[StatusEffectTrigger.END_OF_TURN],
            emoji="🤢",
            display_status=True,
            stack=True,
            delay_consume=True,
            delay_trigger=True,
            delay_for_source_only=True,
        )


class Random(StatusEffect):

    def __init__(self):
        super().__init__(
            effect_type=StatusEffectType.RANDOM,
            name="Random",
            description="You gain a random status effect.",
            trigger=[StatusEffectTrigger.ON_SELF_APPLICATION],
            consumed=[StatusEffectTrigger.ON_SELF_APPLICATION],
            emoji="",
            display_status=False,
        )


class DeathProtection(StatusEffect):

    def __init__(self):
        super().__init__(
            effect_type=StatusEffectType.DEATH_PROTECTION,
            name="Death Protection",
            description="Instead of dying you stay at 1 HP.",
            trigger=[StatusEffectTrigger.ON_DEATH],
            consumed=[StatusEffectTrigger.ON_DEATH],
            emoji="💞",
            damage_type=SkillEffect.HEALING,
            display_status=True,
            apply_on_miss=True,
        )


class HealOverTime(StatusEffect):

    def __init__(self):
        super().__init__(
            effect_type=StatusEffectType.HEAL_OVER_TIME,
            name="Heal",
            description="You gain health.",
            trigger=[StatusEffectTrigger.START_OF_TURN],
            consumed=[StatusEffectTrigger.START_OF_TURN],
            emoji="💚",
            damage_type=SkillEffect.HEALING,
            display_status=True,
        )


class Frogged(StatusEffect):

    def __init__(self):
        super().__init__(
            effect_type=StatusEffectType.FROGGED,
            name="Frogged",
            description="You were transformed into a frog.",
            trigger=[StatusEffectTrigger.START_OF_TURN],
            consumed=[StatusEffectTrigger.END_OF_TURN],
            emoji="🐸",
            display_status=True,
            override=True,
            single_description=True,
        )


class Stun(StatusEffect):

    def __init__(self):
        super().__init__(
            effect_type=StatusEffectType.STUN,
            name="Stun",
            description="You are stunned.",
            trigger=[StatusEffectTrigger.START_OF_TURN],
            consumed=[StatusEffectTrigger.END_OF_TURN],
            emoji="💤",
            display_status=True,
            override=True,
            single_description=True,
        )


class PartyLeech(StatusEffect):

    def __init__(self):
        super().__init__(
            effect_type=StatusEffectType.PARTY_LEECH,
            name="Leech Seed",
            description="You draw health from the enemy.",
            trigger=[StatusEffectTrigger.END_OF_TURN],
            consumed=[StatusEffectTrigger.END_OF_TURN],
            emoji="🌱",
            damage_type=SkillEffect.HEALING,
            display_status=True,
            override=True,
        )