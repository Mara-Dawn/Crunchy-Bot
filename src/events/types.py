from enum import Enum


class EventType(str, Enum):
    INTERACTION = "interaction"
    JAIL = "jail"
    TIMEOUT = "timeout"
    QUOTE = "quote"
    SPAM = "spam"
    BEANS = "beans"
    EQUIPMENT = "equipment"
    INVENTORY = "inventory"
    INVENTORYBATCH = "inventory_batch"
    LOOTBOX = "loot_box"
    BAT = "bat"
    PREDICTION = "prediction"
    GARDEN = "garden"
    NOTIFICATION = "notification"
    ENCOUNTER = "encounter"
    COMBAT = "combat"
    STATUS_EFFECT = "status_effect"
    KARMA = "karma"


class BeansEventType(str, Enum):
    DAILY = "daily"
    SEASON_START = "season_start"
    GAMBA_COST = "gamba_cost"
    GAMBA_PAYOUT = "gamba_payout"
    BONUS_PAYOUT = "bonus_payout"
    LOTTERY_PAYOUT = "lottery_payout"
    LOOTBOX_PAYOUT = "loot_box_payout"
    BALANCE_CHANGE = "balance_change"
    SHOP_PURCHASE = "shop_purchase"
    SHOP_BUYBACK = "shop_buyback"
    USER_TRANSFER = "user_transfer"
    PREDICTION_BET = "prediction_bet"
    PREDICTION_PAYOUT = "prediction_payout"
    PREDICTION_REFUND = "prediction_refund"
    PRESTIGE = "prestige"
    BEAN_PLANT = "bean_plant"
    BEAN_HARVEST = "bean_harvest"
    COMBAT_LOOT = "combat_loot"


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


class GardenEventType(str, Enum):
    WATER = "water"
    PLANT = "plant"
    REMOVE = "remove"
    HARVEST = "harvest"
    NOTIFICATION = "notification"


class EncounterEventType(str, Enum):
    SPAWN = "spawn"
    INITIATE = "initiate"
    COUNTDOWN = "countdown"
    NEW_ROUND = "new_round"
    MEMBER_REQUEST_JOIN = "member_request_join"
    MEMBER_ENGAGE = "member_engage"
    MEMBER_DEFEAT = "member_defeat"
    MEMBER_REVIVE = "member_revive"
    FORCE_SKIP = "force_skip"
    MEMBER_LEAVING = "member_leaving"
    MEMBER_OUT = "member_timeout"
    MEMBER_DISENGAGE = "member_disengage"
    ENEMY_DEFEAT = "enemy_defeat"
    ENEMY_PHASE_CHANGE = "enemy_phase_change"
    END = "end"
    CLEANUP = "cleanup"
    PENALTY50 = "penalty_50"
    PENALTY75 = "penalty_75"
    REMOVE_RESTRICTION = "remove_restriction"


class CombatEventType(str, Enum):
    STATUS_EFFECT = "status_effect"
    STATUS_EFFECT_OUTCOME = "status_effect_outcome"
    ENCHANTMENT_EFFECT = "enchantment_effect"
    ENCHANTMENT_EFFECT_OUTCOME = "enchantment_effect_outcome"
    MEMBER_TURN_SKIP = "member_turn_skip"
    MEMBER_TURN_ACTION = "member_turn_action"
    MEMBER_TURN = "member_turn"
    MEMBER_TURN_STEP = "member_turn_step"
    ENEMY_TURN = "enemy_turn"
    ENEMY_TURN_STEP = "enemy_turn_step"
    MEMBER_END_TURN = "member_end_turn"
    ENEMY_END_TURN = "enemy_end_turn"


class EquipmentEventType(str, Enum):
    SHOP_BUY = "shop_buy"


class UIEventType(str, Enum):
    STOP_INTERACTIONS = "stop_interactions"
    RESUME_INTERACTIONS = "resume_interactions"
    SHOW_INVENTORY = "show_inventory"
    SHOW_SHOP = "show_shop"
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

    INVENTORY_REFRESH = "inventory_refresh"
    INVENTORY_RESPONSE_CONFIRM_SUBMIT = "inventory_response_confirm_submit"
    INVENTORY_USER_REFRESH = "inventory_user_refresh"
    INVENTORY_ITEM_ACTION = "inventory_item_action"
    INVENTORY_SELL = "inventory_sell"
    INVENTORY_COMBINE = "inventory_combine"

    GARDEN_SELECT_PLOT = "garden_select_plot"
    GARDEN_DETACH = "garden_detach"

    GARDEN_PLOT_WATER = "garden_plot_water"
    GARDEN_PLOT_PLANT = "garden_plot_plant"
    GARDEN_PLOT_HARVEST = "garden_plot_harvest"
    GARDEN_PLOT_BACK = "garden_plot_back"
    GARDEN_PLOT_REMOVE = "garden_plot_remove"
    GARDEN_REFRESH = "garden_plot_refresh"
    GARDEN_PLOT_BLOCK = "garden_plot_block"

    COMBAT_LOADED = "combat_loaded"
    COMBAT_ENGAGE = "combat_engage"
    COMBAT_REMOVE_RESTRICTION = "combat_remove_restriction"
    COMBAT_LEAVE = "combat_leave"
    COMBAT_APPROVE = "combat_approve"
    COMBAT_INITIATE = "combat_initiate"
    COMBAT_USE_SKILL = "combat_use_skill"
    COMBAT_DM_PING = "combat_dm_ping"
    COMBAT_TIMEOUT = "combat_timeout"
    COMBAT_FULL = "combat_full"
    COMBAT_DISAPPEAR = "combat_disappear"
    COMBAT_FORCE_USE = "combat_force_use"

    CLAIM_SPECIAL_DROP = "claim_special_drop"

    MAIN_MENU_STATE_CHANGE = "main_menu_state_change"

    GEAR_EQUIP = "gear_equip"
    GEAR_DISMANTLE = "gear_dismantle"
    GEAR_OPEN_SELECT = "gear_open_select"
    GEAR_LOCK = "gear_lock"
    GEAR_UNLOCK = "gear_unlock"

    SKILL_EQUIP_VIEW = "skill_equip_view"
    SKILL_MANAGE_VIEW = "skill_manage_view"
    SKILLS_EQUIP = "skills_equip"
    SKILL_EQUIP = "skill_equip"

    FORGE_VIEW = "forge_view"
    FORGE_USE = "forge_use"
    FORGE_COMBINE = "forge_combine"
    FORGE_OPEN_SHOP = "forge_open_select"
    FORGE_SHOP_BUY = "forge_shop_buy"
    FORGE_ADD_ITEM = "forge_add_item"
    FORGE_CLEAR = "forge_clear"

    ENCHANTMENTS_OPEN = "enchantments_open"
    ENCHANTMENTS_APPLY = "enchantments_apply"

    SCRAP_BALANCE_CHANGED = "scrap_balance_changed"

    COMBAT_ENGAGE_UPDATE = "combat_engage_update"
    ENCOUNTER_INITIATED = "encounter_initiated"

    USER_SETTING_EDIT = "user_setting_edit"
    USER_SETTING_STATE = "user_setting_state"
    USER_SETTING_SHOW_OVERVIEW = "user_setting_show_overview"
    USER_SETTING_APPLY = "user_setting_apply"
    USER_SETTING_REFRESH = "user_setting_refresh"
