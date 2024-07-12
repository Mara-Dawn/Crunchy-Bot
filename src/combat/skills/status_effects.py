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
