from combat.skills.status_effect import StatusEffect
from combat.skills.types import StatusEffectTrigger, StatusEffectType


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
            trigger=[StatusEffectTrigger.END_OF_TURN],
            consumed=[StatusEffectTrigger.END_OF_TURN],
            priority=1,
            emoji="🩹",
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
            override=True,
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
            stack=True,
        )


class Inspired(StatusEffect):

    def __init__(self):
        super().__init__(
            effect_type=StatusEffectType.INSPIRED,
            name="Inspired",
            description="Increased Crit Chance",
            trigger=[StatusEffectTrigger.ON_ATTACK],
            consumed=[StatusEffectTrigger.END_OF_TURN],
            emoji="🍑",
            display_status=True,
            delay_to_next_turn=True,
            override=True,
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
        )
