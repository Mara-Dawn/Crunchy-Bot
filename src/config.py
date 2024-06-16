class Config:

    # General Combat
    COMBAT_INITIAL_WAIT = 90

    ENEMY_HEALTH_SCALING = {
        1: 7.88,
        2: 11.66,
        3: 34.48,
        4: 72.59,
        5: 142.57,
        6: 204.11,
        7: 341.81,
        8: 461.41,
        9: 589.27,
        10: 764.64,
        11: 1114.75,
        12: 1486.36,
        # 12: 1751.51,
    }

    OPPONENT_DAMAGE_BASE = {
        1: 250,
        2: 274.05,
        3: 331.78,
        4: 393.60,
        5: 471.88,
        6: 563.82,
        7: 618.98,
        8: 671.76,
        9: 734.08,
        10: 792.80,
        11: 845.32,
        12: 1012.75,
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

    # Code Block Formatting
    ENEMY_MAX_WIDTH = 30
    COMBAT_EMBED_MAX_WIDTH = 40
    ITEM_MAX_WIDTH = 40
    SHOP_ITEM_MAX_WIDTH = 40
    INVENTORY_ITEM_MAX_WIDTH = 50

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
