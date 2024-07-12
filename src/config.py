class Config:

    # General Combat
    # COMBAT_INITIAL_WAIT = 90
    COMBAT_INITIAL_WAIT = 10

    DEFAULT_TIMEOUT = 60 * 5
    SHORT_TIMEOUT = 60
    TIMEOUT_COUNT_LIMIT = 3

    ENEMY_HEALTH_SCALING = {
        1: 7.88,
        2: 11.66,
        3: 35.02,
        4: 71.34,
        5: 131.13,
        6: 195.01,
        7: 305.15,
        8: 413.28,
        9: 535.76,
        10: 688.03,
        11: 940.70,
        12: 1198.12,
        # 12: 1751.51,
    }

    OPPONENT_DAMAGE_BASE = {
        1: 250,
        2: 274.05,
        3: 325.79,
        4: 395.58,
        5: 458.11,
        6: 529.87,
        7: 586.03,
        8: 642.17,
        9: 703.50,
        10: 764.18,
        11: 822.77,
        12: 940.77,
        # 12: 1076.95,
    }

    CHARACTER_BASE_INITIATIVE = 10
    CHARACTER_ENCOUNTER_SCALING_FACOTR = 1
    OPPONENT_ENCOUNTER_SCALING_FACTOR = 0.95
    OPPONENT_LEVEL_SCALING_FACTOR = 0.97
    OPPONENT_DAMAGE_VARIANCE = 0.05
    SKILL_TYPE_PENALTY = 0.2

    ENCOUNTER_MIN_LVL_SCALING = 0.65
    ENEMY_HEALTH_LVL_FALLOFF = 0.95
    AVERAGE_PLAYER_POTENCY = 2

    # Status Effects
    BLEED_SCALING = 0.25
    BLIND_MISS_CHANCE = 0.5
    RAGE_QUIT_THRESHOLD = 0.1

    # Code Block Formatting
    ENEMY_MAX_WIDTH = 30
    COMBAT_EMBED_MAX_WIDTH = 40
    ITEM_MAX_WIDTH = 40
    SHOP_ITEM_MAX_WIDTH = 40
    INVENTORY_ITEM_MAX_WIDTH = 50

    # Guild Level Requirements
    LEVEL_REQUIREMENTS = {
        1: 10,
        2: 15,
        3: 25,
        4: 20,
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
