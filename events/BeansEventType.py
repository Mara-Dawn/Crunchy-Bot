from enum import Enum

class BeansEventType(str, Enum):
    DAILY = 'daily'
    GAMBA_COST = 'gamba_cost'
    GAMBA_PAYOUT = 'gamba_payout'
    BONUS_PAYOUT = 'bonus_payout'
    LOTTERY_PAYOUT = 'lottery_payout'
    LOOTBOX_PAYOUT = 'loot_box_payout'
    BALANCE_CHANGE = 'balance_change'
    SHOP_PURCHASE = 'shop_purchase'
    USER_TRANSFER = 'user_transfer'