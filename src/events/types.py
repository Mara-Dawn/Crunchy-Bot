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
    PREDICTION = "prediction"


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
    PREDICTION_BET = "prediction_bet"
    PREDICTION_PAYOUT = "prediction_payout"
    PREDICTION_REFUND = "prediction_refund"


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


class PredictionEventType(str, Enum):
    SUBMIT = "submit"
    APPROVE = "approve"
    LOCK = "lock"
    UNLOCK = "unlock"
    DENY = "deny"
    EDIT = "edit"
    PLACE_BET = "place_bet"
    RESOLVE = "resolve"
    REFUND = "refund"


class UIEventType(str, Enum):
    STOP_INTERACTIONS = "stop_interactions"
    SHOW_INVENTORY = "show_inventory"
    SHOP_BUY = "shop_buy"
    SHOP_CHANGED = "shop_changed"
    SHOP_REFRESH = "refresh_shop"
    SHOP_USER_REFRESH = "refresh_user_shop"
    SHOP_DISABLE = "disable_shop"
    SHOP_RESPONSE_REFRESH = "refresh_shop_response"
    SHOP_RESPONSE_DISABLE = "disable_shop_response"
    SHOP_RESPONSE_EMOJI_UPDATE = "update_shop_response_emoji"
    SHOP_RESPONSE_CONFIRM_SUBMIT = "shop_response_confirm_submit"
    SHOP_RESPONSE_USER_SUBMIT = "shop_response_user_submit"
    SHOP_RESPONSE_COLOR_SUBMIT = "shop_response_color_submit"
    SHOP_RESPONSE_REACTION_SUBMIT = "shop_response_reaction_submit"
    SHOP_RESPONSE_PREDICTION_SUBMIT = "shop_response_prediction_submit"
    REACTION_SELECTED = "reaction_selected"
    CLAIM_LOOTBOX = "claim_lootbox"
    UPDATE_RANKINGS = "update_rankings"

    PREDICTION_REFRESH_ALL = "refresh_prediction_all"
    PREDICTION_USER_REFRESH = "refresh_user_prediction"

    PREDICTION_MODERATION_REFRESH_ALL = "refresh_prediction_moderation_all"
    PREDICTION_MODERATION_REFRESH = "refresh_prediction_moderation"
    PREDICTION_MODERATION_DISABLE = "disable_prediction_moderation"
    PREDICTION_MODERATION_CHANGED = "prediction_moderation_changed"
    PREDICTION_MODERATION_EDIT = "edit_prediction_moderation"

    PREDICTION_INTERACTION_REFRESH = "refresh_prediction_interaction"
    PREDICTION_INTERACTION_DENY = "deny_prediction_interaction"
    PREDICTION_INTERACTION_REFUND = "refund_prediction_interaction"
    PREDICTION_INTERACTION_APPROVE = "approve_prediction_interaction"
    PREDICTION_INTERACTION_LOCK = "lock_prediction_interaction"
    PREDICTION_INTERACTION_UNLOCK = "unlock_prediction_interaction"
    PREDICTION_INTERACTION_EDIT = "edit_prediction_interaction"
    PREDICTION_INTERACTION_CONFIRM_OUTCOME = "confirm_prediction_outcome_interaction"
    PREDICTION_INTERACTION_PARENT_CHANGED = "prediction_interaction_parent_changed"
    PREDICTION_INTERACTION_RESUBMIT = "prediction_interaction_resubmit"

    PREDICTION_REFRESH = "refresh_prediction"
    PREDICTION_FULL_REFRESH = "refresh_prediction_full"
    PREDICTION_DISABLE = "disable_prediction"
    PREDICTION_CHANGED = "prediction_changed"
    PREDICTION_SELECT = "select_prediction"
    PREDICTION_PLACE_BET = "place_bet_prediction"
    PREDICTION_BET_REFRESH = "prediction_bet_refresh"
    PREDICTION_OPEN_UI = "prediction_open_ui"
    PREDICTION_PREDICTION_SUBMIT = "prediction_prediction_submit"

    PREDICTION_OVERVIEW_REFRESH = "prediction_overview_refresh"
