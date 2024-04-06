from enum import Enum


class EventType(str, Enum):
    INTERACTION = "interaction"
    JAIL = "jail"
    TIMEOUT = "timeout"
    QUOTE = "quote"
    SPAM = "spam"
    BEANS = "beans"
    INVENTORY = "inventory"
    LOOTBOX = "loot_box"
    BAT = "bat"


class BeansEventType(str, Enum):
    DAILY = "daily"
    GAMBA_COST = "gamba_cost"
    GAMBA_PAYOUT = "gamba_payout"
    BONUS_PAYOUT = "bonus_payout"
    LOTTERY_PAYOUT = "lottery_payout"
    LOOTBOX_PAYOUT = "loot_box_payout"
    BALANCE_CHANGE = "balance_change"
    SHOP_PURCHASE = "shop_purchase"
    USER_TRANSFER = "user_transfer"


class JailEventType(str, Enum):
    JAIL = "jail"
    RELEASE = "release"
    SLAP = "slap"
    PET = "pet"
    FART = "fart"
    INCREASE = "increase"
    REDUCE = "reduce"


class LootBoxEventType(str, Enum):
    DROP = "drop"
    CLAIM = "claim"
    BUY = "buy"
    OPEN = "open"


class UIEventType(str, Enum):
    STOP_INTERACTIONS = "stop_interactions"
    SHOW_INVENTORY = "show_inventory"
    SHOP_BUY = "shop_buy"
    SHOP_CHANGED = "shop_changed"
    SHOP_REFRESH = "refresh_shop"
    SHOP_DISABLE = "disable_shop"
    SHOP_RESPONSE_REFRESH = "refresh_shop_response"
    SHOP_RESPONSE_DISABLE = "disable_shop_response"
    SHOP_RESPONSE_EMOJI_UPDATE = "update_shop_response_emoji"
    SHOP_RESPONSE_CONFIRM_SUBMIT = "shop_response_confirm_submit"
    SHOP_RESPONSE_USER_SUBMIT = "shop_response_user_submit"
    SHOP_RESPONSE_COLOR_SUBMIT = "shop_response_color_submit"
    SHOP_RESPONSE_REACTION_SUBMIT = "shop_response_reaction_submit"
    REACTION_SELECTED = "reaction_selected"
    CLAIM_LOOTBOX = "claim_lootbox"
