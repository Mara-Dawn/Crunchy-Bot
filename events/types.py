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
    REFRESH_SHOP = "refresh_shop"
    DISABLE_SHOP = "disable_shop"
    REFRESH_SHOP_RESPONSE = "refresh_shop_response"
    DISABLE_SHOP_RESPONSE = "disable_shop_response"
    UPDATE_SHOP_RESPONSE_EMOJI = "update_shop_response_emoji"
