class Config:

    # General Combat
    COMBAT_INITIAL_WAIT = 90
    # COMBAT_INITIAL_WAIT = 10

    DEFAULT_TIMEOUT = 60 * 3
    SHORT_TIMEOUT = 60
    TIMEOUT_COUNT_LIMIT = 2

    ENEMY_HEALTH_SCALING = {
        1: 8.40,
        2: 14.18,
        3: 31.77,
        4: 56.63,
        5: 97.03,
        6: 135.81,
        7: 205.78,
        8: 270.94,
        9: 348.14,
        10: 443.79,
        11: 590.67,
        12: 747.50,
    }

    OPPONENT_DAMAGE_BASE = {
        1: 250,
        2: 274.05,
        3: 335.33,
        4: 381.54,
        5: 458.47,
        6: 516.59,
        7: 567.94,
        8: 619.23,
        9: 672.61,
        10: 726.07,
        11: 778.43,
        12: 851.96,
    }

    AVERAGE_PLAYER_POTENCY = {
        1: 2,
        2: 2.3,
        3: 2.6,
        4: 3,
        5: 3.3,
        6: 3.7,
        7: 4,
        8: 3,
        9: 3,
        10: 3,
        11: 3,
        12: 3,
    }

    CHARACTER_BASE_INITIATIVE = 10
    CHARACTER_LVL_HP_INCREASE = 25
    CHARACTER_ENCOUNTER_SCALING_FACOTR = 1
    OPPONENT_ENCOUNTER_SCALING_FACTOR = 0.95
    OPPONENT_LEVEL_SCALING_FACTOR = 0.97
    OPPONENT_DAMAGE_VARIANCE = 0.05
    SKILL_TYPE_PENALTY = 0.2

    ENCOUNTER_MIN_LVL_SCALING = 0.65
    ENEMY_HEALTH_LVL_FALLOFF = 0.95

    # Status Effects
    BLEED_SCALING = 0.25
    POISON_SCALING = 0.15
    BLIND_MISS_CHANCE = 0.5
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
        1: 15,
        2: 25,
        3: 35,
        # 3: 1,
        4: 99999,
        5: 20,
        6: 25,
        7: 25,
        8: 25,
        9: 30,
        10: 30,
        11: 35,
        12: 40,
    }
    BOSS_LEVELS = [3, 6, 9, 12]
    BOSS_RETRY_REQUIREMENT = 1
    BOSS_KEY_CLAIM_DELAY = 180

    # Scrap
    SCRAP_FORGE_MULTI = 1.5
    SCRAP_SHOP_MULTI = 5
