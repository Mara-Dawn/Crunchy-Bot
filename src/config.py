class Config:

    # General Combat
    # COMBAT_INITIAL_WAIT = 90
    COMBAT_INITIAL_WAIT = 10

    DEFAULT_TIMEOUT = 60 * 3
    SHORT_TIMEOUT = 60
    TIMEOUT_COUNT_LIMIT = 2
    TIMEOUT_JAIL_TIME = 30
    KICK_JAIL_TIME = 60

    ENEMY_HEALTH_SCALING = {
        1: 8.40,
        2: 15.93,
        3: 38.41,
        4: 96.22,
        5: 190.19,
        6: 356.37,
        7: 771.77,
    }

    OPPONENT_DAMAGE_BASE = {
        1: 250,
        2: 272.80,
        3: 335.54,
        4: 418.76,
        5: 639.79,
        6: 748.42,
        7: 834.09,
    }

    AVERAGE_PLAYER_POTENCY = {
        1: 2,
        2: 2.3,
        3: 2.6,
        4: 3,
        5: 3.3,
        6: 3.7,
        7: 4,
    }

    CHARACTER_BASE_INITIATIVE = 10
    CHARACTER_LVL_HP_INCREASE = 25
    CHARACTER_ENCOUNTER_SCALING_FACOTR = 1
    OPPONENT_ENCOUNTER_SCALING_FACTOR = 0.95
    OPPONENT_LEVEL_SCALING_FACTOR = 0.97
    OPPONENT_DAMAGE_VARIANCE = 0.05
    SKILL_TYPE_PENALTY = 0.2

    ENCOUNTER_MIN_LVL_SCALING = 0.65
    ENCOUNTER_MAX_LVL_SIZE_SCALING = 2 / 3
    ENEMY_HEALTH_LVL_FALLOFF = 0.95

    # Status Effects
    BLEED_SCALING = 0.25
    POISON_SCALING = 0.15
    BLIND_MISS_CHANCE = 0.3
    BLIND_DIMINISHING_RETURNS = 0.6
    FROGGED_FAIL_CHANCE = 0.5
    RAGE_QUIT_THRESHOLD = 0.1

    # Code Block Formatting
    ENEMY_MAX_WIDTH = 30
    COMBAT_EMBED_MAX_WIDTH = 40
    ITEM_MAX_WIDTH = 40
    SHOP_ITEM_MAX_WIDTH = 40
    INVENTORY_ITEM_MAX_WIDTH = 50

    # Guild Level Requirements
    LEVEL_REQUIREMENTS = {
        1: 100,
        2: 150,
        3: 175,
        4: 200,
        5: 225,
        6: 250,
        7: 9999999,
    }
    BOSS_LEVELS = [3, 6, 9, 12]
    BOSS_RETRY_REQUIREMENT = 5
    BOSS_KEY_CLAIM_DELAY = 180

    # Scrap
    SCRAP_FORGE_MULTI = 1.5
    SCRAP_SHOP_MULTI = 5
